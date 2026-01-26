import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "logic", "comparison_report.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "logic", "comparison_report_category.txt")

def classify_question_detailed(q_str):
    # Direct Product (직접 검색)
    if "어디" in q_str and ("있어요" in q_str or "있나요" in q_str or "가야" in q_str or "찾아요" in q_str or "코너" in q_str):
        return "Direct Product (직접 검색)"
    if "어디 있죠" in q_str or "어디예요" in q_str or "어디서 찾아요" in q_str:
        return "Direct Product (직접 검색)"

    # Problem Solution (문제 해결/니즈 기반)
    if "방법" in q_str or "법" in q_str or "없어요?" in q_str or "막는 거" in q_str or "해결" in q_str or "안 나게" in q_str or "안 되게" in q_str:
         return "Problem Solution (문제 해결/니즈 기반)"
    
    # Usage/Context (사용 상황/맥락 기반)
    if "때" in q_str or "용" in q_str or "집에서" in q_str or "여행" in q_str or "차 안" in q_str or "아이" in q_str or "여름" in q_str or "겨울" in q_str:
        return "Usage/Context (사용 상황/맥락 기반)"
        
    # Description/Feature (특징/묘사 기반)
    if "이름" in q_str or "뭐에요" in q_str or "설명" in q_str or "그거" in q_str or "생긴 거" in q_str:
        return "Description/Feature (특징/묘사 기반)"
        
    # Part/Refill (부품/리필)
    if "리필" in q_str or "따로" in q_str or "부품" in q_str or "교체" in q_str:
        return "Part/Refill (부품/리필)"
        
    # Fallback
    if "있어요" in q_str or "있나요" in q_str:
        return "Usage/Context (사용 상황/맥락 기반)" # Vague availability usually implies context
        
    return "Other (기타)"

def parse_report(file_path):
    data = []
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return data

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pattern = re.compile(r'^\[(MATCH|MISMATCH|MISSING)\] Q:\s*(.*)')

    for line in lines:
        line = line.strip()
        match = pattern.match(line)
        if match:
            status = match.group(1)
            question = match.group(2)
            data.append({'status': status, 'question': question})
    
    return data

def main():
    print(f"Reading {INPUT_FILE}...")
    entries = parse_report(INPUT_FILE)
    print(f"Total entries parsed: {len(entries)}")

    categories = [
        "Direct Product (직접 검색)",
        "Problem Solution (문제 해결/니즈 기반)",
        "Usage/Context (사용 상황/맥락 기반)",
        "Description/Feature (특징/묘사 기반)",
        "Part/Refill (부품/리필)",
        "Other (기타)"
    ]

    stats = {cat: {"total": 0, "match": 0} for cat in categories}

    for entry in entries:
        status = entry['status']
        q = entry['question']
        
        if status not in ["MATCH", "MISMATCH"]:
            continue

        category = classify_question_detailed(q)
        
        # Ensure category key exists (fallback safety)
        if category not in stats:
             stats[category] = {"total": 0, "match": 0}

        stats[category]["total"] += 1
        if status == "MATCH":
            stats[category]["match"] += 1

    # Generate Report
    output_lines = []
    output_lines.append("=== Detailed Category Accuracy Report ===\n")
    
    grand_total = 0
    grand_match = 0
    
    # Calculate percentages and print
    for cat in categories:
        data = stats.get(cat, {"total": 0, "match": 0})
        total = data["total"]
        match = data["match"]
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
