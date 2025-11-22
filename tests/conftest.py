"""
Pytest configuration and fixtures for testing.
"""

import os

# Set AWS credentials BEFORE any boto3 imports to prevent NoRegionError
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

import pytest
import boto3
from moto import mock_aws


@pytest.fixture
def aws_credentials():
    """Mock AWS credentials for testing."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def s3_client(aws_credentials):
    """Create a mock S3 client."""
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture
def athena_client(aws_credentials):
    """Create a mock Athena client."""
    with mock_aws():
        yield boto3.client("athena", region_name="us-east-1")


@pytest.fixture
def glue_client(aws_credentials):
    """Create a mock Glue client."""
    with mock_aws():
        yield boto3.client("glue", region_name="us-east-1")


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return [
        {
            "transaction_id": "txn_001",
            "customer_id": "cust_123",
            "product_id": "prod_456",
            "quantity": 2,
            "price": 29.99,
            "total_amount": 59.98,
            "transaction_date": "2025-01-15 14:30:45",
            "status": "completed",
        },
        {
            "transaction_id": "txn_002",
            "customer_id": "cust_124",
            "product_id": "prod_457",
            "quantity": 1,
            "price": 49.99,
            "total_amount": 49.99,
            "transaction_date": "2025-01-15 15:20:10",
            "status": "completed",
        },
    ]


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return [
        {
            "product_id": "prod_456",
            "name": "Wireless Mouse",
            "category": "Electronics",
            "brand": "TechBrand",
            "price": 29.99,
            "stock": 150,
        },
        {
            "product_id": "prod_457",
            "name": "Keyboard",
            "category": "Electronics",
            "brand": "TechBrand",
            "price": 49.99,
            "stock": 75,
        },
    ]
