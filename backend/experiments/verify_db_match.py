import os
import sys
import time
import random
import sqlite3
from typing import List, Dict

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend.logic.graph import app

DB_PATH = os.path.join(BASE_DIR, 'backend', 'database', 'products.db')
OUTPUT_FILE = os.path.join(BASE_DIR, 'backend', 'database', 'db_match_report.txt')

def get_random_products(conn, limit=30) -> List[Dict]:
    """Fetch random products from DB for testing."""
    cursor = conn.cursor()
    cursor.execute("SELECT name, category_major FROM products ORDER BY RANDOM() LIMIT ?", (limit,))
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def normalize_category(category_name: str) -> str:
    """Normalizes a category name for consistent comparison."""
    return category_name.lower().strip()

def generate_variant_queries(product_name: str) -> Dict[str, str]:
    """
    Generate 5 types of queries with diverse attributes/patterns.
    """
    # Random choice pools
    colors = ["빨간색", "검정색", "흰색", "파란색", "노란색"]
    materials = ["플라스틱", "스텐", "유리", "나무", "실리콘"]
    sizes = ["큰", "작은", "대형", "소형", "미니", "긴"]
    
    # Pick a random attribute strategy
    attr_type = random.choice(["color", "material", "size"])
    if attr_type == "color":
        attr_prefix = random.choice(colors)
    elif attr_type == "material":
        attr_prefix = random.choice(materials)
    else:
        attr_prefix = random.choice(sizes)

    # Alias Mapping (Official Key -> Slang List)
    alias_map = {
        "단열시트": ["뽁뽁이", "에어캡"],
        "롤클리너": ["돌돌이", "찍찍이"],
        "점착 메모지": ["포스트잇", "메모지"],
        "매직 스펀지": ["매직블럭", "매직클리너"],
        "반창고": ["대일밴드", "밴드"],
        "스테이플러": ["호치키스"],
        "투명 테이프": ["스카치테이프"],
        "순간접착제": ["본드", "강력접착제", "순접"],
        "배수구": ["뚫어뻥", "배수구 뻥", "락스"],
        "건전지": ["배터리"],
        "걸레": ["대걸레", "밀대", "청소포"],
        "휴지통": ["쓰레기통", "분리수거함"],
        "세정제": ["락스", "청소세제"],
        "립밤": ["입술보호제", "챕스틱"],
        "핸드크림": ["손로션"],
        "마우스": ["쥐돌이"],
        "보조배터리": ["보배"],
        "충전기": ["밥통"],
        "우산": ["비닐우산"],
        "슬리퍼": ["실내화", "쓰레빠"]
    }
    
    # Logic: If product name contains a key, use its alias. Else use varied natural fallback.
    alias_variants = [
        f"{product_name} 대용품 찾고 있어요",
        f"{product_name}랑 비슷한 거 뭐 있나요?",
        f"{product_name} 종류 좀 보여주세요",
        f"{product_name} 대신 쓸만한 거 있나요?"
    ]
    alias_query = random.choice(alias_variants)
    
    for official, slangs in alias_map.items():
        if official in product_name:
            chosen_alias = random.choice(slangs)
            alias_query = f"{chosen_alias} 있어요?"
            break

    # Natural Sentence Endings
    endings = ["있나요?", "어디에요?", "어디 있어요?", "찾는데요", "주세요", "재고 있어요?", "어딨죠?", "파나요?"]
    
    def get_ending():
        return random.choice(endings)

    # 1. Basic
    query_basic = f"{product_name} {get_ending()}"
    
    # 2. Attribute
    query_attribute = f"{attr_prefix} {product_name} {get_ending()}"
    
    # 3. Alias (Logic already refined, just apply ending if needed, but alias_variants usually have full sentences)
    # Re-using refined alias logic from previous step, but ensuring variety.
    
    # 4. Brand/Character Mapping
    brand_map = {
        "테이프": ["3M", "스카치", "돼지표"],
        "접착제": ["3M", "돼지표", "록타이트"],
        "청소": ["유한락스", "LG", "홈스타", "베이킹소다"],
        "세제": ["유한락스", "피죤", "비트", "퍼실"],
        "치약": ["페리오", "2080", "죽염", "센소다인"],
        "칫솔": ["오랄비", "페리오"],
        "랩": ["크린랩", "지퍼락"],
        "봉투": ["크린랩", "쓰레기"],
        "건전지": ["에너자이저", "듀라셀", "벡셀"],
        "마우스": ["로지텍", "삼성", "앱코"],
        "충전기": ["삼성", "아이폰", "벨킨"],
        "캐릭터": ["카카오", "헬로키티", "짱구", "디즈니", "춘식이", "산리오", "쿠로미"],
        "인형": ["카카오", "디즈니", "춘식이", "포켓몬"],
        "방향제": ["페브리즈", "양키캔들"],
        "문구": ["모나미", "제트스트림", "3M"],
        "컵": ["춘식이", "미키무스", "스타벅스ST"],
        "텀블러": ["스텐", "락앤락", "써모스"]
    }
    
    # Generic Brand Pool
    generic_brands = ["다이소", "LG", "삼성", "3M", "카카오", "네이처", "홈플러스", "이마트", "노브랜드"]

    brand = "다이소" 
    matched = False
    for keyword, brands in brand_map.items():
        if keyword in product_name:
            brand = random.choice(brands)
            matched = True
            break
            
    if not matched:
        brand = random.choice(generic_brands)
        
    query_brand = f"{brand} {product_name} {get_ending()}"

    # 5. Part Logic (Refined)
    # Part/Refill Mapping (Keyword -> Suffix List)
    part_map = {
        "샤워": ["필터", "헤드", "줄"],
        "펜": ["심", "잉크", "리필심"],
        "클리너": ["리필"],
        "테이프": ["리필", "커터기"],
        "제습제": ["리필"],
        "칫솔": ["꽂이", "걸이", "살균기"],
        "면도기": ["날", "거치대"],
        "비누": ["받침대", "곽", "망"],
        "화분": ["받침", "영양제"],
        "냄비": ["받침대"],
        "디퓨저": ["리필액", "스틱", "공병"],
        "방향제": ["리필"],
        "병": ["뚜껑", "마개", "세척솔"],
        "텀블러": ["세척솔", "뚜껑", "빨대"],
        "구두": ["약", "깔창", "끈"],
        "신발": ["깔창", "끈", "탈취제"]
    }
    
    # Generic Fallbacks
    generic_parts = ["리필", "부속품", "교체용", "액세서리", "거치대", "케이스"]
    
    part_suffix = "부속품" # Default
    matched_part = False
    for keyword, parts in part_map.items():
        if keyword in product_name:
            part_suffix = random.choice(parts)
            matched_part = True
            break
            
    if not matched_part:
        part_suffix = random.choice(generic_parts)

    query_part = f"{product_name} {part_suffix} {random.choice(['있나요?', '따로 팔아요?', '구매 가능한가요?', '찾고 있어요'])}"

    return {
        "1. Basic": query_basic,
        "2. Attribute": query_attribute,
        "3. Alias": alias_query, 
        "4. Brand": query_brand, 
        "5. Part": query_part
    }

def run_db_verification():
    print(f"🔌 Connecting to DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Check total count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    total_db_count = cursor.fetchone()[0]
    
    # 2. Get random sample (Reduced to 6 products x 5 types = 30 tests total, or user wants 30 products?)
    # User said "randomly 30". If we do 30 products * 5 questions = 150 tests. That's good.
    limit = 30
    products = get_random_products(conn, limit)
    conn.close()
    
    print(f"📦 Total Products in DB: {total_db_count}")
    print(f"🎯 Selected {len(products)} products. Generating 5 query variants for each (Total {len(products)*5} tests).")
    print("🚀 Starting Kiosk Logic Verification...", flush=True)
    
    report_lines = []
    report_lines.append(f"🧪 Kiosk Logic Verification Report (5-Type Robustness)")
    report_lines.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Target: Verify if AI maps varied queries to correct 'Category Major'.")
    report_lines.append("=" * 155)
    report_lines.append(f"{'Target Product':<25} | {'Type':<12} | {'Query':<35} | {'Expected Major':<18} | {'Actual Major':<18} | {'Result'}")
    report_lines.append("-" * 155)
    
    passed_count = 0
    total_tests = 0
    
    # Store results by type for grouped reporting
    # structure: { "1. Basic": [ {line_data}, ... ], ... }
    results_by_type = {k: [] for k in generate_variant_queries("test").keys()}
    type_stats = {k: {"pass": 0, "total": 0} for k in results_by_type.keys()}
    
    for product in products:
        target_name = product['name']
        expected_major = product['category_major']
        
        # Generator 5 variants
        variants = generate_variant_queries(target_name)
        
        for q_type, query in variants.items():
            total_tests += 1
            type_stats[q_type]["total"] += 1
            
            # Run AI Logic
            config = {"configurable": {"thread_id": f"verify_{random.randint(10000,99999)}"}}
            
            try:
                response = app.invoke({"query": query}, config=config)
                
                # Extract Result
                actual_major = "Not Found"
                search_results = response.get("search_results", [])
                match_found = False
                
                if search_results:
                    first_item = search_results[0]
                    actual_major = first_item.get('category_major', 'Unknown')
                    
                    # STRICT MATCH
                    if normalize_category(expected_major) == normalize_category(actual_major):
                        match_found = True
                
                status = "✅" if match_found else "❌"
                if match_found: 
                    passed_count += 1
                    type_stats[q_type]["pass"] += 1
                
                # Store result row
                row_str = f"{target_name[:25]:<25} | {query[:35]:<35} | {expected_major[:18]:<18} | {actual_major[:18]:<18} | {status}"
                results_by_type[q_type].append(row_str)
                
            except Exception as e:
                err_row = f"{target_name[:25]:<25} | {query[:35]:<35} | {expected_major[:18]:<18} | ERROR              | ❌ Error"
                results_by_type[q_type].append(err_row)
                print(f"Error on {query}: {e}")

    # Generate Grouped Report
    for q_type, rows in results_by_type.items():
        report_lines.append(f"\n[{q_type}] Results")
        report_lines.append("-" * 155)
        report_lines.append(f"{'Target Product':<25} | {'Query':<35} | {'Expected Major':<18} | {'Actual Major':<18} | {'Result'}")
        report_lines.append("-" * 155)
        report_lines.extend(rows)
        
        # Type Statistics
        t_pass = type_stats[q_type]["pass"]
        t_total = type_stats[q_type]["total"]
        t_rate = (t_pass / t_total * 100) if t_total > 0 else 0
        report_lines.append("-" * 155)
        report_lines.append(f"   >> {q_type} Accuracy: {t_pass}/{t_total} ({t_rate:.1f}%)")
        report_lines.append("=" * 155)

    report_lines.append(f"\nTotal Success Rate: {passed_count}/{total_tests} ({passed_count/total_tests*100:.1f}%)")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print("\n" + "="*30)
    print("Verification Complete!")
    print(f"Report: {OUTPUT_FILE}")
    print("="*30)

if __name__ == "__main__":
    run_db_verification()
