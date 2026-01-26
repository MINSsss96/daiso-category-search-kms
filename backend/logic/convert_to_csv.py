
import os
import re
import csv
import sys

# Use raw string with backslashes for Windows path consistency
base_dir = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic"
input_path = os.path.join(base_dir, 'comparison_report.txt')
output_path = os.path.join(base_dir, 'comparison_report.csv')

def parse_report(file_path):
    data = []
    current_entry = {}
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

    # Regex patterns
    start_pattern = re.compile(r'^\[(MATCH|MISMATCH|MISSING)\] Q:\s*(.*)')
    intention_pattern = re.compile(r'^\s*Intention:\s*(.*)')
    keyword_pattern = re.compile(r'^\s*Keyword:\s*(.*)')
    note_pattern = re.compile(r'^\s*Note:\s*(.*)')

    for line in lines:
        line = line.strip()
        
        match_start = start_pattern.match(line)
        if match_start:
            if current_entry:
                data.append(current_entry)
            
            status = match_start.group(1)
            question = match_start.group(2)
            current_entry = {
                'Status': status,
                'Question': question,
                'Intention': '',
                'Keyword': '',
                'Note': ''
            }
            continue

        if not current_entry:
            continue

        match_intention = intention_pattern.match(line)
        if match_intention:
            current_entry['Intention'] = match_intention.group(1)
            continue

        match_keyword = keyword_pattern.match(line)
        if match_keyword:
            current_entry['Keyword'] = match_keyword.group(1)
            continue

        match_note = note_pattern.match(line)
        if match_note:
            current_entry['Note'] = match_note.group(1)
            continue

    if current_entry:
        data.append(current_entry)

    return data

def save_to_csv(data, output_file):
    if not data:
        print("No data extracted.")
        return

    headers = ['Status', 'Question', 'Intention', 'Keyword', 'Note']
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"Successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    print(f"Processing {input_path}...")
    parsed_data = parse_report(input_path)
    print(f"Extracted {len(parsed_data)} entries.")
    save_to_csv(parsed_data, output_path)
