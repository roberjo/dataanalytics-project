"""
AWS Glue helper utilities for ETL job and crawler operations.
"""
import boto3
from botocore.exceptions import ClientError
import logging
import time
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class GlueHelper:
    """Helper class for AWS Glue operations."""
    
    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize Glue client."""
        self.glue_client = boto3.client('glue', region_name=region_name)
    
    def start_job_run(self, job_name: str, arguments: Optional[Dict] = None) -> Optional[str]:
        """
        Start a Glue job run.
        
        Args:
            job_name: Glue job name
            arguments: Job arguments dictionary
            
        Returns:
            Job run ID or None if error
        """
        try:
            params = {'JobName': job_name}
            if arguments:
                # Glue expects arguments with -- prefix
                params['Arguments'] = {f'--{k}': v for k, v in arguments.items()}
            
            response = self.glue_client.start_job_run(**params)
            job_run_id = response['JobRunId']
            logger.info(f"Started Glue job {job_name}: {job_run_id}")
            return job_run_id
        except ClientError as e:
            logger.error(f"Error starting job run: {e}")
            return None
    
    def get_job_run_status(self, job_name: str, run_id: str) -> Optional[Dict]:
        """
        Get status of a Glue job run.
        
        Args:
            job_name: Glue job name
            run_id: Job run ID
            
        Returns:
            Job run status dictionary or None if error
        """
        try:
            response = self.glue_client.get_job_run(
                JobName=job_name,
                RunId=run_id
            )
            job_run = response['JobRun']
            return {
                'state': job_run['JobRunState'],
                'started_on': job_run.get('StartedOn'),
                'completed_on': job_run.get('CompletedOn'),
                'execution_time': job_run.get('ExecutionTime'),
                'error_message': job_run.get('ErrorMessage')
            }
        except ClientError as e:
            logger.error(f"Error getting job run status: {e}")
            return None
    
    def wait_for_job_run(self, job_name: str, run_id: str,
                        max_wait_seconds: int = 3600) -> str:
        """
        Wait for Glue job run to complete.
        
        Args:
            job_name: Glue job name
            run_id: Job run ID
            max_wait_seconds: Maximum time to wait
            
        Returns:
            Final job state (SUCCEEDED, FAILED, STOPPED, TIMEOUT)
        """
        start_time = time.time()
        
        while True:
            if time.time() - start_time > max_wait_seconds:
                logger.error(f"Job run timeout after {max_wait_seconds} seconds")
                return 'TIMEOUT'
            
            status = self.get_job_run_status(job_name, run_id)
            if not status:
                return 'ERROR'
            
            state = status['state']
            
            if state in ['SUCCEEDED', 'FAILED', 'STOPPED']:
                logger.info(f"Job {job_name} run {run_id} finished with state: {state}")
                
                if state == 'FAILED':
                    logger.error(f"Job failed: {status.get('error_message', 'Unknown error')}")
                
                return state
            
            time.sleep(10)
    
    def start_crawler(self, crawler_name: str) -> bool:
        """
        Start a Glue crawler.
        
        Args:
            crawler_name: Crawler name
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self.glue_client.start_crawler(Name=crawler_name)
            logger.info(f"Started crawler: {crawler_name}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'CrawlerRunningException':
                logger.warning(f"Crawler {crawler_name} is already running")
                return True
            logger.error(f"Error starting crawler: {e}")
            return False
    
    def get_crawler_status(self, crawler_name: str) -> Optional[Dict]:
        """
        Get crawler status.
        
        Args:
            crawler_name: Crawler name
            
        Returns:
            Crawler status dictionary or None if error
        """
        try:
            response = self.glue_client.get_crawler(Name=crawler_name)
            crawler = response['Crawler']
            return {
                'state': crawler.get('State'),
                'last_crawl': crawler.get('LastCrawl'),
                'crawl_elapsed_time': crawler.get('CrawlElapsedTime')
            }
        except ClientError as e:
            logger.error(f"Error getting crawler status: {e}")
            return None
    
    def wait_for_crawler(self, crawler_name: str,
                        max_wait_seconds: int = 1800) -> str:
        """
        Wait for crawler to complete.
        
        Args:
            crawler_name: Crawler name
            max_wait_seconds: Maximum time to wait
            
        Returns:
            Final crawler state (READY, FAILED, TIMEOUT)
        """
        start_time = time.time()
        
        while True:
            if time.time() - start_time > max_wait_seconds:
                logger.error(f"Crawler timeout after {max_wait_seconds} seconds")
                return 'TIMEOUT'
            
            status = self.get_crawler_status(crawler_name)
            if not status:
                return 'ERROR'
            
            state = status['state']
            
            if state == 'READY':
                logger.info(f"Crawler {crawler_name} completed successfully")
                return 'READY'
            elif state == 'FAILED':
                logger.error(f"Crawler {crawler_name} failed")
                return 'FAILED'
            
            time.sleep(10)
    
    def get_database(self, database_name: str) -> Optional[Dict]:
        """
        Get Glue database metadata.
        
        Args:
            database_name: Database name
            
        Returns:
            Database metadata or None if error
        """
        try:
            response = self.glue_client.get_database(Name=database_name)
            return response['Database']
        except ClientError as e:
            logger.error(f"Error getting database: {e}")
            return None
    
    def get_table(self, database_name: str, table_name: str) -> Optional[Dict]:
        """
        Get Glue table metadata.
        
        Args:
            database_name: Database name
            table_name: Table name
            
        Returns:
            Table metadata or None if error
        """
        try:
            response = self.glue_client.get_table(
                DatabaseName=database_name,
                Name=table_name
            )
            return response['Table']
        except ClientError as e:
            logger.error(f"Error getting table: {e}")
            return None
    
    def get_partitions(self, database_name: str, table_name: str) -> List[Dict]:
        """
        Get table partitions.
        
        Args:
            database_name: Database name
            table_name: Table name
            
        Returns:
            List of partition metadata
        """
        try:
            paginator = self.glue_client.get_paginator('get_partitions')
            page_iterator = paginator.paginate(
                DatabaseName=database_name,
                TableName=table_name
            )
            
            partitions = []
            for page in page_iterator:
                partitions.extend(page['Partitions'])
            
            logger.info(f"Found {len(partitions)} partitions for {database_name}.{table_name}")
            return partitions
        except ClientError as e:
            logger.error(f"Error getting partitions: {e}")
            return []
    
    def create_partition(self, database_name: str, table_name: str,
                        partition_values: List[str], location: str) -> bool:
        """
        Create a new partition.
        
        Args:
            database_name: Database name
            table_name: Table name
            partition_values: List of partition values
            location: S3 location for partition data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            table = self.get_table(database_name, table_name)
            if not table:
                return False
            
            partition_input = {
                'Values': partition_values,
                'StorageDescriptor': table['StorageDescriptor'].copy()
            }
            partition_input['StorageDescriptor']['Location'] = location
            
            self.glue_client.create_partition(
                DatabaseName=database_name,
                TableName=table_name,
                PartitionInput=partition_input
            )
            logger.info(f"Created partition {partition_values} for {database_name}.{table_name}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'AlreadyExistsException':
                logger.warning(f"Partition already exists: {partition_values}")
                return True
            logger.error(f"Error creating partition: {e}")
            return False
