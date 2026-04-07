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
Alter table users add column id VARCHAR(255);

select * from users;
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

-----FAMILY MEMBERS

CREATE TABLE IF NOT EXISTS family_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255) NOT NULL REFERENCES users(email) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    relationship VARCHAR(50),
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
    doctor_id  UUID NULL REFERENCES doctors(id) ON DELETE CASCADE,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), 0=Sunday, 1=Monday
    start_time TIME NOT NULL,
    end_time   TIME NOT NULL,
    slot_duration_minutes INT DEFAULT 15,
    slot_duration_minutes INT DEFAULT 15,
    UNIQUE (doctor_id, day_of_week, start_time)
);

create unique index idx_doctor_availability_doctor_day_time on doctor_availability (doctor_id, day_of_week);


-- ──────────────────────────────────────────────────────────────
-- 5. APPOINTMENTS
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS appointments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id      UUID REFERENCES patients(id) ON DELETE CASCADE,
    family_member_id UUID REFERENCES family_members(id) ON DELETE SET NULL,
    doctor_id       UUID REFERENCES doctors(id) ON DELETE CASCADE,
    appointment_at  TIMESTAMPTZ NOT NULL,
    duration_minutes INT DEFAULT 15,
    status          VARCHAR(20) DEFAULT 'scheduled'
                        CHECK (status IN ('pending', 'scheduled', 'completed', 'cancelled', 'no_show', 'in-progress', 'rescheduled')),
    reason          TEXT,
    notes           TEXT,
    cancelled_by    VARCHAR(255) REFERENCES users(email),
    cancelled_at    TIMESTAMPTZ,
    cancel_reason   TEXT,
    drive_link      VARCHAR(500),
    criticality_level INT DEFAULT 1 CHECK (criticality_level BETWEEN 0 AND 1),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);


CREATE OR REPLACE FUNCTION check_start_time_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF (
        SELECT COUNT(*) 
        FROM appointments 
        WHERE start_time = NEW.start_time
    ) == 2 THEN
        RETURN NULL;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION validate_appointment_slot()
RETURNS TRIGGER AS $$
DECLARE
    v_start_time TIME;
    v_end_time TIME;
    v_day_of_week INT;
    v_count INT;
BEGIN
    -- Extract day of week from appointment_at
    v_day_of_week := (EXTRACT(DOW FROM NEW.appointment_at)-1)%7;
    
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
    IF NEW.appointment_at::TIME < v_start_time OR NEW.appointment_at::TIME > v_end_time THEN
        RAISE EXCEPTION 'Appointment time % is not within doctor''s available hours (% to %)',
                NEW.appointment_at::TIME, v_start_time, v_end_time;
    END IF;

    
    IF NEW.appointment_at::TIME >= TIME '13:00:00'
        AND NEW.appointment_at::TIME < TIME '13:30:00' THEN
        RAISE EXCEPTION 'Appointments are not allowed between 1:00 PM and 1:30 PM (lunch break).';
    END IF;

        -- ✅ Overlapping appointments check (max 2 allowed)
        SELECT COUNT(*) INTO v_count
        FROM appointments a
        WHERE a.doctor_id = NEW.doctor_id
        AND a.status = 'scheduled'
        AND (
                NEW.appointment_at >= a.appointment_at AND 
                NEW.appointment_at < (a.appointment_at + INTERVAL '15 minutes')
        );

        IF v_count >= 2 THEN
            RAISE EXCEPTION 'Max 2 overlapping appointments reached.';
        END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
;


DROP TRIGGER IF EXISTS appointment_slot_validation ON appointments;
CREATE TRIGGER appointment_slot_validation
BEFORE INSERT ON appointments
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

CREATE TABLE IF NOT EXISTS google_form_submissions_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    appointment_date VARCHAR(20) NOT NULL,
    appointment_time VARCHAR(20) NOT NULL,
    submission_hash VARCHAR(255) UNIQUE NOT NULL,
    processed BOOLEAN DEFAULT TRUE,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL,
    error_message TEXT
);
drop table if exists google_form_submissions_log;
CREATE INDEX idx_submission_hash ON google_form_submissions_log(submission_hash);
