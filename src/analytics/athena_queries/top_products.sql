-- Top Products by Revenue
-- Returns the top 20 products by revenue in the last 30 days

SELECT 
    p.product_id,
    p.name AS product_name,
    p.category,
    p.brand,
    SUM(t.quantity) AS total_quantity_sold,
    SUM(t.total_amount) AS total_revenue,
    COUNT(DISTINCT t.transaction_id) AS number_of_orders,
    COUNT(DISTINCT t.customer_id) AS unique_customers,
    AVG(t.total_amount) AS avg_order_value,
    ROUND(AVG(p.rating), 2) AS avg_product_rating
FROM curated.transactions t
INNER JOIN curated.products p 
    ON t.product_id = p.product_id
WHERE t.transaction_date >= DATE_ADD('day', -30, CURRENT_DATE)
    AND t.status = 'completed'
GROUP BY 
    p.product_id,
    p.name,
    p.category,
    p.brand
ORDER BY total_revenue DESC
LIMIT 20;
