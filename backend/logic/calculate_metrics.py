
import re
import os

FILE_PATH = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\extracted_keywords_ollama copy.txt"

def calculate_metrics():
    total_latency = 0.0
    total_tokens = 0
    item_count = 0
    
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                
                # Check for stats line
                lat_match = re.search(r'Latency:\s*([\d\.]+)s', line)
                tok_match = re.search(r'T:(\d+)', line)
                
                if lat_match and tok_match:
                    total_latency += float(lat_match.group(1))
                    total_tokens += int(tok_match.group(1))
                    item_count += 1
                
        print(f"Total Items (Queries): {item_count}")
        print(f"Total Latency: {total_latency:.4f}s")
        print(f"Total Tokens: {total_tokens}")
        if item_count > 0:
            print(f"Avg Latency: {total_latency/item_count:.4f}s")
            print(f"Avg Tokens: {total_tokens/item_count:.1f}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    calculate_metrics()
