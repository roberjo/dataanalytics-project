#!/usr/bin/env python3
"""Add noqa comments to suppress expected flake8 warnings."""

# Fix clickstream - the variable is already commented out, just need to verify
with open('src/data-generators/generate_clickstream.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Verify the variable is commented
if '# session_duration' not in content:
    content = content.replace(
        'session_duration = random.randint(60, 1800)',
        '# session_duration = random.randint(60, 1800)  # noqa: F841'
    )
    with open('src/data-generators/generate_clickstream.py', 'w', encoding='utf-8') as f:
        f.write(content)

# Fix Glue job - star imports are required for Glue
with open('src/transformation/glue-jobs/transaction_etl.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'from awsglue.transforms import *' in line and 'noqa' not in line:
        new_lines.append('from awsglue.transforms import *  # noqa: F403,F405\n')
    elif 'from pyspark.sql.types import *' in line and 'noqa' not in line:
        new_lines.append('from pyspark.sql.types import *  # noqa: F403,F405\n')
    else:
        new_lines.append(line)

with open('src/transformation/glue-jobs/transaction_etl.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Added noqa comments for expected warnings!")
