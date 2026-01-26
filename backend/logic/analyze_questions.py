
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from collections import defaultdict
import time
import sys

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "database", "question3.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "logic", "question_analysis_report.txt")

def load_questions():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def classify_question_batch(questions):
    # Process in batches to reduce API calls
    prompt = """
    You are an expert data analyst.
    Classify the following user questions into one of these categories:
    
    1. **Description/Feature (특징/묘사 기반)**: Describing the product's appearance, material, or specific feature without knowing the exact name (e.g., "red thing", "sticky stuff", "round object").
    2. **Problem Solution (문제 해결/니즈 기반)**: Describing a problem to solve or a need (e.g., "stop door banging", "prevent slipping", "organize cables").
    3. **Usage/Context (사용 상황/맥락 기반)**: Describing when or where it is used (e.g., "for camping", "bathroom usage", "travel essential").
    4. **Direct Product (직접 검색)**: Asking for a specific product name (e.g., "Where is the tape?", "Do you have AA batteries?").
    5. **Part/Refill (부품/리필)**: Asking for specific parts, refills, or accessories (e.g., "refill for smooth pen", "lid for this box").
    
    Return the result as a JSON object where typical keys are the questions and values are the categories.
    Format example:
    {
        "question text": "Category Name",
        ...
    }
    
    Questions to classify:
    """
    
    formatted_questions = json.dumps(questions, ensure_ascii=False)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful classifier."},
                {"role": "user", "content": prompt + "\n" + formatted_questions}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return {}

def main():
    questions = load_questions()
    print(f"Total questions: {len(questions)}", flush=True)
    
    batch_size = 10
    results = defaultdict(int) 
    categorized_data = {}

    print("Analyzing...", flush=True)
    
    try:
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i+batch_size]
            classification = classify_question_batch(batch)
            
            for q, category in classification.items():
                results[category] += 1
                categorized_data[q] = category
                
            print(f"Processed {min(i+batch_size, len(questions))}/{len(questions)}", flush=True)
            # time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nProcess interrupted. Saving partial results...", flush=True)
    except Exception as e:
        print(f"\nUnexpected error: {e}", flush=True)

    print("\nAnalysis Result:", flush=True)
    final_report = "=== Question Type Analysis Report ===\n\n"
    for cat, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
        line = f"{cat}: {count} queries"
        print(line, flush=True)
        final_report += line + "\n"
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(final_report)
        f.write("\n\n=== Detailed Classification ===\n")
        for q, cat in categorized_data.items():
            f.write(f"[{cat}] {q}\n")

    print(f"\nReport saved to {OUTPUT_PATH}", flush=True)

if __name__ == "__main__":
    main()
