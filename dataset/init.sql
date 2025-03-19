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
INSERT INTO finance.categories (value, emoji) VALUES ('Food', '127828');
INSERT INTO finance.categories (value, emoji) VALUES ('Payments', '128184');
INSERT INTO finance.categories (value, emoji) VALUES ('Transport', '128640');

CREATE TABLE IF NOT EXISTS finance.accounts (
    id SERIAL PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT INTO finance.accounts (value) VALUES ('Cash');
INSERT INTO finance.accounts (value) VALUES ('Accounts');
INSERT INTO finance.accounts (value) VALUES ('Cards');
INSERT INTO finance.accounts (value) VALUES ('Investments');

CREATE TABLE IF NOT EXISTS finance.transactions (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    amount DECIMAL(10,2),
    category INTEGER NOT NULL,
    account INTEGER NOT NULL,
    FOREIGN KEY(category) REFERENCES finance.categories(id),
    FOREIGN KEY(account) REFERENCES finance.accounts(id)
)
