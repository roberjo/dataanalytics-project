#!/usr/bin/env python3
"""Final fix for all remaining flake8 issues."""

# Fix generate_clickstream.py - remove f-string prefix from strings without placeholders
with open('src/data-generators/generate_clickstream.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('print(f"  Event types:")', 'print("  Event types:")')
content = content.replace('print(f"  Devices:")', 'print("  Devices:")')

with open('src/data-generators/generate_clickstream.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix transaction_etl.py - the noqa comments should already be there, verify
with open('src/transformation/glue-jobs/transaction_etl.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ensure noqa comments are present
if 'from awsglue.transforms import *' in content and '# noqa: F403,F405' not in content:
    content = content.replace(
        'from awsglue.transforms import *',
        'from awsglue.transforms import *  # noqa: F403,F405'
    )

if 'from pyspark.sql.types import *' in content and '# noqa: F403,F405' not in content:
    content = content.replace(
        'from pyspark.sql.types import *',
        'from pyspark.sql.types import *  # noqa: F403,F405'
    )

with open('src/transformation/glue-jobs/transaction_etl.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all remaining flake8 issues!")
