import os
import sys
import sqlite3
import random
import time

# Add project root to path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Root
sys.path.append(BASE_DIR)

from backend.logic.graph import app
from backend.database.insert_mock_data import MOCK_DATA # Use MOCK_DATA directly or DB

# DB Path (for checking existence if needed, but we trust graph execution)
DB_PATH = os.path.join(BASE_DIR, 'backend', 'database', 'products.db')
OUTPUT_FILE = os.path.join(BASE_DIR, 'backend', 'database', 'direct_search_report.txt')

def generate_test_queries():
    """Generate 100 test queries based on mock data names"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products")
    products = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    templates = [
        "{0}",
        "{0} 있어?",
        "{0} 찾아줘",
        "{0} 어디에 있어?",
        "{0} 위치 알려줘",
        "{0} 구매하고 싶어",
        "{0} 재고 있어?",
        "{0} 검색해줘",
        "다이소 {0} 있어?",
        "{0} 파나요?"
    ]
    
    queries = []
    
    # Generate variations
    # We need 100 queries. ~68 products.
    # Take all products once + random ~32 duplicates with different templates
    
    # First pass: 1 per product
    for p in products:
        t = random.choice(templates)
        queries.append((p, t.format(p)))
        
    # Second pass: fill up to 100
    while len(queries) < 100:
        p = random.choice(products)
        t = random.choice(templates)
        q = t.format(p)
        if (p, q) not in queries:
            queries.append((p, q))
            
    return queries[:100]

def run_verification():
    print("Generating 100 Test Queries...")
    test_set = generate_test_queries()
    
    results = []
    total_intent_success = 0
    total_search_success = 0
    
    print(f"Running tests on {len(test_set)} queries... (This may take a minute)")
    
    start_time_all = time.time()
    
    for i, (target_product, query) in enumerate(test_set):
        print(f"Processing {i+1}/{len(test_set)}: {query[:20]}...")
        
        start_time = time.time()
        try:
            # Invoke Graph with Config for MemorySaver
            config = {"configurable": {"thread_id": str(i)}}
            response = app.invoke({"query": query}, config=config)
            
            # Check Intent
            intent = response.get("intent", "unknown")
            is_direct = intent == "direct_search"
            if is_direct:
                total_intent_success += 1
                
            # Check Search Result
            final_res = response.get("final_response", "")
            keyword = response.get("keywords", "")
            
            # Success if NOT "검색 결과가 없습니다" and target keyword logic holds
            # We strictly check if results were found
            has_results = "검색 결과가 없습니다" not in final_res
            
            if has_results:
                total_search_success += 1
                
            results.append({
                "query": query,
                "target": target_product,
                "intent": intent,
                "keyword": keyword,
                "has_results": has_results,
                "response_snippet": final_res.split('\n')[0]
            })
            
        except Exception as e:
            print(f"Error on query {query}: {e}")
            results.append({
                "query": query,
                "target": target_product,
                "intent": "ERROR",
                "keyword": str(e),
                "has_results": False,
                "response_snippet": "Error during execution"
            })
            
    total_time = time.time() - start_time_all
    
    # Generate Report
    report_lines = []
    report_lines.append("=== Direct Search Verification Report ===")
    report_lines.append(f"Total Queries: {len(test_set)}")
    report_lines.append(f"Execution Time: {total_time:.2f}s")
    report_lines.append("-" * 50)
    report_lines.append(f"Intent Accuracy (direct_search): {total_intent_success}/100 ({total_intent_success}%)")
    report_lines.append(f"Search Success Rate (Found Items): {total_search_success}/100 ({total_search_success}%)")
    report_lines.append("=" * 50)
    report_lines.append("\nDetailed Logs:")
    report_lines.append(f"{'Query':<40} | {'Intent':<15} | {'Keyword':<15} | {'Found?'}")
    report_lines.append("-" * 90)
    
    for res in results:
        status = "✅" if res['has_results'] else "❌"
        line = f"{res['query']:<40} | {res['intent']:<15} | {res['keyword']:<15} | {status}"
        report_lines.append(line)
        
    # Write to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print("\n" + "="*30)
    print("Verification Complete!")
    print(f"Report saved to: {OUTPUT_FILE}")
    print(f"Intent Accuracy: {total_intent_success}%")
    print(f"Search Success: {total_search_success}%")
    print("="*30)

if __name__ == "__main__":
    run_verification()
