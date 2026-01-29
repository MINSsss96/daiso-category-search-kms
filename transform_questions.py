import json
import os

path = 'backend/database/part_refill_questions_100.json'
if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Ensure it's a list of strings before transforming
if not isinstance(questions, list) or (questions and not isinstance(questions[0], str)):
    print("File content is not a list of strings, checking if already transformed.")
    if questions and isinstance(questions[0], dict) and "intent" in questions[0]:
         print("Already transformed.")
         exit(0)
    else:
         print("Unexpected format.")
         exit(1)

new_data = [{"query": q, "intent": "part_refill"} for q in questions]

with open(path, 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)

print(f"Successfully transformed {len(new_data)} items.")
