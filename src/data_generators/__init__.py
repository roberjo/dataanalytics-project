"""
Alias package for data generators.
Provides direct imports from the hyphenated directory so tests can use
`src.data_generators.generate_transactions` etc.
"""
import os
import sys

# Add the hyphenated directory to sys.path
_module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data-generators'))
if _module_dir not in sys.path:
    sys.path.insert(0, _module_dir)

# Import generator classes
from generate_transactions import TransactionGenerator
from generate_products import ProductGenerator
from generate_clickstream import ClickstreamGenerator
from generate_reviews import ReviewGenerator

__all__ = [
    "TransactionGenerator",
    "ProductGenerator",
    "ClickstreamGenerator",
    "ReviewGenerator",
]
