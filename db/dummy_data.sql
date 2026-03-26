-- Active: 1773814904573@@127.0.0.1@5432@medapp
-- ============================================================
--  Doctor-Patient Appointment System  |  Dummy Data
--  Realistic test data with proper relationships
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 1. USERS (Doctors, Patients, Nurses)
-- ──────────────────────────────────────────────────────────────

-- Doctors
INSERT INTO users (id, email, password_hash, full_name, role, phone, is_active) VALUES
('doc_001', 'dr.sarah.williams@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Dr. Sarah Williams', 'doctor', '+91-9876543210', true),
('doc_002', 'dr.rajesh.kumar@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Dr. Rajesh Kumar', 'doctor', '+91-9876543211', true),
('doc_003', 'dr.emily.chen@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Dr. Emily Chen', 'doctor', '+91-9876543212', true),
('doc_004', 'dr.mohammed.ali@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Dr. Mohammed Ali', 'doctor', '+91-9876543213', true),
('doc_005', 'dr.priya.sharma@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Dr. Priya Sharma', 'doctor', '+91-9876543214', true),
('doc_006', 'dr.james.wilson@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Dr. James Wilson', 'doctor', '+91-9876543215', true),
('doc_007', 'dr.anita.desai@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Dr. Anita Desai', 'doctor', '+91-9876543216', true),
('doc_008', 'dr.david.brown@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Dr. David Brown', 'doctor', '+91-9876543217', true);

-- Patients
INSERT INTO users (id, email, password_hash, full_name, role, phone, is_active) VALUES
('pat_001', 'amit.patel@gmail.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Amit Patel', 'patient', '+91-9123456780', true),
('pat_002', 'sneha.reddy@yahoo.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Sneha Reddy', 'patient', '+91-9123456781', true),
('pat_003', 'john.smith@outlook.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'John Smith', 'patient', '+91-9123456782', true),
('pat_004', 'lakshmi.nair@gmail.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Lakshmi Nair', 'patient', '+91-9123456783', true),
('pat_005', 'rahul.verma@gmail.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Rahul Verma', 'patient', '+91-9123456784', true),
('pat_006', 'priya.gupta@hotmail.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Priya Gupta', 'patient', '+91-9123456785', true),
('pat_007', 'michael.johnson@gmail.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Michael Johnson', 'patient', '+91-9123456786', true),
('pat_008', 'kavita.singh@gmail.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Kavita Singh', 'patient', '+91-9123456787', true),
('pat_009', 'ravi.krishnan@yahoo.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Ravi Krishnan', 'patient', '+91-9123456788', true),
('pat_010', 'ananya.mehta@gmail.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Ananya Mehta', 'patient', '+91-9123456789', true),
('pat_011', 'sarah.thompson@outlook.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Sarah Thompson', 'patient', '+91-9123456790', true),
('pat_012', 'vikram.rao@gmail.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Vikram Rao', 'patient', '+91-9123456791', true);

-- Nurses
INSERT INTO users (id, email, password_hash, full_name, role, phone, is_active) VALUES
('nur_001', 'mary.jones@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Mary Jones', 'nurse', '+91-9876543220', true),
('nur_002', 'suresh.kumar@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Suresh Kumar', 'nurse', '+91-9876543221', true),
('nur_003', 'jennifer.davis@healthplus.com', '$2b$10$abcdefghijklmnopqrstuvwxyz1234567890', 'Jennifer Davis', 'nurse', '+91-9876543222', true);

-- ──────────────────────────────────────────────────────────────
-- 2. DOCTORS (Extended Profiles)
-- ──────────────────────────────────────────────────────────────
INSERT INTO doctors (user_id, specialty, qualification, consultation_fee) VALUES
('doc_001', 'Cardiology', 'MD, FACC - Harvard Medical School', 1500.00),
('doc_002', 'General Medicine', 'MBBS, MD - AIIMS Delhi', 800.00),
('doc_003', 'Pediatrics', 'MD Pediatrics - Johns Hopkins', 1000.00),
('doc_004', 'Orthopedics', 'MS Orthopedics, DNB - CMC Vellore', 1200.00),
('doc_005', 'Dermatology', 'MD Dermatology - JIPMER', 900.00),
('doc_006', 'Neurology', 'DM Neurology - NIMHANS', 1800.00),
('doc_007', 'Gynecology', 'MS OBG, FRCOG - PGIMER Chandigarh', 1100.00),
('doc_008', 'Psychiatry', 'MD Psychiatry, DNB - NIMHANS', 1300.00);

-- ──────────────────────────────────────────────────────────────
-- 3. PATIENTS (Extended Profiles)
-- ──────────────────────────────────────────────────────────────
INSERT INTO patients (user_id, date_of_birth, blood_group, allergies) VALUES
('pat_001', '1985-03-15', 'O+', 'Penicillin'),
('pat_002', '1992-07-22', 'A+', NULL),
('pat_003', '1978-11-08', 'B+', 'Sulfa drugs'),
('pat_004', '1988-05-30', 'AB+', NULL),
('pat_005', '1995-09-12', 'O-', 'Peanuts, Shellfish'),
('pat_006', '1990-02-18', 'A-', NULL),
('pat_007', '1982-12-25', 'B-', 'Latex'),
('pat_008', '1987-06-14', 'O+', 'Aspirin'),
('pat_009', '1975-08-03', 'AB-', NULL),
('pat_010', '1998-01-20', 'A+', 'Dust mites'),
('pat_011', '1991-04-17', 'B+', NULL),
('pat_012', '1983-10-09', 'O+', 'Iodine contrast');

-- ──────────────────────────────────────────────────────────────
-- 4. DOCTOR AVAILABILITY (Weekly Schedules)
-- ──────────────────────────────────────────────────────────────

-- Dr. Sarah Williams (Cardiology) - Mon, Wed, Fri
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes)
SELECT id, 0, '09:00'::TIME, '13:00'::TIME, 30 FROM doctors WHERE user_id = 'doc_001'
UNION ALL
SELECT id, 2, '09:00'::TIME, '13:00'::TIME, 30 FROM doctors WHERE user_id = 'doc_001'
UNION ALL
SELECT id, 4, '14:00'::TIME, '18:00'::TIME, 30 FROM doctors WHERE user_id = 'doc_001';

-- Dr. Rajesh Kumar (General Medicine) - Mon-Fri
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes)
SELECT id, 0, '08:00'::TIME, '12:00'::TIME, 20 FROM doctors WHERE user_id = 'doc_002'
UNION ALL
SELECT id, 0, '14:00'::TIME, '17:00'::TIME, 20 FROM doctors WHERE user_id = 'doc_002'
UNION ALL
SELECT id, 1, '08:00'::TIME, '12:00'::TIME, 20 FROM doctors WHERE user_id = 'doc_002'
UNION ALL
SELECT id, 2, '08:00'::TIME, '12:00'::TIME, 20 FROM doctors WHERE user_id = 'doc_002'
UNION ALL
SELECT id, 3, '14:00'::TIME, '17:00'::TIME, 20 FROM doctors WHERE user_id = 'doc_002'
UNION ALL
SELECT id, 4, '08:00'::TIME, '12:00'::TIME, 20 FROM doctors WHERE user_id = 'doc_002';

-- Dr. Emily Chen (Pediatrics) - Tue, Thu, Sat
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes)
SELECT id, 1, '10:00'::TIME, '14:00'::TIME, 30 FROM doctors WHERE user_id = 'doc_003'
UNION ALL
SELECT id, 3, '10:00'::TIME, '14:00'::TIME, 30 FROM doctors WHERE user_id = 'doc_003'
UNION ALL
SELECT id, 5, '09:00'::TIME, '13:00'::TIME, 30 FROM doctors WHERE user_id = 'doc_003';

-- Dr. Mohammed Ali (Orthopedics) - Mon, Wed, Fri
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes)
SELECT id, 0, '15:00'::TIME, '19:00'::TIME, 45 FROM doctors WHERE user_id = 'doc_004'
UNION ALL
SELECT id, 2, '15:00'::TIME, '19:00'::TIME, 45 FROM doctors WHERE user_id = 'doc_004'
UNION ALL
SELECT id, 4, '15:00'::TIME, '19:00'::TIME, 45 FROM doctors WHERE user_id = 'doc_004';

-- Dr. Priya Sharma (Dermatology) - Mon-Fri mornings
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes)
SELECT id, generate_series, '09:00'::TIME, '13:00'::TIME, 25 
FROM doctors, generate_series(0, 4) 
WHERE user_id = 'doc_005';

-- Dr. James Wilson (Neurology) - Tue, Thu
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes)
SELECT id, 1, '10:00'::TIME, '16:00'::TIME, 60 FROM doctors WHERE user_id = 'doc_006'
UNION ALL
SELECT id, 3, '10:00'::TIME, '16:00'::TIME, 60 FROM doctors WHERE user_id = 'doc_006';

-- Dr. Anita Desai (Gynecology) - Mon, Wed, Fri, Sat
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes)
SELECT id, 0, '09:00'::TIME, '14:00'::TIME, 30 FROM doctors WHERE user_id = 'doc_007'
UNION ALL
SELECT id, 2, '09:00'::TIME, '14:00'::TIME, 30 FROM doctors WHERE user_id = 'doc_007'
UNION ALL
SELECT id, 4, '09:00'::TIME, '14:00'::TIME, 30 FROM doctors WHERE user_id = 'doc_007'
UNION ALL
SELECT id, 5, '10:00'::TIME, '13:00'::TIME, 30 FROM doctors WHERE user_id = 'doc_007';

-- Dr. David Brown (Psychiatry) - Mon-Fri
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes)
SELECT id, generate_series, '11:00'::TIME, '17:00'::TIME, 50 
FROM doctors, generate_series(0, 4) 
WHERE user_id = 'doc_008';

-- ──────────────────────────────────────────────────────────────
-- 5. APPOINTMENTS (Mix of past, current, and future)
-- ──────────────────────────────────────────────────────────────

-- Completed appointments (past)
INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status)
SELECT 
    p.id, 
    d.id, 
    '2024-03-10 10:00:00+05:30', 
    30, 
    'completed'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_001' AND d.user_id = 'doc_001';


INSERT INTO appointments (patient_user_id, doctor_id, appointment_at, duration_minutes, status, reason, notes)
SELECT 
    p.user_id, 
    d.id, 
    '2024-03-10 10:00:00+05:30', 
    30, 
    'scheduled',
    'Annual cardiac checkup',
    'Blood pressure: 120/80, ECG normal, cholesterol levels good'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_001' AND d.user_id = 'doc_001';

SELECT * from appointments;
INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason, notes)
SELECT 
    p.id, 
    d.id, 
    '2024-03-12 14:30:00+05:30', 
    20, 
    'completed',
    'Fever and body ache for 3 days',
    'Diagnosed with viral fever. Prescribed paracetamol and rest.'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_002' AND d.user_id = 'doc_002';

INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason, notes)
SELECT 
    p.id, 
    d.id, 
    '2024-03-15 11:00:00+05:30', 
    30, 
    'completed',
    'Child vaccination - MMR booster',
    'MMR booster administered. Next follow-up in 6 months.'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_003' AND d.user_id = 'doc_003';

INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason, notes)
SELECT 
    p.id, 
    d.id, 
    '2024-03-18 16:00:00+05:30', 
    45, 
    'completed',
    'Knee pain after sports injury',
    'Mild ACL strain. Physiotherapy recommended for 4 weeks. Ice and compression.'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_005' AND d.user_id = 'doc_004';

INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason, notes)
SELECT 
    p.id, 
    d.id, 
    '2024-03-19 10:30:00+05:30', 
    25, 
    'completed',
    'Skin rash on arms',
    'Eczema flare-up. Prescribed moisturizer and topical steroid cream.'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_006' AND d.user_id = 'doc_005';

-- Cancelled appointments
INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason, cancelled_by, cancelled_at, cancel_reason)
SELECT 
    p.id, 
    d.id, 
    '2024-03-20 15:00:00+05:30', 
    30, 
    'cancelled',
    'Follow-up consultation',
    'pat_007',
    '2024-03-19 08:00:00+05:30',
    'Unable to take time off work'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_007' AND d.user_id = 'doc_001';

INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason, cancelled_by, cancelled_at, cancel_reason)
SELECT 
    p.id, 
    d.id, 
    '2024-03-21 09:00:00+05:30', 
    20, 
    'cancelled',
    'Cough and cold',
    'doc_002',
    '2024-03-20 18:00:00+05:30',
    'Doctor emergency - surgery scheduled'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_008' AND d.user_id = 'doc_002';

-- No-show appointment
INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason, notes)
SELECT 
    p.id, 
    d.id, 
    '2024-03-14 12:00:00+05:30', 
    60, 
    'no_show',
    'Migraine consultation',
    'Patient did not show up. No prior cancellation.'
FROM patients p, doctors d 

-- Scheduled appointments (upcoming)
INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason)
SELECT 
    p.id, 
    d.id, 
    '2024-03-25 09:00:00+05:30', 
    30, 
    'scheduled',
    'Routine prenatal checkup - 2nd trimester'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_004' AND d.user_id = 'doc_007';

select * from patients;
select * from users;
INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason)
SELECT 
    p.id, 
    d.id, 
    '2024-03-26 14:00:00+05:30', 
    50, 
    'scheduled',
    'Anxiety and stress management'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_010' AND d.user_id = 'doc_008';

select * from appointments;
INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason)
SELECT 
    p.id, 
    d.id, 
    '2024-03-27 10:30:00+05:30', 
    30, 
    'scheduled',
    'Chest pain - follow-up from ER visit'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_011' AND d.user_id = 'doc_001';

INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason)
SELECT 
    p.id, 
    d.id, 
    '2024-03-28 15:30:00+05:30', 
    45, 
    'scheduled',
    'Back pain radiating to leg'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_012' AND d.user_id = 'doc_004';

INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason)
SELECT 
    p.id, 
    d.id, 
    '2024-03-29 11:00:00+05:30', 
    30, 
    'scheduled',
    'Child having recurrent ear infections'
FROM patients p, doctors d 
WHERE p.user_id = 'pat_003' AND d.user_id = 'doc_003';

-- ──────────────────────────────────────────────────────────────
-- 6. CHAT MESSAGES (Patient conversation history)
-- ──────────────────────────────────────────────────────────────

-- Chat for patient Amit Patel
INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'user', 'I have been experiencing chest discomfort lately', '2024-03-08 14:30:00+05:30'
FROM patients WHERE user_id = 'pat_001';

INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'assistant', 'I understand your concern. Can you describe the discomfort? Is it a sharp pain, dull ache, or pressure? And when does it typically occur?', '2024-03-08 14:30:15+05:30'
FROM patients WHERE user_id = 'pat_001';

INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'user', 'It feels like pressure, especially after climbing stairs or walking fast', '2024-03-08 14:31:00+05:30'
FROM patients WHERE user_id = 'pat_001';

INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'assistant', 'Given your symptoms of chest pressure during physical activity, I recommend scheduling an appointment with a cardiologist as soon as possible. This could be related to your heart and should be evaluated promptly. Would you like me to help you book an appointment with Dr. Sarah Williams, our cardiologist?', '2024-03-08 14:31:20+05:30'
FROM patients WHERE user_id = 'pat_001';

INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'user', 'Yes please, that would be helpful', '2024-03-08 14:32:00+05:30'
FROM patients WHERE user_id = 'pat_001';

-- Chat for patient Sneha Reddy
INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'user', 'Hi, I have fever since yesterday evening', '2024-03-11 09:00:00+05:30'
FROM patients WHERE user_id = 'pat_002';

INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'assistant', 'I''m sorry to hear you''re not feeling well. What is your current temperature? Do you have any other symptoms like headache, body ache, or cough?', '2024-03-11 09:00:10+05:30'
FROM patients WHERE user_id = 'pat_002';

INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'user', 'Temperature is 101.5°F. Yes, I have body ache and mild headache too', '2024-03-11 09:01:00+05:30'
FROM patients WHERE user_id = 'pat_002';

INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'assistant', 'These symptoms suggest a viral infection. I recommend seeing Dr. Rajesh Kumar, our general medicine specialist, for proper diagnosis and treatment. Would you like to schedule an appointment?', '2024-03-11 09:01:15+05:30'
FROM patients WHERE user_id = 'pat_002';

-- Chat for patient Rahul Verma
INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'user', 'I hurt my knee playing cricket. It''s swollen and painful', '2024-03-16 16:00:00+05:30'
FROM patients WHERE user_id = 'pat_005';

INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'assistant', 'I''m sorry about your injury. Sports injuries need proper evaluation. Have you applied ice to reduce swelling? Can you put weight on the leg?', '2024-03-16 16:00:12+05:30'
FROM patients WHERE user_id = 'pat_005';

INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'user', 'I applied ice pack. I can walk but it hurts', '2024-03-16 16:01:00+05:30'
FROM patients WHERE user_id = 'pat_005';

INSERT INTO chat_messages (patient_id, role, content, created_at)
SELECT id, 'assistant', 'I recommend booking an appointment with Dr. Mohammed Ali, our orthopedic specialist, to assess the injury. An X-ray might be needed to rule out fractures. Would you like to schedule an appointment?', '2024-03-16 16:01:20+05:30'
FROM patients WHERE user_id = 'pat_005';

-- ──────────────────────────────────────────────────────────────
-- 7. FEEDBACK (For completed appointments)
-- ──────────────────────────────────────────────────────────────

-- Feedback for Amit Patel's cardiac checkup
INSERT INTO feedback (appointment_id, patient_id, doctor_id, raw_feedback, ai_rating, ai_summary)
SELECT 
    a.id,
    p.id,
    d.id,
    'Dr. Williams was excellent! She took time to explain everything about my heart health and the test results. Very professional and caring. The clinic was clean and the staff was friendly. Highly recommend!',
    5,
    'Excellent experience with thorough explanation of results, professional and caring approach, clean facility with friendly staff.'
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN doctors d ON a.doctor_id = d.id
WHERE p.user_id = 'pat_001' AND d.user_id = 'doc_001' AND a.status = 'completed';

-- Feedback for Sneha Reddy's viral fever consultation
INSERT INTO feedback (appointment_id, patient_id, doctor_id, raw_feedback, ai_rating, ai_summary)
SELECT 
    a.id,
    p.id,
    d.id,
    'Dr. Kumar was very helpful and diagnosed my condition quickly. He explained what I should do and prescribed the right medicines. I felt better in 2 days. Good doctor.',
    4,
    'Efficient diagnosis and treatment, helpful explanation, effective prescription with quick recovery.'
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN doctors d ON a.doctor_id = d.id
WHERE p.user_id = 'pat_002' AND d.user_id = 'doc_002' AND a.status = 'completed';

-- Feedback for vaccination
INSERT INTO feedback (appointment_id, patient_id, doctor_id, raw_feedback, ai_rating, ai_summary)
SELECT 
    a.id,
    p.id,
    d.id,
    'Dr. Chen is wonderful with children! My son was scared but she made him comfortable. The vaccination was quick and she gave us detailed aftercare instructions. Great pediatrician.',
    5,
    'Excellent pediatric care, child-friendly approach, detailed aftercare guidance.'
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN doctors d ON a.doctor_id = d.id
WHERE p.user_id = 'pat_003' AND d.user_id = 'doc_003' AND a.status = 'completed';

-- Feedback for knee injury
INSERT INTO feedback (appointment_id, patient_id, doctor_id, raw_feedback, ai_rating, ai_summary)
SELECT 
    a.id,
    p.id,
    d.id,
    'Dr. Ali examined my knee thoroughly and explained the injury clearly. The physiotherapy plan he recommended is working well. Appointment was a bit delayed though.',
    4,
    'Thorough examination and clear explanation, effective treatment plan, minor wait time issue.'
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN doctors d ON a.doctor_id = d.id
WHERE p.user_id = 'pat_005' AND d.user_id = 'doc_004' AND a.status = 'completed';

-- Feedback for skin rash
INSERT INTO feedback (appointment_id, patient_id, doctor_id, raw_feedback, ai_rating, ai_summary)
SELECT 
    a.id,
    p.id,
    d.id,
    'Dr. Sharma identified the problem right away. The cream she prescribed worked within a week. However, the consultation felt a bit rushed.',
    3,
    'Accurate diagnosis and effective treatment, but consultation felt rushed.'
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN doctors d ON a.doctor_id = d.id
WHERE p.user_id = 'pat_006' AND d.user_id = 'doc_005' AND a.status = 'completed';

-- ──────────────────────────────────────────────────────────────
-- VERIFICATION QUERIES
-- ──────────────────────────────────────────────────────────────
-- Uncomment to verify data:

-- SELECT COUNT(*) as total_users FROM users;
-- SELECT role, COUNT(*) as count FROM users GROUP BY role;
-- SELECT COUNT(*) as total_doctors FROM doctors;
-- SELECT COUNT(*) as total_patients FROM patients;
-- SELECT COUNT(*) as total_availability_slots FROM doctor_availability;
-- SELECT COUNT(*) as total_appointments FROM appointments;
-- SELECT status, COUNT(*) as count FROM appointments GROUP BY status;
-- SELECT COUNT(*) as total_messages FROM chat_messages;
-- SELECT COUNT(*) as total_feedback FROM feedback;

select  from users;
select * from doctors;
INSERT into doctors (user_id, specialty, qualification, consultation_fee) values ('102385568961894317215', 'Cardiology', 'MD Cardiology - AIIMS Delhi', 1500.00);
Update users set role = 'doctor' where id = '102385568961894317215';

select * from doctor_availability;

INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes)
VALUES ('17b0847e-9ae2-43d7-a186-b4a688f1a889', 1, '09:00:00', '16:00:00', 60)
ON CONFLICT (doctor_id, day_of_week, start_time) 
        DO UPDATE SET 
            end_time = EXCLUDED.end_time, 
            slot_duration_minutes = EXCLUDED.slot_duration_minutes;


INSERT INTO users (id, email, full_name, role, phone)
VALUES
('u1', 'doctor1@gmail.com', 'Dr. Rajesh Kumar', 'doctor', '9876543210'),
('u2', 'jaiswalmuskan2604@gmail.com', 'Dr. Sneha Sharma', 'doctor', '9876543211'),
('u3', 'radhe.muskan26@gmail.com', 'Dr. Arjun Mehta', 'doctor', '9876543212'),
('u5', 'nurse2@gmail.com', 'Priya Singh', 'nurse', '9876543214'),
('u6', 'nurse3@gmail.com', 'Kavya Nair', 'nurse', '9876543215');

select * from users;
INSERT INTO doctors (user_email, specialty, qualification, consultation_fee)
VALUES
('jaiswalmuskan2604@gmail.com', 'Cardiology', 'MBBS, MD Cardiology', 800),
('radhe.muskan26@gmail.com', 'Dermatology', 'MBBS, MD Dermatology', 500),
('doctor1@gmail.com', 'Orthopedics', 'MBBS, MS Orthopedics', 700);


select * from nurses;
INSERT INTO nurses (user_email, department)
VALUES
('nurse2@gmail.com', 'Emergency'),
('nurse3@gmail.com', 'General Ward');

INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason, notes)
VALUES ('f8d78b23-a5aa-4765-9dac-16410f0718cb', '610a79b0-56f1-4f87-8008-ed064c054f74', '2026-03-25T15:00:00', 30, 'scheduled', 'Consultation', '')

select * from users where email='jaiswalmuskan2603@gmail.com';

INSERT INTO appointments (patient_id, doctor_id, appointment_at, duration_minutes, status, reason, notes)
VALUES ('f8d78b23-a5aa-4765-9dac-16410f0718cb', '610a79b0-56f1-4f87-8008-ed064c054f74', '2026-03-25T16:00:00', 30, 'scheduled', 'Consultation', '')

select * from appointments;