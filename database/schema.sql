-- ─────────────────────────────────────────────────────
--  MediScript AI — Supabase Database Schema
--  Run this in: Supabase Dashboard → SQL Editor → Run
-- ─────────────────────────────────────────────────────

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         TEXT UNIQUE NOT NULL,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name     TEXT DEFAULT '',
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    last_login    TIMESTAMPTZ
);

-- 2. Prescription Scans
CREATE TABLE IF NOT EXISTS scans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    drug_list       JSONB,
    interactions    JSONB,
    explanation_en  TEXT,
    explanation_ur  TEXT,
    warnings        JSONB,
    tips            JSONB,
    summary         TEXT,
    recommendations JSONB,
    double_check    JSONB,
    drug_count      INT DEFAULT 0,
    has_interaction BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Drug Analytics
CREATE TABLE IF NOT EXISTS drug_analytics (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drug_name  TEXT UNIQUE NOT NULL,
    scan_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. User Activity Log
CREATE TABLE IF NOT EXISTS user_activity (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    action     TEXT NOT NULL,
    details    JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes for performance ───────────────────────────────
CREATE INDEX IF NOT EXISTS idx_scans_user_id    ON scans(user_id);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_user_id ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_count  ON drug_analytics(scan_count DESC);

-- ── Row Level Security (RLS) — enable for production ────
-- ALTER TABLE users        ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE scans        ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;
