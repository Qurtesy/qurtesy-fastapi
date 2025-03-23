-- Create the database 'qurtesy'
CREATE DATABASE qurtesy WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';

-- Connect to the database
\c qurtesy

-- Create schema
CREATE SCHEMA finance AUTHORIZATION postgres;

CREATE TABLE IF NOT EXISTS finance.categories (
    id SERIAL PRIMARY KEY,
    value TEXT NOT NULL,
    emoji TEXT
);
-- INSERT INTO finance.categories (value, emoji) VALUES ('Food', '127828');
-- INSERT INTO finance.categories (value, emoji) VALUES ('Payments', '128184');
-- INSERT INTO finance.categories (value, emoji) VALUES ('Transport', '128640');

CREATE TABLE IF NOT EXISTS finance.accounts (
    id SERIAL PRIMARY KEY,
    value TEXT NOT NULL
);
-- INSERT INTO finance.accounts (value) VALUES ('Cash');
-- INSERT INTO finance.accounts (value) VALUES ('Accounts');
-- INSERT INTO finance.accounts (value) VALUES ('Cards');
-- INSERT INTO finance.accounts (value) VALUES ('Investments');


DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'section_enum') THEN
        CREATE TYPE finance.section_enum AS ENUM (
            'EXPENSE',
            'INCOME',
            'INVESTMENT',
            'LEND',
            'SPLIT'
        );
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS finance.transactions (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    amount DECIMAL(10,2),
    section finance.section_enum NOT NULL,
    category INTEGER NOT NULL,
    account INTEGER NOT NULL,
    -- created_date DATE NOT NULL,
    -- updated_date DATE NOT NULL,
    FOREIGN KEY(category) REFERENCES finance.categories(id),
    FOREIGN KEY(account) REFERENCES finance.accounts(id)
)
