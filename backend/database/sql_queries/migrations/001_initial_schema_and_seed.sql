-- Migration 001: initial schema + seed data
-- Safe to run multiple times.

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS Users (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(50) NOT NULL,
    role varchar(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    phone varchar(15),
    email varchar(30)
);

CREATE TABLE IF NOT EXISTS Items (
    iid INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode varchar(20) UNIQUE,
    type varchar(20),
    title varchar(100),
    author varchar(50),
    place_publisher varchar(50),
    language_location varchar(50)
);

CREATE TABLE IF NOT EXISTS CheckedOut (
    iid INTEGER PRIMARY KEY REFERENCES Items(iid) ON DELETE CASCADE,
    uid INTEGER REFERENCES Users(uid) ON DELETE CASCADE,
    start_date DATE NOT NULL DEFAULT (date('now', 'localtime')),
    due_date DATE NOT NULL,
    CHECK (start_date <= due_date)
);

CREATE INDEX IF NOT EXISTS start_date_idx ON CheckedOut(start_date);
CREATE INDEX IF NOT EXISTS due_date_idx ON CheckedOut(due_date);
CREATE INDEX IF NOT EXISTS barcode_idx ON Items(barcode);
CREATE INDEX IF NOT EXISTS title_idx ON Items(title);
CREATE INDEX IF NOT EXISTS user_idx ON Users(name);

-- -- Seed items only if empty.
-- -- Pretty sure we don't need this - Justin
-- WITH raw_items AS (
--     SELECT * FROM Book
--     UNION ALL
--     SELECT * FROM CDDVD
--     UNION ALL
--     SELECT * FROM VideoTape
-- ),
-- normalized_items AS (
--     SELECT
--         NULLIF(TRIM([Bar-Code]), '') AS cleaned_barcode,
--         Type,
--         Title,
--         Author,
--         [Place, Publisher] AS place_publisher,
--         [Language/Location] AS language_location
--     FROM raw_items
-- ),
-- ranked_items AS (
--     SELECT
--         CASE
--             WHEN cleaned_barcode IS NULL THEN NULL
--             WHEN ROW_NUMBER() OVER (PARTITION BY cleaned_barcode ORDER BY Title, Author) = 1 THEN cleaned_barcode
--             ELSE NULL
--         END AS barcode,
--         Type,
--         Title,
--         Author,
--         place_publisher,
--         language_location
--     FROM normalized_items
-- )
-- INSERT INTO Items(barcode, type, title, author, place_publisher, language_location)
-- SELECT barcode, Type, Title, Author, place_publisher, language_location
-- FROM ranked_items
-- WHERE NOT EXISTS (SELECT 1 FROM Items LIMIT 1);

-- COMMIT;
