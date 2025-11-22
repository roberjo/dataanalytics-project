"""
Unit tests for Lambda functions.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
class TestFileValidator:
    """Test file validator Lambda function."""
    
    def test_detect_data_type(self):
        """Test data type detection from S3 key."""
        from src.ingestion.file_validator import FileValidator
        
        # Test transactions
        validator = FileValidator('bucket', 'raw/transactions/date=2025-01-15/file.csv')
        assert validator.data_type == 'transactions'
        
        # Test products
        validator = FileValidator('bucket', 'raw/products/date=2025-01-15/file.json')
        assert validator.data_type == 'products'
        
        # Test clickstream
        validator = FileValidator('bucket', 'raw/clickstream/date=2025-01-15/file.json')
        assert validator.data_type == 'clickstream'
        
        # Test reviews
        validator = FileValidator('bucket', 'raw/reviews/date=2025-01-15/file.csv')
        assert validator.data_type == 'reviews'
        
        # Test unknown
        validator = FileValidator('bucket', 'raw/unknown/file.csv')
        assert validator.data_type is None
    
    def test_validate_format(self):
        """Test file format validation."""
        from src.ingestion.file_validator import FileValidator
        
        # CSV format
        validator = FileValidator('bucket', 'raw/transactions/file.csv')
        result = validator._validate_format()
        assert result['valid'] is True
        
        # Wrong format
        validator = FileValidator('bucket', 'raw/transactions/file.json')
        result = validator._validate_format()
        assert result['valid'] is False
        assert len(result['errors']) > 0


@pytest.mark.unit
class TestDataQualityCheck:
    """Test data quality check Lambda function."""
    
    def test_data_quality_checker_initialization(self):
        """Test DataQualityChecker initialization."""
        from src.transformation.lambda_functions.data_quality_check import DataQualityChecker
        
        checker = DataQualityChecker(
            database='test_db',
            workgroup='test_workgroup',
            output_location='s3://test/results/'
        )
        
        assert checker.database == 'test_db'
        assert checker.workgroup == 'test_workgroup'
        assert len(checker.checks_passed) == 0
        assert len(checker.checks_failed) == 0
    
    def test_get_summary(self):
        """Test getting summary of checks."""
        from src.transformation.lambda_functions.data_quality_check import DataQualityChecker
        
        checker = DataQualityChecker('test_db')
        
        # Add some mock results
        checker.checks_passed.append({'check': 'test1', 'value': 100})
        checker.checks_failed.append({'check': 'test2', 'reason': 'Failed'})
        
        summary = checker.get_summary()
        
        assert summary['total_checks'] == 2
        assert summary['passed'] == 1
        assert summary['failed'] == 1
        assert summary['success_rate'] == 0.5
        assert summary['all_passed'] is False
