# E-Commerce Data Analytics Pipeline

A production-grade serverless data analytics pipeline built on AWS that ingests, processes, transforms, and visualizes e-commerce data using modern data engineering practices and Infrastructure as Code.

## 🏗️ Architecture Overview

```
Data Sources → S3 Raw Zone → Lambda/Glue ETL → S3 Processed Zone
                                    ↓
                            Glue Data Catalog
                                    ↓
                            Athena Queries → Dashboard/Reports
                                    ↓
                            S3 Curated Zone (analytics-ready)
```

### Architecture Diagram

```
┌─────────────────┐
│  Data Sources   │
│  - Transactions │
│  - Products     │
│  - Clickstream  │
│  - Reviews      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              S3 Data Lake (Raw Zone)                    │
│  s3://bucket/raw/transactions/date=YYYY-MM-DD/          │
│  s3://bucket/raw/products/date=YYYY-MM-DD/              │
│  s3://bucket/raw/clickstream/date=YYYY-MM-DD/           │
│  s3://bucket/raw/reviews/date=YYYY-MM-DD/               │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  EventBridge    │──────│  Step Functions  │
│  S3 Events      │      │  Orchestration   │
└─────────────────┘      └────────┬─────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Lambda          │    │  Glue Crawlers   │    │  Glue ETL Jobs  │
│ File Validator  │    │  Schema Discovery│    │  Transformations│
└─────────────────┘    └──────────────────┘    └────────┬────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────┐
                                          │ S3 Processed Zone        │
                                          │ Parquet + Partitioned    │
                                          └────────┬─────────────────┘
                                                   │
                                                   ▼
                                          ┌──────────────────────────┐
                                          │ Data Quality Checks      │
                                          │ - Row counts             │
                                          │ - Null validation        │
                                          │ - Duplicates             │
                                          │ - Freshness              │
                                          └────────┬─────────────────┘
                                                   │
                                                   ▼
                                          ┌──────────────────────────┐
                                          │ S3 Curated Zone          │
                                          │ Analytics-Ready Tables   │
                                          └────────┬─────────────────┘
                                                   │
         ┌─────────────────────────────────────────┼─────────────────┐
         ▼                                         ▼                 ▼
┌─────────────────┐                    ┌──────────────────┐  ┌──────────────┐
│ Glue Catalog    │                    │  Athena Queries  │  │  Dashboard   │
│ Metadata Store  │                    │  SQL Analytics   │  │  S3+CloudFront│
└─────────────────┘                    └──────────────────┘  └──────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Monitoring & Alerting                      │
│  CloudWatch Dashboards | SNS Notifications              │
└─────────────────────────────────────────────────────────┘
```

## 📊 Use Case: E-Commerce Analytics

This pipeline processes and analyzes:
- **Customer Transactions**: Purchases, returns, refunds
- **Product Catalog**: Product details, categories, pricing
- **Website Clickstream**: User behavior, page views, events
- **Customer Reviews**: Ratings and feedback

### Business Questions Answered

1. **Top-Selling Products by Category**
2. **Customer Lifetime Value (LTV) Analysis**
3. **Conversion Funnel Metrics**
4. **Product Recommendation Insights**
5. **Revenue Trends Over Time**
6. **Customer Segmentation**
7. **Return Rate Analysis**

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Infrastructure as Code** | Terraform |
| **ETL Runtime** | Python 3.11 (pandas, boto3) |
| **Data Processing** | AWS Glue (PySpark), AWS Lambda |
| **Data Storage** | Amazon S3 (Data Lake) |
| **Data Catalog** | AWS Glue Data Catalog |
| **Query Engine** | Amazon Athena |
| **Orchestration** | AWS Step Functions |
| **Event Processing** | Amazon EventBridge |
| **Monitoring** | Amazon CloudWatch, SNS |
| **Dashboard** | Static HTML + Chart.js |
| **CI/CD** | GitHub Actions |

## 📁 Project Structure

```
dataanalytics-project/
├── .github/
│   └── workflows/
│       ├── data-pipeline-ci.yml          # CI tests, linting, validation
│       ├── terraform-plan.yml            # Infrastructure planning
│       ├── deploy-pipeline.yml           # Deployment automation
│       └── data-quality-monitoring.yml   # Scheduled quality checks
├── terraform/
│   ├── modules/
│   │   ├── s3-data-lake/                # S3 buckets with lifecycle
│   │   ├── glue-etl/                    # Glue jobs, crawlers, catalog
│   │   ├── lambda-processors/           # Lambda functions
│   │   ├── athena/                      # Athena workgroup, queries
│   │   ├── step-functions/              # Orchestration workflow
│   │   ├── eventbridge/                 # Event rules and triggers
│   │   └── monitoring/                  # CloudWatch, SNS
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   ├── backend.tf
│   └── provider.tf
├── src/
│   ├── ingestion/
│   │   ├── file_validator.py           # Schema & format validation
│   │   ├── file_router.py              # Route to appropriate pipeline
│   │   └── tests/
│   ├── transformation/
│   │   ├── glue-jobs/
│   │   │   ├── transaction_etl.py      # Transaction processing
│   │   │   ├── product_enrichment.py   # Product data enrichment
│   │   │   ├── clickstream_aggregation.py
│   │   │   └── master_data_merge.py    # Join all sources
│   │   ├── lambda-functions/
│   │   │   ├── lightweight_transform.py
│   │   │   └── data_quality_check.py
│   │   └── tests/
│   ├── analytics/
│   │   ├── athena_queries/
│   │   │   ├── top_products.sql
│   │   │   ├── revenue_by_category.sql
│   │   │   ├── customer_ltv.sql
│   │   │   ├── conversion_funnel.sql
│   │   │   └── daily_kpis.sql
│   │   ├── query_runner.py
│   │   └── tests/
│   ├── orchestration/
│   │   ├── step_functions/
│   │   │   └── pipeline_definition.json
│   │   └── event_handlers/
│   ├── dashboard/
│   │   ├── index.html
│   │   ├── styles.css
│   │   ├── app.js
│   │   └── api_handler.py
│   ├── utils/
│   │   ├── s3_helper.py
│   │   ├── glue_helper.py
│   │   ├── athena_helper.py
│   │   └── logger.py
│   └── data-generators/
│       ├── generate_transactions.py
│       ├── generate_products.py
│       ├── generate_clickstream.py
│       └── generate_reviews.py
├── scripts/
│   ├── check_data_freshness.py
│   ├── validate_schemas.py
│   ├── anomaly_detection.py
│   └── generate_quality_report.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── PIPELINE_GUIDE.md
│   ├── SETUP.md
│   └── TROUBLESHOOTING.md
├── data/                               # Generated sample data
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Terraform >= 1.5.0
- Python 3.11+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/dataanalytics-project.git
cd dataanalytics-project
```

### 2. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and default region
```

### 4. Generate Sample Data

```bash
# Generate sample datasets
python src/data-generators/generate_transactions.py --rows 100000
python src/data-generators/generate_products.py --rows 500
python src/data-generators/generate_clickstream.py --rows 50000
python src/data-generators/generate_reviews.py --rows 2000
```

This creates sample data files in the `data/` directory.

### 5. Deploy Infrastructure

```bash
cd terraform/environments/dev

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Deploy
terraform apply
```

### 6. Upload Sample Data to S3

```bash
# Get bucket name from Terraform output
BUCKET_NAME=$(terraform output -raw data_lake_bucket_name)

# Upload data to raw zone
aws s3 cp ../../data/transactions.csv s3://$BUCKET_NAME/raw/transactions/date=2025-01-15/
aws s3 cp ../../data/products.json s3://$BUCKET_NAME/raw/products/date=2025-01-15/
aws s3 cp ../../data/clickstream.json s3://$BUCKET_NAME/raw/clickstream/date=2025-01-15/
aws s3 cp ../../data/reviews.csv s3://$BUCKET_NAME/raw/reviews/date=2025-01-15/
```

### 7. Trigger the Pipeline

```bash
# Get Step Functions ARN
STATE_MACHINE_ARN=$(terraform output -raw step_functions_arn)

# Start execution
aws stepfunctions start-execution \
  --state-machine-arn $STATE_MACHINE_ARN \
  --input '{"date": "2025-01-15"}'
```

### 8. Monitor Pipeline Execution

```bash
# Check execution status
aws stepfunctions list-executions \
  --state-machine-arn $STATE_MACHINE_ARN \
  --max-results 1

# View CloudWatch logs
aws logs tail /aws/lambda/data-pipeline-dev --follow
```

### 9. Query Data with Athena

```bash
# Get Athena workgroup
WORKGROUP=$(terraform output -raw athena_workgroup_name)

# Run a query
aws athena start-query-execution \
  --query-string "SELECT * FROM curated.transactions LIMIT 10" \
  --work-group $WORKGROUP \
  --result-configuration "OutputLocation=s3://$BUCKET_NAME/athena-results/"
```

### 10. Access the Dashboard

```bash
# Get CloudFront URL
DASHBOARD_URL=$(terraform output -raw dashboard_url)
echo "Dashboard available at: $DASHBOARD_URL"
```

## 📊 Data Schema

### Transactions Table

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | STRING | Unique transaction identifier |
| customer_id | STRING | Customer identifier |
| product_id | STRING | Product identifier |
| quantity | INT | Number of items purchased |
| price | DECIMAL(10,2) | Unit price |
| total_amount | DECIMAL(10,2) | Total transaction amount |
| transaction_date | DATE | Date of transaction |
| status | STRING | completed, returned, refunded |

### Products Table

| Column | Type | Description |
|--------|------|-------------|
| product_id | STRING | Unique product identifier |
| name | STRING | Product name |
| category | STRING | Product category |
| brand | STRING | Brand name |
| price | DECIMAL(10,2) | Current price |
| stock | INT | Available inventory |

### Clickstream Table

| Column | Type | Description |
|--------|------|-------------|
| session_id | STRING | User session identifier |
| customer_id | STRING | Customer identifier |
| event_type | STRING | page_view, product_view, add_to_cart, etc. |
| page | STRING | Page URL |
| timestamp | TIMESTAMP | Event timestamp |
| device | STRING | mobile, desktop, tablet |

### Reviews Table

| Column | Type | Description |
|--------|------|-------------|
| review_id | STRING | Unique review identifier |
| product_id | STRING | Product identifier |
| customer_id | STRING | Customer identifier |
| rating | INT | Rating (1-5) |
| review_text | STRING | Review content |
| review_date | DATE | Review date |

## 🔄 Pipeline Workflow

The Step Functions orchestration executes the following steps:

1. **Validate Files** - Check schema, format, and size
2. **Run Crawlers** - Discover schema and update catalog (parallel)
3. **ETL Jobs** - Transform and clean data (parallel)
   - Transaction ETL
   - Product Enrichment
   - Clickstream Aggregation
4. **Data Quality Checks** - Validate processed data
5. **Merge Master Data** - Join all sources into curated zone
6. **Refresh Athena Tables** - Update partitions
7. **Send Notification** - SNS alert on success/failure

## 📈 Sample Queries

### Top 10 Products by Revenue

```sql
SELECT 
    p.name,
    p.category,
    SUM(t.total_amount) as total_revenue,
    COUNT(*) as order_count
FROM curated.transactions t
JOIN curated.products p ON t.product_id = p.product_id
WHERE t.status = 'completed'
  AND t.transaction_date >= DATE_ADD('day', -30, CURRENT_DATE)
GROUP BY p.name, p.category
ORDER BY total_revenue DESC
LIMIT 10;
```

### Customer Lifetime Value

```sql
SELECT 
    customer_id,
    COUNT(DISTINCT transaction_id) as total_orders,
    SUM(total_amount) as lifetime_value,
    AVG(total_amount) as avg_order_value,
    MIN(transaction_date) as first_purchase,
    MAX(transaction_date) as last_purchase
FROM curated.transactions
WHERE status = 'completed'
GROUP BY customer_id
ORDER BY lifetime_value DESC
LIMIT 100;
```

### Conversion Funnel

```sql
SELECT 
    SUM(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) as page_views,
    SUM(CASE WHEN event_type = 'product_view' THEN 1 ELSE 0 END) as product_views,
    SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) as add_to_carts,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as purchases,
    ROUND(100.0 * SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END), 0), 2) as conversion_rate
FROM curated.clickstream
WHERE DATE(timestamp) >= DATE_ADD('day', -7, CURRENT_DATE);
```

## 💰 Cost Breakdown

Estimated monthly costs for typical usage (dev environment):

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **S3 Storage** | 100 GB | $2.30 |
| **S3 Requests** | 1M PUT, 10M GET | $0.55 |
| **Lambda** | 1M invocations, 512MB | $0.20 |
| **Glue ETL** | 10 DPU-hours/day | $13.20 |
| **Glue Crawler** | 1 hour/day | $0.44 |
| **Athena** | 100 GB scanned | $0.50 |
| **Step Functions** | 1K transitions | $0.03 |
| **CloudWatch** | Logs & Metrics | $1.00 |
| **SNS** | 1K notifications | $0.00 |
| **CloudFront** | 10 GB transfer | $0.85 |
| **TOTAL** | | **~$19.07/month** |

**Production environment** (with higher volume):
- Estimated: $50-150/month depending on data volume and query frequency

### Cost Optimization Tips

1. **Use Partitioning** - Reduces Athena scan costs by 90%+
2. **Parquet Format** - 5-10x smaller than CSV, faster queries
3. **S3 Lifecycle Policies** - Move old data to Glacier
4. **Glue Job Bookmarks** - Process only new data
5. **Athena Result Caching** - Reuse recent query results
6. **Right-size Lambda** - Use appropriate memory settings
7. **Reserved Capacity** - For predictable Glue workloads

## 🔒 Security Features

- **Encryption at Rest**: All S3 buckets use SSE-S3 encryption
- **Encryption in Transit**: TLS 1.2+ for all data transfers
- **IAM Least Privilege**: Role-based access control
- **VPC Endpoints**: Private connectivity to AWS services
- **CloudTrail Logging**: Audit all API calls
- **Secrets Management**: AWS Secrets Manager for credentials
- **Data Masking**: PII data masked in non-prod environments

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/unit/ -v --cov=src
```

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

### Run with LocalStack (Local AWS)

```bash
docker-compose up -d localstack
pytest tests/integration/ --localstack
```

### Data Quality Tests

```bash
python src/transformation/lambda-functions/data_quality_check.py \
  --environment dev \
  --report-output quality-report.json
```

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Detailed architecture and design decisions
- **[Data Dictionary](docs/DATA_DICTIONARY.md)** - Complete schema documentation
- **[Pipeline Guide](docs/PIPELINE_GUIDE.md)** - ETL processes and transformations
- **[Setup Guide](docs/SETUP.md)** - Detailed setup instructions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🔧 Troubleshooting

### Pipeline Execution Failed

```bash
# Check Step Functions execution
aws stepfunctions describe-execution --execution-arn <EXECUTION_ARN>

# Check CloudWatch logs
aws logs tail /aws/lambda/data-pipeline-dev-validator --follow
```

### Glue Job Errors

```bash
# View Glue job logs
aws logs tail /aws-glue/jobs/output --follow

# Check job run details
aws glue get-job-run --job-name transaction-etl --run-id <RUN_ID>
```

### Athena Query Failures

```bash
# Check query execution
aws athena get-query-execution --query-execution-id <QUERY_ID>

# Common issues:
# - Partition not found: Run MSCK REPAIR TABLE <table_name>
# - Schema mismatch: Check Glue catalog schema
```

### Data Quality Issues

```bash
# Run manual quality check
python src/transformation/lambda-functions/data_quality_check.py \
  --table curated.transactions \
  --checks row_count,nulls,duplicates
```

## 🚀 CI/CD Pipeline

GitHub Actions workflows automatically:

1. **On Pull Request**:
   - Run linting (black, pylint, flake8, mypy)
   - Execute unit tests with coverage
   - Validate Terraform configuration
   - Run security scans (tfsec)
   - Generate Terraform plan
   - Comment plan on PR

2. **On Merge to Main**:
   - Package Lambda functions
   - Upload Glue scripts to S3
   - Deploy infrastructure with Terraform
   - Run integration tests
   - Deploy dashboard to S3/CloudFront
   - Send Slack notification

3. **Scheduled (Every 6 hours)**:
   - Run data quality checks
   - Check data freshness
   - Validate schema compliance
   - Detect anomalies
   - Generate quality reports

## 📊 Monitoring & Alerting

### CloudWatch Dashboards

- **Pipeline Health**: Execution success rate, duration, errors
- **Data Quality**: Row counts, null percentages, duplicates
- **Cost Tracking**: Service usage and spend
- **Performance**: Query latency, ETL job duration

### SNS Alerts

- Pipeline execution failures
- Data quality check failures
- Data freshness violations
- Cost threshold exceeded
- Schema evolution detected

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS Data Analytics Reference Architecture
- AWS Well-Architected Framework
- Data Engineering Best Practices

## 📞 Support

For issues and questions:
- Create an issue in this repository
- Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- Review [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)
- Review [AWS Athena Documentation](https://docs.aws.amazon.com/athena/)

---

**Built with ❤️ using AWS Serverless Data Analytics Services**
