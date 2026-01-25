import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "question_ intention.py") # Note spacing in filename
OUTPUT_FILE = os.path.join(BASE_DIR, "question_intention.json")

# Re-run strictly for the specific file structure observed
# The file has mixed blocks. Let's restart the logic cleanly below.

def notLineStartsWithArrow(l):
    return not l.startswith("→")

def convert_robust():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found")
        return

    data = []
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        # Read all, keep empty lines to detect blocks if needed, but simplest is to filter
        raw_lines = f.readlines()

    clean_lines = [l.strip() for l in raw_lines if l.strip()]
    
    i = 0
    while i < len(clean_lines):
        line = clean_lines[i]
        
        # Check if this line is a question or intention start
        # Format 1: Next line starts with →
        if i + 1 < len(clean_lines) and clean_lines[i+1].startswith("→"):
            question = line
            intention = clean_lines[i+1].replace("→", "").strip()
            data.append({"question": question, "intention": intention})
            i += 2
            continue
            
        # Format 2: Next line starts with "의도:"
        if i + 1 < len(clean_lines) and clean_lines[i+1].startswith("의도:"):
            question = line.replace('"', "").strip() # Remove surrounding quotes common in Format 2
            intention = clean_lines[i+1].replace("의도:", "").strip()
            data.append({"question": question, "intention": intention})
            i += 2
            continue

        # If neither, it might be a dangling line or comment
        i += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Converted {len(data)} items to {OUTPUT_FILE}")

if __name__ == "__main__":
    convert_robust()
