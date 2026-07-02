-- Initialize tables and populate them
-- Book, CDDVD and VideoTape tables are pre-populated from the csv files
-- This should be run beforehand in library.db

-- Create Users and Items tables
CREATE TABLE Users (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(50) NOT NULL,
    role varchar(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    phone varchar(15),
    email varchar(30)
);

CREATE TABLE Items (
    iid INT AUTO_INCREMENT PRIMARY KEY,
    barcode varchar(20) UNIQUE,
    type varchar(20),
    title varchar(100),
    author varchar(50),
    place_publisher varchar(50),
    language_location varchar(50)
);

-- Take union of books, CD-DVD and VideoTape tables for all the items
WITH tmp_items AS 
(SELECT * FROM Book
UNION 
SELECT * FROM CDDVD
UNION
SELECT * FROM VideoTape)

INSERT INTO Items(barcode, type, title, author, place_publisher, language_location) 
SELECT [Bar-Code], Type, Title, Author, [Place, Publisher], [Language/Location] FROM tmp_items;

-- Table for check outs

CREATE TABLE CheckedOut (
    iid INT PRIMARY KEY REFERENCES Items(iid) ON DELETE CASCADE,    
    uid INT REFERENCES Users(uid) ON DELETE CASCADE,
    start_date DATE NOT NULL DEFAULT (date('now', 'localtime')),
    due_date DATE NOT NULL,
    CHECK (start_date <= due_date)
);

-- Create indexes for common conditional queries
CREATE INDEX start_date_idx ON CheckedOut(start_date);
CREATE INDEX due_date_idx ON CheckedOut(due_date);
CREATE INDEX barcode_idx ON Items(barcode);
CREATE INDEX title_idx ON Items(title);
CREATE INDEX user_idx ON Users(name);
