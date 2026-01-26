
import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("Error: OPENAI_API_KEY not found in .env")
    exit(1)

# Configure OpenAI
client = OpenAI(api_key=api_key)
MODEL_NAME = "gpt-4o-mini"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "database", "question3.json")

def load_questions():
    if not os.path.exists(JSON_PATH):
        print(f"Error: File not found at {JSON_PATH}")
        return []
    
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

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
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts product keywords from queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        end_time = time.time()
        latency = end_time - start_time
        
        keyword = response.choices[0].message.content.strip()
        
        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        return {
            "keyword": keyword,
            "latency": latency,
            "tokens": {
                "prompt": prompt_tokens,
                "completion": completion_tokens,
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
    
    output_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted_keywords_openai.txt")
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
            # time.sleep(0.1)

    print(f"\nAnalysis complete. Results saved to {output_txt_path}")

if __name__ == "__main__":
    main()
