
import json
import os
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTION_FILE = os.path.join(BASE_DIR, "backend", "database", "question_situation100_intention.json")
KEYWORDS_FILE = os.path.join(BASE_DIR, "backend", "logic", "extracted_keywords_question_situation100_llama.txt")

def normalize(text):
    return unicodedata.normalize('NFC', text).strip()

def main():
    # Load Intentions (JSON)
    with open(INTENTION_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        questions_json = []
        if isinstance(data, list):
            for item in data:
                q = item.get("question") or item.get("query")
                if q: questions_json.append(normalize(q))
        else:
            for item in data.get("questions", []):
                q = item.get("question") or item.get("query")
                if q: questions_json.append(normalize(q))
    
    # Load Keywords (TXT)
    questions_txt = []
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if "-> Keyword:" in line:
                clean_line = line.split("(Latency:")[0].strip()
                parts = clean_line.split("-> Keyword:")
                if len(parts) >= 2:
                    q = parts[0].replace("Q: ", "").strip()
                    questions_txt.append(normalize(q))
                    
    print(f"JSON Questions: {len(questions_json)}")
    print(f"TXT Questions: {len(questions_txt)}")
    
    set_json = set(questions_json)
    set_txt = set(questions_txt)
    
    missing_in_txt = set_json - set_txt
    missing_in_json = set_txt - set_json
    
    print(f"Missing in TXT (Not extracted): {len(missing_in_txt)}")
    for q in list(missing_in_txt)[:5]:
        print(f" - '{q}'")
        
    print(f"Missing in JSON (Extracted but not in DB?): {len(missing_in_json)}")
    for q in list(missing_in_json)[:5]:
        print(f" - '{q}'")
        
    # Check for near matches
    if missing_in_txt:
        print("\nChecking for near matches:")
        sample = list(missing_in_txt)[0]
        print(f"Sample missing: '{sample}'")
        for q_txt in questions_txt:
            if sample in q_txt or q_txt in sample:
                print(f" -> Found partial match in TXT: '{q_txt}'")
            # checking common punctuation differences?
            if sample.replace("?", "") == q_txt.replace("?", ""):
                 print(f" -> Found punctuation match in TXT: '{q_txt}'")

if __name__ == "__main__":
    main()
