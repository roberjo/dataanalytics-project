-- Conversion Funnel Analysis
-- Tracks user journey from page view to purchase

WITH daily_funnel AS (
    SELECT 
        DATE(timestamp) AS date,
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN session_id END) AS sessions_with_pageview,
        COUNT(DISTINCT CASE WHEN event_type = 'product_view' THEN session_id END) AS sessions_with_product_view,
        COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN session_id END) AS sessions_with_add_to_cart,
        COUNT(DISTINCT CASE WHEN event_type = 'checkout_start' THEN session_id END) AS sessions_with_checkout,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END) AS sessions_with_purchase,
        
        -- Event counts
        SUM(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) AS total_page_views,
        SUM(CASE WHEN event_type = 'product_view' THEN 1 ELSE 0 END) AS total_product_views,
        SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS total_add_to_carts,
        SUM(CASE WHEN event_type = 'checkout_start' THEN 1 ELSE 0 END) AS total_checkouts,
        SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS total_purchases
    FROM curated.clickstream
    WHERE timestamp >= DATE_ADD('day', -7, CURRENT_DATE)
    GROUP BY DATE(timestamp)
)
SELECT 
    date,
    sessions_with_pageview,
    sessions_with_product_view,
    sessions_with_add_to_cart,
    sessions_with_checkout,
    sessions_with_purchase,
    
    -- Conversion rates between stages
    ROUND(100.0 * sessions_with_product_view / NULLIF(sessions_with_pageview, 0), 2) AS pageview_to_product_rate,
    ROUND(100.0 * sessions_with_add_to_cart / NULLIF(sessions_with_product_view, 0), 2) AS product_to_cart_rate,
    ROUND(100.0 * sessions_with_checkout / NULLIF(sessions_with_add_to_cart, 0), 2) AS cart_to_checkout_rate,
    ROUND(100.0 * sessions_with_purchase / NULLIF(sessions_with_checkout, 0), 2) AS checkout_to_purchase_rate,
    
    -- Overall conversion rate
    ROUND(100.0 * sessions_with_purchase / NULLIF(sessions_with_pageview, 0), 2) AS overall_conversion_rate,
    
    -- Drop-off analysis
    sessions_with_pageview - sessions_with_product_view AS dropoff_after_pageview,
    sessions_with_product_view - sessions_with_add_to_cart AS dropoff_after_product_view,
    sessions_with_add_to_cart - sessions_with_checkout AS dropoff_after_add_to_cart,
    sessions_with_checkout - sessions_with_purchase AS dropoff_after_checkout
FROM daily_funnel
ORDER BY date DESC;
