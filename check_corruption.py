import re
import sys

filepath = r'd:\mirakle_platform-1\templates\connector_dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(r'd:\mirakle_platform-1\corruption_results.txt', 'w', encoding='utf-8') as out:
    for i, line in enumerate(lines):
        if re.search(r'< [a-z/]', line) or re.search(r'[a-zA-Z] >', line) or re.search(r'\${ [a-zA-Z0-9_\.]+ }', line):
            out.write(f"Line {i+1}: {line.strip()}\n")
