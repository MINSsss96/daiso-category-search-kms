
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
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    questions = load_questions()
    if not questions:
        return

    print(f"Loaded {len(questions)} questions.")
    print("-" * 50)
    
    # Process only first 5 for testing to avoid wait/cost limits in this run, 
    # or process all if user wants. The prompt implied "Program to do it", 
    # so I will set it to process all but maybe with a small sleep to be safe? 
    # 1.5 Flash is fast/cheap. Let's do a subset first or stream them.
    # User said "make a program", so it should work for the file.
    
    output_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted_keywords.txt")
    print(f"Saving results to: {output_txt_path}")

    with open(output_txt_path, "w", encoding="utf-8") as f:
        for i, q in enumerate(questions):
            keyword = extract_keyword(q)
            # Format: Question -> Keyword
            line = f"Q: {q} -> Keyword: {keyword}"
            print(f"[{i+1}/{len(questions)}] {line}")
            f.write(line + "\n")
            f.flush() 

    print(f"\nAnalysis complete. Results saved to {output_txt_path}")

if __name__ == "__main__":
    main()
