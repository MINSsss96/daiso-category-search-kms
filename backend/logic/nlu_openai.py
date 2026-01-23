
import os
import json
import uuid
import time
import datetime
import asyncio
from typing import List, Dict, Tuple, Union
from dotenv import load_dotenv
from openai import AsyncOpenAI
from .schemas import NLUResponse, Intent, NLUSlots
from .prompts import SYSTEM_PROMPT_V1, TAIL_QUESTION_PROMPT, AUX_PROMPT_KEYWORDS, KEYWORD_EXPANSION_PROMPT

load_dotenv()

_client = None
MODEL_NAME = "gpt-4o-mini"

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("WARNING: OPENAI_API_KEY is not set.")
        _client = AsyncOpenAI(api_key=api_key)
    return _client

def log_debug(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"[{timestamp}] {msg}")
    try:
        with open("nlu_debug.log", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except:
        pass

async def analyze_text(text: str, history: List[Dict[str, str]] = []) -> NLUResponse:
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    log_debug(f"[{request_id}] Analyzing (OpenAI): {text} | History: {len(history)} turns")

    # Format History
    history_text = ""
    if history:
        history_text = "## Conversation History\n"
        for turn in history:
            role = turn["role"]
            content = turn["text"]
            history_text += f"{role}: {content}\n"
    
    try:
        client = get_client()
        final_prompt = f"{history_text}\nUser's Current Input: {text}"
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_V1},
            {"role": "user", "content": final_prompt}
        ]

        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0  # Deterministic for NLU
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if response.usage:
            usage["prompt_tokens"] = response.usage.prompt_tokens
            usage["completion_tokens"] = response.usage.completion_tokens
            usage["total_tokens"] = response.usage.total_tokens
            
        content = response.choices[0].message.content
        data = json.loads(content)
        
        intent_val = data.get("intent", "UNSUPPORTED")
        if intent_val not in Intent.__members__:
            intent_val = "UNSUPPORTED"
            
        return NLUResponse(
            request_id=request_id,
            intent=Intent[intent_val],
            slots=NLUSlots(**data.get("slots", {})),
            needs_clarification=data.get("needs_clarification", False),
            latency_ms=latency_ms,
            token_usage=usage
        )

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        log_debug(f"[{request_id}] Error: {e}")
        return NLUResponse(
            request_id=request_id,
            intent=Intent.UNSUPPORTED,
            slots=NLUSlots(),
            needs_clarification=False,
            generated_question=f"Error: {str(e)}",
            latency_ms=latency_ms
        )

async def generate_tail_question(context: str, slots: dict, db_context: str = "") -> str:
    try:
        client = get_client()
        
        formatted_prompt = TAIL_QUESTION_PROMPT.format(
            context=context, 
            slots=json.dumps(slots, ensure_ascii=False),
            db_context=db_context
        )
        
        messages = [{"role": "user", "content": formatted_prompt}]
        
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "자세히 말씀해 주시면 찾아드릴게요."

async def infer_product_keywords(text: str, return_usage: bool = False) -> Union[List[str], Tuple[List[str], Dict]]:
    try:
        client = get_client()
        prompt = AUX_PROMPT_KEYWORDS.format(text=text)
        
        # Add a nudge to ensure JSON list format
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Output must be a valid JSON list of strings."},
            {"role": "user", "content": prompt}
        ]

        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3
        )
        
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if response.usage:
            usage["prompt_tokens"] = response.usage.prompt_tokens
            usage["completion_tokens"] = response.usage.completion_tokens
            usage["total_tokens"] = response.usage.total_tokens
        
        content = response.choices[0].message.content
        # Clean up code blocks if present (e.g. ```json ... ```)
        if content.startswith("```"):
            content = content.strip().split("\n", 1)[-1].rsplit("\n", 1)[0]
            if content.startswith("json"):
                 content = content[4:]
        
        keywords = json.loads(content)
        if not isinstance(keywords, list): keywords = []
        
        if return_usage:
            return keywords, usage
        return keywords
        
    except Exception as e:
        log_debug(f"Inference error: {e}")
        empty_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if return_usage:
            return [], empty_usage
        return []

async def expand_search_keywords(product_name: str, return_usage: bool = False) -> Union[List[str], Tuple[List[str], Dict]]:
    try:
        client = get_client()
        prompt = KEYWORD_EXPANSION_PROMPT.format(product_name=product_name)
        
        messages = [
            {"role": "system", "content": "You are a JSON-speaking assistant. Output exactly a JSON list of strings."},
            {"role": "user", "content": prompt}
        ]
        
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3
        )
        
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if response.usage:
            usage["prompt_tokens"] = response.usage.prompt_tokens
            usage["completion_tokens"] = response.usage.completion_tokens
            usage["total_tokens"] = response.usage.total_tokens
            
        content = response.choices[0].message.content
        
        # Robust JSON cleaning
        content = content.strip()
        if content.startswith("```"):
            # Remove first line (e.g., ```json) and last line (```)
            lines = content.split('\n')
            if len(lines) >= 3:
                content = '\n'.join(lines[1:-1])
            else:
                content = content.replace('```json', '').replace('```', '')

        keywords = json.loads(content)
        if not isinstance(keywords, list): keywords = [product_name]
        
        if return_usage:
            return keywords, usage
        return keywords

    except Exception as e:
        log_debug(f"Keyword expansion error for {product_name}: {e}")
        empty_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if return_usage:
             return [product_name], empty_usage
        return [product_name]
