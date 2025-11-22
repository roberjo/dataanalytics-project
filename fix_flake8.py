#!/usr/bin/env python3
"""Fix flake8 issues in source files."""

import re

# Fix generate_reviews.py
with open('src/data-generators/generate_reviews.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('print(f"  Rating distribution:")', 'print("  Rating distribution:")')

with open('src/data-generators/generate_reviews.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix data_generators/__init__.py - move imports to top
with open('src/data_generators/__init__.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Rewrite the file with imports at top
new_content = '''"""
Alias package for data generators.
Provides direct imports from the hyphenated directory so tests can use
`src.data_generators.generate_transactions` etc.
"""
import os
import sys

# Add the hyphenated directory to sys.path
_module_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data-generators")
)
if _module_dir not in sys.path:
    sys.path.insert(0, _module_dir)

# Import generator classes
from generate_transactions import TransactionGenerator  # noqa: E402
from generate_products import ProductGenerator  # noqa: E402
from generate_clickstream import ClickstreamGenerator  # noqa: E402
from generate_reviews import ReviewGenerator  # noqa: E402

__all__ = [
    "TransactionGenerator",
    "ProductGenerator",
    "ClickstreamGenerator",
    "ReviewGenerator",
]
'''

with open('src/data_generators/__init__.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

# Fix file_validator.py - remove unused import
with open('src/ingestion/file_validator.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'from typing import List' not in line or 'Dict' in line:
        new_lines.append(line)

with open('src/ingestion/file_validator.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Fix transaction_etl.py - remove unused import and add noqa comments
with open('src/transformation/glue-jobs/transaction_etl.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove unused datetime import
content = content.replace('from datetime import datetime\n', '')
# Add noqa comments for star imports
content = content.replace(
    'from awsglue.transforms import *',
    'from awsglue.transforms import *  # noqa: F403,F405'
)
content = content.replace(
    'from pyspark.sql.types import *',
    'from pyspark.sql.types import *  # noqa: F403,F405'
)

with open('src/transformation/glue-jobs/transaction_etl.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix data_quality_check.py files - remove unused import and trailing whitespace
for path in ['src/transformation/lambda-functions/data_quality_check.py',
             'src/transformation/lambda_functions/data_quality_check.py']:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            # Skip unused timedelta import
            if 'from datetime import datetime, timedelta' in line:
                new_lines.append('from datetime import datetime\n')
            else:
                # Remove trailing whitespace
                new_lines.append(line.rstrip() + '\n' if line.strip() else '\n')
        
        # Fix long lines
        content = ''.join(new_lines)
        content = content.replace(
            "f'Null percentage {null_pct:.2%} exceeds threshold {max_null_pct:.2%}'",
            "(\n                        f'Null percentage {null_pct:.2%} exceeds '\n"
            "                        f'threshold {max_null_pct:.2%}'\n                    )"
        )
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except FileNotFoundError:
        pass

print("Fixed all flake8 issues!")
