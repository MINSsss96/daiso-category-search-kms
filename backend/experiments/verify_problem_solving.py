import os
import sys
import time
import random

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend.logic.graph import app
from backend.database.insert_mock_data import MOCK_DATA

OUTPUT_FILE = os.path.join(BASE_DIR, 'backend', 'database', 'problem_solving_report.txt')

# Define some templates to generate problems from product names/categories
PROBLEM_TEMPLATES = [
    ("청소/욕실", ["화장실이 너무 더러워", "욕실 청소해야 돼", "타일에 곰팡이가 생겼어", "배수구가 막혔어"]),
    ("주방용품", ["설거지할 때 불편해", "음식 보관이 힘들어", "싱크대 물이 튀어", "주방 정리가 안 돼"]),
    ("수납/정리", ["방이 너무 지저분해", "물건 정리할 공간이 부족해", "책상이 엉망이야", "옷장에 자리가 없어"]),
    ("공구/디지털", ["전선이 꼬였어", "건전지가 다 떨어졌어", "핸드폰 충전이 안 돼", "뭔가를 고쳐야 해"]),
    ("인테리어", ["방 분위기를 바꾸고 싶어", "벽이 허전해", "바닥 긁힘 방지가 필요해", "창문으로 바람이 들어와"]),
    ("문구/팬시", ["공부할 때 필요한 게 없어", "서류 정리가 안 돼", "편지를 쓰고 싶어", "다이어리 꾸미고 싶어"]),
    ("뷰티/위생", ["여행 갈 때 덜어가야 해", "화장솜이 필요해", "머리끈이 없어", "손톱 정리가 필요해"]),
    ("펫", ["강아지 간식이 필요해", "고양이 장난감이 없어", "반려동물 털이 날려", "배변 처리가 곤란해"])
]

def generate_scenarios():
    scenarios = []
    
    # Create mapping of category -> keywords
    # We will try to map products to general problems
    
    # To get 100 queries, we'll iterate products and assign a "Problem" that *might* be relevant
    # This is imperfect without manual mapping, but we can simulate the "Selection" phase well.
    
    # Strategy:
    # 1. Pick a product from MOCK_DATA.
    # 2. Pick a problem template based on its category.
    # 3. Set the product name as the "Target".
    # 4. In the test loop, if options are presented, we look for the option most similar to the Target.
    
    used_problems = set()
    
    while len(scenarios) < 100:
        target_item = random.choice(MOCK_DATA)
        major_cat = target_item['category_major']
        
        # Find relevant templates
        templates = []
        for cat_key, temps in PROBLEM_TEMPLATES:
            if cat_key in major_cat or major_cat in cat_key:
                templates.extend(temps)
        
        if not templates:
            templates = ["생활에 불편함이 있어", "집안일이 힘들어", "뭔가 필요해"] # Generic fallback
            
        problem = random.choice(templates)
        
        # Add some variation to problem string to avoid exact dupes in LLM cache/logs
        # (e.g. append random spaces or slight variations if strictly needed, but here simple dupes are okay)
        
        scenarios.append({
            "problem": problem,
            "target_product": target_item['name'],
            "target_id": target_item['id'],
            "target_keywords": target_item['name'].split() # Simple keyword list
        })
        
    return scenarios

def select_best_option(options_text, target_product):
    """
    options_text: "1. 곰팡이 제거제, 2. 청소솔, 3. 락스"
    target_product: "강력 곰팡이 제거제 (젤타입)"
    
    Logic: Find option index with highest token overlap with target_product.
    """
    try:
        # Parse options: Assume "N. Text" format
        options = {}
        # Split by comma or newline
        # Heuristic split
        parts = options_text.replace('\n', ',').split(',')
        
        for part in parts:
            part = part.strip()
            if not part: continue
            # Extract number
            if '.' in part:
                num_str, content = part.split('.', 1)
                if num_str.strip().isdigit():
                    options[num_str.strip()] = content.strip()
        
        if not options:
            return "1" # Fallback
            
        best_opt = "1"
        max_score = -1
        
        target_tokens = set(target_product.split())
        
        for num, content in options.items():
            content_tokens = set(content.split())
            # Overlap score
            # Simple exact match of words
            score = 0
            for t in target_tokens:
                for c in content_tokens:
                    if t in c or c in t: # Substring match
                        score += 1
            
            if score > max_score:
                max_score = score
                best_opt = num
                
        return best_opt
    except:
        return "1"

def run_verification():
    print("Generating 100 Problem Scenarios...")
    scenarios = generate_scenarios()
    
    results = []
    success_count = 0
    
    print(f"Running tests on {len(scenarios)} scenarios... (This allows checking clarification logic)")
    
    for i, scenario in enumerate(scenarios):
        problem = scenario['problem']
        target = scenario['target_product']
        print(f"[{i+1}/100] Prob: {problem} -> Target: {target}")
        
        # Config for state memory
        config = {"configurable": {"thread_id": f"test_prob_{i}"}}
        
        try:
            # 1. Send Problem
            response = app.invoke({"query": problem}, config=config)
            
            final_res = response.get("final_response", "")
            clarification_opts = response.get("clarification_options")
            
            # 2. Handle Clarification
            if clarification_opts:
                print(f"    -> Clarification Asked: {clarification_opts}")
                
                # Auto-select best option
                selection = select_best_option(clarification_opts, target)
                print(f"    -> Auto-selecting: {selection}")
                
                # Send Selection
                response = app.invoke({"query": selection}, config=config)
                final_res = response.get("final_response", "")
            
            # 3. Check Result
            # Success if target name (or significant part) is in final response
            # Or if ANY result was found (looser condition)
            
            has_results = "검색 결과가 없습니다" not in final_res
            keyword = response.get("keywords", "N/A")
            
            # Refined success: Did we find the *intended* product?
            # Check if target_product name is in the response text
            # (Note: response usually lists names)
            found_specific = target in final_res
            
            status = "FOUND" if has_results else "MISS"
            
            results.append({
                "problem": problem,
                "target": target,
                "clarification": clarification_opts if clarification_opts else "None (Direct)",
                "selection": selection if clarification_opts else "N/A",
                "final_keyword": keyword,
                "status": status,
                "found_target": found_specific
            })
            
            if has_results:
                success_count += 1
                
        except Exception as e:
            print(f"    -> Error: {e}")
            results.append({
                "problem": problem,
                "target": target,
                "status": "ERROR",
                "error": str(e)
            })

    # Report
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== Problem Solving & Clarification Report ===\n")
        f.write(f"Total Scenarios: {len(scenarios)}\n")
        f.write(f"Any Result Found: {success_count}/100\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Problem':<25} | {'Target':<20} | {'Clarification Opts':<30} | {'Sel':<3} | {'Result'}\n")
        f.write("-" * 80 + "\n")
        
        for r in results:
            if "error" in r:
                f.write(f"{r['problem'][:20]:<25} | {r['target'][:20]:<20} | ERROR: {r['error']}\n")
                continue
                
            clarif_short = (r['clarification'][:28] + "..") if len(r['clarification']) > 30 else r['clarification']
            found_mark = "✅" if r['status'] == "FOUND" else "❌"
            
            f.write(f"{r['problem'][:25]:<25} | {r['target'][:20]:<20} | {clarif_short:<30} | {r['selection']:<3} | {found_mark} ({r['final_keyword']})\n")

    print("\n" + "="*30)
    print("Verification Complete!")
    print(f"Report saved to: {OUTPUT_FILE}")
    print("="*30)

if __name__ == "__main__":
    run_verification()
