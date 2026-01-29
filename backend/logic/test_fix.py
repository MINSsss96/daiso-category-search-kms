import json
import os
import sys

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    print("Imports successful")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "database", "part_refill_questions_100.json")

def load_questions():
    if not os.path.exists(JSON_PATH):
        print(f"Error: File not found at {JSON_PATH}")
        return []
    
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        return data.get("questions", [])

questions = load_questions()
print(f"Successfully loaded {len(questions)} questions.")
if questions:
    print(f"First question: {questions[0]}")
