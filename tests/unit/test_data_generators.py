"""
Unit tests for data generators.
"""
import pytest
import csv
import json
from pathlib import Path
import tempfile
import os


@pytest.mark.unit
class TestTransactionGenerator:
    """Test transaction data generator."""
    
    def test_generate_transactions(self):
        """Test generating transaction data."""
        import sys
        import os
        # Add data-generators directory to path
        data_gen_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'data-generators')
        if data_gen_path not in sys.path:
            sys.path.insert(0, data_gen_path)
        
        from generate_transactions import TransactionGenerator
        
        generator = TransactionGenerator(num_customers=10, num_products=5)
        
        # Generate a small dataset
        from datetime import datetime
        transactions = generator.generate_transactions(100, datetime.now())
        
        # Verify count
        assert len(transactions) == 100
        
        # Verify structure
        required_fields = [
            'transaction_id', 'customer_id', 'product_id', 'quantity',
            'price', 'total_amount', 'transaction_date', 'status'
        ]
        for txn in transactions[:5]:  # Check first 5
            for field in required_fields:
                assert field in txn
            
            # Verify data types and constraints
            assert txn['quantity'] > 0
            assert txn['price'] > 0
            assert txn['total_amount'] > 0
            assert txn['status'] in ['completed', 'returned', 'refunded']
    
    def test_save_to_csv(self):
        """Test saving transactions to CSV."""
        import sys
        import os
        data_gen_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'data-generators')
        if data_gen_path not in sys.path:
            sys.path.insert(0, data_gen_path)
        from generate_transactions import TransactionGenerator
        from datetime import datetime
        
        generator = TransactionGenerator(num_customers=5, num_products=3)
        transactions = generator.generate_transactions(10, datetime.now())
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            generator.save_to_csv(transactions, Path(temp_file))
            
            # Verify file exists and has content
            assert os.path.exists(temp_file)
            assert os.path.getsize(temp_file) > 0
            
            # Verify CSV structure
            with open(temp_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 10
        finally:
            os.unlink(temp_file)


@pytest.mark.unit
class TestProductGenerator:
    """Test product data generator."""
    
    def test_generate_products(self):
        """Test generating product data."""
        import sys
        import os
        data_gen_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'data-generators')
        if data_gen_path not in sys.path:
            sys.path.insert(0, data_gen_path)
        from generate_products import ProductGenerator
        
        generator = ProductGenerator()
        products = generator.generate_products(50)
        
        # Verify count
        assert len(products) == 50
        
        # Verify structure
        required_fields = ['product_id', 'name', 'category', 'brand', 'price', 'stock']
        for product in products[:5]:
            for field in required_fields:
                assert field in product
            
            # Verify constraints
            assert product['price'] > 0
            assert product['stock'] >= 0
    
    def test_save_to_json(self):
        """Test saving products to JSON."""
        import sys
        import os
        data_gen_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'data-generators')
        if data_gen_path not in sys.path:
            sys.path.insert(0, data_gen_path)
        from generate_products import ProductGenerator
        
        generator = ProductGenerator()
        products = generator.generate_products(10)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            generator.save_to_json(products, Path(temp_file))
            
            # Verify file exists
            assert os.path.exists(temp_file)
            
            # Verify JSON structure (newline-delimited)
            with open(temp_file, 'r') as f:
                lines = f.readlines()
                assert len(lines) == 10
                
                # Verify each line is valid JSON
                for line in lines:
                    product = json.loads(line)
                    assert 'product_id' in product
        finally:
            os.unlink(temp_file)


@pytest.mark.unit
class TestClickstreamGenerator:
    """Test clickstream data generator."""
    
    def test_generate_session_events(self):
        """Test generating session events."""
        import sys
        import os
        data_gen_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'data-generators')
        if data_gen_path not in sys.path:
            sys.path.insert(0, data_gen_path)
        from generate_clickstream import ClickstreamGenerator
        from datetime import datetime
        
        generator = ClickstreamGenerator(num_customers=10, num_products=5)
        events = generator.generate_session_events(
            'sess_001', 'cust_001', datetime.now()
        )
        
        # Verify events were generated
        assert len(events) >= 3
        
        # Verify structure
        for event in events:
            assert 'session_id' in event
            assert 'event_type' in event
            assert 'timestamp' in event
            assert event['session_id'] == 'sess_001'


@pytest.mark.unit
class TestReviewGenerator:
    """Test review data generator."""
    
    def test_generate_review(self):
        """Test generating a single review."""
        import sys
        import os
        data_gen_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'data-generators')
        if data_gen_path not in sys.path:
            sys.path.insert(0, data_gen_path)
        from generate_reviews import ReviewGenerator
        from datetime import datetime
        
        generator = ReviewGenerator(num_customers=10, num_products=5)
        review = generator.generate_review(1, datetime.now())
        
        # Verify structure
        required_fields = [
            'review_id', 'product_id', 'customer_id', 'rating',
            'review_text', 'review_date'
        ]
        for field in required_fields:
            assert field in review
        
        # Verify constraints
        assert 1 <= review['rating'] <= 5
        assert review['helpful_votes'] >= 0
