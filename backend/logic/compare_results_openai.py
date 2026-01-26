
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load Env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not set")
    exit(1)

client = OpenAI(api_key=api_key)
MODEL_NAME = "gpt-4o-mini"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTENTION_FILE = os.path.join(BASE_DIR, "database", "question_intention.json")
KEYWORDS_FILE = os.path.join(BASE_DIR, "logic", "extracted_keywords_openai.txt") # Use OpenAI extracted keywords
OUTPUT_FILE = os.path.join(BASE_DIR, "logic", "comparison_report_openai.txt") # Output to a separate file

def load_extracted_keywords():
    mapping = {}
    if not os.path.exists(KEYWORDS_FILE):
        print(f"Keywords file not found at {KEYWORDS_FILE}")
        return mapping
        
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            # Format: Q: ... -> Keyword: ...
            if "-> Keyword:" in line:
                # Remove metric info if present
                clean_line = line.split("(Latency:")[0].strip()
                
                parts = clean_line.split("-> Keyword:")
                if len(parts) >= 2:
                    q = parts[0].replace("Q: ", "").strip()
                    k = parts[1].strip()
                    mapping[q] = k
    return mapping

def load_intentions():
    with open(INTENTION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_match(question, intention, keyword):
    try:
        prompt = f"""
        Task: Evaluate if the Extracted Keyword matches the User Intention for a given Question.
        
        Question: "{question}"
        Target Intention: "{intention}"
        Extracted Keyword: "{keyword}"
        
        Is this keyword a reasonably good search term to fulfill the intention?
        - If the keyword helps find the product described in the intention, say MATCH.
        - If the keyword is wrong or irrelevant, say MISMATCH.
        
        Output format: MATCH | <Reasoning> or MISMATCH | <Reasoning>
        """
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant evaluating keyword extraction quality."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR | {e}"

def main():
    print("Loading data...")
    intentions = load_intentions()
    extracted_map = load_extracted_keywords()
    
    if not extracted_map:
        print("No extracted keywords found to compare.")
        return

    results = []
    match_count = 0
    total_count = 0
    
    print(f"Comparing {len(intentions)} items...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== Keyword Extraction Evaluation (OpenAI) ===\n\n")
        
        for item in intentions:
            q = item["question"]
            target = item["intention"]
            
            # Simple normalization for matching keys
            keyword = extracted_map.get(q)
            
            if not keyword:
                # Try finding key that contains this question text
                for k, v in extracted_map.items():
                    if q in k or k in q:
                        keyword = v
                        break
            
            if not keyword:
                f.write(f"[MISSING] Q: {q}\n  Intention: {target}\n  -> No extracted keyword found.\n\n")
                continue
                
            total_count += 1
            evaluation = evaluate_match(q, target, keyword)
            
            status = "UNKNOWN"
            if evaluation.startswith("MATCH"):
                status = "MATCH"
                match_count += 1
            elif evaluation.startswith("MISMATCH"):
                status = "MISMATCH"
            
            result_str = f"[{status}] Q: {q}\n  Intention: {target}\n  Keyword: {keyword}\n  Note: {evaluation}\n"
            print(f"[{total_count}] {status} : {q[:20]}... -> {keyword}")
            f.write(result_str + "\n")
            f.flush()

        if total_count > 0:
            summary = f"\n=== SUMMARY ===\nTotal Evaluated: {total_count}\nMatches: {match_count}\nAccuracy: {match_count/total_count*100:.1f}%\n"
            f.write(summary)
            print(summary)
        else:
            print("No items evaluated.")

if __name__ == "__main__":
    main()
