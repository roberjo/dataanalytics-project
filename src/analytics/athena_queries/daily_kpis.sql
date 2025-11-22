-- Daily KPIs Dashboard
-- Key performance indicators for daily business monitoring

SELECT 
    DATE(t.transaction_date) AS date,
    
    -- Order metrics
    COUNT(DISTINCT t.transaction_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.transaction_id END) AS completed_orders,
    COUNT(DISTINCT CASE WHEN t.status = 'returned' THEN t.transaction_id END) AS returned_orders,
    COUNT(DISTINCT CASE WHEN t.status = 'refunded' THEN t.transaction_id END) AS refunded_orders,
    
    -- Customer metrics
    COUNT(DISTINCT t.customer_id) AS unique_customers,
    COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.customer_id END) AS paying_customers,
    
    -- Revenue metrics
    SUM(CASE WHEN t.status = 'completed' THEN t.total_amount ELSE 0 END) AS revenue,
    AVG(CASE WHEN t.status = 'completed' THEN t.total_amount END) AS avg_order_value,
    SUM(CASE WHEN t.status = 'completed' THEN t.quantity ELSE 0 END) AS units_sold,
    
    -- Product metrics
    COUNT(DISTINCT t.product_id) AS unique_products_sold,
    
    -- Return metrics
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN t.status = 'returned' THEN t.transaction_id END) / 
          NULLIF(COUNT(DISTINCT t.transaction_id), 0), 2) AS return_rate_pct,
    
    -- Time-based metrics
    COUNT(DISTINCT CASE WHEN t.is_weekend THEN t.transaction_id END) AS weekend_orders,
    COUNT(DISTINCT CASE WHEN t.transaction_hour BETWEEN 9 AND 17 THEN t.transaction_id END) AS business_hours_orders,
    
    -- Revenue categories
    COUNT(DISTINCT CASE WHEN t.revenue_category = 'high' THEN t.transaction_id END) AS high_value_orders,
    COUNT(DISTINCT CASE WHEN t.revenue_category = 'medium' THEN t.transaction_id END) AS medium_value_orders,
    COUNT(DISTINCT CASE WHEN t.revenue_category = 'low' THEN t.transaction_id END) AS low_value_orders
    
FROM curated.transactions t
WHERE t.transaction_date >= DATE_ADD('day', -90, CURRENT_DATE)
GROUP BY DATE(t.transaction_date)
ORDER BY date DESC;
