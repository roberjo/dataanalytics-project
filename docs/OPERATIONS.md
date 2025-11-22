# Operations Runbook

## Overview

This runbook provides operational procedures, monitoring guidelines, and incident response protocols for the data analytics pipeline.

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Monitoring & Alerts](#monitoring--alerts)
3. [Incident Response](#incident-response)
4. [Maintenance Procedures](#maintenance-procedures)
5. [Performance Tuning](#performance-tuning)
6. [Disaster Recovery](#disaster-recovery)

---

## Daily Operations

### Morning Checks (9:00 AM)

#### 1. Pipeline Health Check

```bash
# Check Step Functions executions (last 24 hours)
aws stepfunctions list-executions \
  --state-machine-arn ${STATE_MACHINE_ARN} \
  --max-results 50 \
  --query 'executions[?startDate>=`'$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S)'`].[name,status,startDate]' \
  --output table

# Expected: All executions in SUCCEEDED status
```

#### 2. Data Freshness Check

```bash
# Check latest data in curated zone
aws s3 ls s3://${DATA_BUCKET}/curated/transactions/ --recursive | tail -10

# Run Athena query for data freshness
aws athena start-query-execution \
  --query-string "SELECT MAX(transaction_date) as latest_date FROM curated.transactions" \
  --work-group ${WORKGROUP} \
  --result-configuration "OutputLocation=s3://${DATA_BUCKET}/athena-results/"

# Expected: Data from yesterday or today
```

#### 3. Error Log Review

```bash
# Check Lambda errors (last 24 hours)
aws logs filter-log-events \
  --log-group-name /aws/lambda/data-pipeline-${ENVIRONMENT}-validator \
  --start-time $(date -u -d '24 hours ago' +%s)000 \
  --filter-pattern "ERROR"

# Check Glue job errors
aws logs filter-log-events \
  --log-group-name /aws-glue/jobs/error \
  --start-time $(date -u -d '24 hours ago' +%s)000 \
  --filter-pattern "ERROR"
```

#### 4. Cost Check

```bash
# Get yesterday's costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '1 day ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity DAILY \
  --metrics UnblendedCost \
  --filter file://cost-filter.json

# Expected: Within budget ($20/day for dev, $100/day for prod)
```

### Weekly Checks (Monday 9:00 AM)

#### 1. Data Quality Report

```bash
# Run comprehensive data quality checks
python scripts/data-quality/generate_quality_report.py \
  --database analytics_${ENVIRONMENT} \
  --output reports/quality_$(date +%Y%m%d).html

# Review report for:
# - Row count trends
# - Null percentage changes
# - Duplicate records
# - Data freshness
```

#### 2. Performance Review

```bash
# Glue job duration trends
aws glue get-job-runs \
  --job-name transaction-etl-${ENVIRONMENT} \
  --max-results 50 \
  --query 'JobRuns[].[Id,ExecutionTime,JobRunState]' \
  --output table

# Lambda function performance
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=data-pipeline-${ENVIRONMENT}-validator \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average,Maximum
```

#### 3. Storage Review

```bash
# Check S3 storage usage
aws s3 ls s3://${DATA_BUCKET}/ --recursive --summarize | tail -2

# Check storage by zone
aws s3 ls s3://${DATA_BUCKET}/raw/ --recursive --summarize | tail -2
aws s3 ls s3://${DATA_BUCKET}/processed/ --recursive --summarize | tail -2
aws s3 ls s3://${DATA_BUCKET}/curated/ --recursive --summarize | tail -2

# Expected: Growth within projections
```

### Monthly Checks (First Monday 9:00 AM)

#### 1. Security Audit

```bash
# Review IAM policies
aws iam list-attached-role-policies --role-name data-pipeline-glue-role-${ENVIRONMENT}

# Check S3 bucket policies
aws s3api get-bucket-policy --bucket ${DATA_BUCKET}

# Review CloudTrail logs for unauthorized access
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceType,AttributeValue=AWS::S3::Bucket \
  --start-time $(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%S) \
  --max-results 50
```

#### 2. Cost Optimization Review

```bash
# Monthly cost breakdown
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '1 month ago' +%Y-%m-01),End=$(date -u +%Y-%m-01) \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Identify optimization opportunities:
# - Unused resources
# - Over-provisioned services
# - Lifecycle policy effectiveness
```

---

## Monitoring & Alerts

### CloudWatch Dashboards

#### Main Pipeline Dashboard

**URL**: `https://console.aws.amazon.com/cloudwatch/home?region=${AWS_REGION}#dashboards:name=data-pipeline-${ENVIRONMENT}`

**Widgets**:
1. Step Functions execution status (last 24h)
2. Lambda invocation count and errors
3. Glue job success/failure rate
4. Athena query count and data scanned
5. S3 storage usage by zone
6. Cost trends

#### Data Quality Dashboard

**Metrics**:
- Row count by table
- Null percentage trends
- Duplicate record count
- Data freshness (hours since last update)
- Schema validation failures

### Alert Configuration

#### Critical Alerts (PagerDuty)

1. **Pipeline Failure**
   - Condition: Step Functions execution fails
   - Action: Page on-call engineer
   - Response time: 15 minutes

2. **Data Freshness**
   - Condition: No new data for 6 hours
   - Action: Page on-call engineer
   - Response time: 30 minutes

3. **High Error Rate**
   - Condition: >10% Lambda errors in 5 minutes
   - Action: Page on-call engineer
   - Response time: 15 minutes

#### Warning Alerts (Email/Slack)

1. **Slow Processing**
   - Condition: Glue job duration >2x average
   - Action: Email team
   - Response time: 2 hours

2. **High Costs**
   - Condition: Daily cost >20% over budget
   - Action: Email team lead
   - Response time: 4 hours

3. **Data Quality Issues**
   - Condition: Quality check failure
   - Action: Slack notification
   - Response time: 4 hours

### Metrics to Monitor

| Metric | Normal Range | Warning Threshold | Critical Threshold |
|--------|--------------|-------------------|-------------------|
| Pipeline success rate | >99% | <95% | <90% |
| Data freshness | <2 hours | 2-6 hours | >6 hours |
| Lambda error rate | <1% | 1-5% | >5% |
| Glue job duration | <30 min | 30-60 min | >60 min |
| Athena query time | <10 sec | 10-30 sec | >30 sec |
| Daily cost (dev) | $15-20 | $20-25 | >$25 |
| Daily cost (prod) | $80-100 | $100-120 | >$120 |

---

## Incident Response

### Severity Levels

**SEV-1 (Critical)**
- Pipeline completely down
- Data loss or corruption
- Security breach
- Response time: 15 minutes
- Escalation: Immediate

**SEV-2 (High)**
- Partial pipeline failure
- Significant performance degradation
- Data quality issues affecting business
- Response time: 1 hour
- Escalation: 2 hours

**SEV-3 (Medium)**
- Minor performance issues
- Non-critical data quality issues
- Single component failure with redundancy
- Response time: 4 hours
- Escalation: 8 hours

**SEV-4 (Low)**
- Cosmetic issues
- Documentation updates
- Feature requests
- Response time: Next business day
- Escalation: N/A

### Incident Response Procedures

#### Step 1: Identify and Classify

```bash
# Check overall pipeline status
./scripts/ops/check_pipeline_health.sh

# Classify severity based on impact:
# - How many users affected?
# - Is data being lost?
# - Can we recover automatically?
# - What's the business impact?
```

#### Step 2: Contain

```bash
# For data corruption: Stop ingestion
aws events disable-rule --name data-pipeline-schedule-${ENVIRONMENT}

# For runaway costs: Disable expensive resources
aws glue stop-job-run --job-name transaction-etl-${ENVIRONMENT} --run-id ${RUN_ID}

# For security issues: Revoke access
aws iam detach-role-policy --role-name data-pipeline-role --policy-arn ${POLICY_ARN}
```

#### Step 3: Investigate

```bash
# Collect logs
aws logs tail /aws/lambda/data-pipeline-${ENVIRONMENT}-validator \
  --since 1h --format short > incident_lambda_logs.txt

aws logs tail /aws-glue/jobs/output \
  --since 1h --format short > incident_glue_logs.txt

# Check execution history
aws stepfunctions get-execution-history \
  --execution-arn ${EXECUTION_ARN} \
  --max-results 100 > incident_execution_history.json

# Review CloudWatch metrics
aws cloudwatch get-metric-data \
  --metric-data-queries file://incident_metrics.json \
  --start-time $(date -u -d '2 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S)
```

#### Step 4: Resolve

Follow specific runbooks:
- [Pipeline Failure Runbook](#pipeline-failure-runbook)
- [Data Quality Issue Runbook](#data-quality-issue-runbook)
- [Performance Degradation Runbook](#performance-degradation-runbook)
- [Cost Spike Runbook](#cost-spike-runbook)

#### Step 5: Communicate

```bash
# Update status page
curl -X POST https://status-api.example.com/incidents \
  -H "Authorization: Bearer ${STATUS_API_KEY}" \
  -d '{"title":"Data Pipeline Issue","status":"investigating"}'

# Notify stakeholders
python scripts/ops/send_incident_notification.py \
  --severity SEV-2 \
  --title "Pipeline Delay" \
  --description "Processing delayed by 2 hours" \
  --eta "2 hours"
```

#### Step 6: Document

Create incident report:
```markdown
# Incident Report: [YYYY-MM-DD-###]

## Summary
- **Date**: 2025-01-15
- **Duration**: 2 hours
- **Severity**: SEV-2
- **Impact**: Data processing delayed

## Timeline
- 10:00 AM: Alert triggered
- 10:15 AM: Investigation started
- 10:45 AM: Root cause identified
- 11:30 AM: Fix deployed
- 12:00 PM: Verified resolved

## Root Cause
Glue job failed due to schema mismatch in source data.

## Resolution
Updated schema validation logic to handle new field.

## Action Items
1. Add schema validation tests
2. Improve error messages
3. Update monitoring alerts
```

### Specific Runbooks

#### Pipeline Failure Runbook

**Symptoms**: Step Functions execution fails

**Investigation**:
```bash
# 1. Check execution status
aws stepfunctions describe-execution --execution-arn ${EXECUTION_ARN}

# 2. Identify failed step
aws stepfunctions get-execution-history --execution-arn ${EXECUTION_ARN} \
  | jq '.events[] | select(.type | contains("Failed"))'

# 3. Check component logs
# (Lambda, Glue, or other service based on failed step)
```

**Resolution**:
```bash
# 1. Fix underlying issue (see specific error)

# 2. Reprocess failed data
aws stepfunctions start-execution \
  --state-machine-arn ${STATE_MACHINE_ARN} \
  --input "{\"bucket\":\"${DATA_BUCKET}\",\"key\":\"${FAILED_KEY}\"}"

# 3. Verify success
aws stepfunctions describe-execution --execution-arn ${NEW_EXECUTION_ARN}
```

#### Data Quality Issue Runbook

**Symptoms**: Quality check failures, anomalous data

**Investigation**:
```bash
# 1. Run quality report
python scripts/data-quality/generate_quality_report.py

# 2. Compare with historical data
aws athena start-query-execution \
  --query-string "
    SELECT 
      date,
      COUNT(*) as row_count,
      COUNT(DISTINCT customer_id) as unique_customers
    FROM curated.transactions
    WHERE date >= DATE_ADD('day', -7, CURRENT_DATE)
    GROUP BY date
    ORDER BY date
  "

# 3. Check source data
aws s3 ls s3://${DATA_BUCKET}/raw/transactions/date=$(date +%Y-%m-%d)/
```

**Resolution**:
```bash
# 1. If source data issue: Contact data provider

# 2. If transformation issue: Fix ETL logic and reprocess
aws glue start-job-run \
  --job-name transaction-etl-${ENVIRONMENT} \
  --arguments '--reprocess_date='$(date +%Y-%m-%d)

# 3. Verify data quality
python scripts/data-quality/validate_schemas.py --table transactions
```

#### Performance Degradation Runbook

**Symptoms**: Slow query times, long job durations

**Investigation**:
```bash
# 1. Check Glue job metrics
aws glue get-job-runs --job-name transaction-etl-${ENVIRONMENT} \
  --max-results 10 \
  --query 'JobRuns[].[Id,ExecutionTime,DPUSeconds]'

# 2. Check Athena query performance
aws athena get-query-execution --query-execution-id ${QUERY_ID} \
  --query 'QueryExecution.[Statistics.DataScannedInBytes,Statistics.EngineExecutionTimeInMillis]'

# 3. Check data volume
aws s3 ls s3://${DATA_BUCKET}/raw/transactions/ --recursive --summarize
```

**Resolution**:
```bash
# 1. Optimize Glue job (increase DPUs)
aws glue update-job \
  --job-name transaction-etl-${ENVIRONMENT} \
  --job-update MaxCapacity=10.0

# 2. Optimize Athena queries (add partitions, use columnar format)

# 3. Implement data archival
python scripts/ops/archive_old_data.py --older-than 90
```

#### Cost Spike Runbook

**Symptoms**: Unexpected high AWS costs

**Investigation**:
```bash
# 1. Identify cost drivers
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '7 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# 2. Check for runaway resources
aws glue list-jobs --query 'Jobs[?contains(Name, `data-pipeline`)].Name'
aws lambda list-functions --query 'Functions[?contains(FunctionName, `data-pipeline`)].FunctionName'

# 3. Review Athena data scanned
aws athena list-query-executions --max-results 50
```

**Resolution**:
```bash
# 1. Stop unnecessary resources
aws glue stop-job-run --job-name ${JOB_NAME} --run-id ${RUN_ID}

# 2. Implement cost controls
# - Add query result caching
# - Optimize partitioning
# - Review lifecycle policies

# 3. Set up budget alerts
aws budgets create-budget --account-id ${AWS_ACCOUNT_ID} \
  --budget file://budget-config.json
```

---

## Maintenance Procedures

### Scheduled Maintenance Windows

**Weekly**: Sunday 2:00 AM - 4:00 AM UTC
**Monthly**: First Sunday 2:00 AM - 6:00 AM UTC

### Pre-Maintenance Checklist

- [ ] Notify stakeholders 48 hours in advance
- [ ] Backup current state
- [ ] Prepare rollback plan
- [ ] Test changes in staging
- [ ] Schedule maintenance window
- [ ] Disable monitoring alerts

### Maintenance Procedures

#### Update Lambda Functions

```bash
# 1. Create deployment package
cd src/ingestion
zip -r ../../dist/lambda/file_validator_v2.zip file_validator.py

# 2. Test in staging
aws lambda update-function-code \
  --function-name data-pipeline-staging-validator \
  --zip-file fileb://dist/lambda/file_validator_v2.zip

# 3. Verify staging
aws lambda invoke \
  --function-name data-pipeline-staging-validator \
  --payload '{"test": true}' \
  response.json

# 4. Deploy to production
aws lambda update-function-code \
  --function-name data-pipeline-prod-validator \
  --zip-file fileb://dist/lambda/file_validator_v2.zip

# 5. Verify production
aws lambda invoke \
  --function-name data-pipeline-prod-validator \
  --payload '{"test": true}' \
  response.json
```

#### Update Glue Jobs

```bash
# 1. Upload new script
aws s3 cp src/transformation/glue-jobs/transaction_etl_v2.py \
  s3://${SCRIPTS_BUCKET}/glue-jobs/transaction_etl_v2.py

# 2. Update job definition
aws glue update-job \
  --job-name transaction-etl-${ENVIRONMENT} \
  --job-update ScriptLocation=s3://${SCRIPTS_BUCKET}/glue-jobs/transaction_etl_v2.py

# 3. Test with small dataset
aws glue start-job-run \
  --job-name transaction-etl-${ENVIRONMENT} \
  --arguments '--test_mode=true'

# 4. Monitor execution
aws glue get-job-run \
  --job-name transaction-etl-${ENVIRONMENT} \
  --run-id ${RUN_ID}
```

#### Rotate Secrets

```bash
# 1. Generate new credentials
NEW_KEY=$(aws iam create-access-key --user-name data-pipeline-user)

# 2. Update Secrets Manager
aws secretsmanager update-secret \
  --secret-id data-pipeline-credentials \
  --secret-string "{\"access_key\":\"${NEW_ACCESS_KEY}\",\"secret_key\":\"${NEW_SECRET_KEY}\"}"

# 3. Update Lambda environment variables
aws lambda update-function-configuration \
  --function-name data-pipeline-${ENVIRONMENT}-validator \
  --environment Variables={SECRET_ARN=arn:aws:secretsmanager:...}

# 4. Delete old credentials
aws iam delete-access-key \
  --user-name data-pipeline-user \
  --access-key-id ${OLD_ACCESS_KEY}
```

### Post-Maintenance Checklist

- [ ] Verify all components operational
- [ ] Run end-to-end test
- [ ] Check monitoring dashboards
- [ ] Re-enable alerts
- [ ] Document changes
- [ ] Notify stakeholders of completion

---

## Performance Tuning

### Glue Job Optimization

```python
# Increase parallelism
spark.conf.set("spark.default.parallelism", "200")
spark.conf.set("spark.sql.shuffle.partitions", "200")

# Enable adaptive query execution
spark.conf.set("spark.sql.adaptive.enabled", "true")

# Optimize file size
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")  # 128 MB
```

### Athena Query Optimization

```sql
-- Use partitioning
SELECT * FROM transactions
WHERE year = 2025 AND month = 1 AND day = 15

-- Use columnar format (Parquet)
-- Compress data (Snappy)

-- Limit columns
SELECT transaction_id, total_amount
FROM transactions
-- Instead of SELECT *

-- Use approximate functions for large datasets
SELECT APPROX_DISTINCT(customer_id) FROM transactions
```

### Lambda Optimization

```python
# Increase memory (improves CPU)
aws lambda update-function-configuration \
  --function-name data-pipeline-validator \
  --memory-size 1024

# Use provisioned concurrency
aws lambda put-provisioned-concurrency-config \
  --function-name data-pipeline-validator \
  --provisioned-concurrent-executions 5
```

---

## Disaster Recovery

### Backup Strategy

**What to Backup**:
- Terraform state (S3 versioning enabled)
- Glue Data Catalog (AWS Backup)
- Lambda function code (S3 versioning)
- Configuration files (Git)

**Backup Schedule**:
- Continuous: S3 versioning
- Daily: Glue catalog snapshots
- Weekly: Full configuration backup

### Recovery Procedures

#### Scenario 1: Accidental Data Deletion

```bash
# 1. Identify deleted data
aws s3api list-object-versions \
  --bucket ${DATA_BUCKET} \
  --prefix curated/transactions/

# 2. Restore from version
aws s3api copy-object \
  --copy-source ${DATA_BUCKET}/curated/transactions/data.parquet?versionId=${VERSION_ID} \
  --bucket ${DATA_BUCKET} \
  --key curated/transactions/data.parquet

# 3. Verify restoration
aws s3 ls s3://${DATA_BUCKET}/curated/transactions/
```

#### Scenario 2: Infrastructure Failure

```bash
# 1. Switch to backup region
export AWS_REGION=us-west-2

# 2. Deploy infrastructure
cd terraform/environments/${ENVIRONMENT}
terraform init
terraform apply

# 3. Restore data from backup
aws s3 sync s3://${BACKUP_BUCKET}/ s3://${DATA_BUCKET}/

# 4. Verify pipeline
./scripts/ops/verify_pipeline.sh
```

#### Scenario 3: Complete Region Outage

```bash
# 1. Activate DR plan
./scripts/dr/activate_dr.sh

# 2. Update DNS/endpoints to DR region

# 3. Notify stakeholders

# 4. Monitor DR environment

# 5. Plan failback when primary region recovers
```

### RTO/RPO Targets

| Component | RTO | RPO |
|-----------|-----|-----|
| Pipeline infrastructure | 4 hours | 24 hours |
| Data processing | 2 hours | 1 hour |
| Analytics queries | 1 hour | 24 hours |
| Monitoring/alerts | 30 minutes | N/A |

---

**Last Updated**: 2025-11-22  
**Version**: 1.0  
**On-Call**: ops-team@example.com  
**Escalation**: engineering-lead@example.com
