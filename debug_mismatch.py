
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTION_FILE = os.path.join(BASE_DIR, "backend", "database", "question_situation100_intention.json")
KEYWORDS_FILE = os.path.join(BASE_DIR, "backend", "logic", "extracted_keywords_question_situation100_openai.txt")

def load_intentions():
    with open(INTENTION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        return data.get("questions", [])

def load_keywords():
    mapping = {}
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "-> Keyword:" in line:
                clean_line = line.split("(Latency:")[0].strip()
                parts = clean_line.split("-> Keyword:")
                if len(parts) >= 2:
                    q = parts[0].replace("Q: ", "").strip()
                    mapping[q] = parts[1].strip()
    return mapping

def main():
    intentions = load_intentions()
    keywords = load_keywords()
    
    print(f"Loaded {len(intentions)} intentions")
    print(f"Loaded {len(keywords)} keywords")
    
    matches = 0
    mismatches = 0
    
    for item in intentions:
        q = item.get("question", "")
        if q in keywords:
            matches += 1
        else:
            mismatches += 1
            print(f"MISSING: '{q}'")
            # Try to find close match
            for k in keywords:
                if q == k:
                    print(f"  Exact match found in keys! (What?)")
                if q.strip() == k.strip():
                     print(f"  Strip match found! '{k}'")
                elif q in k:
                    print(f"  Substring match (q in k): '{k}'")
                elif k in q:
                    print(f"  Substring match (k in q): '{k}'")
                
                # Check char codes for first failing one
                if mismatches == 1:
                    print(f"  Comparing first mismatch detailed:")
                    print(f"  Intention: {[ord(c) for c in q]}")
                    # Find the corresponding line in keywords roughly
                    # We know they SHOULD be in same order mostly
                    pass

    print(f"Total Matches: {matches}")
    print(f"Total Mismatches: {mismatches}")

if __name__ == "__main__":
    main()
