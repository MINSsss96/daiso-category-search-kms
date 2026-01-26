import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "logic", "comparison_report.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "logic", "final_category_report.txt")

def classify_question_detailed(q_str):
    if not q_str:
        return "Other (기타)"
        
    # Direct Product (직접 검색)
    if "어디" in q_str and ("있어요" in q_str or "있나요" in q_str or "가야" in q_str or "찾아요" in q_str or "코너" in q_str or "있죠" in q_str or "예요" in q_str):
        return "Direct Product (직접 검색)"
    if "어디" in q_str and "찾으려" in q_str:
         return "Direct Product (직접 검색)"

    # Problem Solution (문제 해결/니즈 기반)
    if "방법" in q_str or "법" in q_str or "막는 거" in q_str or "해결" in q_str or "안 나게" in q_str or "안 되게" in q_str or "안 묻게" in q_str or "안 새게" in q_str or "안 흘리게" in q_str or "안 아프게" in q_str or "안 엉키게" in q_str:
         return "Problem Solution (문제 해결/니즈 기반)"
    if "없어요?" in q_str and "말고" in q_str: # "이거 말고 다른거 없어요?"
        return "Problem Solution (문제 해결/니즈 기반)"
    
    # Part/Refill (부품/리필)
    if "리필" in q_str or "따로" in q_str or "부품" in q_str or "교체" in q_str or "뚜껑만" in q_str:
        return "Part/Refill (부품/리필)"

    # Description/Feature (특징/묘사 기반)
    if "이름" in q_str or "뭐에요" in q_str or "설명" in q_str or "그거" in q_str or "생긴 거" in q_str or "뭐예요" in q_str:
        return "Description/Feature (특징/묘사 기반)"
        
    # Usage/Context (사용 상황/맥락 기반)
    if "때" in q_str or "용" in q_str or "집에서" in q_str or "여행" in q_str or "차 안" in q_str or "아이" in q_str or "여름" in q_str or "겨울" in q_str or "비 오는" in q_str or "캠핑" in q_str:
        return "Usage/Context (사용 상황/맥락 기반)"
    # Fallback for "Usage/Context" (availability check often implies context if not direct location)
    if "있어요" in q_str or "있나요" in q_str:
        return "Usage/Context (사용 상황/맥락 기반)"
        
    return "Other (기타)"

def main():
    print(f"Reading {INPUT_FILE}...")
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    data = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    
    print(f"Total entries parsed: {len(data)}")

    categories = [
        "Direct Product (직접 검색)",
        "Problem Solution (문제 해결/니즈 기반)",
        "Usage/Context (사용 상황/맥락 기반)",
        "Description/Feature (특징/묘사 기반)",
        "Part/Refill (부품/리필)",
        "Other (기타)"
    ]

    stats = {cat: {"total": 0, "match": 0} for cat in categories}

    for entry in data:
        status = entry.get('Status', '').strip()
        q = entry.get('Question', '').strip()
        
        if status not in ["MATCH", "MISMATCH"]:
            continue

        category = classify_question_detailed(q)
        
        # Ensure category key exists
        if category not in stats:
             category = "Other (기타)"

        stats[category]["total"] += 1
        if status == "MATCH":
            stats[category]["match"] += 1

    # Generate Report
    output_lines = []
    output_lines.append("=== Detailed Category Accuracy Report ===\n")
    
    grand_total = 0
    grand_match = 0
    
    for cat in categories:
        d = stats[cat]
        total = d["total"]
        match = d["match"]
        accuracy = (match / total * 100) if total > 0 else 0.0
        
        grand_total += total
        grand_match += match
        
        output_lines.append(f"Category: {cat}")
        output_lines.append(f"  Total: {total}")
        output_lines.append(f"  Matches: {match}")
        output_lines.append(f"  Accuracy: {accuracy:.1f}%\n")

    grand_accuracy = (grand_match / grand_total * 100) if grand_total > 0 else 0.0
    output_lines.append("=== TOTAL SUMMARY ===")
    output_lines.append(f"Total Evaluated: {grand_total}")
    output_lines.append(f"Matches: {grand_match}")
    output_lines.append(f"Overall Accuracy: {grand_accuracy:.1f}%")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
