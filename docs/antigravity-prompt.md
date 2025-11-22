Data Analytics Pipeline
You are an expert data engineer and AWS solutions architect. Build a complete serverless data analytics pipeline that ingests, processes, transforms, and visualizes data using modern AWS data services and Infrastructure as Code.

PROJECT OVERVIEW:
Create an end-to-end data pipeline that demonstrates ETL processes, data quality checks, automated orchestration, and analytics capabilities. Use a realistic dataset (e.g., e-commerce transactions, website analytics, or IoT sensor data).

USE CASE SCENARIO:
Build an e-commerce analytics pipeline that processes:
- Customer transaction data (purchases, returns, refunds)
- Product catalog data
- Website clickstream data
- Customer reviews and ratings

The pipeline should answer business questions like:
- What are the top-selling products by category?
- Customer lifetime value analysis
- Conversion funnel metrics
- Product recommendation insights
- Revenue trends over time

PIPELINE ARCHITECTURE:
Data Sources → S3 Raw Zone → Lambda/Glue ETL → S3 Processed Zone
→ Glue Data Catalog → Athena Queries → Dashboard/Reports
↓
S3 Curated Zone (analytics-ready)

FUNCTIONAL REQUIREMENTS:

1. Data Ingestion Layer:
   - S3 bucket with three zones: raw/, processed/, curated/
   - Accept CSV, JSON, and Parquet formats
   - Automatic file detection with EventBridge
   - File validation (schema, format, size)
   - Deduplication logic
   - Error handling and dead letter queue

2. ETL Processing:
   - Clean and standardize data
   - Join multiple data sources
   - Calculate derived metrics
   - Handle missing values
   - Data type conversions
   - Partition data by date for query optimization

3. Data Catalog:
   - Glue crawlers to auto-discover schema
   - Data catalog with table definitions
   - Partition management
   - Schema evolution handling

4. Query Layer:
   - Athena workgroup with cost controls
   - Predefined named queries for common analytics
   - Query result caching
   - Partitioned queries for performance

5. Orchestration:
   - Step Functions workflow for pipeline execution
   - Scheduled daily runs
   - Event-driven processing for real-time files
   - Error handling and retries
   - SNS notifications for pipeline status

6. Data Quality:
   - Row count validation
   - Schema validation
   - Null value checks
   - Duplicate detection
   - Data freshness monitoring
   - Anomaly detection for key metrics

7. Visualization (Simple Dashboard):
   - Static HTML dashboard with charts (Chart.js)
   - Hosted on S3 + CloudFront
   - Query Athena via Lambda API
   - Auto-refresh every hour

TECHNICAL STACK:
- ETL Runtime: Python 3.11 (with pandas, boto3)
- Glue: Python shell jobs or Spark jobs
- IaC: Terraform
- CI/CD: GitHub Actions
- AWS Services: S3, Lambda, Glue, Athena, Step Functions, EventBridge, CloudWatch, SNS

SAMPLE DATASETS TO GENERATE:

1. **transactions.csv** (100k rows):
```csv
transaction_id,customer_id,product_id,quantity,price,total_amount,transaction_date,status
txn_001,cust_123,prod_456,2,29.99,59.98,2025-01-15,completed
txn_002,cust_124,prod_457,1,49.99,49.99,2025-01-15,completed
```

2. **products.json**:
```json
{
  "product_id": "prod_456",
  "name": "Wireless Mouse",
  "category": "Electronics",
  "brand": "TechBrand",
  "price": 29.99,
  "stock": 150
}
```

3. **clickstream.json** (streaming data):
```json
{
  "session_id": "sess_789",
  "customer_id": "cust_123",
  "event_type": "page_view",
  "page": "/product/prod_456",
  "timestamp": "2025-01-15T10:30:45Z",
  "device": "mobile"
}
```

4. **reviews.csv**:
```csv
review_id,product_id,customer_id,rating,review_text,review_date
rev_001,prod_456,cust_123,5,"Great product!",2025-01-16
```

TERRAFORM STRUCTURE:
terraform/
├── modules/
│   ├── s3-data-lake/
│   │   ├── main.tf (3 buckets with lifecycle policies)
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── glue-etl/
│   │   ├── main.tf (Glue jobs, crawlers, catalog database)
│   │   ├── glue-scripts/ (ETL scripts uploaded to S3)
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── lambda-processors/
│   │   ├── main.tf (validation, transformation functions)
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── athena/
│   │   ├── main.tf (workgroup, named queries, result bucket)
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── step-functions/
│   │   ├── main.tf (state machine definition)
│   │   ├── state-machine.json
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── eventbridge/
│   │   ├── main.tf (rules for file uploads, schedules)
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/
│       ├── main.tf (CloudWatch dashboards, alarms, SNS)
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── backend.tf
└── provider.tf

DATA PROCESSING FUNCTIONS:
src/
├── ingestion/
│   ├── file_validator.py
│   │   - Validate file format
│   │   - Check schema compliance
│   │   - Detect encoding
│   │   - Calculate file hash for deduplication
│   ├── file_router.py
│   │   - Route files to appropriate processing pipeline
│   │   - Trigger appropriate Glue job or Lambda
│   └── tests/
├── transformation/
│   ├── glue-jobs/
│   │   ├── transaction_etl.py
│   │   │   - Parse CSV/JSON
│   │   │   - Clean null values
│   │   │   - Standardize date formats
│   │   │   - Calculate derived fields
│   │   │   - Write Parquet to processed zone
│   │   ├── product_enrichment.py
│   │   │   - Join products with categories
│   │   │   - Calculate inventory metrics
│   │   ├── clickstream_aggregation.py
│   │   │   - Sessionize user activity
│   │   │   - Calculate conversion metrics
│   │   └── master_data_merge.py
│   │       - Join all data sources
│   │       - Create analytics-ready tables
│   ├── lambda-functions/
│   │   ├── lightweight_transform.py
│   │   │   - For small files < 100MB
│   │   │   - Quick transformations
│   │   └── data_quality_check.py
│   │       - Row count validation
│   │       - Null percentage checks
│   │       - Duplicate detection
│   └── tests/
├── analytics/
│   ├── athena_queries/
│   │   ├── top_products.sql
│   │   ├── revenue_by_category.sql
│   │   ├── customer_ltv.sql
│   │   ├── conversion_funnel.sql
│   │   └── daily_kpis.sql
│   ├── query_runner.py
│   │   - Execute Athena queries
│   │   - Cache results
│   │   - Return JSON for dashboard
│   └── tests/
├── orchestration/
│   ├── step_functions/
│   │   └── pipeline_definition.json
│   │       Steps:
│   │       1. Validate incoming files
│   │       2. Run Glue crawlers
│   │       3. Execute ETL jobs (parallel)
│   │       4. Data quality checks
│   │       5. Update curated zone
│   │       6. Refresh Athena tables
│   │       7. Send success/failure notification
│   └── event_handlers/
│       ├── s3_trigger.py
│       └── schedule_trigger.py
├── dashboard/
│   ├── index.html
│   │   - Simple analytics dashboard
│   │   - Charts using Chart.js
│   ├── api_handler.py
│   │   - Lambda function to query Athena
│   │   - Return JSON data for charts
│   ├── styles.css
│   └── app.js
├── utils/
│   ├── s3_helper.py
│   ├── glue_helper.py
│   ├── athena_helper.py
│   └── logger.py
└── data-generators/
├── generate_transactions.py
├── generate_products.py
├── generate_clickstream.py
└── generate_reviews.py

GLUE ETL JOB EXAMPLE (transaction_etl.py):
```python
Key transformations:
1. Read CSV from S3 raw zone
2. Convert date strings to datetime
3. Handle null values (fill or drop)
4. Calculate total_amount if missing
5. Add processing_date partition column
6. Filter out invalid transactions (amount < 0)
7. Deduplicate by transaction_id
8. Write as Parquet with snappy compression
9. Partition by date for query optimization
10. Update Glue catalog
```

STEP FUNCTIONS WORKFLOW:
```json
{
  "Comment": "E-commerce Data Pipeline",
  "StartAt": "ValidateFiles",
  "States": {
    "ValidateFiles": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:file-validator",
      "Next": "RunCrawlers"
    },
    "RunCrawlers": {
      "Type": "Parallel",
      "Branches": [
        {"StartAt": "CrawlTransactions", ...},
        {"StartAt": "CrawlProducts", ...},
        {"StartAt": "CrawlClickstream", ...}
      ],
      "Next": "ETLJobs"
    },
    "ETLJobs": {
      "Type": "Parallel",
      "Branches": [
        {"StartAt": "TransformTransactions", ...},
        {"StartAt": "EnrichProducts", ...},
        {"StartAt": "AggregateClickstream", ...}
      ],
      "Next": "DataQualityChecks"
    },
    "DataQualityChecks": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:data-quality",
      "Next": "MergeMasterData"
    },
    "MergRetryjson    "MergeMasterData": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "master-data-merge"
      },
      "Next": "RefreshAthena"
    },
    "RefreshAthena": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:refresh-athena-tables",
      "Next": "SendSuccessNotification"
    },
    "SendSuccessNotification": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:...:pipeline-notifications",
        "Subject": "Pipeline Success",
        "Message.$": "$.result"
      },
      "End": true
    }
  }
}
GITHUB ACTIONS WORKFLOWS:

.github/workflows/data-pipeline-ci.yml:

yamlname: Data Pipeline CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Lint Python code
        run: |
          black --check src/
          pylint src/
          flake8 src/
          mypy src/
      
      - name: Validate SQL queries
        run: |
          pip install sqlfluff
          sqlfluff lint src/analytics/athena_queries/
      
      - name: Run unit tests
        run: |
          pytest src/ --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
      
      - name: Test data generators
        run: |
          python src/data-generators/generate_transactions.py --rows 100
          python src/data-generators/generate_products.py --rows 50
      
      - name: Validate Glue scripts
        run: |
          python -m py_compile src/transformation/glue-jobs/*.py
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
      
      - name: Terraform fmt check
        run: terraform fmt -check -recursive terraform/
      
      - name: Terraform validate
        run: |
          cd terraform/environments/dev
          terraform init -backend=false
          terraform validate
      
      - name: TFSec security scan
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          working_directory: terraform/
      
      - name: Test with LocalStack
        run: |
          docker-compose up -d localstack
          pytest src/tests/integration/ --localstack

.github/workflows/terraform-plan.yml:

yamlname: Terraform Plan

on:
  pull_request:
    paths:
      - 'terraform/**'

jobs:
  plan:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/GitHubActionsRole
          aws-region: us-east-1
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
      
      - name: Terraform Init
        run: |
          cd terraform/environments/dev
          terraform init
      
      - name: Terraform Plan
        id: plan
        run: |
          cd terraform/environments/dev
          terraform plan -no-color -out=tfplan
        continue-on-error: true
      
      - name: Comment Plan on PR
        uses: actions/github-script@v6
        with:
          script: |
            const output = `#### Terraform Plan 📖
            \`\`\`
            ${{ steps.plan.outputs.stdout }}
            \`\`\`
            `;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            })
      
      - name: Infracost estimate
        run: |
          curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh
          infracost breakdown --path terraform/environments/dev --format json --out-file infracost.json
          infracost comment github --path infracost.json --repo $GITHUB_REPOSITORY --pull-request ${{ github.event.pull_request.number }}
        env:
          INFRACOST_API_KEY: ${{ secrets.INFRACOST_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

.github/workflows/deploy-pipeline.yml:

yamlname: Deploy Data Pipeline

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'dev'
        type: choice
        options:
          - dev
          - staging
          - prod

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/GitHubActionsRole
          aws-region: us-east-1
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Package Lambda functions
        run: |
          cd src/ingestion
          pip install -r requirements.txt -t package/
          cd package && zip -r ../ingestion.zip . && cd ..
          zip -g ingestion.zip *.py
          
          cd ../transformation/lambda-functions
          pip install -r requirements.txt -t package/
          cd package && zip -r ../transformation.zip . && cd ..
          zip -g transformation.zip *.py
      
      - name: Upload Glue scripts to S3
        run: |
          aws s3 sync src/transformation/glue-jobs/ s3://my-pipeline-scripts-${{ github.event.inputs.environment || 'dev' }}/glue-jobs/
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
      
      - name: Terraform Apply
        run: |
          cd terraform/environments/${{ github.event.inputs.environment || 'dev' }}
          terraform init
          terraform apply -auto-approve
      
      - name: Generate sample data
        if: github.event.inputs.environment == 'dev'
        run: |
          python src/data-generators/generate_transactions.py --rows 10000
          python src/data-generators/generate_products.py --rows 500
          python src/data-generators/generate_clickstream.py --rows 50000
          python src/data-generators/generate_reviews.py --rows 2000
      
      - name: Upload sample data to S3
        if: github.event.inputs.environment == 'dev'
        run: |
          aws s3 cp data/transactions.csv s3://my-data-lake-dev/raw/transactions/date=2025-01-15/
          aws s3 cp data/products.json s3://my-data-lake-dev/raw/products/date=2025-01-15/
          aws s3 cp data/clickstream.json s3://my-data-lake-dev/raw/clickstream/date=2025-01-15/
          aws s3 cp data/reviews.csv s3://my-data-lake-dev/raw/reviews/date=2025-01-15/
      
      - name: Trigger pipeline execution
        run: |
          EXECUTION_ARN=$(aws stepfunctions start-execution \
            --state-machine-arn arn:aws:states:us-east-1:${{ secrets.AWS_ACCOUNT_ID }}:stateMachine:data-pipeline-${{ github.event.inputs.environment || 'dev' }} \
            --input '{"date": "2025-01-15"}' \
            --query 'executionArn' \
            --output text)
          
          echo "Pipeline execution started: $EXECUTION_ARN"
      
      - name: Run integration tests
        run: |
          pytest src/tests/integration/ --environment=${{ github.event.inputs.environment || 'dev' }}
      
      - name: Deploy dashboard
        run: |
          cd src/dashboard
          aws s3 sync . s3://my-dashboard-${{ github.event.inputs.environment || 'dev' }}/ --exclude "*.py"
      
      - name: Notify on Slack
        if: always()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Data Pipeline Deployment: ${{ job.status }}",
              "environment": "${{ github.event.inputs.environment || 'dev' }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

.github/workflows/data-quality-monitoring.yml:

yamlname: Data Quality Monitoring

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/GitHubActionsRole
          aws-region: us-east-1
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install boto3 pandas great_expectations
      
      - name: Run data quality checks
        run: |
          python src/transformation/lambda-functions/data_quality_check.py \
            --environment prod \
            --report-output quality-report.json
      
      - name: Check data freshness
        run: |
          python scripts/check_data_freshness.py \
            --threshold-hours 24
      
      - name: Validate schema compliance
        run: |
          python scripts/validate_schemas.py \
            --catalog-database analytics_prod
      
      - name: Detect anomalies
        run: |
          python scripts/anomaly_detection.py \
            --metrics revenue,transactions,users \
            --lookback-days 30
      
      - name: Generate report
        run: |
          python scripts/generate_quality_report.py \
            --input quality-report.json \
            --output quality-report.html
      
      - name: Upload report to S3
        run: |
          aws s3 cp quality-report.html s3://my-reports-prod/quality/$(date +%Y-%m-%d)/
      
      - name: Send alerts if failures
        if: failure()
        run: |
          aws sns publish \
            --topic-arn arn:aws:sns:us-east-1:${{ secrets.AWS_ACCOUNT_ID }}:data-quality-alerts \
            --subject "Data Quality Check Failed" \
            --message "Data quality monitoring detected issues. Check the report for details."
DATA QUALITY CHECKS TO IMPLEMENT:
python# src/transformation/lambda-functions/data_quality_check.py

class DataQualityChecker:
    def __init__(self, athena_client, s3_client):
        self.athena = athena_client
        self.s3 = s3_client
    
    def check_row_counts(self, table_name, expected_min):
        """Ensure minimum row count"""
        query = f"SELECT COUNT(*) as cnt FROM {table_name}"
        result = self.execute_query(query)
        count = result[0]['cnt']
        
        if count < expected_min:
            raise DataQualityException(
                f"Row count {count} below threshold {expected_min}"
            )
        return count
    
    def check_null_percentages(self, table_name, columns, max_null_pct=0.1):
        """Check null percentages for critical columns"""
        for col in columns:
            query = f"""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) as nulls
                FROM {table_name}
            """
            result = self.execute_query(query)
            null_pct = result[0]['nulls'] / result[0]['total']
            
            if null_pct > max_null_pct:
                raise DataQualityException(
                    f"Column {col} has {null_pct:.2%} nulls (threshold: {max_null_pct:.2%})"
                )
    
    def check_duplicates(self, table_name, unique_columns):
        """Detect duplicate records"""
        cols = ', '.join(unique_columns)
        query = f"""
            SELECT {cols}, COUNT(*) as cnt
            FROM {table_name}
            GROUP BY {cols}
            HAVING COUNT(*) > 1
        """
        result = self.execute_query(query)
        
        if result:
            raise DataQualityException(
                f"Found {len(result)} duplicate records in {table_name}"
            )
    
    def check_data_freshness(self, table_name, date_column, max_age_hours=24):
        """Ensure data is recent"""
        query = f"""
            SELECT MAX({date_column}) as latest_date
            FROM {table_name}
        """
        result = self.execute_query(query)
        latest = datetime.fromisoformat(result[0]['latest_date'])
        age_hours = (datetime.now() - latest).total_seconds() / 3600
        
        if age_hours > max_age_hours:
            raise DataQualityException(
                f"Data is {age_hours:.1f} hours old (threshold: {max_age_hours})"
            )
    
    def check_value_ranges(self, table_name, column, min_val, max_val):
        """Validate numeric ranges"""
        query = f"""
            SELECT 
                MIN({column}) as min_val,
                MAX({column}) as max_val
            FROM {table_name}
        """
        result = self.execute_query(query)
        
        if result[0]['min_val'] < min_val or result[0]['max_val'] > max_val:
            raise DataQualityException(
                f"Column {column} has values outside range [{min_val}, {max_val}]"
            )
    
    def check_referential_integrity(self, parent_table, child_table, key):
        """Check foreign key relationships"""
        query = f"""
            SELECT COUNT(*) as orphans
            FROM {child_table} c
            LEFT JOIN {parent_table} p ON c.{key} = p.{key}
            WHERE p.{key} IS NULL
        """
        result = self.execute_query(query)
        
        if result[0]['orphans'] > 0:
            raise DataQualityException(
                f"Found {result[0]['orphans']} orphaned records in {child_table}"
            )
ATHENA NAMED QUERIES:
sql-- top_products.sql
SELECT 
    p.name,
    p.category,
    SUM(t.quantity) as total_quantity,
    SUM(t.total_amount) as total_revenue,
    COUNT(DISTINCT t.customer_id) as unique_customers
FROM curated.transactions t
JOIN curated.products p ON t.product_id = p.product_id
WHERE t.transaction_date >= DATE_ADD('day', -30, CURRENT_DATE)
    AND t.status = 'completed'
GROUP BY p.name, p.category
ORDER BY total_revenue DESC
LIMIT 20;

-- customer_ltv.sql
WITH customer_metrics AS (
    SELECT 
        customer_id,
        MIN(transaction_date) as first_purchase,
        MAX(transaction_date) as last_purchase,
        COUNT(DISTINCT transaction_id) as total_orders,
        SUM(total_amount) as lifetime_value,
        AVG(total_amount) as avg_order_value
    FROM curated.transactions
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN lifetime_value >= 1000 THEN 'High Value'
        WHEN lifetime_value >= 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment,
    COUNT(*) as customer_count,
    AVG(lifetime_value) as avg_ltv,
    AVG(total_orders) as avg_orders,
    AVG(avg_order_value) as avg_order_value
FROM customer_metrics
GROUP BY 1
ORDER BY avg_ltv DESC;

-- conversion_funnel.sql
WITH funnel_data AS (
    SELECT 
        DATE(timestamp) as date,
        SUM(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) as page_views,
        SUM(CASE WHEN event_type = 'product_view' THEN 1 ELSE 0 END) as product_views,
        SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) as add_to_carts,
        SUM(CASE WHEN event_type = 'checkout_start' THEN 1 ELSE 0 END) as checkout_starts,
        SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as purchases
    FROM curated.clickstream
    WHERE timestamp >= DATE_ADD('day', -7, CURRENT_DATE)
    GROUP BY DATE(timestamp)
)
SELECT 
    date,
    page_views,
    product_views,
    ROUND(100.0 * product_views / NULLIF(page_views, 0), 2) as view_to_product_rate,
    add_to_carts,
    ROUND(100.0 * add_to_carts / NULLIF(product_views, 0), 2) as product_to_cart_rate,
    checkout_starts,
    ROUND(100.0 * checkout_starts / NULLIF(add_to_carts, 0), 2) as cart_to_checkout_rate,
    purchases,
    ROUND(100.0 * purchases / NULLIF(checkout_starts, 0), 2) as checkout_to_purchase_rate,
    ROUND(100.0 * purchases / NULLIF(page_views, 0), 2) as overall_conversion_rate
FROM funnel_data
ORDER BY date DESC;

-- daily_kpis.sql
SELECT 
    DATE(transaction_date) as date,
    COUNT(DISTINCT transaction_id) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(total_amount) as revenue,
    AVG(total_amount) as avg_order_value,
    SUM(quantity) as units_sold,
    COUNT(DISTINCT CASE WHEN status = 'returned' THEN transaction_id END) as returns,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN status = 'returned' THEN transaction_id END) / COUNT(DISTINCT transaction_id), 2) as return_rate
FROM curated.transactions
WHERE transaction_date >= DATE_ADD('day', -90, CURRENT_DATE)
GROUP BY DATE(transaction_date)
ORDER BY date DESC;
SIMPLE DASHBOARD (index.html):
html<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="dashboard">
        <header>
            <h1>E-Commerce Analytics Dashboard</h1>
            <div class="last-updated">Last Updated: <span id="timestamp"></span></div>
        </header>
        
        <div class="kpi-cards">
            <div class="card">
                <h3>Total Revenue</h3>
                <div class="value" id="total-revenue">$0</div>
                <div class="change positive" id="revenue-change">+0%</div>
            </div>
            <div class="card">
                <h3>Total Orders</h3>
                <div class="value" id="total-orders">0</div>
                <div class="change" id="orders-change">+0%</div>
            </div>
            <div class="card">
                <h3>Avg Order Value</h3>
                <div class="value" id="avg-order-value">$0</div>
                <div class="change" id="aov-change">+0%</div>
            </div>
            <div class="card">
                <h3>Conversion Rate</h3>
                <div class="value" id="conversion-rate">0%</div>
                <div class="change" id="conversion-change">+0%</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-container">
                <h2>Revenue Trend (30 Days)</h2>
                <canvas id="revenue-chart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2>Top Products</h2>
                <canvas id="products-chart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2>Conversion Funnel</h2>
                <canvas id="funnel-chart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2>Customer Segments</h2>
                <canvas id="segments-chart"></canvas>
            </div>
        </div>
    </div>
    
    <script src="app.js"></script>
</body>
</html>
javascript// app.js
const API_ENDPOINT = 'https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com';

async function fetchData(query) {
    const response = await fetch(`${API_ENDPOINT}/analytics?query=${query}`);
    return response.json();
}

async function updateDashboard() {
    try {
        // Fetch all data
        const [revenueData, productsData, funnelData, segmentsData, kpisData] = await Promise.all([
            fetchData('daily_kpis'),
            fetchData('top_products'),
            fetchData('conversion_funnel'),
            fetchData('customer_ltv'),
            fetchData('current_kpis')
        ]);
        
        // Update KPI cards
        document.getElementById('total-revenue').textContent = 
            `$${(kpisData.total_revenue / 1000).toFixed(1)}K`;
        document.getElementById('total-orders').textContent = 
            kpisData.total_orders.toLocaleString();
        document.getElementById('avg-order-value').textContent = 
            `$${kpisData.avg_order_value.toFixed(2)}`;
        document.getElementById('conversion-rate').textContent = 
            `${kpisData.conversion_rate.toFixed(2)}%`;
        
        // Revenue trend chart
        new Chart(document.getElementById('revenue-chart'), {
            type: 'line',
            data: {
                labels: revenueData.map(d => d.date),
                datasets: [{
                    label: 'Revenue',
                    data: revenueData.map(d => d.revenue),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });
        
        // Top products chart
        new Chart(document.getElementById('products-chart'), {
            type: 'bar',
            data: {
                labels: productsData.slice(0, 10).map(d => d.name),
                datasets: [{
                    label: 'Revenue',
                    data: productsData.slice(0, 10).map(d => d.total_revenue),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true
            }
        });
        
        // Conversion funnel chart
        new Chart(document.getElementById('funnel-chart'), {
            type: 'bar',
            data: {
                labels: ['Page Views', 'Product Views', 'Add to Cart', 'Checkout', 'Purchase'],
                datasets: [{
                    label: 'Count',
                    data: [
                        funnelData[0].page_views,
                        funnelData[0].product_views,
                        funnelData[0].add_to_carts,
                        funnelData[0].checkout_starts,
                        funnelData[0].purchases
                    ],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(75, 192, 192, 0.5)',
                        'rgba(153, 102, 255, 0.5)'
                    ]
                }]
            }
        });
        
        // Customer segments chart
        new Chart(document.getElementById('segments-chart'), {
            type: 'doughnut',
            data: {
                labels: segmentsData.map(d => d.customer_segment),
                datasets: [{
                    data: segmentsData.map(d => d.customer_count),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)'
                    ]
                }]
            }
        });
        
        // Update timestamp
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
        
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Initial load
updateDashboard();

// Auto-refresh every hour
setInterval(updateDashboard, 3600000);
```

DOCUMENTATION REQUIREMENTS:

1. **README.md** must include:
   - Architecture diagram showing data flow
   - List of AWS services used
   - Setup instructions step-by-step
   - How to generate sample data
   - How to trigger the pipeline
   - How to query data with Athena
   - Cost breakdown
   - Troubleshooting guide

2. **DATA_DICTIONARY.md**:
   - Schema for each table
   - Column descriptions
   - Data types
   - Sample values
   - Partition strategy

3. **PIPELINE_GUIDE.md**:
   - ETL job descriptions
   - Transformation logic
   - Data quality rules
   - Monitoring and alerting
   - How to add new data sources

DELIVERABLES:
1. Complete data pipeline codebase
2. Terraform infrastructure (all modules)
3. GitHub Actions workflows (4 workflows)
4. Data generators for sample data
5. Glue ETL scripts
6. Lambda functions
7. Step Functions workflow
8. Athena queries
9. Simple dashboard
10. Comprehensive documentation
11. Architecture diagrams
12. Test suite

CONSTRAINTS:
- Pipeline must complete in < 30 minutes for 1M records
- Query performance < 5 seconds for aggregations
- Data quality checks must catch 99% of issues
- Cost < $20/month for typical usage
- All data encrypted at rest and in transit
- Must handle schema evolution gracefully

Build this with production-grade data engineering practices, comprehensive monitoring, and excellent documentation to showcase data platform skills.
```