-- ============================================================
--  Doctor-Patient Appointment System  |  PostgreSQL Schema
--  Complete Reset & Recreation Script
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ──────────────────────────────────────────────────────────────
-- DROP ALL TABLES (in correct order to avoid FK constraints)
-- ──────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS doctor_availability CASCADE;
DROP TABLE IF EXISTS nurses CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS doctors CASCADE;
DROP TABLE IF EXISTS users CASCADE;
