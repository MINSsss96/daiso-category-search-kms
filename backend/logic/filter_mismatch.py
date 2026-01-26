
import os

base_dir = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic"
input_file = os.path.join(base_dir, 'comparison_report.txt')
output_file = os.path.join(base_dir, 'comparison_mismatch_report.txt')

print(f"Reading from {input_file}")
if not os.path.exists(input_file):
    print(f"Error: {input_file} not found.")
    exit(1)

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Read {len(lines)} lines.")
output_lines = []
recording = False

for line in lines:
    stripped = line.strip()
    if stripped.startswith('[MISMATCH]'):
        recording = True
        output_lines.append(line)
    elif stripped.startswith('[MATCH]'):
        recording = False
    elif stripped.startswith('==='):
        recording = False
    else:
        if recording:
            output_lines.append(line)

print(f"Found {len(output_lines)} mismatch lines.")

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    print(f"Successfully wrote to {output_file}")
except Exception as e:
    print(f"Error writing file: {e}")
