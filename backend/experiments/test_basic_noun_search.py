import os
import sys
import sqlite3
import random
import time

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend.logic.graph import app

DB_PATH = os.path.join(BASE_DIR, 'backend', 'database', 'products.db')
OUTPUT_FILE = os.path.join(BASE_DIR, 'backend', 'database', 'test_basic_noun_report.txt')

def get_random_products(limit=30):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name, category_major, category_middle FROM products ORDER BY RANDOM() LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def generate_query(product_name):
    templates = [
        "{0} 어디 있어요?",
        "{0} 어디에 있나요?",
        "{0} 위치 알려줘",
        "{0} 찾고 싶어"
    ]
    return random.choice(templates).format(product_name)

def run_test():
    print("Fetching 30 random products...", flush=True)
    products = get_random_products(30)
    
    results = []
    
    print(f"Running Basic Noun Test on {len(products)} products...", flush=True)
    
    for i, item in enumerate(products):
        name = item['name']
        # Use only the core name if possible (e.g. remove parentheses for query generation for realism)
        # But user asked to use products based on DB. Let's use full name or simplified.
        # "가위 어디 있어요?" -> "사무용 가위 커터칼 세트" might be the name.
        # Let's use the full name for exact match testing first.
        
        query = generate_query(name)
        print(f"[{i+1}/30] Testing: {query}", flush=True)
        
        config = {"configurable": {"thread_id": f"basic_noun_{i}"}}
        
        try:
            start = time.time()
            response = app.invoke({"query": query}, config=config)
            duration = time.time() - start
            
            intent = response.get("intent", "unknown")
            final_res = response.get("final_response", "")
            
            # Check Intent
            intent_pass = (intent == "direct_search")
            
            # Check Search Result
            # We expect the specific product to be in the list
            found = name in final_res
            
            # Extract Category from DB data for verification display
            expected_cat = f"{item['category_major']}/{item['category_middle']}"
            
            results.append({
                "product": name,
                "query": query,
                "intent": intent,
                "intent_pass": intent_pass,
                "found": found,
                "category": expected_cat,
                "response": final_res.replace('\n', ' ')[:100] + "..."
            })
            
        except Exception as e:
            print(f"  -> Error: {e}")
            results.append({
                "product": name,
                "query": query,
                "intent": "ERROR",
                "intent_pass": False,
                "found": False,
                "category": "Error",
                "response": str(e)
            })

    # Generate Report
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("📋 1. 기본형 (Basic Noun) 테스트 결과\n")
        f.write(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Samples: {len(products)}\n")
        f.write("-" * 120 + "\n")
        f.write(f"{'Product':<30} | {'Query':<30} | {'Intent':<15} | {'Category':<20} | {'Found?'}\n")
        f.write("-" * 120 + "\n")
        
        pass_count = 0
        for r in results:
            mark = "✅" if (r['intent_pass'] and r['found']) else "❌"
            if mark == "✅": pass_count += 1
            
            f.write(f"{r['product'][:30]:<30} | {r['query'][:30]:<30} | {r['intent']:<15} | {r['category']:<20} | {mark}\n")
            
        f.write("-" * 120 + "\n")
        f.write(f"Success Rate: {pass_count}/{len(products)} ({pass_count/len(products)*100:.1f}%)\n")

    print("\n" + "="*30)
    print("Test Complete!")
    print(f"Saved to: {OUTPUT_FILE}")
    print(f"Success Rate: {pass_count}/{len(products)}")
    print("="*30)

if __name__ == "__main__":
    run_test()
