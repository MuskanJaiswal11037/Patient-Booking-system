-- Active: 1773814904573@@127.0.0.1@5432@medapp
-- ============================================================
--  Doctor-Patient Appointment System  |  PostgreSQL Schema
-- ============================================================

CREATE DATABASE medapp;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ──────────────────────────────────────────────────────────────
-- 1. USERS  (auth table, all roles)
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('patient', 'doctor', 'nurse', 'admin')),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

select * from users;
alter table users drop COLUMN id;

-- DOCTORS
CREATE TABLE IF NOT EXISTS doctors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255) UNIQUE NOT NULL REFERENCES users(email) ON DELETE CASCADE,
    specialty VARCHAR(100) NOT NULL,
    qualification VARCHAR(255),
    consultation_fee NUMERIC(10,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

------ NURSES
CREATE TABLE IF NOT EXISTS nurses(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255) UNIQUE NOT NULL REFERENCES users(email) ON DELETE CASCADE,
    department VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
-- 3. PATIENTS  (extended profile)
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS patients (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email    VARCHAR(255) UNIQUE NOT NULL REFERENCES users(email) ON DELETE CASCADE,
    date_of_birth DATE,
    blood_group   VARCHAR(5),
    allergies     TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

create table admin_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255) UNIQUE NOT NULL REFERENCES users(email) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
-- 4. DOCTOR AVAILABILITY  (weekly recurring slots)
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS doctor_availability (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id  UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Mon, 6=Sun
    start_time TIME NOT NULL,
    end_time   TIME NOT NULL,
    slot_duration_minutes INT DEFAULT 30,
    UNIQUE (doctor_id, day_of_week, start_time)
);

-- ──────────────────────────────────────────────────────────────
-- 5. APPOINTMENTS
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS appointments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id     UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id       UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    appointment_at  TIMESTAMPTZ NOT NULL,
    duration_minutes INT DEFAULT 30,
    status          VARCHAR(20) DEFAULT 'pending'
                        CHECK (status IN ('pending', 'scheduled', 'completed', 'cancelled', 'no_show')),
    reason          TEXT,
    notes           TEXT,
    cancelled_by    VARCHAR(255) REFERENCES users(email),
    cancelled_at    TIMESTAMPTZ,
    cancel_reason   TEXT,
    criticality_level VARCHAR(20) CHECK (criticality_level IN ('low', 'medium', 'high')) DEFAULT 'low',
    is_confirmed BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION check_doctor_availability(
    p_doctor_id UUID,
    p_appointment_at TIMESTAMP WITH TIME ZONE,
    p_appointment_id UUID DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN NOT EXISTS (
        SELECT 1 FROM appointments
        WHERE doctor_id = p_doctor_id
        AND status = 'scheduled'
        AND id != COALESCE(p_appointment_id, '00000000-0000-0000-0000-000000000000')
        AND appointment_at != p_appointment_at
     ) ;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION validate_appointment_slot()
RETURNS TRIGGER AS $$
DECLARE
    v_start_time TIME;
    v_end_time TIME;
    v_day_of_week INT;
BEGIN
    -- Extract day of week from appointment_at
    v_day_of_week := EXTRACT(DOW FROM NEW.appointment_at);
    
    -- Get doctor's availability for this day
    SELECT start_time, end_time INTO v_start_time, v_end_time
    FROM doctor_availability 
    WHERE doctor_id = NEW.doctor_id 
    AND day_of_week = v_day_of_week
    LIMIT 1;

    -- Check if doctor has availability on this day
    IF v_start_time IS NULL THEN
        RAISE EXCEPTION 'Doctor is not available on this day. Please choose a different date.';
    END IF;
        
    -- Check if appointment time falls within available hours
    IF NEW.appointment_at::TIME <= v_start_time OR NEW.appointment_at::TIME >= v_end_time THEN
        RAISE EXCEPTION 'Appointment time % is not within doctor''s available hours (% to %)',
                NEW.appointment_at::TIME, v_start_time, v_end_time;
    END IF;

    IF NEW.appointment_at < NOW() THEN
        RAISE EXCEPTION 'Appointment time cannot be in the past.';
    END IF;
    
    IF NEW.appointment_at::TIME >= TIME '13:00:00'
        AND NEW.appointment_at::TIME < TIME '13:30:00' THEN
        RAISE EXCEPTION 'Appointments are not allowed between 1:00 PM and 1:30 PM (lunch break).';
    END IF;
    -- Only check if status is 'scheduled'
    IF NEW.status = 'scheduled' THEN
        IF NOT check_doctor_availability(
            NEW.doctor_id, 
            NEW.appointment_at,
            NEW.id
        ) THEN
            RAISE EXCEPTION 'Doctor is busy during that time slot. Please choose a different time.';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
;


DROP TRIGGER IF EXISTS appointment_slot_validation ON appointments;
CREATE TRIGGER appointment_slot_validation
BEFORE INSERT OR UPDATE ON appointments
FOR EACH ROW EXECUTE FUNCTION validate_appointment_slot();


-- ──────────────────────────────────────────────────────────────
-- 7. FEEDBACK & RATINGS
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feedback (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id     UUID NOT NULL REFERENCES patients(id),
    doctor_id      UUID NOT NULL REFERENCES doctors(id),
    raw_feedback   TEXT NOT NULL,
    ai_rating      INT CHECK (ai_rating BETWEEN 1 AND 5),
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

create table calender_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    event_uid VARCHAR(255) NOT NULL,
    sequence INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INSERT INTO appointments (id, patient_id, doctor_id, appointment_at, status, reason, created_at, updated_at)
--             VALUES (%s,4e9d7565-a7f7-4764-8f76-61f56088ed19, 2df39159-ee26-4153-adcb-49ac1605e257, %s, %s, %s, NOW(), NOW())
--             id, appointment_at, status;


