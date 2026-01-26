
import os
import re
import sys
import subprocess

# Ensure pandas and openpyxl are installed
try:
    import pandas as pd
except ImportError:
    print("pandas not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
    import pandas as pd

try:
    import openpyxl
except ImportError:
    print("openpyxl not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl

base_dir = r"c:/Users/301/dev/daiso-category-search-kms/backend/logic"
input_path = os.path.join(base_dir, 'comparison_report.txt')
output_path = os.path.join(base_dir, 'comparison_report.xlsx')

def parse_report(file_path):
    data = []
    current_entry = {}
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Regex patterns
    # [MATCH] Q: question text
    start_pattern = re.compile(r'^\[(MATCH|MISMATCH|MISSING)\] Q:\s*(.*)')
    intention_pattern = re.compile(r'^\s*Intention:\s*(.*)')
    keyword_pattern = re.compile(r'^\s*Keyword:\s*(.*)')
    note_pattern = re.compile(r'^\s*Note:\s*(.*)')

    for line in lines:
        line = line.strip()
        
        # Start of new entry
        match_start = start_pattern.match(line)
        if match_start:
            # Save previous entry if exists
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

        # Check for other fields
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

    # Add the last entry
    if current_entry:
        data.append(current_entry)

    return data

def save_to_excel(data, output_file):
    if not data:
        print("No data extracted.")
        return

    df = pd.DataFrame(data)
    
    # Reorder columns if needed
    columns = ['Status', 'Question', 'Intention', 'Keyword', 'Note']
    # Ensure all columns exist
    for col in columns:
        if col not in df.columns:
            df[col] = ''
    
    df = df[columns]

    try:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"Successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")

if __name__ == "__main__":
    print(f"Processing {input_path}...")
    parsed_data = parse_report(input_path)
    print(f"Extracted {len(parsed_data)} entries.")
    save_to_excel(parsed_data, output_path)
