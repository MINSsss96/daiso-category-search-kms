import sys
import os
import re

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from backend.database.GroundTruth import QUESTION_DATA
except ImportError:
    print("Error: Could not import QUESTION_DATA from backend.database.GroundTruth")
    sys.exit(1)

def parse_workflow_output(file_path):
    """
    Parses the workflow output text file to extract intent and keywords for each question.
    Returns a dictionary keyed by question text (or ID if possible, but text is safer here since ID isn't in output log explicitly for all lines).
    """
    results = {}
    
    current_question = None
    current_data = {
        "intent": None,
        "extracted_products": [],
        "generated_keywords": []
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        
        # Match Question: --- [Q1] Customer asks: '...' ---
        q_match = re.search(r"--- \[Q\d+\] Customer asks: '(.*)' ---", line)
        if q_match:
            # Save previous if exists
            if current_question:
                results[current_question] = current_data
            
            current_question = q_match.group(1)
            current_data = {
                "intent": None,
                "extracted_products": [],
                "generated_keywords": []
            }
            continue
            
        # Match Intent: -> Determined Intent: explicit
        intent_match = re.search(r"-> Determined Intent: (.*)", line)
        if intent_match:
            current_data["intent"] = intent_match.group(1).strip()
            continue
            
        # Match Extracted Products (Explicit): -> Extracted Products: ['...']
        ep_match = re.search(r"-> Extracted Products: \[(.*)\]", line)
        if ep_match:
            # Parse list string loosely
            content = ep_match.group(1)
            items = [item.strip().strip("'").strip('"') for item in content.split(',')]
            current_data["extracted_products"].extend([i for i in items if i])
            continue
            
        # Match Inferred Products (Implicit): -> Inferred Products: ['...']
        ip_match = re.search(r"-> Inferred Products: \[(.*)\]", line)
        if ip_match:
             # Parse list string loosely
            content = ip_match.group(1)
            items = [item.strip().strip("'").strip('"') for item in content.split(',')]
            current_data["extracted_products"].extend([i for i in items if i])
            continue

        # Match Generated Keywords: -> Generated Keywords: ['...']
        gk_match = re.search(r"-> Generated Keywords: \[(.*)\]", line)
        if gk_match:
            content = gk_match.group(1)
            items = [item.strip().strip("'").strip('"') for item in content.split(',')]
            current_data["generated_keywords"].extend([i for i in items if i])
            continue

    # Save last one
    if current_question:
        results[current_question] = current_data
        
    return results

def verify_performance(output_file):
    if not os.path.exists(output_file):
        print(f"Error: Output file not found at {output_file}")
        return

    parsed_results = parse_workflow_output(output_file)
    
    total_questions = len(QUESTION_DATA)
    intent_correct = 0
    keyword_match_count = 0
    
    print(f"=== NLU Performance Verification Report ===")
    print(f"Ground Truth Size: {total_questions} items")
    print(f"Parsed Results Size: {len(parsed_results)} items\n")
    
    failures = []
    
    for item in QUESTION_DATA:
        q_text = item["query"]
        expected_intent = item["expected_intent"]
        ground_truth_keywords = [k.replace(" ", "") for k in item["ground_truth"]] # Normalize spaces for comparison
        
        if q_text not in parsed_results:
            print(f"[MISSING] Question not found in output: {q_text}")
            failures.append({"type": "missing", "question": q_text})
            continue
            
        result = parsed_results[q_text]
        actual_intent = result["intent"]
        
        # Combine extracted products and generated keywords for broad matching
        # Users care if the *concept* was found.
        all_found_keywords = result["extracted_products"] + result["generated_keywords"]
        all_found_keywords_norm = [k.replace(" ", "") for k in all_found_keywords]
        
        # 1. Verify Intent
        if actual_intent == expected_intent:
            intent_correct += 1
        else:
            failures.append({
                "type": "intent_mismatch",
                "question": q_text,
                "expected": expected_intent,
                "actual": actual_intent
            })
            
        # 2. Verify Keywords
        # Check if ANY ground truth keyword is contained in ANY found keyword (partial match)
        # or if ANY found keyword is contained in ANY ground truth keyword
        match_found = False
        matched_kw = []
        
        for gt in ground_truth_keywords:
            for found in all_found_keywords_norm:
                # Check for substring match in either direction (flexible matching)
                if gt in found or found in gt:
                    match_found = True
                    matched_kw.append(f"{gt} <-> {found}")
                    break
            if match_found:
                break
        
        if match_found:
            keyword_match_count += 1
        else:
            failures.append({
                "type": "keyword_mismatch",
                "question": q_text,
                "expected": item["ground_truth"],
                "actual": all_found_keywords[:5] # Show top 5
            })

    # Calculate Metrics
    intent_accuracy = (intent_correct / total_questions) * 100
    keyword_accuracy = (keyword_match_count / total_questions) * 100
    
    detailed_report_path = os.path.join(os.path.dirname(output_file), "nlu_detailed_report.txt")
    detailed_lines = []
    detailed_lines.append(f"=== NLU Detailed Performance Report (All Questions) ===")
    detailed_lines.append(f"Total Questions: {total_questions}")
    detailed_lines.append(f"Intent Accuracy: {intent_accuracy:.2f}%")
    detailed_lines.append(f"Keyword Accuracy: {keyword_accuracy:.2f}%")
    detailed_lines.append("="*80)
    detailed_lines.append(f"{'ID':<4} | {'Query':<50} | {'Exp. Intent':<10} | {'Act. Intent':<10} | {'Intent Check':<12} | {'Keyword Check':<12}")
    detailed_lines.append("-" * 120)

    for item in QUESTION_DATA:
        q_id = item["id"]
        q_text = item["query"]
        expected_intent = item["expected_intent"]
        ground_truth_keywords = [k.replace(" ", "") for k in item["ground_truth"]] # Normalize
        
        # Prepare row data
        q_display = (q_text[:47] + '...') if len(q_text) > 50 else q_text
        
        if q_text not in parsed_results:
             detailed_lines.append(f"{q_id:<4} | {q_display:<50} | {expected_intent:<10} | {'MISSING':<10} | {'FAIL':<12} | {'FAIL':<12}")
             continue

        result = parsed_results[q_text]
        actual_intent = result["intent"]
        all_found_keywords = result["extracted_products"] + result["generated_keywords"]
        all_found_keywords_norm = [k.replace(" ", "") for k in all_found_keywords]

        # Intent Check
        intent_status = "PASS" if actual_intent == expected_intent else "FAIL"
        
        # Keyword Check
        keyword_status = "FAIL"
        for gt in ground_truth_keywords:
            for found in all_found_keywords_norm:
                if gt in found or found in gt:
                    keyword_status = "PASS"
                    break
            if keyword_status == "PASS":
                break
        
        detailed_lines.append(f"{q_id:<4} | {q_display:<50} | {expected_intent:<10} | {actual_intent:<10} | {intent_status:<12} | {keyword_status:<12}")

        # Failure Details (only if something failed)
        if intent_status == "FAIL" or keyword_status == "FAIL":
             detailed_lines.append(f"   [DETAILS] GT Keywords: {item['ground_truth']}")
             detailed_lines.append(f"   [DETAILS] Extracted:   {all_found_keywords[:6]}...")
             if intent_status == "FAIL":
                  detailed_lines.append(f"   [NOTE] Intent Mismatch: Expected '{expected_intent}' but got '{actual_intent}'")
             detailed_lines.append("-" * 120)

    with open(detailed_report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(detailed_lines))
    print(f"\nDetailed report written to: {detailed_report_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("output_file", help="Path to the workflow output text file")
    args = parser.parse_args()
    
    print("Starting verification...")
    verify_performance(args.output_file)
