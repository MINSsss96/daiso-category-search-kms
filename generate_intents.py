import json
import os
import time
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "backend", "database", "part_refill_questions_100.json")

def generate_intents(questions):
    prompt_intro = """
    당신은 다이소 고객의 질문 의도를 분석하는 AI입니다.
    질문을 보고, 고객이 구매하고자 하는 구체적인 상품이나 해결책을 '구매' 형태로 요약해 주세요.
    part_refill과 관련된 질문들이므로, '부품 교체', '리필', '소모품 구매' 등의 맥락을 살려주세요.
    
    [Format Example]
    Q: "물에 젖어도 냄새 안 나는 거 있어요?"
    A: 항균 매트 / 속건 타월 구매
    
    Q: "열 받아도 안 녹는 거 있어요?"
    A: 내열 매트 / 실리콘 받침 구매
    
    Q: "샤프심만 따로 파나요?"
    A: 샤프심 리필 구매
    
    Q: "다이어리 속지 리필용 찾고 있어요."
    A: 다이어리 속지 / 리필용 종이 구매

    [Task]
    아래 질문들의 의도(intention)를 위와 같은 형식(상품명 / 대안상품명 구매)으로 작성해 주세요.
    출력은 오직 결과 리스트(JSON Array of strings)만 주세요.
    질문 개수와 동일한 개수의 리스트를 반환해야 합니다.
    """
    
    batch_size = 10  # Reduced batch size
    all_intents = []
    
    total = len(questions)
    
    for i in range(0, total, batch_size):
        batch = questions[i:i+batch_size]
        batch_queries = [q["query"] for q in batch]
        
        prompt_content = json.dumps(batch_queries, ensure_ascii=False, indent=2)
        full_prompt = f"{prompt_intro}\n\nQuestions ({len(batch)} items):\n{prompt_content}\n\nOutput JSON Array:"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Processing batch {i//batch_size + 1}/{(total+batch_size-1)//batch_size} ({len(batch)} items)...", flush=True)
                response = model.generate_content(full_prompt)
                
                # Extract JSON
                text = response.text.replace("```json", "").replace("```", "").strip()
                # Find list start/end
                start = text.find('[')
                end = text.rfind(']') + 1
                if start != -1 and end != -1:
                    text = text[start:end]
                
                batch_intents = json.loads(text)
                
                if len(batch_intents) != len(batch):
                    print(f"Mismatch: Expected {len(batch)}, got {len(batch_intents)}. Retrying...", flush=True)
                    continue

                all_intents.extend(batch_intents)
                print(f"Batch success. Total collected: {len(all_intents)}", flush=True)
                break
            except Exception as e:
                print(f"Error on attempt {attempt+1}: {e}", flush=True)
                time.sleep(2)
        else:
            print("Failed batch after retries. Filling with fallback.", flush=True)
            all_intents.extend([f"{q} 관련 상품 구매" for q in batch_queries])

        time.sleep(1)

    return all_intents

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    print(f"Reading from {INPUT_FILE}...", flush=True)
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Generate intents
    new_intents = generate_intents(data)
    
    if new_intents and len(new_intents) == len(data):
        for idx, item in enumerate(data):
            item["intent"] = new_intents[idx]
        
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully updated {len(data)} items with intents.", flush=True)
    else:
        print(f"Critical mismatch: Data {len(data)} vs Intents {len(new_intents)}", flush=True)

if __name__ == "__main__":
    main()
