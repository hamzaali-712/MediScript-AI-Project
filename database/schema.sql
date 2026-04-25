-- ─────────────────────────────────────────────────────────────────────────────
--  MediScript AI — Supabase Database Schema
--  Run this in: Supabase Dashboard → SQL Editor → New Query → Run
--  Order matters: run in sequence (users before scans, etc.)
-- ─────────────────────────────────────────────────────────────────────────────

-- ── 1. Users Table ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         TEXT UNIQUE NOT NULL,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name     TEXT DEFAULT '',
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    last_login    TIMESTAMPTZ
);

-- ── 2. Prescription Scans Table ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    drug_list       JSONB DEFAULT '[]',
    interactions    JSONB DEFAULT '[]',
    explanation_en  TEXT DEFAULT '',
    explanation_ur  TEXT DEFAULT '',
    warnings        JSONB DEFAULT '[]',
    tips            JSONB DEFAULT '[]',
    summary         TEXT DEFAULT '',
    recommendations JSONB DEFAULT '{}',
    double_check    JSONB DEFAULT '{}',
    drug_count      INT DEFAULT 0,
    has_interaction BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── 3. Drug Analytics Table ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS drug_analytics (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drug_name  TEXT UNIQUE NOT NULL,
    scan_count INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 4. User Activity Log Table ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_activity (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    action     TEXT NOT NULL,
    details    JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes for performance ───────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_scans_user_id         ON scans(user_id);
CREATE INDEX IF NOT EXISTS idx_scans_created_at      ON scans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_has_interaction ON scans(has_interaction);
CREATE INDEX IF NOT EXISTS idx_activity_user_id      ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_created_at   ON user_activity(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_count       ON drug_analytics(scan_count DESC);
CREATE INDEX IF NOT EXISTS idx_users_email           ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username        ON users(username);

-- ── Row Level Security (RLS) ──────────────────────────────────────────────────
-- Uncomment for production security:
-- ALTER TABLE users         ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE scans         ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;

-- ── Basic RLS Policies (optional, enable if using Supabase Auth) ──────────────
-- CREATE POLICY "Users can read own data"
--   ON users FOR SELECT USING (auth.uid() = id);
-- CREATE POLICY "Users can read own scans"
--   ON scans FOR SELECT USING (auth.uid() = user_id);
