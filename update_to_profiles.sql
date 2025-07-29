-- Create profiles table for split participants
CREATE TABLE IF NOT EXISTS finance.profiles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    avatar_url TEXT,
    default_account_id INTEGER REFERENCES finance.accounts(id),
    is_self BOOLEAN NOT NULL DEFAULT FALSE, -- Indicates if this is your own profile
    created_date DATE NOT NULL DEFAULT NOW(),
    updated_date DATE NOT NULL DEFAULT NOW(),
    UNIQUE(name)
);

-- Update split_participants table to use profile_id instead of account_id
ALTER TABLE finance.split_participants 
DROP CONSTRAINT IF EXISTS split_participants_account_id_fkey;

ALTER TABLE finance.split_participants 
DROP COLUMN IF EXISTS account_id;

ALTER TABLE finance.split_participants 
ADD COLUMN IF NOT EXISTS profile_id INTEGER REFERENCES finance.profiles(id);

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_split_participants_profile ON finance.split_participants(profile_id);

-- Create a default "self" profile (you can update this with your actual details)
INSERT INTO finance.profiles (name, is_self, default_account_id) 
VALUES ('Me', true, 1)
ON CONFLICT (name) DO NOTHING;

-- Add some example profiles for testing
INSERT INTO finance.profiles (name, email, default_account_id, is_self) VALUES
('John Doe', 'john@example.com', 5, false),
('Jane Smith', 'jane@example.com', 6, false),
('Alex Johnson', 'alex@example.com', null, false)
ON CONFLICT (name) DO NOTHING;
