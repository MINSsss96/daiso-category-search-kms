
import os

base_dir = r"c:/Users/301/dev/daiso-category-search-kms/backend/logic"
input_path = os.path.join(base_dir, 'comparison_report.txt')
output_path = os.path.join(base_dir, 'comparison_mismatch_report.txt')

print(f"Reading {input_path}")
try:
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except FileNotFoundError:
    print("File not found!")
    exit(1)

mismatches = []
recording = False
for line in lines:
    stripped = line.strip()
    if stripped.startswith('[MISMATCH]'):
        recording = True
        mismatches.append(line)
    elif stripped.startswith('[MATCH]'):
        recording = False
    elif stripped.startswith('==='): # Header or footer
        recording = False
    else:
        if recording:
            mismatches.append(line)

print(f"Found {len(mismatches)} mismatch lines.")

with open(output_path, 'w', encoding='utf-8') as f:
    f.writelines(mismatches)

print(f"Wrote to {output_path}")
