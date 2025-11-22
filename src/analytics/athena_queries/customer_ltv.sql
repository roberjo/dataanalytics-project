-- Customer Lifetime Value Analysis
-- Segments customers based on their total spending and purchase behavior

WITH customer_metrics AS (
    SELECT 
        customer_id,
        MIN(transaction_date) AS first_purchase_date,
        MAX(transaction_date) AS last_purchase_date,
        COUNT(DISTINCT transaction_id) AS total_orders,
        COUNT(DISTINCT CASE WHEN status = 'completed' THEN transaction_id END) AS completed_orders,
        COUNT(DISTINCT CASE WHEN status = 'returned' THEN transaction_id END) AS returned_orders,
        SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) AS lifetime_value,
        AVG(CASE WHEN status = 'completed' THEN total_amount END) AS avg_order_value,
        SUM(CASE WHEN status = 'completed' THEN quantity ELSE 0 END) AS total_items_purchased,
        DATE_DIFF('day', MIN(transaction_date), MAX(transaction_date)) AS customer_tenure_days
    FROM curated.transactions
    GROUP BY customer_id
),
customer_segments AS (
    SELECT 
        *,
        CASE 
            WHEN lifetime_value >= 1000 THEN 'VIP'
            WHEN lifetime_value >= 500 THEN 'High Value'
            WHEN lifetime_value >= 100 THEN 'Medium Value'
            ELSE 'Low Value'
        END AS customer_segment,
        CASE 
            WHEN total_orders >= 10 THEN 'Frequent'
            WHEN total_orders >= 5 THEN 'Regular'
            WHEN total_orders >= 2 THEN 'Occasional'
            ELSE 'One-time'
        END AS purchase_frequency_segment,
        ROUND(CAST(returned_orders AS DOUBLE) / NULLIF(total_orders, 0) * 100, 2) AS return_rate_pct
    FROM customer_metrics
)
SELECT 
    customer_segment,
    purchase_frequency_segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(lifetime_value), 2) AS avg_ltv,
    ROUND(AVG(total_orders), 1) AS avg_orders,
    ROUND(AVG(avg_order_value), 2) AS avg_order_value,
    ROUND(AVG(customer_tenure_days), 0) AS avg_tenure_days,
    ROUND(AVG(return_rate_pct), 2) AS avg_return_rate_pct,
    SUM(lifetime_value) AS total_segment_revenue
FROM customer_segments
GROUP BY customer_segment, purchase_frequency_segment
ORDER BY total_segment_revenue DESC;
