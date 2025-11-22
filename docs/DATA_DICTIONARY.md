# Data Dictionary

Complete schema documentation for all tables in the e-commerce analytics pipeline.

## Table of Contents

1. [Transactions](#transactions)
2. [Products](#products)
3. [Clickstream](#clickstream)
4. [Reviews](#reviews)

---

## Transactions

**Table Name**: `curated.transactions`  
**Source**: Transaction processing system  
**Update Frequency**: Real-time / Daily batch  
**Partitioning**: `year`, `month`, `day`  
**Format**: Parquet (Snappy compression)  
**Row Count**: ~100K-1M per day

### Schema

| Column Name | Data Type | Nullable | Description | Sample Values |
|-------------|-----------|----------|-------------|---------------|
| `transaction_id` | STRING | No | Unique transaction identifier | `txn_000000001` |
| `customer_id` | STRING | No | Customer identifier | `cust_000123` |
| `product_id` | STRING | No | Product identifier | `prod_000456` |
| `quantity` | INT | No | Number of items purchased | `1`, `2`, `5` |
| `price` | DECIMAL(10,2) | No | Unit price at time of purchase | `29.99`, `149.99` |
| `total_amount` | DECIMAL(10,2) | No | Total transaction amount (quantity × price) | `59.98`, `149.99` |
| `transaction_date` | TIMESTAMP | No | Date and time of transaction | `2025-01-15 14:30:45` |
| `status` | STRING | No | Transaction status | `completed`, `returned`, `refunded` |
| `processing_timestamp` | TIMESTAMP | No | When record was processed | `2025-01-15 15:00:00` |
| `processing_date` | DATE | No | Date record was processed | `2025-01-15` |
| `revenue_category` | STRING | No | Revenue classification | `high`, `medium`, `low` |
| `transaction_hour` | INT | No | Hour of day (0-23) | `14`, `9`, `22` |
| `day_of_week` | INT | No | Day of week (1=Sunday, 7=Saturday) | `1`, `3`, `7` |
| `is_weekend` | BOOLEAN | No | Whether transaction occurred on weekend | `true`, `false` |
| `year` | INT | No | Partition: Year | `2025` |
| `month` | INT | No | Partition: Month | `1`, `12` |
| `day` | INT | No | Partition: Day | `1`, `31` |

### Business Rules

- `total_amount` must equal `quantity × price` (±$0.01 tolerance)
- `quantity` must be > 0
- `price` must be > 0
- `transaction_date` cannot be in the future
- `status` values are lowercase and trimmed

### Revenue Categories

| Category | Criteria |
|----------|----------|
| `high` | total_amount >= $100 |
| `medium` | $50 <= total_amount < $100 |
| `low` | total_amount < $50 |

### Sample Query

```sql
SELECT 
    DATE(transaction_date) as date,
    COUNT(*) as total_transactions,
    SUM(total_amount) as revenue
FROM curated.transactions
WHERE year = 2025 AND month = 1
    AND status = 'completed'
GROUP BY DATE(transaction_date)
ORDER BY date DESC;
```

---

## Products

**Table Name**: `curated.products`  
**Source**: Product catalog system  
**Update Frequency**: Daily batch  
**Partitioning**: None (dimension table)  
**Format**: Parquet (Snappy compression)  
**Row Count**: ~500-5000

### Schema

| Column Name | Data Type | Nullable | Description | Sample Values |
|-------------|-----------|----------|-------------|---------------|
| `product_id` | STRING | No | Unique product identifier | `prod_000456` |
| `name` | STRING | No | Product name | `Wireless Mouse`, `Laptop Stand` |
| `category` | STRING | No | Product category | `Electronics`, `Clothing` |
| `brand` | STRING | No | Brand name | `TechBrand`, `StyleCo` |
| `price` | DECIMAL(10,2) | No | Current price | `29.99`, `199.99` |
| `stock` | INT | No | Available inventory | `150`, `0` |
| `weight_kg` | DECIMAL(5,2) | Yes | Product weight in kilograms | `0.25`, `2.50` |
| `rating` | DECIMAL(2,1) | Yes | Average customer rating (1-5) | `4.5`, `3.2` |
| `review_count` | INT | Yes | Number of reviews | `127`, `0` |
| `is_active` | BOOLEAN | No | Whether product is currently available | `true`, `false` |

### Categories

- Electronics
- Clothing
- Home & Garden
- Sports & Outdoors
- Books
- Toys & Games
- Health & Beauty
- Automotive
- Office Supplies
- Pet Supplies

### Sample Query

```sql
SELECT 
    category,
    COUNT(*) as product_count,
    AVG(price) as avg_price,
    AVG(rating) as avg_rating
FROM curated.products
WHERE is_active = true
GROUP BY category
ORDER BY product_count DESC;
```

---

## Clickstream

**Table Name**: `curated.clickstream`  
**Source**: Website analytics  
**Update Frequency**: Real-time / Hourly batch  
**Partitioning**: `year`, `month`, `day`, `hour`  
**Format**: Parquet (Snappy compression)  
**Row Count**: ~50K-500K per hour

### Schema

| Column Name | Data Type | Nullable | Description | Sample Values |
|-------------|-----------|----------|-------------|---------------|
| `session_id` | STRING | No | Unique session identifier | `sess_000000789` |
| `customer_id` | STRING | Yes | Customer identifier (null if not logged in) | `cust_000123`, `null` |
| `event_type` | STRING | No | Type of event | `page_view`, `product_view`, `add_to_cart` |
| `page` | STRING | No | Page URL or path | `/`, `/product/prod_456` |
| `timestamp` | TIMESTAMP | No | Event timestamp | `2025-01-15 10:30:45.123` |
| `device` | STRING | No | Device type | `desktop`, `mobile`, `tablet` |
| `browser` | STRING | No | Browser name | `Chrome`, `Safari`, `Firefox` |
| `ip_address` | STRING | Yes | Client IP address | `192.168.1.1` |
| `user_agent` | STRING | Yes | Full user agent string | `Mozilla/5.0...` |
| `year` | INT | No | Partition: Year | `2025` |
| `month` | INT | No | Partition: Month | `1` |
| `day` | INT | No | Partition: Day | `15` |
| `hour` | INT | No | Partition: Hour | `10` |

### Event Types

| Event Type | Description |
|------------|-------------|
| `page_view` | User viewed a page |
| `product_view` | User viewed product details |
| `add_to_cart` | User added item to cart |
| `remove_from_cart` | User removed item from cart |
| `checkout_start` | User started checkout process |
| `purchase` | User completed purchase |
| `search` | User performed search |

### Device Distribution

Typical distribution:
- Desktop: 50%
- Mobile: 40%
- Tablet: 10%

### Sample Query

```sql
-- Conversion funnel
SELECT 
    DATE(timestamp) as date,
    COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN session_id END) as sessions,
    COUNT(DISTINCT CASE WHEN event_type = 'product_view' THEN session_id END) as product_views,
    COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN session_id END) as add_to_carts,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END) as purchases
FROM curated.clickstream
WHERE year = 2025 AND month = 1
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

---

## Reviews

**Table Name**: `curated.reviews`  
**Source**: Customer review system  
**Update Frequency**: Daily batch  
**Partitioning**: `year`, `month`  
**Format**: Parquet (Snappy compression)  
**Row Count**: ~2K-20K per day

### Schema

| Column Name | Data Type | Nullable | Description | Sample Values |
|-------------|-----------|----------|-------------|---------------|
| `review_id` | STRING | No | Unique review identifier | `rev_000000001` |
| `product_id` | STRING | No | Product being reviewed | `prod_000456` |
| `customer_id` | STRING | No | Customer who wrote review | `cust_000123` |
| `rating` | INT | No | Star rating (1-5) | `5`, `3`, `1` |
| `review_text` | STRING | Yes | Review content | `Great product!` |
| `review_date` | DATE | No | Date review was submitted | `2025-01-16` |
| `verified_purchase` | BOOLEAN | No | Whether reviewer purchased the product | `true`, `false` |
| `helpful_votes` | INT | No | Number of helpful votes | `12`, `0` |
| `year` | INT | No | Partition: Year | `2025` |
| `month` | INT | No | Partition: Month | `1` |

### Rating Distribution

Typical distribution (skewed positive):
- 5 stars: 50%
- 4 stars: 30%
- 3 stars: 10%
- 2 stars: 5%
- 1 star: 5%

### Business Rules

- `rating` must be between 1 and 5
- `helpful_votes` must be >= 0
- `review_date` cannot be in the future
- ~80% of reviews are from verified purchases

### Sample Query

```sql
SELECT 
    p.name as product_name,
    COUNT(*) as review_count,
    AVG(r.rating) as avg_rating,
    SUM(CASE WHEN r.verified_purchase THEN 1 ELSE 0 END) as verified_reviews
FROM curated.reviews r
JOIN curated.products p ON r.product_id = p.product_id
WHERE r.year = 2025 AND r.month = 1
GROUP BY p.name
HAVING COUNT(*) >= 10
ORDER BY avg_rating DESC
LIMIT 20;
```

---

## Data Lineage

### Transactions

```
Source System (CSV)
    ↓
S3 Raw Zone (raw/transactions/)
    ↓
Glue Crawler (schema discovery)
    ↓
Glue ETL Job (transaction_etl.py)
    - Clean data
    - Calculate derived fields
    - Deduplicate
    ↓
S3 Processed Zone (processed/transactions/)
    ↓
Data Quality Checks
    ↓
S3 Curated Zone (curated/transactions/)
    ↓
Athena Queries
```

### Products

```
Source System (JSON)
    ↓
S3 Raw Zone (raw/products/)
    ↓
Glue Crawler
    ↓
Glue ETL Job (product_enrichment.py)
    - Enrich with category data
    - Calculate metrics
    ↓
S3 Curated Zone (curated/products/)
    ↓
Athena Queries
```

## Data Retention

| Zone | Retention Period | Storage Class |
|------|------------------|---------------|
| Raw | 1 year | Standard → IA (30d) → Glacier (90d) |
| Processed | 6 months | Standard → IA (60d) → Glacier (180d) |
| Curated | Indefinite | Standard → IA (90d) |
| Athena Results | 7 days | Standard (auto-delete) |

## Data Quality Metrics

### Completeness
- Required fields: 0% null
- Optional fields: <10% null

### Accuracy
- Duplicates: 0%
- Invalid values: <0.1%

### Timeliness
- Data freshness: <24 hours
- Processing latency: <30 minutes

### Consistency
- Cross-table referential integrity: 100%
- Data type consistency: 100%

---

**Last Updated**: 2025-01-15  
**Version**: 1.0  
**Maintained By**: Data Engineering Team
