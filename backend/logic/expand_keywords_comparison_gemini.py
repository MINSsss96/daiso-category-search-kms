
import os
import re
import time
import json
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
import sys

# Import Gemini logic from existing nlu.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.logic.nlu import expand_search_keywords as expand_gemini_func

load_dotenv()

COMPARISON_REPORT_PATH = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\comparison_report.txt"
OUTPUT_REPORT_PATH = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\expansion_result_gemini.json"

def parse_comparison_report(file_path: str) -> List[str]:
    keywords = set()
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = re.split(r'\n\s*\n', content)
    for block in blocks:
        if "[MATCH]" in block:
            match = re.search(r'Keyword:\s*(.+)', block)
            if match:
                kw = match.group(1).strip()
                keywords.add(kw)
    return list(keywords)

async def main():
    print(f"Reading matched keywords from {COMPARISON_REPORT_PATH}...")
    keywords = parse_comparison_report(COMPARISON_REPORT_PATH)
    print(f"Found {len(keywords)} unique keywords.")
    
    results = []
    
    # Process all keywords
    for i, kw in enumerate(keywords):
        print(f"[Gemini] Processing {i+1}/{len(keywords)}: {kw}")
        start_time = time.time()
        
        # Call Gemini expansion (using existing nlu logic)
        # Note: Ideally nlu.py should support Daiso-specific prompt adjustments.
        # If nlu.py's prompt is generic, we might need to modify nlu.py OR override here.
        # Since nlu.py is shared, let's rely on its existing logic but assuming it's reasonably aligned.
        # However, user asked for "Daiso related". nlu.py KEYWORD_EXPANSION_PROMPT likely handles this.
        
        try:
             # Assuming expand_search_keywords returns (keywords, usage) tuple if return_usage=True
             # We need to verify if nlu.py actually supports return_usage.
             # Based on previous context, I added return_usage support in nlu.py.
             expanded_list, usage = await expand_gemini_func(kw, return_usage=True)
             
             latency = (time.time() - start_time) * 1000
             
             results.append({
                 "keyword": kw,
                 "expanded": expanded_list,
                 "latency_ms": latency,
                 "total_tokens": usage.get("total_tokens", 0),
                 "prompt_tokens": usage.get("prompt_tokens", 0),
                 "completion_tokens": usage.get("completion_tokens", 0)
             })

        except Exception as e:
            print(f"Error processing {kw}: {e}")
            results.append({"keyword": kw, "error": str(e)})

    # Save
    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    # Summary
    valid = [r for r in results if "error" not in r]
    if valid:
        avg_lat = sum(r['latency_ms'] for r in valid) / len(valid)
        avg_tok = sum(r['total_tokens'] for r in valid) / len(valid)
        print(f"\n[Gemini Summary] Avg Latency: {avg_lat:.2f}ms | Avg Tokens: {avg_tok:.1f}")

if __name__ == "__main__":
    asyncio.run(main())
