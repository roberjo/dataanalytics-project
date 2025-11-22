"""
Unit tests for S3 helper utilities.
"""
import pytest
from src.utils.s3_helper import S3Helper


@pytest.mark.unit
class TestS3Helper:
    """Test S3Helper class."""
    
    def test_upload_file(self, s3_client):
        """Test file upload to S3."""
        # Create bucket
        bucket_name = 'test-bucket'
        s3_client.create_bucket(Bucket=bucket_name)
        
        # Create helper
        helper = S3Helper()
        
        # Create a test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('test content')
            temp_file = f.name
        
        # Upload file
        result = helper.upload_file(temp_file, bucket_name, 'test.txt')
        
        # Verify
        assert result is True
        
        # Check file exists
        response = s3_client.head_object(Bucket=bucket_name, Key='test.txt')
        assert response['ContentLength'] > 0
        
        # Cleanup
        import os
        os.unlink(temp_file)
    
    def test_object_exists(self, s3_client):
        """Test checking if object exists."""
        bucket_name = 'test-bucket'
        s3_client.create_bucket(Bucket=bucket_name)
        
        # Put an object
        s3_client.put_object(Bucket=bucket_name, Key='test.txt', Body=b'test')
        
        helper = S3Helper()
        
        # Test existing object
        assert helper.object_exists(bucket_name, 'test.txt') is True
        
        # Test non-existing object
        assert helper.object_exists(bucket_name, 'nonexistent.txt') is False
    
    def test_list_objects(self, s3_client):
        """Test listing objects in bucket."""
        bucket_name = 'test-bucket'
        s3_client.create_bucket(Bucket=bucket_name)
        
        # Put multiple objects
        s3_client.put_object(Bucket=bucket_name, Key='prefix/file1.txt', Body=b'test1')
        s3_client.put_object(Bucket=bucket_name, Key='prefix/file2.txt', Body=b'test2')
        s3_client.put_object(Bucket=bucket_name, Key='other/file3.txt', Body=b'test3')
        
        helper = S3Helper()
        
        # List with prefix
        objects = helper.list_objects(bucket_name, 'prefix/')
        assert len(objects) == 2
        
        # List all
        objects = helper.list_objects(bucket_name)
        assert len(objects) == 3
