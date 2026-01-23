import sys
import os
import asyncio

# Add project root to sys.path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import TypedDict, List, Literal, Annotated, Dict
from langgraph.graph import StateGraph, END
from backend.logic.nlu import analyze_text, infer_product_keywords, expand_search_keywords
from backend.logic.schemas import Intent as NluIntent

# --- 1. State Definition (GraphState) ---
class GraphState(TypedDict):
    query: str                                  # 사용자 질문
    intent: Literal["explicit", "implicit"]     # 질문 의도
    product_name: List[str]                     # 추출되거나 추론된 상품명 리스트
    search_keywords: List[str]                  # 최종 확장된 검색 키워드 리스트
    total_tokens: int                           # [New] Total Token Usage
    total_latency_ms: int                       # [New] Total Latency (ms)
    keyword_count: int                          # [New] Number of Keywords
    filters: Dict[str, int]                     # [New] Filters (min_price, max_price)

# --- 2. Nodes (Graph Nodes) ---

def analyze_intent(state: GraphState) -> GraphState:
    import time
    start_time = time.time()
    
    print(f"\n--- [Node: analyze_intent] Processing: {state['query']} ---")
    query = state['query']
    
    # Run async NLU analysis synchronously
    nlu_response = asyncio.run(analyze_text(query))
    
    intent = "implicit"
    product_names = []
    
    if nlu_response.slots.item:
        intent = "explicit"
        # [Mod] Use query_rewrite if available (supports Color/Attrs), else fallback to item
        if nlu_response.slots.query_rewrite:
             product_names = [nlu_response.slots.query_rewrite]
        else:
             product_names = [nlu_response.slots.item]
    elif "건전지" in query:
         intent = "explicit"
         product_names = ["건전지"]
    
    print(f"  -> Determined Intent: {intent}")
    if intent == "explicit":
        print(f"  -> Extracted Products: {product_names}")
    
    # [Mod] Extract Price Filters
    filters = {}
    if nlu_response.slots.min_price is not None:
        filters["min_price"] = nlu_response.slots.min_price
    if nlu_response.slots.max_price is not None:
        filters["max_price"] = nlu_response.slots.max_price
    
    if filters:
        print(f"  -> Extracted Filters: {filters}")

    # Metrics
    latency = int((time.time() - start_time) * 1000)
    tokens = 0
    if nlu_response.token_usage:
        tokens = nlu_response.token_usage.get("total_tokens", 0)
        if not tokens:
            tokens = nlu_response.token_usage.get("prompt_tokens", 0) + nlu_response.token_usage.get("completion_tokens", 0)

    current_tokens = state.get("total_tokens", 0) + tokens
    current_latency = state.get("total_latency_ms", 0) + latency

    return {
        "intent": intent,
        "product_name": product_names,
        "filters": filters,
        "total_tokens": current_tokens,
        "total_latency_ms": current_latency
    }

def infer_product_name(state: GraphState) -> GraphState:
    import time
    start_time = time.time()
    
    print(f"\n--- [Node: infer_product_name] Inferring from: {state['query']} ---")
    
    # [Mod] Request token usage
    inferred_names, usage = asyncio.run(infer_product_keywords(state['query'], return_usage=True))
    
    if not inferred_names:
        inferred_names = ["다이소 추천 상품"]
        
    print(f"  -> Inferred Products: {inferred_names}")
    
    latency = int((time.time() - start_time) * 1000)
    
    # Accumulate tokens
    tokens = usage.get("total_tokens", 0)
    if not tokens:
        tokens = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)

    current_tokens = state.get("total_tokens", 0) + tokens
    current_latency = state.get("total_latency_ms", 0) + latency
    
    return {
        "product_name": inferred_names,
        "total_tokens": current_tokens,
        "total_latency_ms": current_latency
    }

def expand_keywords(state: GraphState) -> GraphState:
    import time
    start_time = time.time()
    
    products = state['product_name']
    print(f"\n--- [Node: expand_keywords] Expanding keywords for: {products} ---")
    
    all_keywords = []
    total_node_tokens = 0
    
    for product in products:
        # [Mod] Request token usage per expansion call
        expanded, usage = asyncio.run(expand_search_keywords(product, return_usage=True))
        all_keywords.extend(expanded)
        
        # Sum tokens from each call
        t = usage.get("total_tokens", 0)
        if not t:
            t = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
        total_node_tokens += t
    
    seen = set()
    deduped_keywords = []
    for k in all_keywords:
        if k not in seen:
            deduped_keywords.append(k)
            seen.add(k)
    
    print(f"  -> Generated Keywords: {deduped_keywords}")
    
    latency = int((time.time() - start_time) * 1000)
    
    current_tokens = state.get("total_tokens", 0) + total_node_tokens
    current_latency = state.get("total_latency_ms", 0) + latency
    
    return {
        "search_keywords": deduped_keywords,
        "keyword_count": len(deduped_keywords),
        "total_tokens": current_tokens,
        "total_latency_ms": current_latency
    }

# --- 3. Edges (Graph Edges) ---

def route_intent(state: GraphState) -> Literal["expand_keywords", "infer_product_name"]:
    intent = state['intent']
    if intent == "explicit":
        print("  [Edge] Routing to: expand_keywords (FAST TRACK)")
        return "expand_keywords"
    else:
        print("  [Edge] Routing to: infer_product_name (SLOW TRACK)")
        return "infer_product_name"

# --- 4. Graph Construction ---

workflow = StateGraph(GraphState)

workflow.add_node("analyze_intent", analyze_intent)
workflow.add_node("infer_product_name", infer_product_name)
workflow.add_node("expand_keywords", expand_keywords)

workflow.set_entry_point("analyze_intent")

workflow.add_conditional_edges(
    "analyze_intent",
    route_intent,
    {
        "expand_keywords": "expand_keywords",
        "infer_product_name": "infer_product_name"
    }
)

workflow.add_edge("infer_product_name", "expand_keywords")
workflow.add_edge("expand_keywords", END)

app = workflow.compile()

if __name__ == "__main__":
    import sys
    import os
    import asyncio
    
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    from backend.database.question2 import QUESTION_DATA
    
    # Use all questions (100 items)
    questions_list = QUESTION_DATA[0]["questions"]
    
    print(f"DEBUG: Starting execution with {len(questions_list)} questions...")
    
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflow_output.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        sys.stdout = f
        
        print(f"Loaded {len(questions_list)} questions.")
        print(f"=== Processing ALL {len(questions_list)} Questions ===\n")
        
        explicit_stats = {"count": 0, "total_ms": 0, "total_tokens": 0, "total_keywords": 0}
        implicit_stats = {"count": 0, "total_ms": 0, "total_tokens": 0, "total_keywords": 0}

        for i, customer_query in enumerate(questions_list, 1):
            header = f"--- [Q{i}] Customer asks: '{customer_query}' ---"
            print(header)
            
            inputs = {
                "query": customer_query, 
                "intent": "implicit", 
                "product_name": [], 
                "search_keywords": [],
                "keyword_count": 0,
                "filters": {},
                "total_tokens": 0,
                "total_latency_ms": 0
            }
            
            final_state = inputs.copy()
            for output in app.stream(inputs):
                for key, value in output.items():
                    final_state.update(value)
            
            # Print Metrics for this query
            if final_state:
                intent = final_state.get('intent', 'unknown')
                lat = final_state.get('total_latency_ms', 0)
                tok = final_state.get('total_tokens', 0)
                kw_count = final_state.get('keyword_count', 0)
                filter_info = final_state.get('filters', {})
                filter_str = f" | Filters: {filter_info}" if filter_info else ""
                
                print(f"  [Metrics] Path: {intent.upper()} | Latency: {lat}ms | Tokens: {tok} | Keywords: {kw_count}{filter_str}")
                
                if intent == "explicit":
                    explicit_stats["count"] += 1
                    explicit_stats["total_ms"] += lat
                    explicit_stats["total_tokens"] += tok
                    explicit_stats["total_keywords"] += kw_count
                else:
                    implicit_stats["count"] += 1
                    implicit_stats["total_ms"] += lat
                    implicit_stats["total_tokens"] += tok
                    implicit_stats["total_keywords"] += kw_count

        print("\n=== Performance Summary ===")
        if explicit_stats["count"] > 0:
            avg_ms = explicit_stats["total_ms"] / explicit_stats["count"]
            avg_tok = explicit_stats["total_tokens"] / explicit_stats["count"]
            avg_kw = explicit_stats["total_keywords"] / explicit_stats["count"]
            print(f"[Explicit Path] Avg Latency: {avg_ms:.2f}ms | Avg Tokens: {avg_tok:.2f} | Avg Keywords: {avg_kw:.2f}")
        
        if implicit_stats["count"] > 0:
            avg_ms = implicit_stats["total_ms"] / implicit_stats["count"]
            avg_tok = implicit_stats["total_tokens"] / implicit_stats["count"]
            avg_kw = implicit_stats["total_keywords"] / implicit_stats["count"]
            print(f"[Implicit Path] Avg Latency: {avg_ms:.2f}ms | Avg Tokens: {avg_tok:.2f} | Avg Keywords: {avg_kw:.2f}")

        print("\nGraph compiled and executed successfully!")
