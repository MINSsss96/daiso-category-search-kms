
import os
import re

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "logic", "comparison_report_question3_llama.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "logic", "category_breakdown_report_llama.txt")

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
    lines = content.split('\n')
    current_item = {}
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # New Item Start
        if line.startswith("[MATCH] Q:") or line.startswith("[MISMATCH] Q:") or line.startswith("[UNKNOWN] Q:"):
            if current_item:
                data.append(current_item)
            
            is_match = line.startswith("[MATCH]")
            q_text = line.split("Q:", 1)[1].strip()
            
            # Treat UNKNOWN as MISMATCH for now or handle separately?
            # User output example had MATCH and MISMATCH. UNKNOWN often means mismatch or error.
            # Let's count MATCH as match, others as mismatch.
            status = "MATCH" if is_match else "MISMATCH"
            
            current_item = {
                "status": status,
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
    log_path = os.path.join(BASE_DIR, "logic", "debug_log.txt")
    with open(log_path, "w") as log:
        log.write("Starting script...\n")
        try:
            log.write(f"Input file: {INPUT_FILE}\n")
            if not os.path.exists(INPUT_FILE):
                log.write(f"Error: Input file not found: {INPUT_FILE}\n")
                return

            data = parse_report(INPUT_FILE)
            log.write(f"Parsed {len(data)} items.\n")

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

            log.write("Categorization complete. Writing output...\n")
            
            # Output Generation
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("=== Category Breakdown Report (Llama 3.2) ===\n\n")
                
                all_matches = sum(len(cat_data[c]["MATCH"]) for c in categories)
                all_total = len(data)
                accuracy = (all_matches / all_total * 100) if all_total > 0 else 0
                
                f.write(f"Total Evaluated: {all_total}\n")
                f.write(f"Global Accuracy: {accuracy:.1f}% ({all_matches}/{all_total})\n\n")
                
                for i, cat in enumerate(categories, 1):
                    matches = cat_data[cat]["MATCH"]
                    mismatches = cat_data[cat]["MISMATCH"]
                    total = len(matches) + len(mismatches)
                    acc = (len(matches)/total * 100) if total > 0 else 0
                    
                    f.write(f"## {i}. {cat}\n")
                    f.write(f"- **Total**: {total}\n")
                    f.write(f"- **Accuracy**: {acc:.1f}% ({len(matches)}/{total})\n\n")
                    
                    f.write(f"### [MISMATCHING QUESTIONS] (Sample)\n")
                    if mismatches:
                        for idx, m in enumerate(mismatches[:5], 1): # First 5 samples
                            f.write(f"{idx}. \"{m['q']}\" (Extracted: \"{m['k']}\" -> Intention: {m['i']})\n")
                    else:
                        f.write("    (None)\n")
                    f.write("\n")
                    
                    f.write(f"### [MATCHING QUESTIONS] (Sample)\n")
                    if matches:
                         for m in matches[:5]: # First 5 samples
                            f.write(f"- \"{m['q']}\" -> \"{m['k']}\"\n")
                    else:
                        f.write("    (None)\n")
                    
                    f.write("\n")
            
            log.write(f"Report saved to {OUTPUT_FILE}\n")
            print(f"Report saved to {OUTPUT_FILE}")

        except Exception as e:
            log.write(f"Exception occurred: {str(e)}\n")
            import traceback
            traceback.print_exc(file=log)
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
