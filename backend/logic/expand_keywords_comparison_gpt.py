
import os
import re
import time
import json
import asyncio
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

COMPARISON_REPORT_PATH = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\comparison_report.txt"
OUTPUT_REPORT_PATH = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\expansion_result_gpt.json"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

KEYWORD_EXPANSION_PROMPT = """
You are a keyword expansion expert for 'Daiso' (a variety store).
Given a core product keyword, list 5-10 related keywords that a user might search for in a Daiso context (e.g., synonyms, specific product types, related purpose).
Return ONLY a JSON object with a key "keywords" containing the list of strings.

Product: {product_name}
JSON:
"""

def parse_comparison_report(file_path: str) -> List[str]:
    keywords = set()
    if not os.path.exists(file_path): return []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = re.split(r'\n\s*\n', content)
    for block in blocks:
        if "[MATCH]" in block:
            match = re.search(r'Keyword:\s*(.+)', block)
            if match:
                keywords.add(match.group(1).strip())
    return list(keywords)

async def expand_gpt(keyword: str):
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Daiso search."},
                {"role": "user", "content": KEYWORD_EXPANSION_PROMPT.format(product_name=keyword)}
            ],
            response_format={"type": "json_object"}
        )
        latency = (time.time() - start_time) * 1000
        
        content = response.choices[0].message.content
        try:
             data = json.loads(content)
             expanded = data.get("keywords", [])
        except:
             expanded = [keyword]

        usage = response.usage
        return {
            "keyword": keyword,
            "expanded": expanded,
            "latency_ms": latency,
            "total_tokens": usage.total_tokens,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens
        }
    except Exception as e:
        return {"keyword": keyword, "error": str(e)}

async def main():
    print(f"Reading keywords from {COMPARISON_REPORT_PATH}...")
    keywords = parse_comparison_report(COMPARISON_REPORT_PATH)
    print(f"Found {len(keywords)} unique keywords.")
    
    results = []
    # Async gathering might be too fast for checking progress, doing sequential for simplicity/rate-limits
    # or smaller batches
    
    for i, kw in enumerate(keywords):
        print(f"[GPT] Processing {i+1}/{len(keywords)}: {kw}")
        res = await expand_gpt(kw)
        results.append(res)

    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    valid = [r for r in results if "error" not in r]
    if valid:
        avg_lat = sum(r['latency_ms'] for r in valid) / len(valid)
        avg_tok = sum(r['total_tokens'] for r in valid) / len(valid)
        print(f"\n[GPT Summary] Avg Latency: {avg_lat:.2f}ms | Avg Tokens: {avg_tok:.1f}")

if __name__ == "__main__":
    asyncio.run(main())
