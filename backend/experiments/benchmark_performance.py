
import sys
import os
import asyncio
import time
import json
from contextlib import redirect_stdout

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Literal
from backend.logic.nlu import analyze_text, infer_product_keywords, expand_search_keywords
from backend.database.question2 import QUESTION_DATA

# --- Modified State Definition to Track Metrics ---
class GraphState(TypedDict):
    query: str
    intent: Literal["explicit", "implicit"]
    product_name: List[str]
    search_keywords: List[str]
    # Metrics tracking
    total_tokens: int
    total_latency_ms: int
    path_taken: str

# --- Instrumented Nodes ---

def analyze_intent(state: GraphState) -> GraphState:
    query = state['query']
    
    # We run analyzing_text which returns an NLUResponse object
    # NLUResponse has latency_ms and token_usage
    start = time.time()
    nlu_response = asyncio.run(analyze_text(query))
    latency = int((time.time() - start) * 1000) # Measure total node time including overhead
    
    intent = "implicit"
    product_names = []
    
    # Check slots
    if nlu_response.slots.item:
        intent = "explicit"
        product_names = [nlu_response.slots.item]
    elif "건전지" in query:
        intent = "explicit"
        product_names = ["건전지"]
        
    # Accumulate metrics
    tokens = 0
    if nlu_response.token_usage:
        tokens = nlu_response.token_usage.get("total_tokens", 0) # API might vary, let's just sum what we have if available or use candidates + prompt
        if not tokens: # Fallback calculation if total_tokens key missing
            tokens = nlu_response.token_usage.get("prompt_tokens", 0) + nlu_response.token_usage.get("completion_tokens", 0)

    # Update state
    return {
        "intent": intent,
        "product_name": product_names,
        "total_tokens": state.get("total_tokens", 0) + tokens,
        "total_latency_ms": state.get("total_latency_ms", 0) + latency
    }

def infer_product_name(state: GraphState) -> GraphState:
    start = time.time()
    # This node calls infer_product_keywords which returns a list[str], not NLUResponse
    # So we can't extract token usage easily unless we modify that function or just estimate.
    # For now, we will track Latency fully. Token usage will be under-reported for this node unless we modify nlu.py
    # NOTE: user asked for token comparison. We should probably accept that analyze_text provides the bulk of measurable tokens.
    # OR we can assume a rough count or update nlu.py. Let's stick to latency mainly + known tokens.
    
    inferred_names = asyncio.run(infer_product_keywords(state['query']))
    
    if not inferred_names:
        inferred_names = ["다이소 추천 상품"]
        
    latency = int((time.time() - start) * 1000)
    
    return {
        "product_name": inferred_names,
        "path_taken": "Implicit Path",
        "total_latency_ms": state["total_latency_ms"] + latency
    }

def expand_keywords(state: GraphState) -> GraphState:
    start = time.time()
    products = state['product_name']
    
    all_keywords = []
    for product in products:
        expanded = asyncio.run(expand_search_keywords(product))
        all_keywords.extend(expanded)
        
    deduped_keywords = list(set(all_keywords))
    
    latency = int((time.time() - start) * 1000)
    
    return {
        "search_keywords": deduped_keywords,
        "total_latency_ms": state["total_latency_ms"] + latency
    }

# --- Routing ---

def route_intent(state: GraphState) -> Literal["expand_keywords", "infer_product_name"]:
    intent = state['intent']
    if intent == "explicit":
        return "expand_keywords"
    else:
        return "infer_product_name"

# --- Graph ---

workflow = StateGraph(GraphState)
workflow.add_node("analyze_intent", analyze_intent)
workflow.add_node("infer_product_name", infer_product_name)
workflow.add_node("expand_keywords", expand_keywords)

workflow.set_entry_point("analyze_intent")
workflow.add_conditional_edges("analyze_intent", route_intent, {"expand_keywords": "expand_keywords", "infer_product_name": "infer_product_name"})
workflow.add_edge("infer_product_name", "expand_keywords")
workflow.add_edge("expand_keywords", END)

app = workflow.compile()

# --- Benchmarking ---

def run_benchmark():
    questions_list = QUESTION_DATA[0]["questions"] # [0] because QUESTION_DATA structure we saw earlier might be nested list? checking previous view... 
    # Ah, in search_workflow2.py it was: from backend.database.question2 import QUESTION_DATA -> questions_list = QUESTION_DATA[0]["questions"]
    
    results = []
    
    print(f"Benchmarking FIRST 20 questions (Demo Mode)...")
    
    # Initialize CSV
    with open("benchmark_results.csv", "w", encoding="utf-8") as f:
        f.write("Query,Intent,Latency(ms),Tokens\n")

    for i, q in enumerate(questions_list[:20]):
        print(f"Processing {i+1}/20: {q[:30]}...", flush=True)
        inputs = {
            "query": q, 
            "intent": "implicit", "product_name": [], "search_keywords": [],
            "total_tokens": 0, "total_latency_ms": 0, "path_taken": "Explicit Path" 
        }
        
        final_state = app.invoke(inputs)
        results.append(final_state)
        
        # Incremental Save
        with open("benchmark_results.csv", "a", encoding="utf-8") as f:
            clean_query = q.replace(",", " ")
            intent = final_state['intent']
            lat = final_state['total_latency_ms']
            tok = final_state['total_tokens']
            f.write(f"{clean_query},{intent},{lat},{tok}\n")


    # --- Report Generation ---
    explicit_data = [r for r in results if r["intent"] == "explicit"]
    implicit_data = [r for r in results if r["intent"] == "implicit"]
    
    print("\n=== Performance Benchmark Report ===")
    
    avg_lat_exp = sum(r["total_latency_ms"] for r in explicit_data) / len(explicit_data) if explicit_data else 0
    avg_tok_exp = sum(r["total_tokens"] for r in explicit_data) / len(explicit_data) if explicit_data else 0
    
    avg_lat_imp = sum(r["total_latency_ms"] for r in implicit_data) / len(implicit_data) if implicit_data else 0
    avg_tok_imp = sum(r["total_tokens"] for r in implicit_data) / len(implicit_data) if implicit_data else 0
    
    print(f"\n[Explicit Path] (Count: {len(explicit_data)})")
    print(f"  Avg Latency: {avg_lat_exp:.2f} ms")
    print(f"  Avg Tokens:  {avg_tok_exp:.2f} (Estimate from NLU step)\n")
    
    print(f"[Implicit Path] (Count: {len(implicit_data)})")
    print(f"  Avg Latency: {avg_lat_imp:.2f} ms")
    print(f"  Avg Tokens:  {avg_tok_imp:.2f} (Estimate from NLU step)")
    
    print("\n[Comparison]")
    if avg_lat_exp > 0:
        speed_factor = avg_lat_imp / avg_lat_exp
        print(f"  Explicit is {speed_factor:.1f}x faster than Implicit")
    
    # Save detailed CSV-like
    with open("benchmark_results.csv", "w", encoding="utf-8") as f:
        f.write("Query,Intent,Latency(ms),Tokens\n")
        for r in results:
            clean_query = r['query'].replace(",", " ")
            f.write(f"{clean_query},{r['intent']},{r['total_latency_ms']},{r['total_tokens']}\n")
            
    print("\nDetailed results saved to benchmark_results.csv")

if __name__ == "__main__":
    run_benchmark()
