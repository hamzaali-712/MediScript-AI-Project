-- ============================================================
-- MediScript AI — Supabase PostgreSQL Schema
-- Run this ONCE in Supabase Dashboard → SQL Editor → New Query → RUN
-- HackData V1 | GDGoC CUI Wah
-- ============================================================

-- 1. USERS TABLE (login/signup)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'patient',   -- patient | admin
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ
);

-- 2. SCANS TABLE (every prescription analyzed)
CREATE TABLE IF NOT EXISTS scans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    drug_list TEXT,          -- JSON: [{name, dosage, frequency, duration, route, instructions}]
    interactions TEXT,       -- JSON: [{drug1, drug2, severity, description, source}]
    explanation_en TEXT,     -- English explanation from Gemini
    explanation_ur TEXT,     -- Roman Urdu explanation from Gemini
    warnings TEXT,           -- JSON: ['warning1', 'warning2']
    tips TEXT,               -- JSON: ['tip1', 'tip2']
    summary TEXT,            -- One-sentence summary
    recommendations TEXT,    -- JSON: medicine recommendations from AI
    double_check TEXT,       -- JSON: double-check results
    drug_count INT DEFAULT 0,
    has_interaction BOOLEAN DEFAULT FALSE,
    report_generated BOOLEAN DEFAULT FALSE
);

-- 3. DRUG ANALYTICS TABLE
CREATE TABLE IF NOT EXISTS drug_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    drug_name TEXT UNIQUE NOT NULL,
    scan_count INT DEFAULT 1,
    interaction_count INT DEFAULT 0,
    severity_avg FLOAT DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. USER ACTIVITY LOG
CREATE TABLE IF NOT EXISTS user_activity (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action TEXT,   -- 'login', 'scan', 'report_download', 'logout'
    details TEXT   -- JSON details
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE drug_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;

-- Allow all operations for hackathon (tighten in production)
CREATE POLICY IF NOT EXISTS allow_all_users ON users FOR ALL USING (true);
CREATE POLICY IF NOT EXISTS allow_all_scans ON scans FOR ALL USING (true);
CREATE POLICY IF NOT EXISTS allow_all_analytics ON drug_analytics FOR ALL USING (true);
CREATE POLICY IF NOT EXISTS allow_all_activity ON user_activity FOR ALL USING (true);
