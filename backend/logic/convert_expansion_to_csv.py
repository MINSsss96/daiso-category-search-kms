
import json
import csv
import os

# File paths
GEMINI_JSON = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\expansion_result_gemini.json"
GPT_JSON = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\expansion_result_gpt.json"

GEMINI_CSV = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\expansion_result_gemini.csv"
GPT_CSV = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\expansion_result_gpt.csv"

def convert_json_to_csv(json_path, csv_path, model_name):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Prepare CSV rows
    rows = []
    total_latency = 0
    total_tokens = 0
    total_prompt = 0
    total_completion = 0
    total_expanded_count = 0
    valid_count = 0
    
    for item in data:
        keyword = item.get("keyword", "")
        expanded = item.get("expanded", [])
        latency = item.get("latency_ms", 0)
        tokens = item.get("total_tokens", 0)
        prompt = item.get("prompt_tokens", 0)
        completion = item.get("completion_tokens", 0)
        error = item.get("error", "")
        
        # Join expanded keywords with semicolon for CSV
        expanded_str = "; ".join(expanded) if expanded else ""
        expanded_count = len(expanded)
        
        rows.append({
            "keyword": keyword,
            "expanded_keywords": expanded_str,
            "expanded_count": expanded_count,
            "latency_ms": round(latency, 2),
            "total_tokens": tokens,
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "error": error
        })
        
        # Sum for average (only if no error)
        if not error:
            valid_count += 1
            total_latency += latency
            total_tokens += tokens
            total_prompt += prompt
            total_completion += completion
            total_expanded_count += expanded_count
    
    # Write CSV with semicolon delimiter for Korean Excel
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ["keyword", "expanded_keywords", "expanded_count", "latency_ms", "total_tokens", "prompt_tokens", "completion_tokens", "error"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)
    
    # Calculate averages
    if valid_count > 0:
        avg_latency = total_latency / valid_count
        avg_tokens = total_tokens / valid_count
        avg_prompt = total_prompt / valid_count
        avg_completion = total_completion / valid_count
        avg_expanded = total_expanded_count / valid_count
    else:
        avg_latency = avg_tokens = avg_prompt = avg_completion = avg_expanded = 0
    
    print(f"\n=== {model_name} Summary ===")
    print(f"Total Items: {len(data)} (Valid: {valid_count})")
    print(f"Avg Latency: {avg_latency:.2f} ms")
    print(f"Avg Total Tokens: {avg_tokens:.2f}")
    print(f"Avg Prompt Tokens: {avg_prompt:.2f}")
    print(f"Avg Completion Tokens: {avg_completion:.2f}")
    print(f"Avg Expanded Keywords: {avg_expanded:.2f}")
    print(f"CSV saved to: {csv_path}")

def main():
    print("Converting JSON to CSV...\n")
    
    if os.path.exists(GEMINI_JSON):
        convert_json_to_csv(GEMINI_JSON, GEMINI_CSV, "Gemini")
    else:
        print(f"File not found: {GEMINI_JSON}")
    
    if os.path.exists(GPT_JSON):
        convert_json_to_csv(GPT_JSON, GPT_CSV, "GPT-4o-mini")
    else:
        print(f"File not found: {GPT_JSON}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
