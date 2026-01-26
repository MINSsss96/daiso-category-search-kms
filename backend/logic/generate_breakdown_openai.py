import csv
import os

# Hardcoded absolute paths
INPUT_FILE = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\comparison_report_openai.csv"
OUTPUT_FILE = r"c:\Users\301\.gemini\antigravity\brain\a27faff9-e48f-43c0-ae9f-1416794f6234\category_breakdown_report_openai_fixed.txt"

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
    if "없어요?" in q_str and "말고" in q_str:
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
    # Fallback
    if "있어요" in q_str or "있나요" in q_str:
        return "Usage/Context (사용 상황/맥락 기반)"
        
    return "Other (기타)"

def main():
    print(f"START: Reading {INPUT_FILE}...")
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: File not found: {INPUT_FILE}")
        return

    data = []
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"ERROR reading file: {e}")
        return
            
    print(f"Total entries loaded: {len(data)}")

    categories = [
        "Direct Product (직접 검색)",
        "Problem Solution (문제 해결/니즈 기반)",
        "Usage/Context (사용 상황/맥락 기반)",
        "Description/Feature (특징/묘사 기반)",
        "Part/Refill (부품/리필)",
        "Other (기타)"
    ]

    categorized_data = {cat: {'MATCH': [], 'MISMATCH': []} for cat in categories}

    for entry in data:
        status = entry.get('Status', '').strip()
        q = entry.get('Question', '').strip()
        keyword = entry.get('Keyword', '').strip()
        
        if status not in ["MATCH", "MISMATCH"]:
            continue

        category = classify_question_detailed(q)
        if category not in categorized_data:
            category = "Other (기타)"
            
        categorized_data[category][status].append({
            'q': q,
            'k': keyword
        })

    # Generate Output
    lines = []
    lines.append("=== Category Breakdown Report (OpenAI) ===")
    lines.append(f"Total Evaluated: {len(data)}\n")

    for cat in categories:
        match_list = categorized_data[cat]['MATCH']
        mismatch_list = categorized_data[cat]['MISMATCH']
        total = len(match_list) + len(mismatch_list)
        accuracy = (len(match_list) / total * 100) if total > 0 else 0.0

        lines.append(f"## {cat}")
        lines.append(f"- **Total**: {total}")
        lines.append(f"- **Accuracy**: {accuracy:.1f}%\n")
        
        lines.append(f"### [MISMATCHING QUESTIONS] ({len(mismatch_list)})")
        if mismatch_list:
            for i, item in enumerate(mismatch_list, 1):
                lines.append(f"{i}. \"{item['q']}\" (Extracted: \"{item['k']}\")")
        else:
            lines.append("(None)")
        lines.append("")
        
        lines.append(f"### [MATCHING QUESTIONS] ({len(match_list)})")
        if match_list:
            for item in match_list:
                lines.append(f"- \"{item['q']}\" -> \"{item['k']}\"")
        else:
             lines.append("(None)")
             
        lines.append("\n" + "="*30 + "\n")

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"SUCCESS: Report generated at {OUTPUT_FILE}")
    except Exception as e:
        print(f"ERROR writing file: {e}")

if __name__ == "__main__":
    main()
