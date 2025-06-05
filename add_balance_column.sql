-- Add balance column to accounts table if it doesn't exist
ALTER TABLE finance.accounts 
ADD COLUMN IF NOT EXISTS balance FLOAT NOT NULL DEFAULT 0.0;

-- Update any existing accounts to have a default balance of 0
UPDATE finance.accounts 
SET balance = 0.0 
WHERE balance IS NULL;
