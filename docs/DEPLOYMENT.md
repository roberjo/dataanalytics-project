# Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the e-commerce data analytics pipeline to AWS environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Infrastructure Deployment](#infrastructure-deployment)
4. [Application Deployment](#application-deployment)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **AWS CLI** v2.x or higher
- **Terraform** v1.5.0 or higher
- **Python** 3.11 or higher
- **Git** 2.x or higher
- **Make** (optional, for convenience commands)

### AWS Requirements

- AWS account with appropriate permissions
- IAM user or role with the following policies:
  - `AmazonS3FullAccess`
  - `AWSGlueConsoleFullAccess`
  - `AmazonAthenaFullAccess`
  - `AWSLambda_FullAccess`
  - `AWSStepFunctionsFullAccess`
  - `CloudWatchFullAccess`
  - `IAMFullAccess`

### Access Requirements

- AWS credentials configured (`aws configure`)
- GitHub repository access (for CI/CD)
- S3 bucket for Terraform state (created separately)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/dataanalytics-project.git
cd dataanalytics-project
```

### 2. Install Dependencies

```bash
# Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installations
python --version
terraform --version
aws --version
```

### 3. Configure AWS Credentials

```bash
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)

# Verify
aws sts get-caller-identity
```

### 4. Set Environment Variables

Create `.env` file (do not commit):

```bash
# Environment
export ENVIRONMENT=dev  # or staging, prod
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Project
export PROJECT_NAME=data-analytics-pipeline
export TERRAFORM_STATE_BUCKET=${PROJECT_NAME}-terraform-state-${AWS_ACCOUNT_ID}

# Notifications
export SNS_EMAIL=your-email@example.com
```

Load environment:
```bash
source .env
```

---

## Infrastructure Deployment

### Phase 1: Terraform State Backend

#### 1.1 Create S3 Bucket for State

```bash
# Create state bucket
aws s3 mb s3://${TERRAFORM_STATE_BUCKET} --region ${AWS_REGION}

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ${TERRAFORM_STATE_BUCKET} \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket ${TERRAFORM_STATE_BUCKET} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket ${TERRAFORM_STATE_BUCKET} \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

#### 1.2 Create DynamoDB Table for State Locking

```bash
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ${AWS_REGION}
```

### Phase 2: Core Infrastructure

#### 2.1 Configure Terraform Backend

Create `terraform/environments/${ENVIRONMENT}/backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "data-analytics-pipeline-terraform-state-123456789012"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

#### 2.2 Initialize Terraform

```bash
cd terraform/environments/${ENVIRONMENT}

# Initialize
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

#### 2.3 Plan Infrastructure

```bash
# Create execution plan
terraform plan -out=tfplan

# Review the plan
# - Check resource counts
# - Verify resource names
# - Review IAM policies
# - Check estimated costs
```

#### 2.4 Apply Infrastructure

```bash
# Apply the plan
terraform apply tfplan

# Confirm with 'yes'

# Expected resources:
# - S3 buckets (data lake, scripts, logs)
# - Glue database and crawlers
# - Glue ETL jobs
# - Lambda functions
# - Step Functions state machine
# - EventBridge rules
# - CloudWatch dashboards
# - SNS topics
# - IAM roles and policies
```

#### 2.5 Save Outputs

```bash
# Save outputs to file
terraform output > ../../../terraform-outputs.txt

# Display key outputs
terraform output data_lake_bucket_name
terraform output step_functions_arn
terraform output athena_workgroup_name
```

---

## Application Deployment

### Phase 3: Deploy Application Code

#### 3.1 Package Lambda Functions

```bash
cd ../../../

# Create deployment packages
mkdir -p dist/lambda

# File validator
cd src/ingestion
zip -r ../../dist/lambda/file_validator.zip file_validator.py
cd ../..

# Data quality check
cd src/transformation/lambda_functions
zip -r ../../../dist/lambda/data_quality_check.zip data_quality_check.py
cd ../../..
```

#### 3.2 Upload Glue Scripts

```bash
# Get scripts bucket from Terraform output
SCRIPTS_BUCKET=$(cd terraform/environments/${ENVIRONMENT} && terraform output -raw scripts_bucket_name)

# Upload Glue ETL scripts
aws s3 cp src/transformation/glue-jobs/transaction_etl.py \
  s3://${SCRIPTS_BUCKET}/glue-jobs/transaction_etl.py

# Verify upload
aws s3 ls s3://${SCRIPTS_BUCKET}/glue-jobs/
```

#### 3.3 Update Lambda Functions

```bash
# Get function names from Terraform output
FILE_VALIDATOR_FUNCTION=$(cd terraform/environments/${ENVIRONMENT} && terraform output -raw file_validator_function_name)
QUALITY_CHECK_FUNCTION=$(cd terraform/environments/${ENVIRONMENT} && terraform output -raw quality_check_function_name)

# Update file validator
aws lambda update-function-code \
  --function-name ${FILE_VALIDATOR_FUNCTION} \
  --zip-file fileb://dist/lambda/file_validator.zip

# Update data quality check
aws lambda update-function-code \
  --function-name ${QUALITY_CHECK_FUNCTION} \
  --zip-file fileb://dist/lambda/data_quality_check.zip
```

### Phase 4: Initialize Data Catalog

#### 4.1 Run Glue Crawlers

```bash
# Start crawlers to discover schema
aws glue start-crawler --name transactions-crawler-${ENVIRONMENT}
aws glue start-crawler --name products-crawler-${ENVIRONMENT}
aws glue start-crawler --name clickstream-crawler-${ENVIRONMENT}
aws glue start-crawler --name reviews-crawler-${ENVIRONMENT}

# Monitor crawler status
aws glue get-crawler --name transactions-crawler-${ENVIRONMENT} \
  --query 'Crawler.State' --output text
```

#### 4.2 Create Athena Named Queries

```bash
# Get workgroup name
WORKGROUP=$(cd terraform/environments/${ENVIRONMENT} && terraform output -raw athena_workgroup_name)

# Create named queries
aws athena create-named-query \
  --name "Top Products" \
  --database analytics_${ENVIRONMENT} \
  --query-string "$(cat src/analytics/athena_queries/top_products.sql)" \
  --work-group ${WORKGROUP}

aws athena create-named-query \
  --name "Customer LTV" \
  --database analytics_${ENVIRONMENT} \
  --query-string "$(cat src/analytics/athena_queries/customer_ltv.sql)" \
  --work-group ${WORKGROUP}

aws athena create-named-query \
  --name "Conversion Funnel" \
  --database analytics_${ENVIRONMENT} \
  --query-string "$(cat src/analytics/athena_queries/conversion_funnel.sql)" \
  --work-group ${WORKGROUP}
```

---

## Post-Deployment Verification

### 1. Infrastructure Verification

```bash
# Check S3 buckets
aws s3 ls | grep ${PROJECT_NAME}

# Check Glue database
aws glue get-database --name analytics_${ENVIRONMENT}

# Check Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `data-pipeline`)].FunctionName'

# Check Step Functions
aws stepfunctions list-state-machines --query 'stateMachines[?contains(name, `data-pipeline`)].name'
```

### 2. Functional Verification

#### 2.1 Upload Test Data

```bash
# Generate test data
python src/data-generators/generate_transactions.py --rows 1000 --output data/test_transactions.csv
python src/data-generators/generate_products.py --rows 100 --output data/test_products.json

# Get data lake bucket
DATA_BUCKET=$(cd terraform/environments/${ENVIRONMENT} && terraform output -raw data_lake_bucket_name)

# Upload to raw zone
aws s3 cp data/test_transactions.csv \
  s3://${DATA_BUCKET}/raw/transactions/date=$(date +%Y-%m-%d)/transactions.csv

aws s3 cp data/test_products.json \
  s3://${DATA_BUCKET}/raw/products/date=$(date +%Y-%m-%d)/products.json
```

#### 2.2 Trigger Pipeline

```bash
# Get Step Functions ARN
STATE_MACHINE_ARN=$(cd terraform/environments/${ENVIRONMENT} && terraform output -raw step_functions_arn)

# Start execution
EXECUTION_ARN=$(aws stepfunctions start-execution \
  --state-machine-arn ${STATE_MACHINE_ARN} \
  --input "{\"bucket\": \"${DATA_BUCKET}\", \"key\": \"raw/transactions/date=$(date +%Y-%m-%d)/transactions.csv\"}" \
  --query 'executionArn' \
  --output text)

echo "Execution started: ${EXECUTION_ARN}"
```

#### 2.3 Monitor Execution

```bash
# Check execution status
aws stepfunctions describe-execution \
  --execution-arn ${EXECUTION_ARN} \
  --query 'status' --output text

# View execution history
aws stepfunctions get-execution-history \
  --execution-arn ${EXECUTION_ARN} \
  --max-results 10
```

#### 2.4 Verify Data Processing

```bash
# Check processed data
aws s3 ls s3://${DATA_BUCKET}/processed/transactions/ --recursive

# Check curated data
aws s3 ls s3://${DATA_BUCKET}/curated/transactions/ --recursive

# Query data with Athena
QUERY_ID=$(aws athena start-query-execution \
  --query-string "SELECT COUNT(*) as count FROM curated.transactions" \
  --work-group ${WORKGROUP} \
  --result-configuration "OutputLocation=s3://${DATA_BUCKET}/athena-results/" \
  --query 'QueryExecutionId' --output text)

# Wait and get results
sleep 5
aws athena get-query-results --query-execution-id ${QUERY_ID}
```

### 3. Monitoring Verification

```bash
# Check CloudWatch dashboards
aws cloudwatch list-dashboards --query 'DashboardEntries[?contains(DashboardName, `data-pipeline`)].DashboardName'

# Check CloudWatch alarms
aws cloudwatch describe-alarms --query 'MetricAlarms[?contains(AlarmName, `data-pipeline`)].AlarmName'

# Check SNS topics
aws sns list-topics --query 'Topics[?contains(TopicArn, `data-pipeline`)].TopicArn'
```

---

## Rollback Procedures

### Emergency Rollback

If deployment fails or causes issues:

#### 1. Rollback Application Code

```bash
# Revert Lambda functions to previous version
aws lambda update-function-code \
  --function-name ${FILE_VALIDATOR_FUNCTION} \
  --s3-bucket ${SCRIPTS_BUCKET} \
  --s3-key lambda/file_validator_previous.zip

# Revert Glue scripts
aws s3 cp s3://${SCRIPTS_BUCKET}/glue-jobs/transaction_etl_previous.py \
  s3://${SCRIPTS_BUCKET}/glue-jobs/transaction_etl.py
```

#### 2. Rollback Infrastructure

```bash
cd terraform/environments/${ENVIRONMENT}

# Get previous state version
terraform state pull > current_state.json

# Rollback to previous Terraform state
# (if state versioning is enabled in S3)
aws s3api list-object-versions \
  --bucket ${TERRAFORM_STATE_BUCKET} \
  --prefix ${ENVIRONMENT}/terraform.tfstate

# Restore previous version
aws s3api get-object \
  --bucket ${TERRAFORM_STATE_BUCKET} \
  --key ${ENVIRONMENT}/terraform.tfstate \
  --version-id <PREVIOUS_VERSION_ID> \
  terraform.tfstate.backup

# Apply previous configuration
terraform apply -auto-approve
```

### Graceful Rollback

For planned rollback:

```bash
# 1. Stop new data ingestion
aws events disable-rule --name data-pipeline-schedule-${ENVIRONMENT}

# 2. Wait for in-flight executions to complete
aws stepfunctions list-executions \
  --state-machine-arn ${STATE_MACHINE_ARN} \
  --status-filter RUNNING

# 3. Revert changes
# (follow emergency rollback steps)

# 4. Re-enable ingestion
aws events enable-rule --name data-pipeline-schedule-${ENVIRONMENT}
```

---

## Troubleshooting

### Common Issues

#### Issue: Terraform State Lock

**Symptom**: "Error locking state: ConditionalCheckFailedException"

**Solution**:
```bash
# Check lock
aws dynamodb get-item \
  --table-name terraform-state-lock \
  --key '{"LockID": {"S": "data-analytics-pipeline-terraform-state/dev/terraform.tfstate"}}'

# Force unlock (use with caution)
terraform force-unlock <LOCK_ID>
```

#### Issue: Lambda Function Timeout

**Symptom**: Lambda function times out during execution

**Solution**:
```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name ${FILE_VALIDATOR_FUNCTION} \
  --timeout 300

# Increase memory
aws lambda update-function-configuration \
  --function-name ${FILE_VALIDATOR_FUNCTION} \
  --memory-size 512
```

#### Issue: Glue Job Fails

**Symptom**: Glue job fails with "Script not found"

**Solution**:
```bash
# Verify script exists
aws s3 ls s3://${SCRIPTS_BUCKET}/glue-jobs/

# Re-upload script
aws s3 cp src/transformation/glue-jobs/transaction_etl.py \
  s3://${SCRIPTS_BUCKET}/glue-jobs/transaction_etl.py

# Check job configuration
aws glue get-job --job-name transaction-etl-${ENVIRONMENT}
```

#### Issue: Athena Query Fails

**Symptom**: "Table not found" error

**Solution**:
```bash
# Run crawler to update catalog
aws glue start-crawler --name transactions-crawler-${ENVIRONMENT}

# Verify table exists
aws glue get-table \
  --database-name analytics_${ENVIRONMENT} \
  --name transactions
```

### Logs and Debugging

```bash
# Lambda logs
aws logs tail /aws/lambda/data-pipeline-${ENVIRONMENT}-validator --follow

# Glue job logs
aws logs tail /aws-glue/jobs/output --follow

# Step Functions execution logs
aws stepfunctions get-execution-history \
  --execution-arn ${EXECUTION_ARN} \
  --max-results 100
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] AWS credentials configured
- [ ] Terraform state backend created
- [ ] Environment variables set
- [ ] Code reviewed and tested
- [ ] Dependencies installed
- [ ] Terraform plan reviewed

### Deployment

- [ ] Terraform apply successful
- [ ] Lambda functions deployed
- [ ] Glue scripts uploaded
- [ ] Crawlers run successfully
- [ ] Named queries created

### Post-Deployment

- [ ] Test data uploaded
- [ ] Pipeline execution successful
- [ ] Data processed correctly
- [ ] Athena queries working
- [ ] Monitoring configured
- [ ] Alerts tested
- [ ] Documentation updated

### Rollback Plan

- [ ] Previous versions backed up
- [ ] Rollback procedure documented
- [ ] Team notified
- [ ] Monitoring in place

---

## Environment-Specific Notes

### Development (dev)

- Lower resource limits
- Shorter data retention
- Test data only
- Cost-optimized settings

### Staging (staging)

- Production-like configuration
- Full integration testing
- Real data samples
- Performance testing

### Production (prod)

- High availability
- Full monitoring
- Automated backups
- Strict access controls
- Change management required

---

**Last Updated**: 2025-11-22  
**Version**: 1.0  
**Maintained By**: DevOps Team
