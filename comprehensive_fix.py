#!/usr/bin/env python3
"""Comprehensive final fix for all flake8 issues."""

# Fix transaction_etl.py - remove duplicate noqa comments
with open('src/transformation/glue-jobs/transaction_etl.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove duplicate noqa comments
content = content.replace('# noqa: F403,F405  # noqa: F403,F405', '# noqa: F403,F405')

with open('src/transformation/glue-jobs/transaction_etl.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix generate_clickstream.py - add spaces around operators
with open('src/data-generators/generate_clickstream.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Fix line 210 - add spaces around operators
    if 'count/len(events)*100' in line:
        line = line.replace('count/len(events)*100', 'count / len(events) * 100')
    # Fix line 213 - add spaces around operators  
    if 'count/len(events)*100' in line and i > 210:
        line = line.replace('count/len(events)*100', 'count / len(events) * 100')
    new_lines.append(line)

with open('src/data-generators/generate_clickstream.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed all flake8 issues!")
