"""
AWS Glue ETL job for processing transaction data.
Reads CSV from S3 raw zone, transforms, and writes Parquet to processed zone.
"""
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from pyspark.sql.types import *
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get job parameters
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'SOURCE_BUCKET',
    'SOURCE_PREFIX',
    'TARGET_BUCKET',
    'TARGET_PREFIX',
    'DATABASE_NAME',
    'TABLE_NAME'
])

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

logger.info(f"Starting job: {args['JOB_NAME']}")
logger.info(f"Source: s3://{args['SOURCE_BUCKET']}/{args['SOURCE_PREFIX']}")
logger.info(f"Target: s3://{args['TARGET_BUCKET']}/{args['TARGET_PREFIX']}")


def clean_transaction_data(df):
    """
    Clean and transform transaction data.
    
    Transformations:
    1. Convert date strings to datetime
    2. Handle null values
    3. Calculate total_amount if missing
    4. Filter invalid transactions
    5. Deduplicate by transaction_id
    6. Add processing metadata
    """
    logger.info(f"Input record count: {df.count()}")
    
    # Convert transaction_date to timestamp
    df = df.withColumn(
        'transaction_date',
        F.to_timestamp('transaction_date', 'yyyy-MM-dd HH:mm:ss')
    )
    
    # Convert numeric columns to proper types
    df = df.withColumn('quantity', F.col('quantity').cast(IntegerType()))
    df = df.withColumn('price', F.col('price').cast(DecimalType(10, 2)))
    df = df.withColumn('total_amount', F.col('total_amount').cast(DecimalType(10, 2)))
    
    # Calculate total_amount if missing or incorrect
    df = df.withColumn(
        'total_amount_calculated',
        F.col('quantity') * F.col('price')
    )
    
    df = df.withColumn(
        'total_amount',
        F.when(
            F.col('total_amount').isNull() | (F.abs(F.col('total_amount') - F.col('total_amount_calculated')) > 0.01),
            F.col('total_amount_calculated')
        ).otherwise(F.col('total_amount'))
    ).drop('total_amount_calculated')
    
    # Filter out invalid transactions
    df = df.filter(
        (F.col('quantity') > 0) &
        (F.col('price') > 0) &
        (F.col('total_amount') > 0) &
        (F.col('transaction_id').isNotNull()) &
        (F.col('customer_id').isNotNull()) &
        (F.col('product_id').isNotNull())
    )
    
    logger.info(f"After filtering invalid records: {df.count()}")
    
    # Deduplicate by transaction_id (keep first occurrence)
    df = df.dropDuplicates(['transaction_id'])
    
    logger.info(f"After deduplication: {df.count()}")
    
    # Add processing metadata
    df = df.withColumn('processing_timestamp', F.current_timestamp())
    df = df.withColumn('processing_date', F.current_date())
    
    # Add partition columns
    df = df.withColumn('year', F.year('transaction_date'))
    df = df.withColumn('month', F.month('transaction_date'))
    df = df.withColumn('day', F.dayofmonth('transaction_date'))
    
    # Standardize status values
    df = df.withColumn(
        'status',
        F.lower(F.trim(F.col('status')))
    )
    
    return df


def calculate_derived_metrics(df):
    """Calculate additional metrics and flags."""
    
    # Add revenue category
    df = df.withColumn(
        'revenue_category',
        F.when(F.col('total_amount') >= 100, 'high')
         .when(F.col('total_amount') >= 50, 'medium')
         .otherwise('low')
    )
    
    # Add transaction hour (for time-based analysis)
    df = df.withColumn('transaction_hour', F.hour('transaction_date'))
    
    # Add day of week
    df = df.withColumn('day_of_week', F.dayofweek('transaction_date'))
    
    # Add is_weekend flag
    df = df.withColumn(
        'is_weekend',
        F.when(F.col('day_of_week').isin([1, 7]), True).otherwise(False)
    )
    
    return df


def main():
    """Main ETL process."""
    
    try:
        # Read CSV data from S3
        source_path = f"s3://{args['SOURCE_BUCKET']}/{args['SOURCE_PREFIX']}"
        logger.info(f"Reading data from: {source_path}")
        
        df = spark.read \
            .option("header", "true") \
            .option("inferSchema", "false") \
            .csv(source_path)
        
        logger.info(f"Schema: {df.schema}")
        
        # Clean and transform data
        df_cleaned = clean_transaction_data(df)
        
        # Calculate derived metrics
        df_final = calculate_derived_metrics(df_cleaned)
        
        # Write to S3 as Parquet with partitioning
        target_path = f"s3://{args['TARGET_BUCKET']}/{args['TARGET_PREFIX']}"
        logger.info(f"Writing data to: {target_path}")
        
        df_final.write \
            .mode('overwrite') \
            .partitionBy('year', 'month', 'day') \
            .parquet(target_path, compression='snappy')
        
        logger.info(f"Successfully wrote {df_final.count()} records")
        
        # Update Glue Data Catalog
        logger.info("Updating Glue Data Catalog")
        
        # Create DynamicFrame for catalog update
        dynamic_frame = DynamicFrame.fromDF(
            df_final,
            glueContext,
            "dynamic_frame"
        )
        
        # Write to catalog
        glueContext.write_dynamic_frame.from_catalog(
            frame=dynamic_frame,
            database=args['DATABASE_NAME'],
            table_name=args['TABLE_NAME'],
            transformation_ctx="write_to_catalog"
        )
        
        # Print summary statistics
        logger.info("=== Summary Statistics ===")
        logger.info(f"Total transactions processed: {df_final.count()}")
        
        status_counts = df_final.groupBy('status').count().collect()
        logger.info("Status distribution:")
        for row in status_counts:
            logger.info(f"  {row['status']}: {row['count']}")
        
        revenue_stats = df_final.agg(
            F.sum('total_amount').alias('total_revenue'),
            F.avg('total_amount').alias('avg_order_value'),
            F.min('total_amount').alias('min_order'),
            F.max('total_amount').alias('max_order')
        ).collect()[0]
        
        logger.info(f"Total revenue: ${revenue_stats['total_revenue']:.2f}")
        logger.info(f"Average order value: ${revenue_stats['avg_order_value']:.2f}")
        logger.info(f"Min order: ${revenue_stats['min_order']:.2f}")
        logger.info(f"Max order: ${revenue_stats['max_order']:.2f}")
        
        job.commit()
        logger.info("Job completed successfully")
    
    except Exception as e:
        logger.error(f"Job failed with error: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
