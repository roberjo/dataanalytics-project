"""
Unit tests for Athena helper utilities.
"""
import pytest
from src.utils.athena_helper import AthenaHelper


@pytest.mark.unit
class TestAthenaHelper:
    """Test AthenaHelper class."""
    
    def test_initialization(self):
        """Test AthenaHelper initialization."""
        helper = AthenaHelper(
            region_name='us-east-1',
            workgroup='test-workgroup',
            output_location='s3://test-bucket/results/'
        )
        
        assert helper.workgroup == 'test-workgroup'
        assert helper.output_location == 's3://test-bucket/results/'
    
    def test_default_initialization(self):
        """Test AthenaHelper with default values."""
        helper = AthenaHelper()
        
        assert helper.workgroup == 'primary'
        assert helper.output_location is None


@pytest.mark.unit  
class TestGlueHelper:
    """Test GlueHelper class."""
    
    def test_initialization(self):
        """Test GlueHelper initialization."""
        from src.utils.glue_helper import GlueHelper
        
        helper = GlueHelper(region_name='us-east-1')
        assert helper.glue_client is not None


@pytest.mark.unit
class TestLogger:
    """Test logger utilities."""
    
    def test_setup_logger(self):
        """Test logger setup."""
        from src.utils.logger import setup_logger
        
        logger = setup_logger('test_logger', level='INFO')
        
        assert logger.name == 'test_logger'
        assert logger.level == 20  # INFO level
    
    def test_get_logger(self):
        """Test getting logger."""
        from src.utils.logger import get_logger
        
        logger = get_logger('test_logger_2')
        assert logger.name == 'test_logger_2'
