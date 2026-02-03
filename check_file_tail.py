
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "backend", "logic", "comparison_report_question3_openai.txt")

def main():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    print(f"Total lines: {len(lines)}")
    print(f"Total lines: {len(lines)}")
    
    matches = sum(1 for line in lines if line.strip().startswith("[MATCH] Q:"))
    print(f"Actual [MATCH] Q: tags in file: {matches}")
    
    mismatches = sum(1 for line in lines if line.strip().startswith("[MISMATCH] Q:"))
    print(f"Actual [MISMATCH] Q: tags in file: {mismatches}")
    
    print(f"Sum: {matches + mismatches}")
    
    print("Last 10 lines:")
    for line in lines[-10:]:
        print(line.strip())

if __name__ == "__main__":
    main()
