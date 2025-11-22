# Setup Guide

Complete step-by-step guide to set up and deploy the e-commerce data analytics pipeline.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [AWS Account Setup](#aws-account-setup)
4. [Infrastructure Deployment](#infrastructure-deployment)
5. [Data Pipeline Execution](#data-pipeline-execution)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **AWS CLI**: [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **Terraform 1.5+**: [Download](https://www.terraform.io/downloads)
- **Git**: [Download](https://git-scm.com/downloads)
- **Make** (optional): For using Makefile commands

### AWS Account Requirements

- Active AWS account
- IAM user with appropriate permissions
- AWS CLI configured with credentials

### Estimated Costs

- **Development**: ~$20/month
- **Production**: ~$100/month (varies with usage)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/dataanalytics-project.git
cd dataanalytics-project
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

**Using Make:**
```bash
make install-dev
```

**Manual:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Verify Installation

```bash
python --version  # Should be 3.11+
pytest --version
terraform --version
aws --version
```

### 5. Generate Sample Data

**Using Make:**
```bash
make generate-data
```

**Manual:**
```bash
python src/data-generators/generate_transactions.py --rows 10000
python src/data-generators/generate_products.py --rows 500
python src/data-generators/generate_clickstream.py --rows 5000
python src/data-generators/generate_reviews.py --rows 1000
```

This creates sample data files in the `data/` directory.

### 6. Run Tests

```bash
make test
# or
pytest tests/ -v
```

## AWS Account Setup

### 1. Create IAM User

1. Go to AWS Console → IAM → Users
2. Click "Add users"
3. Username: `data-pipeline-admin`
4. Access type: Programmatic access
5. Attach policies:
   - `AmazonS3FullAccess`
   - `AWSGlueConsoleFullAccess`
   - `AmazonAthenaFullAccess`
   - `AWSLambda_FullAccess`
   - `AWSStepFunctionsFullAccess`
   - `CloudWatchFullAccess`
   - `IAMFullAccess` (for creating roles)

6. Save the Access Key ID and Secret Access Key

### 2. Configure AWS CLI

```bash
aws configure
```

Enter:
- AWS Access Key ID: `[your-access-key]`
- AWS Secret Access Key: `[your-secret-key]`
- Default region: `us-east-1`
- Default output format: `json`

### 3. Verify AWS Access

```bash
aws sts get-caller-identity
```

Should return your account details.

### 4. Create S3 Backend Bucket (for Terraform state)

```bash
aws s3 mb s3://data-pipeline-terraform-state-[your-account-id]
aws s3api put-bucket-versioning \
  --bucket data-pipeline-terraform-state-[your-account-id] \
  --versioning-configuration Status=Enabled
```

## Infrastructure Deployment

### 1. Configure Terraform Backend

Create `terraform/environments/dev/backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "data-pipeline-terraform-state-[your-account-id]"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### 2. Create DynamoDB Table for State Locking

```bash
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 3. Initialize Terraform

```bash
cd terraform/environments/dev
terraform init
```

### 4. Review Infrastructure Plan

```bash
terraform plan
```

Review the resources that will be created:
- S3 buckets (data lake, scripts, logs)
- Glue database and crawlers
- Glue ETL jobs
- Lambda functions
- Step Functions state machine
- EventBridge rules
- CloudWatch dashboards
- SNS topics

### 5. Deploy Infrastructure

```bash
terraform apply
```

Type `yes` to confirm.

This will take approximately 5-10 minutes.

### 6. Save Outputs

```bash
terraform output > ../../../terraform-outputs.txt
```

Important outputs:
- `data_lake_bucket_name`
- `scripts_bucket_name`
- `step_functions_arn`
- `athena_workgroup_name`

## Data Pipeline Execution

### 1. Upload Glue Scripts to S3

```bash
# Get scripts bucket name
SCRIPTS_BUCKET=$(terraform output -raw scripts_bucket_name)

# Upload Glue ETL scripts
aws s3 cp ../../../src/transformation/glue-jobs/transaction_etl.py \
  s3://$SCRIPTS_BUCKET/glue-jobs/transaction_etl.py
```

### 2. Upload Sample Data to Raw Zone

```bash
# Get data lake bucket name
DATA_BUCKET=$(terraform output -raw data_lake_bucket_name)

# Upload sample data
aws s3 cp ../../../data/transactions.csv \
  s3://$DATA_BUCKET/raw/transactions/date=2025-01-15/transactions.csv

aws s3 cp ../../../data/products.json \
  s3://$DATA_BUCKET/raw/products/date=2025-01-15/products.json

aws s3 cp ../../../data/clickstream.json \
  s3://$DATA_BUCKET/raw/clickstream/date=2025-01-15/clickstream.json

aws s3 cp ../../../data/reviews.csv \
  s3://$DATA_BUCKET/raw/reviews/date=2025-01-15/reviews.csv
```

### 3. Trigger Pipeline Execution

```bash
# Get Step Functions ARN
STATE_MACHINE_ARN=$(terraform output -raw step_functions_arn)

# Start execution
EXECUTION_ARN=$(aws stepfunctions start-execution \
  --state-machine-arn $STATE_MACHINE_ARN \
  --input '{"bucket": "'$DATA_BUCKET'", "key": "raw/transactions/date=2025-01-15/transactions.csv"}' \
  --query 'executionArn' \
  --output text)

echo "Pipeline execution started: $EXECUTION_ARN"
```

### 4. Monitor Execution

**View in AWS Console:**
1. Go to Step Functions → State machines
2. Click on your state machine
3. View the execution graph

**Using CLI:**
```bash
aws stepfunctions describe-execution --execution-arn $EXECUTION_ARN
```

**View Logs:**
```bash
# Lambda logs
aws logs tail /aws/lambda/data-pipeline-dev-validator --follow

# Glue job logs
aws logs tail /aws-glue/jobs/output --follow
```

## Verification

### 1. Check S3 Processed Data

```bash
# List processed files
aws s3 ls s3://$DATA_BUCKET/processed/transactions/ --recursive

# Should see Parquet files partitioned by date
```

### 2. Query Data with Athena

```bash
# Get Athena workgroup
WORKGROUP=$(terraform output -raw athena_workgroup_name)

# Run a test query
QUERY_ID=$(aws athena start-query-execution \
  --query-string "SELECT COUNT(*) as count FROM curated.transactions" \
  --work-group $WORKGROUP \
  --result-configuration "OutputLocation=s3://$DATA_BUCKET/athena-results/" \
  --query 'QueryExecutionId' \
  --output text)

# Wait for query to complete
aws athena get-query-execution --query-execution-id $QUERY_ID

# Get results
aws athena get-query-results --query-execution-id $QUERY_ID
```

### 3. Verify Data Quality

Check CloudWatch Logs for data quality check results:

```bash
aws logs tail /aws/lambda/data-pipeline-dev-quality-check --follow
```

### 4. Test Athena Named Queries

In AWS Console:
1. Go to Athena
2. Select your workgroup
3. Go to "Saved queries"
4. Run the pre-defined queries:
   - Top Products
   - Customer LTV
   - Conversion Funnel
   - Daily KPIs

## Troubleshooting

### Common Issues

#### 1. Terraform Apply Fails

**Error**: "Error creating S3 bucket: BucketAlreadyExists"

**Solution**: Bucket names must be globally unique. Update bucket names in variables.

#### 2. Glue Job Fails

**Error**: "Script not found in S3"

**Solution**: Ensure Glue scripts are uploaded to the scripts bucket:
```bash
aws s3 ls s3://$SCRIPTS_BUCKET/glue-jobs/
```

#### 3. Athena Query Fails

**Error**: "Table not found"

**Solution**: Run Glue crawlers to discover schema:
```bash
aws glue start-crawler --name transactions-crawler
```

#### 4. Step Functions Execution Fails

**Error**: "Lambda function timeout"

**Solution**: Increase Lambda timeout in Terraform configuration.

#### 5. Data Quality Checks Fail

**Error**: "Row count below threshold"

**Solution**: Check if data was properly uploaded to S3 and processed by Glue.

### Getting Help

1. **Check CloudWatch Logs**: All services log to CloudWatch
2. **Review Terraform State**: `terraform show`
3. **AWS Support**: For AWS-specific issues
4. **GitHub Issues**: For code-related issues

## Next Steps

After successful setup:

1. **Customize Data Generators**: Modify to match your use case
2. **Add More ETL Jobs**: Implement additional transformations
3. **Create Dashboard**: Build visualization layer
4. **Set Up Monitoring**: Configure CloudWatch alarms
5. **Implement CI/CD**: Use GitHub Actions for automated deployment
6. **Scale Up**: Increase data volume and DPU allocation

## Cleanup

To avoid ongoing charges, destroy all resources:

```bash
cd terraform/environments/dev

# Delete S3 data first
aws s3 rm s3://$DATA_BUCKET --recursive
aws s3 rm s3://$SCRIPTS_BUCKET --recursive

# Destroy infrastructure
terraform destroy
```

Type `yes` to confirm.

---

**Estimated Setup Time**: 30-60 minutes  
**Difficulty Level**: Intermediate  
**Support**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed help
