"""
S3 helper utilities for data pipeline operations.
"""

import boto3
from botocore.exceptions import ClientError
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class S3Helper:
    """Helper class for S3 operations."""

    def __init__(self, region_name: str = "us-east-1"):
        """Initialize S3 client."""
        self.s3_client = boto3.client("s3", region_name=region_name)
        self.s3_resource = boto3.resource("s3", region_name=region_name)

    def upload_file(self, file_path: str, bucket: str, key: str) -> bool:
        """
        Upload a file to S3.

        Args:
            file_path: Local file path
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.upload_file(file_path, bucket, key)
            logger.info(f"Uploaded {file_path} to s3://{bucket}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading file: {e}")
            return False

    def download_file(self, bucket: str, key: str, file_path: str) -> bool:
        """
        Download a file from S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key
            file_path: Local file path to save

        Returns:
            True if successful, False otherwise
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(bucket, key, file_path)
            logger.info(f"Downloaded s3://{bucket}/{key} to {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Error downloading file: {e}")
            return False

    def list_objects(self, bucket: str, prefix: str = "") -> List[Dict]:
        """
        List objects in S3 bucket with given prefix.

        Args:
            bucket: S3 bucket name
            prefix: Object key prefix

        Returns:
            List of object metadata dictionaries
        """
        try:
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

            objects = []
            for page in pages:
                if "Contents" in page:
                    objects.extend(page["Contents"])

            logger.info(f"Found {len(objects)} objects in s3://{bucket}/{prefix}")
            return objects
        except ClientError as e:
            logger.error(f"Error listing objects: {e}")
            return []

    def delete_object(self, bucket: str, key: str) -> bool:
        """
        Delete an object from S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            logger.info(f"Deleted s3://{bucket}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting object: {e}")
            return False

    def copy_object(
        self, source_bucket: str, source_key: str, dest_bucket: str, dest_key: str
    ) -> bool:
        """
        Copy an object within S3.

        Args:
            source_bucket: Source bucket name
            source_key: Source object key
            dest_bucket: Destination bucket name
            dest_key: Destination object key

        Returns:
            True if successful, False otherwise
        """
        try:
            copy_source = {"Bucket": source_bucket, "Key": source_key}
            self.s3_client.copy_object(
                CopySource=copy_source, Bucket=dest_bucket, Key=dest_key
            )
            logger.info(
                f"Copied s3://{source_bucket}/{source_key} to s3://{dest_bucket}/{dest_key}"
            )
            return True
        except ClientError as e:
            logger.error(f"Error copying object: {e}")
            return False

    def get_object_metadata(self, bucket: str, key: str) -> Optional[Dict]:
        """
        Get metadata for an S3 object.

        Args:
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            Object metadata dictionary or None if error
        """
        try:
            response = self.s3_client.head_object(Bucket=bucket, Key=key)
            return {
                "size": response["ContentLength"],
                "last_modified": response["LastModified"],
                "content_type": response.get("ContentType"),
                "etag": response["ETag"],
            }
        except ClientError as e:
            logger.error(f"Error getting object metadata: {e}")
            return None

    def object_exists(self, bucket: str, key: str) -> bool:
        """
        Check if an object exists in S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            True if object exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False

    def read_json_lines(self, bucket: str, key: str) -> List[Dict]:
        """
        Read JSON lines file from S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            List of parsed JSON objects
        """
        import json

        try:
            obj = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = obj["Body"].read().decode("utf-8")

            records = []
            for line in content.strip().split("\n"):
                if line:
                    records.append(json.loads(line))

            logger.info(f"Read {len(records)} records from s3://{bucket}/{key}")
            return records
        except ClientError as e:
            logger.error(f"Error reading JSON lines: {e}")
            return []

    def write_json_lines(self, records: List[Dict], bucket: str, key: str) -> bool:
        """
        Write JSON lines file to S3.

        Args:
            records: List of dictionaries to write
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            True if successful, False otherwise
        """
        import json

        try:
            content = "\n".join(json.dumps(record) for record in records)
            self.s3_client.put_object(
                Bucket=bucket, Key=key, Body=content.encode("utf-8")
            )
            logger.info(f"Wrote {len(records)} records to s3://{bucket}/{key}")
            return True
        except ClientError as e:
            logger.error(f"Error writing JSON lines: {e}")
            return False
