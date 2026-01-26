
import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load Env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # Try getting from environment if not in .env (though load_dotenv should handle it)
    pass

if not api_key:
    print("Error: OPENAI_API_KEY not set")
    # It's possible the user wants to use Gemini for evaluation like compare_results.py, 
    # but since they referenced comparison_report_openai.txt, I'll stick to OpenAI for the evaluator 
    # to maintain "Judge" consistency with that report format.
    exit(1)

client = OpenAI(api_key=api_key)
MODEL_NAME = "gpt-4o-mini"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTENTION_FILE = os.path.join(BASE_DIR, "database", "question_intention.json")
KEYWORDS_FILE = os.path.join(BASE_DIR, "logic", "extracted_keywords_ollama.txt") # Llama results
OUTPUT_FILE = os.path.join(BASE_DIR, "logic", "comparison_report_llama.txt")

def load_extracted_keywords():
    mapping = {}
    if not os.path.exists(KEYWORDS_FILE):
        print(f"Keywords file not found at {KEYWORDS_FILE}")
        return mapping
        
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading keywords file: {e}")
        return mapping

    # Split content by "Q: " to isolate entries. 
    # Use regex to find "Q: " at line start or file start
    entries = re.split(r'(?:\n|^)Q: ', content)
    
    for entry in entries:
        if not entry.strip():
            continue
            
        # Format: <Question> -> Keyword: <Verbose Text> (Latency: ...)
        if "-> Keyword:" not in entry:
            continue
            
        try:
            # unique separator
            parts = entry.split("-> Keyword:", 1)
            q_part = parts[0].strip()
            k_part_raw = parts[1].strip()
            
            # Remove Latency info from the end
            # Look for "(Latency:" to split
            if "(Latency:" in k_part_raw:
                k_clean = k_part_raw.rsplit("(Latency:", 1)[0].strip()
            else:
                k_clean = k_part_raw
            
            # Additional cleanup of tokens info if somehow latency missing but tokens present?
            # Start of line parsing
            
            mapping[q_part] = k_clean
            
        except Exception as e:
            print(f"Error parsing entry: {entry[:50]}... {e}")
            continue
            
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
        - The Extracted Keyword might be verbose or contain explanation. Look for the core product name inside it.
        
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
    print("Starting main execution...")
    try:
        print("Loading intentions...")
        intentions = load_intentions()
        print(f"Loaded {len(intentions)} intentions.")
        
        print("Loading extracted keywords...")
        extracted_map = load_extracted_keywords()
        print(f"Loaded {len(extracted_map)} extracted keywords.")

        # Debug: Log first 5 extracted keys
        keys = list(extracted_map.keys())[:5]
        for k in keys:
            print(f"Key: {k} -> Val: {extracted_map[k]}")
        
        if not extracted_map:
            print("No extracted keywords found to compare.")
            return

        match_count = 0
        total_count = 0
        
        print(f"Comparing {len(intentions)} items...")
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("=== Keyword Extraction Evaluation (Llama) ===\n\n")
            
            for i, item in enumerate(intentions):
                q = item["question"]
                target = item["intention"]
                
                keyword = extracted_map.get(q)
                
                if not keyword:
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
                
                # Print progress
                print(f"[{total_count}] {status} : {q[:20]}...")
                
                f.write(result_str + "\n")
                f.flush()

            if total_count > 0:
                summary = f"\n=== SUMMARY ===\nTotal Evaluated: {total_count}\nMatches: {match_count}\nAccuracy: {match_count/total_count*100:.1f}%\n"
                f.write(summary)
                print(summary)
            else:
                print("No items evaluated.")
                
        print("Execution finished successfully.")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
