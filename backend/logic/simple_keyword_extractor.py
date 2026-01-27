
import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash") # Updated to 2.0-flash as per nlu.py suggestion


# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "database", "question_situation100.json")

def load_questions():
    if not os.path.exists(JSON_PATH):
        print(f"Error: File not found at {JSON_PATH}")
        return []
    
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("questions", [])

def extract_keyword(query):
    prompt = f"""
    Context: A user is asking for a product in a store (e.g., Daiso).
    Task: Extract the core product keyword from the natural language query.
    Rules:
    - Return ONLY the product name (Korean).
    - If it's vague, infer the most likely product category.
    - Do not include polite phrases like "어디 있어요?" or "주세요".
    - Output strictly the noun.
    
    Query: "{query}"
    Keyword:
    """
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        latency = end_time - start_time
        
        keyword = response.text.strip()
        
        usage = response.usage_metadata
        prompt_tokens = usage.prompt_token_count
        candidates_tokens = usage.candidates_token_count
        total_tokens = usage.total_token_count

        return {
            "keyword": keyword,
            "latency": latency,
            "tokens": {
                "prompt": prompt_tokens,
                "completion": candidates_tokens,
                "total": total_tokens
            }
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    questions = load_questions()
    if not questions:
        return

    print(f"Loaded {len(questions)} questions.")
    print("-" * 50)
    
    output_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted_keywords_real_root.txt")
    print(f"Saving results to: {output_txt_path}")

    with open(output_txt_path, "w", encoding="utf-8") as f:
        for i, q in enumerate(questions):
            result = extract_keyword(q)
            
            if "error" in result:
                line = f"Q: {q} -> Error: {result['error']}"
            else:
                keyword = result["keyword"]
                latency = result["latency"]
                tokens = result["tokens"]
                
                # Format: Question -> Keyword (Latency: Xs, Tokens: [P:X, C:X, T:X])
                line = f"Q: {q} -> Keyword: {keyword}"
                meta_info = f"(Latency: {latency:.3f}s, Tokens: [P:{tokens['prompt']}, C:{tokens['completion']}, T:{tokens['total']}])"
                
                print(f"[{i+1}/{len(questions)}] {line} {meta_info}")
                f.write(f"{line} {meta_info}\n")
            
            f.flush() 

    print(f"\nAnalysis complete. Results saved to {output_txt_path}")

if __name__ == "__main__":
    main()
