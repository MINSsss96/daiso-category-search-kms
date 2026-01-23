import sys
import os
import asyncio

# Add project root to sys.path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import TypedDict, List, Literal, Annotated
from langgraph.graph import StateGraph, END
from backend.logic.nlu import analyze_text, infer_product_keywords, expand_search_keywords
from backend.logic.schemas import Intent as NluIntent

# --- 1. State Definition (GraphState) ---
class GraphState(TypedDict):
    query: str                                  # 사용자 질문
    intent: Literal["explicit", "implicit"]     # 질문 의도
    product_name: List[str]                     # 추출되거나 추론된 상품명 리스트 (수정됨)
    search_keywords: List[str]                  # 최종 확장된 검색 키워드 리스트

# --- 2. Nodes (Graph Nodes) ---

def analyze_intent(state: GraphState) -> GraphState:
    """
    Node A: analyze_intent
    사용자의 질문을 분석하여 의도(intent)를 파악하고, 명시적(explicit)일 경우 상품명(product_name)을 바로 추출한다.
    """
    print(f"\n--- [Node: analyze_intent] Processing: {state['query']} ---")
    query = state['query']
    
    # Run async NLU analysis synchronously
    nlu_response = asyncio.run(analyze_text(query))
    
    intent = "implicit"
    product_names = []
    
    # Specific Item Check
    # If NLU extracted a specific item (slots.item), we treat it as explicit product found
    if nlu_response.slots.item:
        intent = "explicit"
        product_names = [nlu_response.slots.item]
        # normalize: remove nulls if any (though schema handles it)
    
    # Fallback: specific keywords check (legacy/backup)
    elif "건전지" in query:
         intent = "explicit"
         product_names = ["건전지"]
    
    print(f"  -> Determined Intent: {intent}")
    if intent == "explicit":
        print(f"  -> Extracted Products: {product_names}")

    return {
        "intent": intent,
        "product_name": product_names
    }

def infer_product_name(state: GraphState) -> GraphState:
    """
    Node B: infer_product_name
    애매모호한 질문일 경우, 문맥을 통해 적절한 다이소 상품명 하나를 추론한다.
    """
    print(f"\n--- [Node: infer_product_name] Inferring from: {state['query']} ---")
    
    # Run async Inference
    inferred_names = asyncio.run(infer_product_keywords(state['query']))
    
    # If AI fails to return anything, fallback
    if not inferred_names:
        inferred_names = ["다이소 추천 상품"]
        
    print(f"  -> Inferred Products: {inferred_names}")
    
    return {"product_name": inferred_names}

def expand_keywords(state: GraphState) -> GraphState:
    """
    Node C: expand_keywords
    확보된 product_name을 기반으로 검색용 다중 키워드(search_keywords)를 생성한다.
    """
    products = state['product_name']
    print(f"\n--- [Node: expand_keywords] Expanding keywords for: {products} ---")
    
    
    # 1. LLM 호출하여 유사어/동의어 확장
    # keywords_str = invoke_llm(f"Generate search keywords for: {products}")
    
    all_keywords = []

    for product in products:
        # 각 상품명에 대해 구조적 키워드 확장 (LLM)
        expanded = asyncio.run(expand_search_keywords(product))
        all_keywords.extend(expanded)
    
    # 중복 제거 (순서 유지)
    seen = set()
    deduped_keywords = []
    for k in all_keywords:
        if k not in seen:
            deduped_keywords.append(k)
            seen.add(k)
    
    print(f"  -> Generated Keywords: {deduped_keywords}")
    
    return {"search_keywords": deduped_keywords}

# --- 3. Edges (Graph Edges) ---

def route_intent(state: GraphState) -> Literal["expand_keywords", "infer_product_name"]:
    """
    Conditional Edge Logic
    IF intent == 'explicit' -> expand_keywords (바로 이동)
    IF intent == 'implicit' -> infer_product_name (추론 단계로 이동)
    """
    intent = state['intent']
    if intent == "explicit":
        print("  [Edge] Routing to: expand_keywords")
        return "expand_keywords"
    else:
        print("  [Edge] Routing to: infer_product_name")
        return "infer_product_name"

# --- 4. Graph Construction ---

workflow = StateGraph(GraphState)

# 노드 추가
workflow.add_node("analyze_intent", analyze_intent)
workflow.add_node("infer_product_name", infer_product_name)
workflow.add_node("expand_keywords", expand_keywords)

# 엣지 연결
# Entry Point -> analyze_intent
workflow.set_entry_point("analyze_intent")

# Conditional Edge: analyze_intent -> (branch)
workflow.add_conditional_edges(
    "analyze_intent",
    route_intent,
    {
        "expand_keywords": "expand_keywords",
        "infer_product_name": "infer_product_name"
    }
)

# Normal Edge: infer_product_name -> expand_keywords
workflow.add_edge("infer_product_name", "expand_keywords")

# Final Edge: expand_keywords -> END
workflow.add_edge("expand_keywords", END)

# 컴파일
app = workflow.compile()

# --- Explanation of Graph Behavior ---
# 1. [상품명 명시형 케이스]
#    - 입력: "AA 건전지 있어?"
#    - analyze_intent: intent="explicit", product_name="AA 건전지" 판별
#    - route_intent: "explicit" 이므로 "expand_keywords" 노드로 즉시 이동 (infer_product_name 건너뜀)
#    - expand_keywords: "AA 건전지" 기반 키워드 확장
#    - END

# 2. [상품명 비명시형/애매한 케이스]
#    - 입력: "화장실 청소하게 솔 같은 거 있나?"
#    - analyze_intent: intent="implicit" 판별 (구체적 상품명 추출 불확실)
#    - route_intent: "implicit" 이므로 "infer_product_name" 노드로 이동
#    - infer_product_name: 문맥을 통해 "욕실 청소솔" 추론
#    - expand_keywords: "욕실 청소솔" 기반 키워드 확장
#    - END

if __name__ == "__main__":
    import random
    import sys
    import os
    import asyncio
    # Add project root to sys.path to allow imports from backend
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    from backend.logic.nlu import analyze_text, infer_product_keywords, expand_search_keywords
    from backend.logic.schemas import Intent as NluIntent
    import io
    from contextlib import redirect_stdout
    
    # Add project root to path for imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        
    # Import questions from backend.database.question2
    from backend.database.question2 import QUESTION_DATA
    
    # Extract the list of questions
    questions_list = QUESTION_DATA[0]["questions"]
    
    print(f"DEBUG: Starting execution with {len(questions_list)} questions...")
    
    app = workflow.compile()
    
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflow_output.txt")
    
    # Redirect stdout to file with utf-8 encoding to avoid Windows console encoding issues
    with open(output_file, "w", encoding="utf-8") as f:
        sys.stdout = f
        
        print(f"Loaded {len(questions_list)} questions.")
        print(f"=== Processing All {len(questions_list)} Questions ===\n")
        
        for i, customer_query in enumerate(questions_list, 1):
            header = f"--- [Q{i}] Customer asks: '{customer_query}' ---"
            print(header)
            
            inputs = {"query": customer_query, "intent": "implicit", "product_name": [], "search_keywords": []}
            
            # Run graph
            for output in app.stream(inputs):
                pass
            
        print("\nGraph compiled and executed successfully!")
