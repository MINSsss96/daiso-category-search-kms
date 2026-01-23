import os
import sqlite3
from typing import TypedDict, Literal, Optional
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field

# Load Env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is not set in .env")

# --- Database Helper ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
DB_PATH = os.path.join(BASE_DIR, 'database', 'products.db')
print(f"DEBUG: Using Database Path: {DB_PATH}")

def search_products_db(keyword: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    terms = keyword.split()
    query = "SELECT * FROM products WHERE " + " AND ".join(["name LIKE ?"] * len(terms))
    params = [f"%{term}%" for term in terms]
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- LLM Setup ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0,
    google_api_key=api_key
)

# --- State Definition ---
class AgentState(TypedDict):
    query: str
    intent: Optional[str]
    keywords: Optional[str]
    # For multi-turn state
    pending_problem: Optional[str] # If set, we are waiting for clarification
    clarification_options: Optional[str] # The options we gave the user
    final_response: Optional[str]
    search_results: Optional[list]

# --- Nodes ---

def node_input_router(state: AgentState):
    """
    Decide if we are starting a new query or answering a clarification.
    """
    if state.get("pending_problem"):
        print(f"\n[Router] Detected pending problem. Treating input as answer: {state['query']}")
        return {"intent": "resolve_clarification"}
    
    return {"intent": "analyze_new"}

def node_analyze_intent(state: AgentState):
    """
    Classify new user query.
    """
    print(f"\n[Node] Analyzing Intent for: {state['query']}")
    
    prompt = PromptTemplate.from_template(
        """
        Analyze the following user query and classify it into one of two intents:
        1. 'direct_search': The user is looking for a specific product name.
        2. 'problem_solving': The user describes a problem or situation.
        
        Examples:
        "물티슈 있어?" -> direct_search
        "화장실이 너무 더러워" -> problem_solving
        "곰팡이 제거하고 싶어" -> problem_solving
        "AA 건전지" -> direct_search
        
        Return ONLY: 'direct_search' or 'problem_solving'.
        Query: {query}
        """
    )
    chain = prompt | llm | StrOutputParser()
    intent = chain.invoke({"query": state["query"]}).strip().lower()
    
    if "direct" in intent: intent = "direct_search"
    else: intent = "problem_solving"
    
    print(f" -> Detected Intent: {intent}")
    return {"intent": intent}

def node_direct_search(state: AgentState):
    print("\n[Node] Direct Search Extraction")
    prompt = PromptTemplate.from_template(
        """
        Extract the core product search keyword.
        RETURN ONLY THE KOREAN KEYWORD. NO ENGLISH. NO BRACKETS.
        Query: {query}
        """
    )
    chain = prompt | llm | StrOutputParser()
    keyword = chain.invoke({"query": state["query"]}).strip()
    print(f" -> Extracted Keyword: {keyword}")
    return {"keywords": keyword, "pending_problem": None} # Clear state

def node_problem_solving(state: AgentState):
    """
    Analyze problem. If vague, ask for clarification (1, 2, 3).
    If specific, infer keyword.
    """
    print("\n[Node] Problem Solving Analysis")
    query = state["query"]
    
    prompt = PromptTemplate.from_template(
        """
        User Problem: "{query}"
        
        Step 1: Is this problem specific enough to recommend ONE specific product type immediately?
        Step 2: If YES, output "KEYWORD: <Product Name>".
        Step 3: If NO (too vague), provide 3 distinct product categories that could solve it in "OPTIONS: 1. A, 2. B, 3. C" format.
        
        Examples:
        Query: "Bathroom is slippery"
        Output: KEYWORD: 미끄럼방지 매트
        
        Query: "Restroom is dirty" (Could be brush, detergent, or mold remover)
        Output: OPTIONS: 1. 청소솔, 2. 욕실세제, 3. 곰팡이 제거제
        
        Query: "{query}"
        Output:
        """
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"query": query}).strip()
    
    if result.startswith("OPTIONS:"):
        options = result.replace("OPTIONS:", "").strip()
        response = f"어떤 제품을 찾으시나요?\n{options}\n번호나 제품명을 입력해주세요."
        print(f" -> Vague. Asking clarification: {options}")
        # SAVE STATE: We start "pending_problem" mode
        return {
            "final_response": response, 
            "pending_problem": query, 
            "clarification_options": options,
            "intent": "ask_clarification" # Special flag for routing
        }
    else:
        keyword = result.replace("KEYWORD:", "").strip()
        print(f" -> Specific. Keyword: {keyword}")
        return {"keywords": keyword, "pending_problem": None}

def node_resolve_clarification(state: AgentState):
    """
    Combine original problem + User Selection -> Final Keyword.
    """
    original_problem = state["pending_problem"]
    options = state["clarification_options"]
    user_selection = state["query"] # The new input (e.g., "1" or "Sol")
    
    print("\n[Node] Resolving Clarification")
    print(f"Original: {original_problem}, Options: {options}, Selection: {user_selection}")
    
    prompt = PromptTemplate.from_template(
        """
        Context: User had problem "{problem}".
        Options provided: "{options}".
        User selected: "{selection}".
        
        Based on the selection (which might be a number or text), determine the single best product keyword.
        RETURN ONLY THE KOREAN KEYWORD.
        
        Example:
        Options: 1. Brush, 2. Detergent
        Selection: 1
        Keyword: 청소솔
        """
    )
    chain = prompt | llm | StrOutputParser()
    keyword = chain.invoke({
        "problem": original_problem, 
        "options": options, 
        "selection": user_selection
    }).strip()
    
    print(f" -> Resolved Keyword: {keyword}")
    return {"keywords": keyword, "pending_problem": None, "clarification_options": None} # Clear state

def node_finalize_search(state: AgentState):
    print("\n[Node] Finalizing Search")
    keywords = state["keywords"]
    results = search_products_db(keywords)
    
    if results:
        response = f"'{keywords}' 검색 결과 ({len(results)}건):\n"
        for item in results[:5]: 
            cat = f"{item.get('category_major')}/{item.get('category_middle')}"
            response += f"- {item['name']} ({cat}) : {item['price']}원\n"
    else:
        response = f"'{keywords}'에 대한 검색 결과가 없습니다."
        
    return {"final_response": response, "search_results": results}

# --- Router ---
def route_main(state: AgentState):
    if state["intent"] == "resolve_clarification":
        return "resolve_clarification"
    return "analyze_intent"

def route_analyzed(state: AgentState):
    if state["intent"] == "direct_search":
        return "direct_search"
    return "problem_solving"

def route_problem_outcome(state: AgentState):
    if state.get("intent") == "ask_clarification":
        return END # Return to user for input
    return "finalize_search"

# --- Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("input_router", node_input_router)
workflow.add_node("analyze_intent", node_analyze_intent)
workflow.add_node("direct_search", node_direct_search)
workflow.add_node("problem_solving", node_problem_solving)
workflow.add_node("resolve_clarification", node_resolve_clarification)
workflow.add_node("finalize_search", node_finalize_search)

workflow.set_entry_point("input_router")

workflow.add_conditional_edges("input_router", route_main)
workflow.add_conditional_edges("analyze_intent", route_analyzed)
workflow.add_edge("direct_search", "finalize_search")
workflow.add_conditional_edges("problem_solving", route_problem_outcome)
workflow.add_edge("resolve_clarification", "finalize_search")
workflow.add_edge("finalize_search", END)

# Memory for persistence
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# --- Interactive Loop ---
if __name__ == "__main__":
    print("=== LangGraph Interactive Mode (Multi-turn) ===")
    
    # Static thread ID to maintain session memory
    config = {"configurable": {"thread_id": "session_1"}}
    
    while True:
        try:
            query = input("\n질문(또는 번호)을 입력하세요: ")
            if query.lower() in ['exit', 'quit']:
                break
            if not query.strip():
                continue
            
            # Use 'query' to update state
            # Note: LangGraph state update merges keys.
            result = app.invoke({"query": query}, config=config)
            
            # Print response
            print(f"System: {result['final_response']}")
            print("="*30)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
