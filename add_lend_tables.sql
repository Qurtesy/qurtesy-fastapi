-- Add Lend Transactions table
-- Run this script to add the lend functionality to the database

-- Create lend_transactions table
CREATE TABLE IF NOT EXISTS finance.lend_transactions (
    id SERIAL PRIMARY KEY,
    amount FLOAT NOT NULL,
    date DATE NOT NULL,
    lender_profile_id INTEGER NOT NULL REFERENCES finance.profiles(id),
    borrower_profile_id INTEGER NOT NULL REFERENCES finance.profiles(id),
    category_id INTEGER REFERENCES finance.categories(id),
    account_id INTEGER REFERENCES finance.accounts(id),
    note TEXT,
    is_repaid BOOLEAN NOT NULL DEFAULT FALSE,
    repaid_date DATE,
    related_split_transaction_id INTEGER REFERENCES finance.split_transactions(id),
    related_split_participant_id INTEGER REFERENCES finance.split_participants(id),
    created_date DATE NOT NULL DEFAULT CURRENT_DATE,
    updated_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Constraints
    CONSTRAINT lend_amount_positive CHECK (amount > 0),
    CONSTRAINT lend_different_profiles CHECK (lender_profile_id != borrower_profile_id),
    CONSTRAINT lend_repaid_date_logic CHECK (
        (is_repaid = true AND repaid_date IS NOT NULL) OR 
        (is_repaid = false AND repaid_date IS NULL) OR
        (is_repaid = true AND repaid_date IS NULL)
    )
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_lend_transactions_date ON finance.lend_transactions(date);
CREATE INDEX IF NOT EXISTS idx_lend_transactions_lender ON finance.lend_transactions(lender_profile_id);
CREATE INDEX IF NOT EXISTS idx_lend_transactions_borrower ON finance.lend_transactions(borrower_profile_id);
CREATE INDEX IF NOT EXISTS idx_lend_transactions_repaid ON finance.lend_transactions(is_repaid);
CREATE INDEX IF NOT EXISTS idx_lend_transactions_split_ref ON finance.lend_transactions(related_split_transaction_id);

-- Add trigger to update updated_date automatically
CREATE OR REPLACE FUNCTION update_lend_transactions_updated_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_date = CURRENT_DATE;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_lend_transactions_updated_date ON finance.lend_transactions;
CREATE TRIGGER trigger_update_lend_transactions_updated_date
    BEFORE UPDATE ON finance.lend_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_lend_transactions_updated_date();

-- Insert sample data (optional)
-- Uncomment the following lines to add some sample lend data

/*
-- Ensure we have profiles to work with
INSERT INTO finance.profiles (name, email, is_self) VALUES 
    ('Test Self', 'self@example.com', true),
    ('Test Friend', 'friend@example.com', false)
ON CONFLICT (name) DO NOTHING;

-- Insert sample lend transaction
INSERT INTO finance.lend_transactions (
    amount, 
    date, 
    lender_profile_id, 
    borrower_profile_id, 
    note
) VALUES (
    100.00,
    CURRENT_DATE,
    (SELECT id FROM finance.profiles WHERE is_self = true LIMIT 1),
    (SELECT id FROM finance.profiles WHERE is_self = false LIMIT 1),
    'Sample lend transaction'
);
*/

-- Verify the table was created successfully
SELECT 'Lend transactions table created successfully!' as message;
