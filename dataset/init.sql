-- Create the database 'qurtesy'
CREATE DATABASE qurtesy WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';

-- Connect to the database
\c qurtesy

-- Create schema
CREATE SCHEMA finance AUTHORIZATION postgres;

CREATE TYPE finance.section_enum AS ENUM (
    'EXPENSE',
    'INCOME',
    'TRANSFER',
    'INVESTMENT',
    'LEND',
    'SPLIT'
);

CREATE TABLE finance.categories (
    id SERIAL PRIMARY KEY,
    value TEXT NOT NULL,
    emoji TEXT,
    section finance.section_enum NOT NULL,
    UNIQUE (value)
);
INSERT INTO finance.categories (value, emoji, section) VALUES ('Transfer (Default)', null, 'TRANSFER');
-- INSERT INTO finance.categories (value, emoji, section) VALUES ('Payments', '128184', 'EXPENSE');
-- INSERT INTO finance.categories (value, emoji, section) VALUES ('Transport', '128640', 'EXPENSE');

CREATE TABLE finance.accounts (
    id SERIAL PRIMARY KEY,
    value TEXT NOT NULL,
    UNIQUE (value)
);
-- INSERT INTO finance.accounts (value, section) VALUES ('Cash', 'EXPENSE');
-- INSERT INTO finance.accounts (value, section) VALUES ('Accounts', 'EXPENSE');
-- INSERT INTO finance.accounts (value, section) VALUES ('Cards', 'EXPENSE');
-- INSERT INTO finance.accounts (value, section) VALUES ('Investments', 'EXPENSE');

CREATE TABLE finance.transactions (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    credit BOOLEAN NOT NULL DEFAULT FALSE,
    amount DECIMAL(10,2),
    section finance.section_enum NOT NULL,
    category INTEGER NOT NULL,
    account INTEGER NOT NULL,
    note TEXT,
    -- created_date DATE NOT NULL,
    -- updated_date DATE NOT NULL,
    FOREIGN KEY(category) REFERENCES finance.categories(id),
    FOREIGN KEY(account) REFERENCES finance.accounts(id)
)
