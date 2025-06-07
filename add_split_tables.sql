-- Add split transactions table
CREATE TABLE IF NOT EXISTS finance.split_transactions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,  -- Description of the split transaction (e.g., "Dinner at Restaurant")
    total_amount DECIMAL(10,2) NOT NULL,  -- Total amount to be split
    date DATE NOT NULL,
    category_id INTEGER REFERENCES finance.categories(id),
    created_by_account_id INTEGER REFERENCES finance.accounts(id), -- Who created/paid initially
    note TEXT,
    created_date DATE NOT NULL DEFAULT NOW(),
    updated_date DATE NOT NULL DEFAULT NOW()
);

-- Add split participants table (who is involved in the split)
CREATE TABLE IF NOT EXISTS finance.split_participants (
    id SERIAL PRIMARY KEY,
    split_transaction_id INTEGER REFERENCES finance.split_transactions(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES finance.accounts(id),
    share_amount DECIMAL(10,2) NOT NULL, -- How much this participant owes
    is_paid BOOLEAN NOT NULL DEFAULT FALSE, -- Whether this participant has paid their share
    created_date DATE NOT NULL DEFAULT NOW(),
    updated_date DATE NOT NULL DEFAULT NOW(),
    UNIQUE(split_transaction_id, account_id) -- One entry per participant per split
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_split_transactions_date ON finance.split_transactions(date);
CREATE INDEX IF NOT EXISTS idx_split_transactions_created_by ON finance.split_transactions(created_by_account_id);
CREATE INDEX IF NOT EXISTS idx_split_participants_split_id ON finance.split_participants(split_transaction_id);
CREATE INDEX IF NOT EXISTS idx_split_participants_account ON finance.split_participants(account_id);
