
import os
import re
import time
import json
import asyncio
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import Gemini logic from existing nlu.py
# Assuming nlu.py is in the same directory or accessible via sys.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.logic.nlu import expand_search_keywords as expand_gemini, get_genai

# Load environment variables
load_dotenv()

COMPARISON_REPORT_PATH = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\comparison_report.txt"
OUTPUT_REPORT_PATH = r"c:\Users\301\dev\daiso-category-search-kms\backend\logic\expansion_comparison_result.json"

# OpenAI Configuration
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except ImportError:
    openai_client = None

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  # Using a likely available model, can be changed

KEYWORD_EXPANSION_PROMPT = """
You are a search keyword expander for a large variety store (Daiso).
Given a core product keyword, generate a list of 5-10 related search keywords that a user might search for.
Include synonyms, specific types, and related uses.
Return ONLY valid JSON string of a list of strings.

Product: {product_name}
JSON:
"""

def parse_comparison_report(file_path: str) -> List[str]:
    """Parses comparison_report.txt and returns a list of unique matched keywords."""
    keywords = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Regex to find [MATCH] blocks and extract Keyword
    # Pattern looks for [MATCH] ... Keyword: ...
    # We iterate line by line to be safe or use blocks
    
    blocks = re.split(r'\n\s*\n', content)
    for block in blocks:
        if "[MATCH]" in block:
            match = re.search(r'Keyword:\s*(.+)', block)
            if match:
                kw = match.group(1).strip()
                keywords.add(kw)
    
    return list(keywords)

async def expand_openai(keyword: str) -> Dict[str, Any]:
    if not openai_client:
        return {"error": "OpenAI library not found or API key missing"}
        
    start_time = time.time()
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON only."},
                {"role": "user", "content": KEYWORD_EXPANSION_PROMPT.format(product_name=keyword)}
            ],
            response_format={"type": "json_object"}
        )
        latency = (time.time() - start_time) * 1000
        
        content = response.choices[0].message.content
        try:
            keywords = json.loads(content).get("keywords", [])
            if not keywords and isinstance(json.loads(content), list):
                 keywords = json.loads(content)
            elif not keywords:
                 # Check if the root is the list
                 data = json.loads(content)
                 if isinstance(data, list): keywords = data
                 else: keywords = list(data.values())[0] if data else []
        except:
            keywords = [keyword]

        usage = response.usage
        return {
            "model": "gpt-4o-mini",
            "keywords": keywords,
            "latency_ms": latency,
            "total_tokens": usage.total_tokens,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens
        }
    except Exception as e:
        return {"model": "gpt-4o-mini", "error": str(e), "latency_ms": (time.time() - start_time) * 1000}

async def expand_llama(keyword: str) -> Dict[str, Any]:
    start_time = time.time()
    try:
        # Construct prompt
        prompt = KEYWORD_EXPANSION_PROMPT.format(product_name=keyword)
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
        )
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("response", "")
            
            # Parse JSON from content
            try:
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    keywords = parsed
                elif isinstance(parsed, dict):
                     # Try to find a list value
                     keywords = next((v for v in parsed.values() if isinstance(v, list)), [keyword])
                else:
                    keywords = [keyword]
            except:
                keywords = [keyword]
                
            # Token usage from Ollama (often estimated or provided in specific fields)
            # Ollama returns 'eval_count' (completion) and 'prompt_eval_count' (prompt)
            prompt_tokens = data.get("prompt_eval_count", 0)
            completion_tokens = data.get("eval_count", 0)
            total_tokens = prompt_tokens + completion_tokens
            
            return {
                "model": OLLAMA_MODEL,
                "keywords": keywords,
                "latency_ms": latency,
                "total_tokens": total_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens
            }
        else:
             return {"model": OLLAMA_MODEL, "error": f"Status {response.status_code}", "latency_ms": latency}
             
    except Exception as e:
        return {"model": OLLAMA_MODEL, "error": str(e), "latency_ms": (time.time() - start_time) * 1000}

async def expand_gemini_wrapper(keyword: str) -> Dict[str, Any]:
    # Wrapper to normalize nlu.py structure to our report format
    start_time = time.time()
    try:
        # nlu.py expand_search_keywords returns (keywords, usage_dict) if return_usage=True
        # We need to check if existing nlu.py supports return_usage.
        # Based on previous view_file, it does support it (lines 185, 211).
        
        keywords, usage = await expand_gemini(keyword, return_usage=True)
        latency = (time.time() - start_time) * 1000
        
        return {
            "model": "gemini-2.0-flash",
            "keywords": keywords,
            "latency_ms": latency,
            "total_tokens": usage.get("total_tokens", 0),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0)
        }
    except Exception as e:
        return {"model": "gemini-2.0-flash", "error": str(e), "latency_ms": (time.time() - start_time) * 1000}

async def main():
    print(f"Reading keywords from {COMPARISON_REPORT_PATH}...")
    keywords = parse_comparison_report(COMPARISON_REPORT_PATH)
    print(f"Found {len(keywords)} unique keywords to expand.")
    
    # We will process a subset if there are too many, or just report progress
    # For coding task, let's process reasonable amount or all.
    # Let's take top 5 for quick demonstration or all if safe.
    # User might want to run it for all. I'll include a limit for safety but set high.
    
    results = []
    
    for i, kw in enumerate(keywords):
        print(f"Processing [{i+1}/{len(keywords)}]: {kw}")
        
        # Parallel execution for speed
        res_gemini, res_openai, res_llama = await asyncio.gather(
            expand_gemini_wrapper(kw),
            expand_openai(kw),
            expand_llama(kw)
        )
        
        results.append({
            "keyword": kw,
            "results": [res_gemini, res_openai, res_llama]
        })
        
        # Optional: Sleep to avoid rate limits if necessary
        # await asyncio.sleep(0.1)

    # Save Results
    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Expansion complete. Results saved to {OUTPUT_REPORT_PATH}")
    
    # Print Summary
    print("\n=== Summary ===")
    models = ["gemini-2.0-flash", "gpt-4o-mini", OLLAMA_MODEL]
    for model in models:
        model_results = [r for res in results for r in res['results'] if r['model'] == model and "error" not in r]
        if not model_results:
            print(f"Model {model}: No successful results.")
            continue
            
        avg_lat = sum(r['latency_ms'] for r in model_results) / len(model_results)
        avg_tok = sum(r['total_tokens'] for r in model_results) / len(model_results)
        print(f"Model {model}: Avg Latency={avg_lat:.2f}ms, Avg Tokens={avg_tok:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
