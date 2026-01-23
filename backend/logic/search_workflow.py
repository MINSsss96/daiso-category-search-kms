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

        
    # Hardcoded to avoid import issues
    questions_list = [
      "건전지 어디에 있어요?", "멀티탭 코너는 몇 번이에요?", "순간접착제는 어디로 가야 돼요?",
      "욕실 슬리퍼 찾는데 안 보여요.", "다이소 꿀템이라고 하던데, '리들샷' 재고 있나요?",
      "아이폰 충전 케이블은 어디 쪽에 있나요?", "포장지랑 편지지는 어디 있어요?",
      "옷걸이 종류는 어디 모여 있어요?", "강아지 배변 패드는 2층에 있나요?",
      "줄자는 공구 쪽에 있나요, 문구 쪽에 있나요?", "싱크대 물 안 튀게 막아주는 거 있어요?",
      "의자 끌 때 소리 안 나게 끼우는 거 찾는데요.", "새로 이사했는데 문틈으로 바람 들어오는 거 막는 스펀지 같은 거요.",
      "화장실 타일 사이에 낀 곰팡이 없애는 젤 있나요?", "그... 옷에 핀 보풀 제거하는 기계 있어요?",
      "신발장 냄새 제거하는 탈취제 같은 거 어디 봐요?", "벽에 못 안 박고 액자 걸 수 있는 끈끈이 있어요?",
      "여행 가는데 화장품 덜어갈 작은 공병들 모아둔 곳이요.", "방충망에 구멍 났는데 그거 때우는 스티커 있나요?",
      "키보드 사이에 먼지 빼는 젤리 같은 거 찾고 있어요?", "매직블럭(매직스펀지) 큰 거는 없어요?",
      "배수구 거름망 스타킹처럼 된 거요.", "에어프라이어에 까는 종이 호일 어디 있죠?",
      "고무장갑 M사이즈는 어디에 걸려 있나요?", "밀폐용기 중에 유리로 된 것만 모아둔 곳 있어요?",
      "기름 닦는 키친타월은 휴지 쪽에 있나요, 주방 쪽에 있나요?", "텀블러 닦는 긴 솔 찾아요.",
      "음식물 쓰레기 봉투도 파나요?", "인덕션 상판 닦는 전용 세제 있나요?",
      "과일 씻을 때 쓰는 베이킹소다는 어디 있어요?", "뽁뽁이(에어캡) 롤로 말려 있는 거 있어요?",
      "택배 보낼 때 쓰는 박스 테이프 투명한 거요.", "다이어리 꾸미는 스티커 모아둔 매대는 어디예요?",
      "화이트보드 마카랑 지우개 세트로 된 거 있나요?", "제본할 때 쓰는 링 같은 거 파나요?",
      "축의금 봉투 글씨 안 쓰여 있는 걸로 찾는데요.", "네임펜 얇은 거 말고 굵은 거는요?",
      "가위가 잘 안 드는데 여기서 제일 잘 드는 가위 추천해 주세요.", "초강력 자석 있나요?",
      "서류 정리하는 파일 꽂이 투명한 색깔 있어요?", "앞머리 롤(헤어롤) 제일 큰 사이즈 어디 있어요?",
      "화장 퍼프 대용량으로 든 거 찾아요.", "젤 네일 굽는 램프도 파나요?",
      "머리끈 검은색 고무줄만 들어있는 거요.", "여행용 샴푸/린스 키트 있나요?",
      "여드름 났을 때 붙이는 패치 어디 있죠?", "발 뒤꿈치 각질 제거하는 돌 같은 거요.",
      "손거울 탁상용으로 세울 수 있는 거 찾아요.", "남자들 쓰는 왁스나 스프레이도 있나요?",
      "속눈썹 뷰러 고무 리필만 따로 파나요?", "자전거 자물쇠 비밀번호 설정되는 거요.",
      "차량용 핸드폰 거치대 송풍구에 끼우는 거 있나요?", "캠핑 갈 때 쓸 일회용 숯이나 그릴 파나요?",
      "드라이버 세트 정밀 드라이버 포함된 거요.", "실리콘 쏘는 총(코킹건)이랑 실리콘 어디 있어요?",
      "낚시용품 코너가 따로 있나요?", "뜨개질 실이랑 바늘 찾는 중인데요.",
      "화분에 꽂는 영양제 초록색 그거요.", "페인트 붓이랑 롤러 작은 사이즈 있나요?",
      "차 긁힌 데 바르는 컴파운드 같은 거 파나요?", "생일 파티 풍선 중에 숫자 풍선 있어요?",
      "아이들 가지고 노는 슬라임 종류 많은 곳이 어디예요?", "크리스마스 트리 장식볼 찾는데요.",
      "비눗방울 놀이하는 거 큰 거 있나요?", "할로윈 분장 소품 어디 있나요?",
      "파티용 고깔모자랑 폭죽 있나요?", "어버이날 카네이션 브로치 조화로 된 거요.",
      "스케치북이랑 크레파스 유치원생 쓸 만한 거요.", "선물 상자 예쁜 거 파는 코너 좀 알려주세요."
    ]
    
    print("DEBUG: Starting execution...")
    
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
