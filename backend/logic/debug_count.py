
import re
import os

FILE_PATH = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\comparison_report copy.txt"

def count_matches_and_keywords():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count [MATCH]
    matches = re.findall(r'\[MATCH\]', content)
    total_matches = len(matches)

    # Extract Keywords from [MATCH] blocks
    # Looking for: [MATCH] ... Keyword: <value> ...
    # We strip whitespace to handle duplicates like "용기" vs "용기 "
    keywords = []
    
    # Split by double newline to separate blocks roughly
    blocks = re.split(r'\n\s*\n', content)
    for block in blocks:
        if "[MATCH]" in block:
            # Extract Keyword line
            match_kw = re.search(r'Keyword:\s*(.+)', block)
            if match_kw:
                kw = match_kw.group(1).strip()
                keywords.append(kw)
    
    unique_keywords = set(keywords)

    print(f"File: {os.path.basename(FILE_PATH)}")
    print(f"Total '[MATCH]' occurrences: {total_matches}")
    print(f"Total Keywords found in MATCH blocks: {len(keywords)}")
    print(f"Total Unique Keywords (Deduplicated): {len(unique_keywords)}")
    
    # Optional: Print duplicates to be sure
    if len(keywords) != len(unique_keywords):
        print(f"Duplicates removed: {len(keywords) - len(unique_keywords)}")

if __name__ == "__main__":
    count_matches_and_keywords()
