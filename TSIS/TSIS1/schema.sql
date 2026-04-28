-- ============================================================
-- TSIS1 Schema Extension
-- Extends the existing "phonebook" table from Practice 7
-- Run this ONCE in pgAdmin after your Practice 7 table exists
-- ============================================================

-- 1. Groups / categories
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO groups (name) VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- 2. Add new columns to phonebook
ALTER TABLE phonebook
    ADD COLUMN IF NOT EXISTS email     VARCHAR(100),
    ADD COLUMN IF NOT EXISTS birthday  DATE,
    ADD COLUMN IF NOT EXISTS group_id  INTEGER REFERENCES groups(id) ON DELETE SET NULL;

-- 3. Separate phones table (multiple phones per contact)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES phonebook(contact_id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) DEFAULT 'mobile' CHECK (type IN ('home', 'work', 'mobile'))
);
