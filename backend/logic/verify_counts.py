import csv
import sys

csv_path = r'c:\Users\301\dev\daiso-category-search-kms\backend\logic\comparison_report_openai.csv'

try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        total = 0
        matches = 0
        mismatches = 0
        others = 0
        
        for row in reader:
            total += 1
            status = row.get('Status', '').strip().upper()
            if status == 'MATCH':
                matches += 1
            elif status == 'MISMATCH':
                mismatches += 1
            else:
                others += 1
                
        with open('verify_counts_result.txt', 'w') as out_f:
            out_f.write(f"Total rows: {total}\n")
            out_f.write(f"Matches: {matches}\n")
            out_f.write(f"Mismatches: {mismatches}\n")
            out_f.write(f"Others: {others}\n")
            
            if total > 0:
                accuracy = (matches / total) * 100
                out_f.write(f"Calculated Accuracy: {accuracy:.2f}%\n")
            else:
                out_f.write("No data found.\n")

except Exception as e:
    with open('verify_counts_result.txt', 'w') as out_f:
        out_f.write(f"Error: {e}\n")
