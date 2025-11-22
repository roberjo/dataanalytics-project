"""
Lambda function to validate incoming data files.
Checks file format, schema compliance, size, and deduplication.
"""

import json
import boto3
import hashlib
import csv
from io import StringIO
from typing import Dict, List, Optional
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")


# Expected schemas for each data type
SCHEMAS = {
    "transactions": {
        "required_columns": [
            "transaction_id",
            "customer_id",
            "product_id",
            "quantity",
            "price",
            "total_amount",
            "transaction_date",
            "status",
        ],
        "format": "csv",
    },
    "products": {
        "required_fields": [
            "product_id",
            "name",
            "category",
            "brand",
            "price",
            "stock",
        ],
        "format": "json",
    },
    "clickstream": {
        "required_fields": [
            "session_id",
            "customer_id",
            "event_type",
            "page",
            "timestamp",
            "device",
        ],
        "format": "json",
    },
    "reviews": {
        "required_columns": [
            "review_id",
            "product_id",
            "customer_id",
            "rating",
            "review_text",
            "review_date",
        ],
        "format": "csv",
    },
}


class FileValidator:
    """Validate data files before processing."""

    def __init__(self, bucket: str, key: str):
        self.bucket = bucket
        self.key = key
        self.data_type = self._detect_data_type()
        self.schema = SCHEMAS.get(self.data_type)

    def _detect_data_type(self) -> Optional[str]:
        """Detect data type from S3 key path."""
        for data_type in SCHEMAS.keys():
            if f"/{data_type}/" in self.key:
                return data_type
        return None

    def validate(self) -> Dict:
        """
        Run all validation checks.

        Returns:
            Validation result dictionary
        """
        result = {"valid": True, "errors": [], "warnings": [], "metadata": {}}

        if not self.data_type:
            result["valid"] = False
            result["errors"].append("Unknown data type")
            return result

        # Get file metadata
        try:
            response = s3_client.head_object(Bucket=self.bucket, Key=self.key)
            file_size = response["ContentLength"]
            result["metadata"]["size_bytes"] = file_size
            result["metadata"]["last_modified"] = response["LastModified"].isoformat()
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error accessing file: {str(e)}")
            return result

        # Check file size (max 1GB for Lambda processing)
        if file_size > 1024 * 1024 * 1024:
            result["warnings"].append(
                "File size exceeds 1GB, will use Glue for processing"
            )
            result["metadata"]["use_glue"] = True
        else:
            result["metadata"]["use_glue"] = False

        # Check file format
        format_valid = self._validate_format()
        if not format_valid["valid"]:
            result["valid"] = False
            result["errors"].extend(format_valid["errors"])
            return result

        # Check schema
        schema_valid = self._validate_schema()
        if not schema_valid["valid"]:
            result["valid"] = False
            result["errors"].extend(schema_valid["errors"])
        else:
            result["metadata"]["row_count"] = schema_valid.get("row_count", 0)

        # Check for duplicates
        duplicate_check = self._check_duplicates()
        if duplicate_check["is_duplicate"]:
            result["valid"] = False
            result["errors"].append("Duplicate file detected")
            result["metadata"]["duplicate_of"] = duplicate_check["original_file"]
        else:
            result["metadata"]["file_hash"] = duplicate_check["file_hash"]

        return result

    def _validate_format(self) -> Dict:
        """Validate file format matches expected type."""
        result = {"valid": True, "errors": []}

        expected_format = self.schema["format"]

        if expected_format == "csv" and not self.key.endswith(".csv"):
            result["valid"] = False
            result["errors"].append(f'Expected CSV file, got {self.key.split(".")[-1]}')
        elif expected_format == "json" and not self.key.endswith(".json"):
            result["valid"] = False
            result["errors"].append(
                f'Expected JSON file, got {self.key.split(".")[-1]}'
            )

        return result

    def _validate_schema(self) -> Dict:
        """Validate file schema matches expected schema."""
        result = {"valid": True, "errors": [], "row_count": 0}

        try:
            # Download first 1MB to check schema
            response = s3_client.get_object(
                Bucket=self.bucket, Key=self.key, Range="bytes=0-1048576"
            )
            content = response["Body"].read().decode("utf-8")

            if self.schema["format"] == "csv":
                result = self._validate_csv_schema(content)
            elif self.schema["format"] == "json":
                result = self._validate_json_schema(content)

        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error reading file: {str(e)}")

        return result

    def _validate_csv_schema(self, content: str) -> Dict:
        """Validate CSV schema."""
        result = {"valid": True, "errors": [], "row_count": 0}

        try:
            reader = csv.DictReader(StringIO(content))
            headers = reader.fieldnames

            required_columns = self.schema["required_columns"]
            missing_columns = set(required_columns) - set(headers)

            if missing_columns:
                result["valid"] = False
                result["errors"].append(f"Missing required columns: {missing_columns}")

            # Count rows in sample
            result["row_count"] = sum(1 for _ in reader)

        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Invalid CSV format: {str(e)}")

        return result

    def _validate_json_schema(self, content: str) -> Dict:
        """Validate JSON schema (newline-delimited JSON)."""
        result = {"valid": True, "errors": [], "row_count": 0}

        try:
            lines = content.strip().split("\n")
            required_fields = self.schema["required_fields"]

            for i, line in enumerate(lines[:100]):  # Check first 100 records
                if not line:
                    continue

                try:
                    record = json.loads(line)
                    missing_fields = set(required_fields) - set(record.keys())

                    if missing_fields:
                        result["valid"] = False
                        result["errors"].append(
                            f"Line {i+1}: Missing required fields: {missing_fields}"
                        )
                        break

                    result["row_count"] += 1

                except json.JSONDecodeError as e:
                    result["valid"] = False
                    result["errors"].append(f"Line {i+1}: Invalid JSON: {str(e)}")
                    break

        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error parsing JSON: {str(e)}")

        return result

    def _check_duplicates(self) -> Dict:
        """Check if file is a duplicate based on content hash."""
        try:
            # Calculate file hash
            response = s3_client.get_object(Bucket=self.bucket, Key=self.key)
            file_content = response["Body"].read()
            file_hash = hashlib.md5(file_content).hexdigest()

            # Check DynamoDB for existing hash
            table_name = "data-pipeline-file-hashes"
            try:
                table = dynamodb.Table(table_name)
                response = table.get_item(Key={"file_hash": file_hash})

                if "Item" in response:
                    return {
                        "is_duplicate": True,
                        "file_hash": file_hash,
                        "original_file": response["Item"]["s3_key"],
                    }
                else:
                    # Store hash for future checks
                    table.put_item(
                        Item={
                            "file_hash": file_hash,
                            "s3_key": self.key,
                            "bucket": self.bucket,
                            "timestamp": response["LastModified"].isoformat(),
                        }
                    )
            except Exception as e:
                logger.warning(f"DynamoDB check failed: {e}")

            return {"is_duplicate": False, "file_hash": file_hash}

        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
            return {"is_duplicate": False, "file_hash": None}


def lambda_handler(event, context):
    """
    Lambda handler for file validation.

    Event format:
    {
        "bucket": "bucket-name",
        "key": "raw/transactions/date=2025-01-15/file.csv"
    }
    """
    try:
        # Parse event
        if "Records" in event:
            # S3 event notification
            record = event["Records"][0]
            bucket = record["s3"]["bucket"]["name"]
            key = record["s3"]["object"]["key"]
        else:
            # Direct invocation
            bucket = event["bucket"]
            key = event["key"]

        logger.info(f"Validating file: s3://{bucket}/{key}")

        # Validate file
        validator = FileValidator(bucket, key)
        result = validator.validate()

        logger.info(f"Validation result: {json.dumps(result)}")

        return {
            "statusCode": 200 if result["valid"] else 400,
            "body": json.dumps(result),
            "validation_result": result,
        }

    except Exception as e:
        logger.error(f"Error in file validation: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"valid": False, "errors": [str(e)]}),
        }
