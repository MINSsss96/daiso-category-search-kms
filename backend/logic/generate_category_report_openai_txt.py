

import os
import re

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "logic", "comparison_report_question3_openai.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "logic", "category_breakdown_report_openai.txt")

def classify_question(q_str):
    q_str = q_str.strip()
    if not q_str:
        return "Other (기타)"
        
    # Direct Product (직접 검색)
    if "어디" in q_str and ("있어요" in q_str or "있나요" in q_str or "가야" in q_str or "찾아요" in q_str or "코너" in q_str or "있죠" in q_str or "예요" in q_str):
        return "Direct Product (직접 검색형)"
    if "어디" in q_str and "찾으려" in q_str:
         return "Direct Product (직접 검색형)"

    # Problem Solution (문제 해결/니즈 기반)
    if "방법" in q_str or "법" in q_str or "막는 거" in q_str or "해결" in q_str or "안 나게" in q_str or "안 되게" in q_str or "안 묻게" in q_str or "안 새게" in q_str or "안 흘리게" in q_str or "안 아프게" in q_str or "안 엉키게" in q_str:
         return "Problem Solving/Needs (문제 해결/ 니즈 기반)"
    if "없어요?" in q_str and "말고" in q_str:
        return "Problem Solving/Needs (문제 해결/ 니즈 기반)"
    
    # Part/Refill (부품/리필)
    if "리필" in q_str or "따로" in q_str or "부품" in q_str or "교체" in q_str or "뚜껑만" in q_str:
        return "Part/Refill (부품/리필형)"

    # Description/Feature (특징/묘사 기반)
    if "이름" in q_str or "뭐에요" in q_str or "설명" in q_str or "그거" in q_str or "생긴 거" in q_str or "뭐예요" in q_str:
        return "Feature/Description (특징/묘사 기반)"
        
    # Usage/Context (사용 상황/맥락 기반)
    if "때" in q_str or "용" in q_str or "집에서" in q_str or "여행" in q_str or "차 안" in q_str or "아이" in q_str or "여름" in q_str or "겨울" in q_str or "비 오는" in q_str or "캠핑" in q_str:
        return "Situation/Context (사용 상황/맥락 기반)"

    # Fallback to Situation if "있어요/있나요"
    if "있어요" in q_str or "있나요" in q_str:
        return "Situation/Context (사용 상황/맥락 기반)"
        
    return "Other (기타)"

def parse_report(file_path):
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract blocks starting with [MATCH] or [MISMATCH]
    # The file format is likely:
    # [STATUS] Q: ...
    #   Intention: ...
    #   Keyword: ...
    #   Note: ...
    
    # Regex to capture blocks more robustly
    # We look for lines starting with [MATCH] or [MISMATCH]
    lines = content.split('\n')
    current_item = {}
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # New Item Start
        if line.startswith("[MATCH] Q:") or line.startswith("[MISMATCH] Q:"):
            if current_item:
                data.append(current_item)
            
            is_match = line.startswith("[MATCH]")
            q_text = line.split("Q:", 1)[1].strip()
            
            current_item = {
                "status": "MATCH" if is_match else "MISMATCH",
                "q": q_text,
                "i": "",
                "k": ""
            }
        
        elif line.startswith("Intention:") and current_item:
            current_item["i"] = line.split("Intention:", 1)[1].strip()
            
        elif line.startswith("Keyword:") and current_item:
            current_item["k"] = line.split("Keyword:", 1)[1].strip()
            
    # Append last item
    if current_item:
        data.append(current_item)
            
    return data

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Required input file not found: {INPUT_FILE}")
        return

    data = parse_report(INPUT_FILE)
    print(f"Parsed {len(data)} items.")

    categories = [
        "Direct Product (직접 검색형)",
        "Part/Refill (부품/리필형)",
        "Situation/Context (사용 상황/맥락 기반)",
        "Problem Solving/Needs (문제 해결/ 니즈 기반)",
        "Feature/Description (특징/묘사 기반)",
        "Other (기타)"
    ]
    
    cat_data = {c: {"MATCH": [], "MISMATCH": []} for c in categories}
    
    for item in data:
        cat = classify_question(item["q"])
        if cat not in cat_data:
             cat = "Other (기타)"
        cat_data[cat][item["status"]].append(item)

    # Output Generation
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== Category Breakdown Report ===\n")
        
        all_matches = sum(len(cat_data[c]["MATCH"]) for c in categories)
        all_total = len(data)
        accuracy = (all_matches / all_total * 100) if all_total > 0 else 0
        
        f.write(f"Total Evaluated: {all_total}\n")
        f.write(f"Matches: {all_matches}\n")
        f.write(f"Accuracy: {accuracy:.1f}%\n\n")
        
        for cat in categories:
            matches = cat_data[cat]["MATCH"]
            mismatches = cat_data[cat]["MISMATCH"]
            total = len(matches) + len(mismatches)
            acc = (len(matches)/total * 100) if total > 0 else 0
            
            f.write(f"## {cat} (Total: {total}, Accuracy: {acc:.1f}%)\n")
            
            f.write(f"  [MISMATCHING QUESTIONS] ({len(mismatches)})\n")
            if mismatches:
                for m in mismatches:
                    f.write(f"    - Q: {m['q']}\n")
                    f.write(f"      Intention: {m['i']}\n")
                    f.write(f"      Extracted: {m['k']}\n")
            else:
                f.write("    (None)\n")
            f.write("\n")
            
            f.write(f"  [MATCHING QUESTIONS] ({len(matches)})\n")
            # Compact view for matches as per user preference (or list all?)
            # User asked "match랑 mismatch 나한테 보여줘" -> show both
            if matches:
                 for m in matches:
                    f.write(f"    - {m['q']} -> {m['k']}\n")
            else:
                f.write("    (None)\n")
            
            f.write("\n" + "="*50 + "\n\n")

    print(f"Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
