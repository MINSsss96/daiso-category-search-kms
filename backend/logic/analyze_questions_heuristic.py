
import json
import os
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "database", "question3.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "logic", "question_analysis_report.txt")

def load_questions():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def classify_heuristic(q):
    q_str = str(q)
    if "어디" in q_str and ("있어요" in q_str or "있나요" in q_str or "가야" in q_str or "찾아요" in q_str):
        return "Direct Product (직접 검색)"
    elif "방법" in q_str or "법" in q_str or "없어요?" in q_str:
         return "Problem Solution (문제 해결/니즈 기반)"
    elif "때" in q_str or "용" in q_str or "집에서" in q_str or "여행" in q_str:
        return "Usage/Context (사용 상황/맥락 기반)"
    elif "이름" in q_str or "뭐에요" in q_str or "설명" in q_str:
        return "Description/Feature (특징/묘사 기반)"
    elif "리필" in q_str or "따로" in q_str or "부품" in q_str:
        return "Part/Refill (부품/리필)"
    else:
        # Fallback based on typical endings
        if "있어요" in q_str or "있나요" in q_str:
            return "Usage/Context (사용 상황/맥락 기반)" # Vague availability check
        return "Other (기타)"

def main():
    questions = load_questions()
    print(f"Total questions: {len(questions)}")
    
    results = defaultdict(int)
    categorized_data = {}

    for q in questions:
        cat = classify_heuristic(q)
        results[cat] += 1
        categorized_data[q] = cat

    print("\nAnalysis Result:")
    final_report = "=== Question Type Analysis Report (Heuristic) ===\n\n"
    for cat, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
        line = f"{cat}: {count} queries"
        print(line)
        final_report += line + "\n"
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(final_report)
        f.write("\n\n=== Detailed Classification ===\n")
        for q, cat in categorized_data.items():
            f.write(f"[{cat}] {q}\n")

    print(f"\nReport saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
