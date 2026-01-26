
import os
import re
import time
import json
import asyncio
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()

COMPARISON_REPORT_PATH = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\comparison_report.txt"
OUTPUT_REPORT_PATH = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\expansion_result_llama.json"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2" 

KEYWORD_EXPANSION_PROMPT = """
You are a keyword expansion expert for 'Daiso' (다이소, a Korean variety store).
Given a core product keyword, list 5-10 related keywords that a user might search for in a Daiso context.

**IMPORTANT RULES:**
1. ALL keywords MUST be in Korean (한국어).
2. Only use English for common loanwords that Koreans actually use in English (e.g., USB, LED, PVC).
3. Do NOT use Chinese characters or any other language.
4. Examples of good keywords: 수납함, 정리함, 플라스틱 통, 주방용품
5. Examples of bad keywords: storage box, 收纳盒

Return output as valid JSON with key "keywords".

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

def expand_llama(keyword: str):
    start_time = time.time()
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": KEYWORD_EXPANSION_PROMPT.format(product_name=keyword),
                "stream": False,
                "format": "json"
            }
        )
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("response", "")
            try:
                parsed = json.loads(content)
                expanded = parsed.get("keywords", [])
                if not expanded and isinstance(parsed, list): expanded = parsed
            except:
                expanded = [keyword]
                
            prompt_tokens = data.get("prompt_eval_count", 0)
            completion_tokens = data.get("eval_count", 0)
            
            return {
                "keyword": keyword,
                "expanded": expanded,
                "latency_ms": latency,
                "total_tokens": prompt_tokens + completion_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens
            }
        else:
            return {"keyword": keyword, "error": f"Status {response.status_code}"}
            
    except Exception as e:
        return {"keyword": keyword, "error": str(e)}

async def main():
    print(f"Reading keywords from {COMPARISON_REPORT_PATH}...")
    keywords = parse_comparison_report(COMPARISON_REPORT_PATH)
    print(f"Found {len(keywords)} unique keywords.")
    
    results = []
    
    for i, kw in enumerate(keywords):
        print(f"[Llama] Processing {i+1}/{len(keywords)}: {kw}")
        # Llama requests are synchronous via requests lib, so we call directly or wrap in to_thread
        res = await asyncio.to_thread(expand_llama, kw)
        results.append(res)

    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    valid = [r for r in results if "error" not in r]
    if valid:
        avg_lat = sum(r['latency_ms'] for r in valid) / len(valid)
        avg_tok = sum(r['total_tokens'] for r in valid) / len(valid)
        print(f"\n[Llama Summary] Avg Latency: {avg_lat:.2f}ms | Avg Tokens: {avg_tok:.1f}")

if __name__ == "__main__":
    asyncio.run(main())
