SELECT 
    strftime('%Y-%m-%d', u.created_at) as signup_date,
    COUNT(*) as signups,
    COUNT(*) FILTER (WHERE u.email_verified_at IS NOT NULL) as email_verified,
    COUNT(*) FILTER (WHERE u.first_purchase_at IS NOT NULL) as first_purchase,
    ROUND(100.0 * COUNT(*) FILTER (WHERE u.first_purchase_at IS NOT NULL) / COUNT(*), 1) as conversion_pct
FROM users u
WHERE u.created_at >= date('now', '-90 days')
GROUP BY strftime('%Y-%m-%d', u.created_at)
ORDER BY signup_date DESC;
