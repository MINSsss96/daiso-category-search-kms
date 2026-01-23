import sqlite3
import os

# Set DB path relative to this script
DB_PATH = os.path.join(os.path.dirname(__file__), 'products.db')

MOCK_DATA = [
  { "id": "1001", "name": "욕실 미끄럼방지 매트 (그레이)", "category_major": "욕실용품", "category_middle": "안전용품", "price": 3000 },
  { "id": "1002", "name": "투명 논슬립 스티커 (10매)", "category_major": "욕실용품", "category_middle": "안전용품", "price": 1000 },
  { "id": "1003", "name": "강력 곰팡이 제거제 (젤타입)", "category_major": "청소용품", "category_middle": "욕실세제", "price": 2000 },
  { "id": "1004", "name": "배수구 냄새 차단 트랩", "category_major": "욕실용품", "category_middle": "배수구", "price": 2000 },
  { "id": "1005", "name": "규조토 발매트 (M)", "category_major": "욕실용품", "category_middle": "매트", "price": 5000 },
  { "id": "1006", "name": "다용도 수납 바구니 (중)", "category_major": "수납", "category_middle": "바구니", "price": 1000 },
  { "id": "1007", "name": "매직 스펀지 (대용량)", "category_major": "청소용품", "category_middle": "청소도구", "price": 2000 },
  { "id": "1008", "name": "스텐 배수구 거름망", "category_major": "주방용품", "category_middle": "싱크대", "price": 2000 },
  { "id": "1009", "name": "초파리 트랩 (용액포함)", "category_major": "청소용품", "category_middle": "살충제", "price": 2000 },
  { "id": "1010", "name": "방충망 보수 테이프", "category_major": "공구", "category_middle": "보수용품", "price": 1000 },
  { "id": "1011", "name": "의자 발커버 (4개입)", "category_major": "인테리어", "category_middle": "소품", "price": 1000 },
  { "id": "1012", "name": "방음 충격 흡수 패드", "category_major": "공구", "category_middle": "안전용품", "price": 1000 },
  { "id": "1013", "name": "틈새 먼지제거 브러쉬", "category_major": "청소용품", "category_middle": "청소도구", "price": 1000 },
  { "id": "1014", "name": "물기제거 스퀴지 (유리창닦이)", "category_major": "청소용품", "category_middle": "욕실청소", "price": 1000 },
  { "id": "1015", "name": "압축봉 (화이트/소형)", "category_major": "인테리어", "category_middle": "커튼봉", "price": 2000 },
  { "id": "1016", "name": "네트망 (69x33cm)", "category_major": "인테리어", "category_middle": "네트망", "price": 2000 },
  { "id": "1017", "name": "케이블 정리 박스", "category_major": "전기용품", "category_middle": "정리", "price": 3000 },
  { "id": "1018", "name": "실리콘 냄비받침", "category_major": "주방용품", "category_middle": "조리도구", "price": 2000 },
  { "id": "1019", "name": "전자레인지 덮개", "category_major": "주방용품", "category_middle": "보관용기", "price": 1000 },
  { "id": "1020", "name": "옷장용 제습제 (걸이형)", "category_major": "청소용품", "category_middle": "세탁", "price": 1000 },
  { "id": "1021", "name": "신발 냄새 제거 스프레이", "category_major": "청소용품", "category_middle": "방향제", "price": 2000 },
  { "id": "1022", "name": "극세사 걸레 (3매입)", "category_major": "청소용품", "category_middle": "청소도구", "price": 2000 },
  { "id": "1023", "name": "화장품 정리함 (아크릴)", "category_major": "수납", "category_middle": "화장대", "price": 3000 },
  { "id": "1024", "name": "방수 앞치마", "category_major": "주방용품", "category_middle": "패브릭", "price": 3000 },
  { "id": "1025", "name": "문닫힘 방지 스토퍼", "category_major": "육아/안전", "category_middle": "안전용품", "price": 1000 },
  { "id": "1026", "name": "모서리 보호대 (투명)", "category_major": "육아/안전", "category_middle": "안전용품", "price": 1000 },
  { "id": "1027", "name": "변기 세정제 (볼 타입)", "category_major": "청소용품", "category_middle": "욕실세제", "price": 1000 },
  { "id": "1028", "name": "싱크대 물막이", "category_major": "주방용품", "category_middle": "싱크대", "price": 2000 },
  { "id": "1029", "name": "다용도 S자 고리 (5개)", "category_major": "수납", "category_middle": "후크", "price": 1000 },
  { "id": "1030", "name": "창문 뽁뽁이 단열시트", "category_major": "인테리어", "category_middle": "단열", "price": 3000 },
  { "id": "2001", "name": "욕실 미끄럼방지 매트 (그레이)", "category_major": "청소/욕실", "category_middle": "욕실용품", "price": 5000 },
  { "id": "2002", "name": "배수구 냄새 차단 트랩", "category_major": "청소/욕실", "category_middle": "욕실용품", "price": 2000 },
  { "id": "2003", "name": "초파리 트랩 (용액포함)", "category_major": "청소/욕실", "category_middle": "방충용품", "price": 2000 },
  { "id": "2004", "name": "의자 발커버 (4개입/브라운)", "category_major": "인테리어/원예", "category_middle": "인테리어소품", "price": 1000 },
  { "id": "2005", "name": "곰팡이 제거 젤 (튜브형)", "category_major": "청소/욕실", "category_middle": "주방/청소세제", "price": 2000 },
  { "id": "2006", "name": "전선 정리 케이블 박스 (중)", "category_major": "공구/디지털", "category_middle": "전기용품", "price": 3000 },
  { "id": "2007", "name": "꼭꼬핀 (일자형/3개)", "category_major": "인테리어/원예", "category_middle": "인테리어소품", "price": 1000 },
  { "id": "2008", "name": "방충망 보수 테이프 (소)", "category_major": "청소/욕실", "category_middle": "방충용품", "price": 1000 },
  { "id": "2009", "name": "창문 뽁뽁이 단열시트", "category_major": "인테리어/원예", "category_middle": "시트지", "price": 3000 },
  { "id": "2010", "name": "의류 압축팩 (L)", "category_major": "수납/정리", "category_middle": "행거/리빙박스", "price": 1000 },
  { "id": "2011", "name": "싱크대 물막이 (투명)", "category_major": "주방용품", "category_middle": "싱크대용품", "price": 2000 },
  { "id": "2012", "name": "전선 보호 튜브 (2m)", "category_major": "공구/디지털", "category_middle": "전기용품", "price": 1000 },
  { "id": "2013", "name": "여행용 리필 용기 세트 (5p)", "category_major": "뷰티/위생", "category_middle": "미용소품", "price": 2000 },
  { "id": "2014", "name": "배수구 뻥 (1L)", "category_major": "청소/욕실", "category_middle": "청소용품", "price": 1000 },
  { "id": "2015", "name": "차량용 디퓨저 (블랙체리)", "category_major": "공구/디지털", "category_middle": "자동차용품", "price": 3000 },
  { "id": "2016", "name": "알카라인 건전지 AA (4개입)", "category_major": "공구/디지털", "category_middle": "전기용품", "price": 1000 },
  { "id": "2017", "name": "물티슈 (100매/캡형)", "category_major": "청소/욕실", "category_middle": "휴지통/비닐봉투", "price": 1000 },
  { "id": "2018", "name": "초강력 순간접착제 (젤타입)", "category_major": "문구/팬시", "category_middle": "사무용품", "price": 1000 },
  { "id": "2019", "name": "사무용 가위 커터칼 세트", "category_major": "문구/팬시", "category_middle": "사무용품", "price": 2000 },
  { "id": "2020", "name": "아이폰 8핀 고속충전 케이블 (1m)", "category_major": "공구/디지털", "category_middle": "디지털/모바일", "price": 2000 },
  { "id": "2021", "name": "투명 L홀더 파일 A4 (10매)", "category_major": "문구/팬시", "category_middle": "파일/바인더", "price": 1000 },
  { "id": "2022", "name": "쓰레기봉투 20L (20매)", "category_major": "청소/욕실", "category_middle": "휴지통/비닐봉투", "price": 1000 },
  { "id": "2023", "name": "일회용 종이컵 (50개입)", "category_major": "주방용품", "category_middle": "일회용품", "price": 1000 },
  { "id": "2024", "name": "대나무 젓가락 (100개입)", "category_major": "주방용품", "category_middle": "일회용품", "price": 1000 },
  { "id": "2025", "name": "매직스펀지 (대용량/큐브형)", "category_major": "청소/욕실", "category_middle": "청소용품", "price": 2000 },
  { "id": "2026", "name": "EVA 욕실 슬리퍼 (260mm)", "category_major": "청소/욕실", "category_middle": "욕실용품", "price": 3000 },
  { "id": "2027", "name": "다이어리 마스킹 테이프 (체크)", "category_major": "문구/팬시", "category_middle": "포장/파티", "price": 1000 },
  { "id": "2028", "name": "스테인리스 빨대 세트 (세척솔포함)", "category_major": "주방용품", "category_middle": "테이블웨어", "price": 2000 },
  { "id": "2029", "name": "전자레인지용 덮개 (대)", "category_major": "주방용품", "category_middle": "보관용기", "price": 1000 },
  { "id": "2030", "name": "3단 자동 우산 (블랙)", "category_major": "패션/잡화", "category_middle": "우산/양산", "price": 5000 },
  { "id": "3001", "name": "내열 유리컵 (350ml)", "category_major": "주방용품", "category_middle": "컵/텀블러", "price": 2000 },
  { "id": "3002", "name": "도자기 대접 (화이트)", "category_major": "주방용품", "category_middle": "식기", "price": 3000 },
  { "id": "3003", "name": "바디 샤워볼 (핑크)", "category_major": "청소/욕실", "category_middle": "욕실용품", "price": 1000 },
  { "id": "3004", "name": "컬러 점착 메모지 (75x75mm)", "category_major": "문구/팬시", "category_middle": "노트/메모", "price": 1000 },
  { "id": "3005", "name": "헬로키티 캐릭터 빗", "category_major": "뷰티/위생", "category_middle": "미용소품", "price": 2000 },
  { "id": "3006", "name": "카카오프렌즈 칫솔 (라이언)", "category_major": "뷰티/위생", "category_middle": "구강관리", "price": 2000 },
  { "id": "3007", "name": "롤클리너 리필 (2개입)", "category_major": "청소/욕실", "category_middle": "청소도구", "price": 2000 },
  { "id": "3008", "name": "규조토 비누 받침대 (그레이)", "category_major": "청소/욕실", "category_middle": "욕실용품", "price": 2000 },
  { "id": "3009", "name": "벽걸이 칫솔 꽂이 (4구)", "category_major": "청소/욕실", "category_middle": "욕실용품", "price": 1000 },
  { "id": "3010", "name": "크린랩 (30cm x 50m)", "category_major": "주방용품", "category_middle": "주방소모품", "price": 2000 }
]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def safe_init_category_tables():
    """Ensure category columns exist"""
    print("Checking database schema...")
    conn = get_connection()
    cursor = conn.cursor()
    
    # Add category columns to products table if not exists
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN category_major TEXT')
        print("  - Added column: category_major")
    except:
        pass # Already exists
        
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN category_middle TEXT')
        print("  - Added column: category_middle")
    except:
        pass # Already exists
    
    conn.commit()
    conn.close()

def insert_data():
    conn = get_connection()
    cursor = conn.cursor()
    
    print(f"Connecting to database: {DB_PATH}")
    print("Processing mock data...")
    
    new_count = 0
    update_count = 0
    
    for item in MOCK_DATA:
        name = item['name']
        price = item['price']
        major = item['category_major']
        middle = item['category_middle']
            
        # Check if product already exists
        cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing product
            cursor.execute('''
                UPDATE products 
                SET price = ?, category_major = ?, category_middle = ?
                WHERE name = ?
            ''', (price, major, middle, name))
            update_count += 1
        else:
            # Insert new product
            cursor.execute('''
                INSERT INTO products (name, price, category_major, category_middle, rank)
                VALUES (?, ?, ?, ?, 0)
            ''', (name, price, major, middle))
            new_count += 1
            
    conn.commit()
    conn.close()
    
    print("-" * 30)
    print(f"Success!")
    print(f"  - Inserted: {new_count}")
    print(f"  - Updated:  {update_count}")
    print("-" * 30)

if __name__ == "__main__":
    try:
        safe_init_category_tables()
        insert_data()
    except Exception as e:
        print(f"Error: {e}")
