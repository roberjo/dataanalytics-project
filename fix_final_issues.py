#!/usr/bin/env python3
"""Fix whitespace issues in generate_reviews.py and suppress Glue warnings."""

# Fix generate_reviews.py - add spaces around operators
with open('src/data-generators/generate_reviews.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('verified/len(reviews)*100', 'verified / len(reviews) * 100')
content = content.replace('count/len(reviews)*100', 'count / len(reviews) * 100')

with open('src/data-generators/generate_reviews.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix transaction_etl.py - add noqa to line 175 specifically
with open('src/transformation/glue-jobs/transaction_etl.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines, 1):
    if i == 175 and 'DynamicFrame.fromDF' in line and 'noqa' not in line:
        # Add noqa comment to this specific line
        line = line.rstrip() + '  # noqa: F405\n'
    new_lines.append(line)

with open('src/transformation/glue-jobs/transaction_etl.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed all remaining issues!")
