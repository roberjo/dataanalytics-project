"""
Athena helper utilities for query execution and result handling.
"""
import boto3
from botocore.exceptions import ClientError
import logging
import time
from typing import List, Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class AthenaHelper:
    """Helper class for Athena operations."""
    
    def __init__(self, region_name: str = 'us-east-1', 
                 workgroup: str = 'primary',
                 output_location: Optional[str] = None):
        """
        Initialize Athena client.
        
        Args:
            region_name: AWS region
            workgroup: Athena workgroup name
            output_location: S3 location for query results
        """
        self.athena_client = boto3.client('athena', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.workgroup = workgroup
        self.output_location = output_location
    
    def execute_query(self, query: str, database: str = 'default',
                     wait: bool = True, max_wait_seconds: int = 300) -> Optional[str]:
        """
        Execute an Athena query.
        
        Args:
            query: SQL query string
            database: Database name
            wait: Whether to wait for query completion
            max_wait_seconds: Maximum time to wait for completion
            
        Returns:
            Query execution ID or None if error
        """
        try:
            execution_params = {
                'QueryString': query,
                'QueryExecutionContext': {'Database': database},
                'WorkGroup': self.workgroup
            }
            
            if self.output_location:
                execution_params['ResultConfiguration'] = {
                    'OutputLocation': self.output_location
                }
            
            response = self.athena_client.start_query_execution(**execution_params)
            query_execution_id = response['QueryExecutionId']
            
            logger.info(f"Started query execution: {query_execution_id}")
            
            if wait:
                self.wait_for_query(query_execution_id, max_wait_seconds)
            
            return query_execution_id
        except ClientError as e:
            logger.error(f"Error executing query: {e}")
            return None
    
    def wait_for_query(self, query_execution_id: str, 
                      max_wait_seconds: int = 300) -> str:
        """
        Wait for query to complete.
        
        Args:
            query_execution_id: Query execution ID
            max_wait_seconds: Maximum time to wait
            
        Returns:
            Final query state (SUCCEEDED, FAILED, CANCELLED)
        """
        start_time = time.time()
        
        while True:
            if time.time() - start_time > max_wait_seconds:
                logger.error(f"Query timeout after {max_wait_seconds} seconds")
                return 'TIMEOUT'
            
            response = self.athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            state = response['QueryExecution']['Status']['State']
            
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                logger.info(f"Query {query_execution_id} finished with state: {state}")
                
                if state == 'FAILED':
                    reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                    logger.error(f"Query failed: {reason}")
                
                return state
            
            time.sleep(1)
    
    def get_query_results(self, query_execution_id: str,
                         max_results: int = 1000) -> List[Dict]:
        """
        Get query results as list of dictionaries.
        
        Args:
            query_execution_id: Query execution ID
            max_results: Maximum number of results to return
            
        Returns:
            List of result rows as dictionaries
        """
        try:
            paginator = self.athena_client.get_paginator('get_query_results')
            page_iterator = paginator.paginate(
                QueryExecutionId=query_execution_id,
                PaginationConfig={'MaxItems': max_results}
            )
            
            results = []
            column_names = None
            
            for page in page_iterator:
                rows = page['ResultSet']['Rows']
                
                # First row contains column names
                if column_names is None:
                    column_names = [col['VarCharValue'] for col in rows[0]['Data']]
                    rows = rows[1:]  # Skip header row
                
                # Parse data rows
                for row in rows:
                    values = [col.get('VarCharValue') for col in row['Data']]
                    results.append(dict(zip(column_names, values)))
            
            logger.info(f"Retrieved {len(results)} results from query {query_execution_id}")
            return results
        except ClientError as e:
            logger.error(f"Error getting query results: {e}")
            return []
    
    def get_query_results_df(self, query_execution_id: str,
                            max_results: int = 1000) -> pd.DataFrame:
        """
        Get query results as pandas DataFrame.
        
        Args:
            query_execution_id: Query execution ID
            max_results: Maximum number of results to return
            
        Returns:
            DataFrame with query results
        """
        results = self.get_query_results(query_execution_id, max_results)
        return pd.DataFrame(results)
    
    def execute_and_get_results(self, query: str, database: str = 'default',
                               max_results: int = 1000) -> List[Dict]:
        """
        Execute query and return results in one call.
        
        Args:
            query: SQL query string
            database: Database name
            max_results: Maximum number of results to return
            
        Returns:
            List of result rows as dictionaries
        """
        query_execution_id = self.execute_query(query, database, wait=True)
        if query_execution_id:
            return self.get_query_results(query_execution_id, max_results)
        return []
    
    def execute_and_get_df(self, query: str, database: str = 'default',
                          max_results: int = 1000) -> pd.DataFrame:
        """
        Execute query and return results as DataFrame.
        
        Args:
            query: SQL query string
            database: Database name
            max_results: Maximum number of results to return
            
        Returns:
            DataFrame with query results
        """
        results = self.execute_and_get_results(query, database, max_results)
        return pd.DataFrame(results)
    
    def create_named_query(self, name: str, query: str, 
                          database: str, description: str = '') -> Optional[str]:
        """
        Create a named query in Athena.
        
        Args:
            name: Query name
            query: SQL query string
            database: Database name
            description: Query description
            
        Returns:
            Named query ID or None if error
        """
        try:
            response = self.athena_client.create_named_query(
                Name=name,
                Description=description,
                Database=database,
                QueryString=query,
                WorkGroup=self.workgroup
            )
            logger.info(f"Created named query: {name}")
            return response['NamedQueryId']
        except ClientError as e:
            logger.error(f"Error creating named query: {e}")
            return None
    
    def repair_table(self, table_name: str, database: str = 'default') -> bool:
        """
        Run MSCK REPAIR TABLE to add partitions.
        
        Args:
            table_name: Table name
            database: Database name
            
        Returns:
            True if successful, False otherwise
        """
        query = f"MSCK REPAIR TABLE {table_name}"
        query_execution_id = self.execute_query(query, database, wait=True)
        
        if query_execution_id:
            state = self.wait_for_query(query_execution_id)
            return state == 'SUCCEEDED'
        return False
    
    def get_table_metadata(self, table_name: str, 
                          database: str = 'default') -> Optional[Dict]:
        """
        Get table metadata from Glue catalog.
        
        Args:
            table_name: Table name
            database: Database name
            
        Returns:
            Table metadata dictionary or None if error
        """
        glue_client = boto3.client('glue')
        
        try:
            response = glue_client.get_table(
                DatabaseName=database,
                Name=table_name
            )
            return response['Table']
        except ClientError as e:
            logger.error(f"Error getting table metadata: {e}")
            return None
