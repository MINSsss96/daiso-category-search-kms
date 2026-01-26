
import os
import json
import time
import ollama

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "database", "question3.json")

# Model Name (Make sure you have run 'ollama run llama3' in terminal at least once)
MODEL_NAME = "llama3" 

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
        
        response = ollama.chat(model=MODEL_NAME, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        
        end_time = time.time()
        latency = end_time - start_time
        
        keyword = response['message']['content'].strip()
        
        # Ollama returns token counts in response['eval_count'] and response['prompt_eval_count']
        # Note: keys might vary slightly by version, checking common response structure
        prompt_tokens = response.get('prompt_eval_count', 0)
        completion_tokens = response.get('eval_count', 0)
        total_tokens = prompt_tokens + completion_tokens

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
    print(f"Using Ollama model: {MODEL_NAME}")
    print("-" * 50)
    
    output_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted_keywords_ollama.txt")
    print(f"Saving results to: {output_txt_path}")

    with open(output_txt_path, "w", encoding="utf-8") as f:
        for i, q in enumerate(questions):
            result = extract_keyword(q)
            
            if "error" in result:
                line = f"Q: {q} -> Error: {result['error']}"
                print(f"[{i+1}/{len(questions)}] {line}")
                f.write(f"{line}\n")
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
