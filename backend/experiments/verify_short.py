import os
import sys
import sqlite3
import time

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend.logic.graph import app

OUTPUT_FILE = os.path.join(BASE_DIR, 'backend', 'database', 'short_report.txt')

def run_short_test():
    print("Starting Short Verification (5 items)...", flush=True)
    
    queries = [
        "물티슈 있어?",
        "대나무 젓가락 파나요?",
        "화장실이 미끄러워", # Should trigger intent analysis -> problem solving
        "AA 건전지",
        "3단 우산 구매"
    ]
    
    results = []
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== Short Verification Report ===\n")
    
    for i, q in enumerate(queries):
        print(f"Testing {i+1}: {q}", flush=True)
        try:
            start = time.time()
            response = app.invoke({"query": q})
            duration = time.time() - start
            
            intent = response.get("intent", "unknown")
            final_res = response.get("final_response", "")
            
            # Simple check
            status = "FOUND" if "검색 결과가 없습니다" not in final_res else "NOT FOUND"
            
            log_line = f"Query: {q:<20} | Intent: {intent:<15} | Status: {status} | Time: {duration:.2f}s"
            print(f"  -> {log_line}", flush=True)
            
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
                
        except Exception as e:
            print(f"  -> Error: {e}", flush=True)
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"Query: {q} | ERROR: {e}\n")

    print(f"Done! Saved to {OUTPUT_FILE}", flush=True)

if __name__ == "__main__":
    run_short_test()
