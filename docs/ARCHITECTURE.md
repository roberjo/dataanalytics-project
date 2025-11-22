# Architecture Guide

## Overview

This document provides a detailed overview of the e-commerce data analytics pipeline architecture, design decisions, and implementation details.

## Table of Contents

1. [Architecture Principles](#architecture-principles)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Design Decisions](#design-decisions)
5. [Scalability & Performance](#scalability--performance)
6. [Security](#security)
7. [Cost Optimization](#cost-optimization)

## Architecture Principles

The pipeline is built on the following principles:

### 1. Serverless-First
- **No server management**: All compute is serverless (Lambda, Glue, Athena)
- **Auto-scaling**: Automatically scales with data volume
- **Pay-per-use**: Only pay for actual usage

### 2. Data Lake Architecture
- **Three-zone design**: Raw → Processed → Curated
- **Schema-on-read**: Flexible schema evolution
- **Partitioning**: Date-based partitioning for query optimization

### 3. Event-Driven
- **S3 events**: Trigger processing on file uploads
- **EventBridge**: Schedule daily batch processing
- **Step Functions**: Orchestrate complex workflows

### 4. Infrastructure as Code
- **Terraform**: All infrastructure defined as code
- **Modular design**: Reusable Terraform modules
- **Environment parity**: Dev, staging, prod environments

### 5. Data Quality First
- **Validation**: File validation before processing
- **Quality checks**: Automated data quality checks
- **Monitoring**: Continuous monitoring and alerting

## System Components

### Data Ingestion Layer

#### S3 Data Lake
```
s3://data-lake-{env}/
├── raw/                    # Raw data as received
│   ├── transactions/
│   │   └── date=YYYY-MM-DD/
│   ├── products/
│   │   └── date=YYYY-MM-DD/
│   ├── clickstream/
│   │   └── date=YYYY-MM-DD/
│   └── reviews/
│       └── date=YYYY-MM-DD/
├── processed/              # Cleaned and transformed
│   ├── transactions/
│   ├── products/
│   ├── clickstream/
│   └── reviews/
├── curated/                # Analytics-ready
│   ├── transactions/
│   ├── products/
│   ├── clickstream/
│   └── reviews/
└── athena-results/         # Query results
```

**Design Decisions:**
- **Partitioning by date**: Enables partition pruning in Athena
- **Separate zones**: Clear separation of concerns
- **Parquet format**: Columnar format for analytical queries

#### File Validator Lambda
- **Purpose**: Validate incoming files before processing
- **Checks**:
  - File format (CSV vs JSON)
  - Schema compliance
  - File size
  - Deduplication (MD5 hash)
- **Output**: Validation result with metadata

### ETL Processing Layer

#### AWS Glue

**Glue Crawlers:**
- Automatically discover schema
- Update Glue Data Catalog
- Run on schedule or on-demand

**Glue ETL Jobs:**

1. **Transaction ETL** (`transaction_etl.py`)
   - Read CSV from raw zone
   - Clean and validate data
   - Calculate derived metrics
   - Write Parquet to processed zone
   - Partition by year/month/day

2. **Product Enrichment** (`product_enrichment.py`)
   - Read JSON from raw zone
   - Join with category data
   - Calculate inventory metrics
   - Write to processed zone

3. **Clickstream Aggregation** (`clickstream_aggregation.py`)
   - Sessionize user activity
   - Calculate conversion metrics
   - Aggregate by time periods

4. **Master Data Merge** (`master_data_merge.py`)
   - Join all data sources
   - Create analytics-ready tables
   - Write to curated zone

**Glue Configuration:**
- **DPU**: 2-10 DPUs based on data volume
- **Timeout**: 2880 minutes (48 hours)
- **Retries**: 3 attempts with exponential backoff
- **Bookmarks**: Track processed data

### Data Catalog Layer

#### AWS Glue Data Catalog
- **Databases**:
  - `raw_{env}`: Raw data tables
  - `processed_{env}`: Processed data tables
  - `curated_{env}`: Analytics-ready tables

- **Tables**: Auto-discovered by crawlers
- **Partitions**: Managed automatically
- **Schema Evolution**: Handled gracefully

### Query Layer

#### Amazon Athena
- **Workgroup**: Separate workgroup per environment
- **Cost Controls**: Query result limits, data scanned limits
- **Named Queries**: Pre-defined analytical queries
- **Result Caching**: 24-hour cache for identical queries

**Query Optimization:**
- Partition pruning
- Columnar format (Parquet)
- Compression (Snappy)
- Predicate pushdown

### Orchestration Layer

#### AWS Step Functions

**Pipeline Workflow:**
```
1. Validate Files (Lambda)
   ↓
2. Run Crawlers (Parallel)
   - Transactions Crawler
   - Products Crawler
   - Clickstream Crawler
   ↓
3. ETL Jobs (Parallel)
   - Transaction ETL
   - Product Enrichment
   - Clickstream Aggregation
   ↓
4. Data Quality Checks (Lambda)
   ↓
5. Merge Master Data (Glue)
   ↓
6. Refresh Athena Tables (Lambda)
   ↓
7. Send Notification (SNS)
```

**Error Handling:**
- Retry logic with exponential backoff
- Catch blocks for graceful failure
- SNS notifications on failure

#### Amazon EventBridge
- **S3 Events**: Trigger on file upload
- **Scheduled Events**: Daily batch processing
- **Custom Events**: Manual triggers

### Monitoring & Alerting

#### Amazon CloudWatch
- **Metrics**:
  - Lambda invocations, duration, errors
  - Glue job success/failure, duration
  - Athena queries, data scanned
  - Step Functions executions

- **Logs**:
  - Lambda function logs
  - Glue job logs
  - Step Functions execution history

- **Dashboards**:
  - Pipeline health dashboard
  - Cost tracking dashboard
  - Data quality dashboard

#### Amazon SNS
- **Topics**:
  - `pipeline-notifications`: Success/failure alerts
  - `data-quality-alerts`: Quality check failures
  - `cost-alerts`: Budget threshold alerts

## Data Flow

### Batch Processing Flow

```
1. Data Upload
   └─> S3 raw zone (CSV/JSON files)
   
2. Event Trigger
   └─> EventBridge detects S3 upload
   └─> Triggers Step Functions execution
   
3. Validation
   └─> Lambda validates file format, schema, size
   └─> Checks for duplicates (MD5 hash)
   └─> Stores metadata in DynamoDB
   
4. Schema Discovery
   └─> Glue Crawlers scan raw data
   └─> Update Glue Data Catalog
   └─> Create/update table definitions
   
5. ETL Processing
   └─> Glue jobs read from raw zone
   └─> Clean, transform, enrich data
   └─> Write Parquet to processed zone
   └─> Partition by date
   
6. Data Quality
   └─> Lambda runs quality checks
   └─> Validates row counts, nulls, duplicates
   └─> Checks data freshness
   └─> Sends alerts if failures
   
7. Curated Layer
   └─> Glue job merges all sources
   └─> Creates analytics-ready tables
   └─> Writes to curated zone
   
8. Query Layer
   └─> Athena queries curated tables
   └─> Results cached for 24 hours
   └─> Dashboard displays metrics
```

### Real-Time Processing Flow (Future Enhancement)

```
1. Streaming Data
   └─> Kinesis Data Streams
   
2. Stream Processing
   └─> Kinesis Data Analytics
   └─> Real-time transformations
   
3. Data Storage
   └─> Kinesis Firehose → S3
   └─> DynamoDB for low-latency access
   
4. Visualization
   └─> QuickSight for real-time dashboards
```

## Design Decisions

### Why Serverless?

**Pros:**
- No infrastructure management
- Auto-scaling
- Pay-per-use pricing
- High availability built-in

**Cons:**
- Cold start latency (mitigated with provisioned concurrency)
- Execution time limits (handled with Glue for long-running jobs)
- Vendor lock-in (mitigated with abstraction layers)

### Why Parquet?

**Advantages:**
- Columnar storage (faster analytical queries)
- Compression (5-10x smaller than CSV)
- Schema evolution support
- Native support in Athena, Glue, Spark

**Comparison:**
| Format | Size | Query Speed | Compression |
|--------|------|-------------|-------------|
| CSV    | 1x   | 1x          | None        |
| JSON   | 1.2x | 0.8x        | Gzip        |
| Parquet| 0.1x | 10x         | Snappy      |

### Why Three Zones?

**Raw Zone:**
- Immutable source of truth
- Preserves original data
- Enables reprocessing

**Processed Zone:**
- Cleaned and validated
- Standardized format
- Ready for analysis

**Curated Zone:**
- Business-ready datasets
- Joined and enriched
- Optimized for queries

### Why Step Functions?

**Alternatives Considered:**
- **Airflow**: More complex, requires infrastructure
- **AWS Data Pipeline**: Less flexible, legacy service
- **Glue Workflows**: Limited orchestration capabilities

**Step Functions Advantages:**
- Visual workflow designer
- Built-in error handling
- Native AWS service integration
- Serverless execution

## Scalability & Performance

### Horizontal Scaling

**Lambda:**
- Concurrent executions: 1000 (default)
- Can request increase to 10,000+

**Glue:**
- DPU auto-scaling: 2-100 DPUs
- Parallel job execution

**Athena:**
- Unlimited concurrent queries
- Automatic query parallelization

### Performance Optimization

**Partitioning:**
```sql
-- Without partitioning
SELECT * FROM transactions WHERE date = '2025-01-15'
-- Scans entire table (100 GB)

-- With partitioning
SELECT * FROM transactions WHERE year=2025 AND month=1 AND day=15
-- Scans only partition (100 MB)
```

**Compression:**
- Snappy: Fast compression/decompression
- 5-10x size reduction
- Lower S3 storage costs
- Faster data transfer

**Columnar Format:**
- Only read required columns
- 10-100x faster for analytical queries

### Throughput

**Expected Performance:**
| Data Volume | Processing Time | Cost |
|-------------|----------------|------|
| 1 GB        | 5 minutes      | $0.10 |
| 10 GB       | 15 minutes     | $0.50 |
| 100 GB      | 45 minutes     | $2.00 |
| 1 TB        | 3 hours        | $15.00 |

## Security

### Data Encryption

**At Rest:**
- S3: SSE-S3 (AES-256)
- Glue: Encrypted job bookmarks
- Athena: Encrypted query results

**In Transit:**
- TLS 1.2+ for all data transfers
- VPC endpoints for private connectivity

### Access Control

**IAM Roles:**
- Least privilege principle
- Separate roles for each service
- No long-term credentials

**S3 Bucket Policies:**
- Block public access
- Enforce encryption
- Audit logging enabled

**Glue Data Catalog:**
- Resource-level permissions
- Fine-grained access control

### Compliance

**Audit Logging:**
- CloudTrail: All API calls
- S3 access logs
- VPC Flow Logs

**Data Governance:**
- Data classification tags
- Retention policies
- PII data masking

## Cost Optimization

### Cost Breakdown (Monthly)

**Development Environment:**
| Service | Usage | Cost |
|---------|-------|------|
| S3 Storage | 100 GB | $2.30 |
| S3 Requests | 1M | $0.55 |
| Lambda | 1M invocations | $0.20 |
| Glue | 10 DPU-hours/day | $13.20 |
| Athena | 100 GB scanned | $0.50 |
| Step Functions | 1K transitions | $0.03 |
| **Total** | | **~$19/month** |

**Production Environment:**
| Service | Usage | Cost |
|---------|-------|------|
| S3 Storage | 1 TB | $23.00 |
| S3 Requests | 10M | $5.50 |
| Lambda | 10M invocations | $2.00 |
| Glue | 50 DPU-hours/day | $66.00 |
| Athena | 1 TB scanned | $5.00 |
| Step Functions | 10K transitions | $0.25 |
| **Total** | | **~$102/month** |

### Cost Optimization Strategies

1. **Partitioning**: Reduce Athena scan costs by 90%+
2. **Parquet**: Reduce storage and scan costs by 80%+
3. **Lifecycle Policies**: Move old data to Glacier
4. **Glue Bookmarks**: Process only new data
5. **Athena Caching**: Reuse query results
6. **Right-sizing**: Use appropriate Lambda memory
7. **Reserved Capacity**: For predictable workloads

### Cost Monitoring

**CloudWatch Alarms:**
- Daily spend threshold
- Monthly budget alerts
- Anomaly detection

**Cost Allocation Tags:**
- Environment (dev/staging/prod)
- Team/Project
- Data source

---

**Last Updated**: 2025-01-15  
**Version**: 1.0  
**Author**: Data Engineering Team
