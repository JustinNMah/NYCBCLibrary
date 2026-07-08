BEGIN TRANSACTION;

DELETE FROM Users;

DELETE FROM sqlite_sequence
WHERE name = 'Users';

INSERT INTO Users (
    name,
    role,
    phone,
    email,
    hashed_password
)
VALUES (
    'System User',
    'system',
    NULL,
    NULL,
    NULL
);

COMMIT;