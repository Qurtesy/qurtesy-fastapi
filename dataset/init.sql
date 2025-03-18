-- Check if the database 'qurtesy' exists
IF NOT EXISTS (SELECT 1 FROM pg_database where datname = 'qurtesy') THEN
    -- Create the database 'qurtesy' if it does not exist
    CREATE DATABASE qurtesy WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';
END IF;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY NOT NULL,
    value TEXT NOT NULL,
    emoji TEXT
);
INSERT INTO categories (value, emoji) VALUES ('Food', '127828');
INSERT INTO categories (value, emoji) VALUES ('Payments', '128184');
INSERT INTO categories (value, emoji) VALUES ('Transport', '128640');

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
);
INSERT INTO accounts (value) VALUES ('Cash');
INSERT INTO accounts (value) VALUES ('Accounts');
INSERT INTO accounts (value) VALUES ('Cards');
INSERT INTO accounts (value) VALUES ('Investments');

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY NOT NULL,
    date TEXT NOT NULL,
    amount DECIMAL(10,2),
    category INTEGER NOT NULL,
    account INTEGER NOT NULL,

    FOREIGN KEY(category) REFERENCES categories(id),
    FOREIGN KEY(account) REFERENCES accounts(id)
)
