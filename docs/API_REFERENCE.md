# API Reference

## Overview

This document provides detailed API reference for all modules, classes, and functions in the data analytics pipeline.

---

## Table of Contents

1. [Utilities](#utilities)
2. [Data Generators](#data-generators)
3. [Ingestion Layer](#ingestion-layer)
4. [Transformation Layer](#transformation-layer)
5. [Analytics Layer](#analytics-layer)

---

## Utilities

### S3Helper

**Module**: `src.utils.s3_helper`

Helper class for Amazon S3 operations.

#### Constructor

```python
S3Helper(region_name: str = 'us-east-1')
```

**Parameters:**
- `region_name` (str): AWS region name. Default: 'us-east-1'

**Example:**
```python
from src.utils.s3_helper import S3Helper

s3 = S3Helper(region_name='us-west-2')
```

#### Methods

##### upload_file()

Upload a local file to S3.

```python
upload_file(file_path: str, bucket: str, key: str) -> bool
```

**Parameters:**
- `file_path` (str): Local file path to upload
- `bucket` (str): S3 bucket name
- `key` (str): S3 object key (destination path)

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = s3.upload_file(
    file_path='/tmp/data.csv',
    bucket='my-data-lake',
    key='raw/transactions/data.csv'
)
```

##### download_file()

Download a file from S3 to local filesystem.

```python
download_file(bucket: str, key: str, file_path: str) -> bool
```

**Parameters:**
- `bucket` (str): S3 bucket name
- `key` (str): S3 object key
- `file_path` (str): Local destination path

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = s3.download_file(
    bucket='my-data-lake',
    key='processed/transactions/data.parquet',
    file_path='/tmp/data.parquet'
)
```

##### list_objects()

List objects in S3 bucket with optional prefix.

```python
list_objects(bucket: str, prefix: str = '') -> List[Dict]
```

**Parameters:**
- `bucket` (str): S3 bucket name
- `prefix` (str): Object key prefix for filtering. Default: ''

**Returns:**
- `List[Dict]`: List of object metadata dictionaries

**Example:**
```python
objects = s3.list_objects(
    bucket='my-data-lake',
    prefix='raw/transactions/'
)
for obj in objects:
    print(f"Key: {obj['Key']}, Size: {obj['Size']}")
```

##### object_exists()

Check if an object exists in S3.

```python
object_exists(bucket: str, key: str) -> bool
```

**Parameters:**
- `bucket` (str): S3 bucket name
- `key` (str): S3 object key

**Returns:**
- `bool`: True if object exists, False otherwise

**Example:**
```python
if s3.object_exists('my-bucket', 'data/file.csv'):
    print("File exists")
```

##### read_json_lines()

Read JSON Lines file from S3.

```python
read_json_lines(bucket: str, key: str) -> List[Dict]
```

**Parameters:**
- `bucket` (str): S3 bucket name
- `key` (str): S3 object key

**Returns:**
- `List[Dict]`: List of parsed JSON objects

**Example:**
```python
records = s3.read_json_lines(
    bucket='my-bucket',
    key='data/products.json'
)
```

##### write_json_lines()

Write JSON Lines file to S3.

```python
write_json_lines(records: List[Dict], bucket: str, key: str) -> bool
```

**Parameters:**
- `records` (List[Dict]): List of dictionaries to write
- `bucket` (str): S3 bucket name
- `key` (str): S3 object key

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
records = [
    {'id': 1, 'name': 'Product A'},
    {'id': 2, 'name': 'Product B'}
]
success = s3.write_json_lines(records, 'my-bucket', 'data/products.json')
```

---

### AthenaHelper

**Module**: `src.utils.athena_helper`

Helper class for Amazon Athena operations.

#### Constructor

```python
AthenaHelper(
    region_name: str = 'us-east-1',
    workgroup: str = 'primary',
    output_location: str = None
)
```

**Parameters:**
- `region_name` (str): AWS region name
- `workgroup` (str): Athena workgroup name
- `output_location` (str): S3 location for query results

**Example:**
```python
from src.utils.athena_helper import AthenaHelper

athena = AthenaHelper(
    workgroup='analytics-workgroup',
    output_location='s3://my-bucket/athena-results/'
)
```

#### Methods

##### execute_query()

Execute an Athena SQL query.

```python
execute_query(
    query: str,
    database: str = None,
    wait: bool = True
) -> str
```

**Parameters:**
- `query` (str): SQL query to execute
- `database` (str): Database name. Optional
- `wait` (bool): Wait for query completion. Default: True

**Returns:**
- `str`: Query execution ID

**Example:**
```python
query_id = athena.execute_query(
    query="SELECT * FROM transactions WHERE date = '2025-01-15'",
    database='analytics_prod'
)
```

##### get_query_results()

Get query results as list of dictionaries.

```python
get_query_results(query_execution_id: str) -> List[Dict]
```

**Parameters:**
- `query_execution_id` (str): Query execution ID

**Returns:**
- `List[Dict]`: Query results as list of dictionaries

**Example:**
```python
results = athena.get_query_results(query_id)
for row in results:
    print(row)
```

##### get_query_results_as_dataframe()

Get query results as pandas DataFrame.

```python
get_query_results_as_dataframe(query_execution_id: str) -> pd.DataFrame
```

**Parameters:**
- `query_execution_id` (str): Query execution ID

**Returns:**
- `pd.DataFrame`: Query results as DataFrame

**Example:**
```python
df = athena.get_query_results_as_dataframe(query_id)
print(df.head())
```

---

### GlueHelper

**Module**: `src.utils.glue_helper`

Helper class for AWS Glue operations.

#### Constructor

```python
GlueHelper(region_name: str = 'us-east-1')
```

**Parameters:**
- `region_name` (str): AWS region name

**Example:**
```python
from src.utils.glue_helper import GlueHelper

glue = GlueHelper(region_name='us-east-1')
```

#### Methods

##### start_job_run()

Start a Glue job execution.

```python
start_job_run(
    job_name: str,
    arguments: Dict[str, str] = None
) -> str
```

**Parameters:**
- `job_name` (str): Glue job name
- `arguments` (Dict[str, str]): Job arguments. Optional

**Returns:**
- `str`: Job run ID

**Example:**
```python
run_id = glue.start_job_run(
    job_name='transaction-etl',
    arguments={
        '--input_path': 's3://bucket/raw/transactions/',
        '--output_path': 's3://bucket/processed/transactions/'
    }
)
```

##### get_job_run_status()

Get status of a Glue job run.

```python
get_job_run_status(job_name: str, run_id: str) -> str
```

**Parameters:**
- `job_name` (str): Glue job name
- `run_id` (str): Job run ID

**Returns:**
- `str`: Job status ('RUNNING', 'SUCCEEDED', 'FAILED', etc.)

**Example:**
```python
status = glue.get_job_run_status('transaction-etl', run_id)
print(f"Job status: {status}")
```

##### start_crawler()

Start a Glue crawler.

```python
start_crawler(crawler_name: str) -> bool
```

**Parameters:**
- `crawler_name` (str): Crawler name

**Returns:**
- `bool`: True if started successfully

**Example:**
```python
success = glue.start_crawler('transactions-crawler')
```

---

## Data Generators

### TransactionGenerator

**Module**: `src.data-generators.generate_transactions`

Generate synthetic e-commerce transaction data.

#### Constructor

```python
TransactionGenerator(num_customers: int = 1000, num_products: int = 500)
```

**Parameters:**
- `num_customers` (int): Number of unique customers. Default: 1000
- `num_products` (int): Number of unique products. Default: 500

**Example:**
```python
from generate_transactions import TransactionGenerator

generator = TransactionGenerator(num_customers=5000, num_products=1000)
```

#### Methods

##### generate_transactions()

Generate transaction records.

```python
generate_transactions(num_rows: int, base_date: datetime) -> List[Dict]
```

**Parameters:**
- `num_rows` (int): Number of transactions to generate
- `base_date` (datetime): Base date for transaction dates

**Returns:**
- `List[Dict]`: List of transaction dictionaries

**Example:**
```python
from datetime import datetime

transactions = generator.generate_transactions(
    num_rows=10000,
    base_date=datetime.now()
)
```

##### save_to_csv()

Save transactions to CSV file.

```python
save_to_csv(transactions: List[Dict], output_path: Path) -> None
```

**Parameters:**
- `transactions` (List[Dict]): Transaction records
- `output_path` (Path): Output file path

**Example:**
```python
from pathlib import Path

generator.save_to_csv(
    transactions,
    Path('data/transactions.csv')
)
```

---

### ProductGenerator

**Module**: `src.data-generators.generate_products`

Generate synthetic product catalog data.

#### Constructor

```python
ProductGenerator()
```

**Example:**
```python
from generate_products import ProductGenerator

generator = ProductGenerator()
```

#### Methods

##### generate_products()

Generate product records.

```python
generate_products(num_products: int) -> List[Dict]
```

**Parameters:**
- `num_products` (int): Number of products to generate

**Returns:**
- `List[Dict]`: List of product dictionaries

**Example:**
```python
products = generator.generate_products(500)
```

---

## Ingestion Layer

### FileValidator

**Module**: `src.ingestion.file_validator`

AWS Lambda function for validating incoming data files.

#### Class: FileValidator

```python
FileValidator(bucket: str, key: str)
```

**Parameters:**
- `bucket` (str): S3 bucket name
- `key` (str): S3 object key

#### Methods

##### validate()

Perform comprehensive file validation.

```python
validate() -> Dict
```

**Returns:**
- `Dict`: Validation result with structure:
  ```python
  {
      'valid': bool,
      'errors': List[str],
      'warnings': List[str],
      'metadata': Dict
  }
  ```

**Example:**
```python
validator = FileValidator('my-bucket', 'raw/transactions/file.csv')
result = validator.validate()

if result['valid']:
    print("File is valid")
else:
    print(f"Errors: {result['errors']}")
```

#### Lambda Handler

```python
lambda_handler(event: Dict, context: Any) -> Dict
```

**Event Structure:**
```json
{
    "Records": [{
        "s3": {
            "bucket": {"name": "my-bucket"},
            "object": {"key": "raw/transactions/file.csv"}
        }
    }]
}
```

**Returns:**
```json
{
    "statusCode": 200,
    "body": "{...validation result...}"
}
```

---

## Transformation Layer

### DataQualityChecker

**Module**: `src.transformation.lambda_functions.data_quality_check`

Perform data quality checks on processed data.

#### Constructor

```python
DataQualityChecker(
    database: str,
    workgroup: str = 'primary',
    output_location: str = None
)
```

**Parameters:**
- `database` (str): Athena database name
- `workgroup` (str): Athena workgroup
- `output_location` (str): S3 location for query results

#### Methods

##### check_row_count()

Check if table has minimum number of rows.

```python
check_row_count(table_name: str, expected_min: int) -> bool
```

**Parameters:**
- `table_name` (str): Table name
- `expected_min` (int): Minimum expected row count

**Returns:**
- `bool`: True if check passes

##### check_null_percentages()

Check null percentages for critical columns.

```python
check_null_percentages(
    table_name: str,
    columns: List[str],
    max_null_pct: float = 0.1
) -> bool
```

**Parameters:**
- `table_name` (str): Table name
- `columns` (List[str]): Columns to check
- `max_null_pct` (float): Maximum allowed null percentage

**Returns:**
- `bool`: True if all checks pass

##### get_summary()

Get summary of all quality checks.

```python
get_summary() -> Dict
```

**Returns:**
```python
{
    'total_checks': int,
    'passed': int,
    'failed': int,
    'success_rate': float,
    'all_passed': bool,
    'checks_passed': List[Dict],
    'checks_failed': List[Dict]
}
```

---

## Analytics Layer

### SQL Queries

All SQL queries are located in `src/analytics/athena_queries/`.

#### top_products.sql

Identify top products by revenue.

**Parameters:**
- Uses last 30 days of data
- Joins `curated.transactions` and `curated.products`

**Returns:**
- Top 20 products by revenue
- Includes: product details, quantity sold, revenue, orders, customers, AOV, rating

**Usage:**
```sql
-- Execute in Athena
-- Results show top performing products
```

#### customer_ltv.sql

Calculate customer lifetime value and segmentation.

**Returns:**
- Customer segments: VIP, High Value, Medium Value, Low Value
- Frequency segments: Frequent, Regular, Occasional, One-time
- Metrics: LTV, orders, return rate, tenure

#### conversion_funnel.sql

Analyze conversion funnel metrics.

**Returns:**
- Sessions at each funnel stage
- Conversion rates between stages
- Drop-off analysis

#### daily_kpis.sql

Daily business KPIs dashboard.

**Returns:**
- Order metrics (total, completed, returned, refunded)
- Customer metrics (unique, paying)
- Revenue metrics (total, AOV, units sold)
- Return rates and time-based metrics

---

## Error Handling

All modules implement consistent error handling:

```python
try:
    # Operation
    result = operation()
except ClientError as e:
    logger.error(f"AWS error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

---

## Logging

All modules use Python's standard logging:

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Usage
logger.info("Operation started")
logger.error("Operation failed", exc_info=True)
```

---

## Best Practices

1. **Always specify region**: Pass `region_name` to helpers
2. **Use context managers**: For file operations and resources
3. **Handle errors gracefully**: Catch specific exceptions
4. **Log operations**: Use appropriate log levels
5. **Validate inputs**: Check parameters before operations
6. **Clean up resources**: Close connections and delete temp files

---

**Last Updated**: 2025-11-22  
**Version**: 1.0  
**Maintained By**: Data Engineering Team
