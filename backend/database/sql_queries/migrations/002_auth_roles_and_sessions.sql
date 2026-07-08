-- Migration 002: upgrade the existing 001 schema.
-- Rebuilds Users to add password hashing, JWT session storage, and librarian role support.
-- Run this once after migration 001 has already been applied.

PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS Users_new;

CREATE TABLE IF NOT EXISTS Users_new (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(50) NOT NULL,
    role varchar(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'librarian', 'system')),
    phone varchar(15),
    email varchar(30),
    hashed_password varchar(255),
    session_token TEXT
);

-- INSERT INTO Users_new (uid, name, role, phone, email, hashed_password, session_token)
-- SELECT
--     uid,
--     name,
--     CASE WHEN role IN ('user', 'admin', 'librarian') THEN role ELSE 'user' END,
--     phone,
--     email,
--     NULL,
--     NULL
-- FROM Users;

DROP TABLE IF EXISTS Users;
ALTER TABLE Users_new RENAME TO Users;

CREATE INDEX IF NOT EXISTS user_idx ON Users(name);

COMMIT;
PRAGMA foreign_keys = ON;