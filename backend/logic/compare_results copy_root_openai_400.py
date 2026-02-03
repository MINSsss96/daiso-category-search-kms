
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from openai import OpenAI
import unicodedata

# Load Env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # Try getting it from the user's previously mentioned pattern or just warn
    print("Error: OPENAI_API_KEY not found in .env")
    exit(1)

client = OpenAI(api_key=api_key)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTENTION_FILE = os.path.join(BASE_DIR, "database", "question_intention.json")
KEYWORDS_FILE = os.path.join(BASE_DIR, "logic", "extracted_keywords_question3_openai.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "logic", "comparison_report_question3_openai.txt")

def load_extracted_keywords():
    mapping = {}
    if not os.path.exists(KEYWORDS_FILE):
        return mapping
        
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            # Format: Q: ... -> Keyword: ... (Latency: ...)
            if "-> Keyword:" in line:
                # Remove metric info if present
                clean_line = line.split("(Latency:")[0].strip()
                
                parts = clean_line.split("-> Keyword:")
                if len(parts) >= 2:
                    q = parts[0].replace("Q: ", "").strip()
                    q = unicodedata.normalize('NFC', q)
                    k = parts[1].strip()
                    mapping[q] = k
    print(f"Loaded {len(mapping)} keywords from file.")
    return mapping

def load_intentions():
    with open(INTENTION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        return data.get("questions", [])

def evaluate_match(question, intention, keyword):
    try:
        prompt = f"""
        Role: You are a judge evaluating search keywords for Daiso products.
        Task: Determine if the 'Extracted Keyword' is a valid search term for the 'Target Intention'.

        [Daiso Knowledge Base]
        - **Monster Clear Gel (몬스터클리어젤)**: A strong, residue-free double-sided adhesive gel tape. Matches "Remove residue", "Strong fixation".
        - **Kkokkopin (꼭꼬핀)**: A hook for wallpaper that doesn't leave needle marks. Matches "Wall hook", "No trace".
        - **Magic Block (매직블럭)**: A melamine sponge for cleaning. Matches "Cleaner", "Stain remover".
        - **Diatomaceous Earth Mat (규조토발매트)**: A hard, stone-like bath mat that dries instantly. Matches "Quick dry", "Mat".
        - **Door Stopper (도어스토퍼)**: Prevents door slamming. Matches "Noise reduction", "Door safety".

        [Evaluation Rules]
        1. **Specific is Good**: If the User Intention is generic but the Keyword is a specific product from the Knowledge Base (or similar), it IS A MATCH.
        2. **Category Consistency**: If the Keyword is a totally different category (e.g., "Scrubber" for "Mat"), it is a MISMATCH.
        3. **Function over Form**: If the keyword solves the *core problem* described in the intention, it is a MATCH.

        [Input]
        Question: "{question}"
        Target Intention: "{intention}"
        Extracted Keyword: "{keyword}"
        
        Is this keyword a reasonably good search term to fulfill the intention?
        - If the keyword helps find the product described in the intention, say MATCH.
        - If the keyword is wrong or irrelevant, say MISMATCH.
        
        Output format: MATCH | <Reasoning> or MISMATCH | <Reasoning>
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR | {e}"

def main():
    print("Loading data...")
    intentions = load_intentions()
    extracted_map = load_extracted_keywords()
    
    results = []
    match_count = 0
    total_count = 0
    
    print(f"Comparing {len(intentions)} items...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== Keyword Extraction Evaluation ===\n\n")
        
        for item in intentions:
            q = item["question"]
            q = unicodedata.normalize('NFC', q)
            target = item["intention"]
            
            # Simple normalization for matching keys
            # Extracted keys might differ slightly in whitespace or quotes
            # We try exact match first
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

        summary = f"\n=== SUMMARY ===\nTotal Evaluated: {total_count}\nMatches: {match_count}\nAccuracy: {match_count/total_count*100:.1f}%\n"
        f.write(summary)
        print(summary)

if __name__ == "__main__":
    main()
