-- Script to check and fix split participants with missing profiles

-- Check for split participants without profiles
SELECT sp.id, sp.split_transaction_id, sp.profile_id, p.name as profile_name
FROM finance.split_participants sp
LEFT JOIN finance.profiles p ON sp.profile_id = p.id
WHERE p.id IS NULL;

-- Check split transactions with their participants
SELECT st.id, st.name, st.total_amount, 
       COUNT(sp.id) as participant_count,
       COUNT(p.id) as valid_participants
FROM finance.split_transactions st
LEFT JOIN finance.split_participants sp ON st.id = sp.split_transaction_id
LEFT JOIN finance.profiles p ON sp.profile_id = p.id
GROUP BY st.id, st.name, st.total_amount;

-- Delete orphaned split participants (participants without valid profiles)
-- Uncomment to execute:
-- DELETE FROM finance.split_participants 
-- WHERE profile_id NOT IN (SELECT id FROM finance.profiles);
