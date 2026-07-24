SELECT 
    strftime('%Y-%m-01', transaction_date) as month,
    COUNT(DISTINCT customer_id) as active_users,
    COUNT(DISTINCT customer_id) FILTER (WHERE customer_type='Enterprise') as enterprise_users,
    COUNT(DISTINCT customer_id) FILTER (WHERE customer_type='SMB') as smb_users
FROM transactions
JOIN customers USING(customer_id)
WHERE transaction_date >= date('now', '-12 months')
GROUP BY strftime('%Y-%m-01', transaction_date)
ORDER BY month DESC;
