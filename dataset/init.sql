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
    UNIQUE (value),
    created_date DATE NOT NULL,
    updated_date DATE NOT NULL
);

INSERT INTO finance.categories (value, emoji, section, created_date, updated_date) VALUES
    ('Food','🍟','EXPENSE', NOW(), NOW()),
    ('Education','📘','EXPENSE', NOW(), NOW()),
    ('Transports','🚃','EXPENSE', NOW(), NOW()),
    ('Payments','💸','EXPENSE', NOW(), NOW()),
    ('Gift','🧸','EXPENSE', NOW(), NOW()),
    ('Entertainment','🎮','EXPENSE', NOW(), NOW()),
    ('Recording', null, 'EXPENSE', NOW(), NOW()),
    ('Salary','💰','INCOME', NOW(), NOW()),
    ('Groww','🦍','INVESTMENT', NOW(), NOW()),
    ('Transfer (Default)', null, 'TRANSFER', NOW(), NOW());

CREATE TABLE finance.accounts (
    id SERIAL PRIMARY KEY,
    value TEXT NOT NULL,
    UNIQUE (value),
    created_date DATE NOT NULL,
    updated_date DATE NOT NULL
);

INSERT INTO finance.accounts (value, created_date, updated_date) VALUES
    ('Cash', NOW(), NOW()),
    ('Accounts', NOW(), NOW()),
    ('Cards', NOW(), NOW()),
    ('Investments', NOW(), NOW());

CREATE TABLE finance.transactions (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    credit BOOLEAN NOT NULL DEFAULT FALSE,
    amount DECIMAL(10,2),
    section finance.section_enum NOT NULL,
    category INTEGER,
    account INTEGER,
    note TEXT,
    created_date DATE NOT NULL,
    updated_date DATE NOT NULL,
    FOREIGN KEY(category) REFERENCES finance.categories(id),
    FOREIGN KEY(account) REFERENCES finance.accounts(id)
)
