
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTION_FILE = os.path.join(BASE_DIR, "backend", "database", "question_intention.json")

def main():
    with open(INTENTION_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Total items: {len(data)}")
    
    indices = [0, 142, 152, 247, 367]
    names = [
        "Direct Search (Start)", 
        "Part/Refill (Start)", 
        "Situation (Start)", 
        "Problem (Start)", 
        "Description (Start)"
    ]
    
    for i, idx in enumerate(indices):
        if idx < len(data):
            print(f"Index {idx} [{names[i]}]: {data[idx]['question']}")
        else:
            print(f"Index {idx} out of bounds")

if __name__ == "__main__":
    main()
