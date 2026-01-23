import sqlite3
import os

# Set DB path relative to this script
DB_PATH = os.path.join(os.path.dirname(__file__), 'products.db')

TEST_QUERIES = [
    # --- 문제 해결형 (의도 파악 필요) -> 'hard' difficulty ---
    ("화장실 바닥이 물기 때문에 너무 미끄러워.", "hard"),
    ("싱크대 배수구에서 냄새가 너무 심하게 올라와.", "hard"),
    ("여름이라 자꾸 초파리가 날아다니는데 잡는 거 있어?", "hard"),
    ("윗집 층간소음 때문에 그런데 의자 끄는 소리 안 나게 하는 거 뭘 사야 해?", "hard"),
    ("욕실 타일 사이사이에 낀 까만 곰팡이 좀 없애고 싶어.", "hard"),
    ("책상 밑에 전선들이 너무 지저분하게 엉켜 있어.", "hard"),
    ("벽지에 못질 안 하고 액자 걸 수 있는 방법 있을까?", "hard"),
    ("방충망에 구멍이 나서 거기로 벌레가 들어오는 것 같아.", "hard"),
    ("겨울 되니까 창문에서 찬바람이 너무 들어와.", "hard"),
    ("옷장에 옷이 너무 많아서 공간이 부족해.", "hard"),
    ("설거지하고 나면 앞치마가 다 젖어서 불편해.", "hard"),
    ("강아지가 자꾸 전선을 물어뜯어.", "hard"),
    ("여행 가는데 샴푸랑 로션 덜어갈 통 필요해.", "hard"),
    ("세면대 물이 잘 안 내려가고 꽉 막혔어.", "hard"),
    ("새 차 샀는데 차 안에 둘 만한 냄새 좋은 거 추천해줘.", "hard"),

    # --- 상품 직접 검색형 (키워드 매칭) -> 'normal' difficulty ---
    ("AA 건전지 묶음 있어?", "normal"),
    ("물티슈 100매짜리 찾아줘.", "normal"),
    ("순간접착제 어디 있어?", "normal"),
    ("커터칼이랑 가위 세트.", "normal"),
    ("아이폰 충전 케이블.", "normal"),
    ("A4 용지 파일철.", "normal"),
    ("쓰레기봉투 20리터.", "normal"),
    ("일회용 종이컵.", "normal"),
    ("나무젓가락 100개입.", "normal"),
    ("매직블럭.", "normal"),
    ("욕실용 슬리퍼.", "normal"),
    ("다이어리 꾸미기용 마스킹 테이프.", "normal"),
    ("스테인리스 빨대.", "normal"),
    ("전자레인지용 덮개.", "normal"),
    ("3단 우산.", "normal")
]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_test_table():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ensure table exists (re-using definition from database.py but adding flexibility)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_utterances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utterance TEXT NOT NULL,
            difficulty TEXT CHECK(difficulty IN ('normal', 'hard')),
            expected_product_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (expected_product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()

def insert_queries():
    conn = get_connection()
    cursor = conn.cursor()
    
    print(f"Connecting to database: {DB_PATH}")
    print("Inserting test queries...")
    
    count = 0
    for query, difficulty in TEST_QUERIES:
        # Check if already exists to avoid duplicates
        cursor.execute("SELECT 1 FROM test_utterances WHERE utterance = ?", (query,))
        if cursor.fetchone():
            continue
            
        cursor.execute('''
            INSERT INTO test_utterances (utterance, difficulty)
            VALUES (?, ?)
        ''', (query, difficulty))
        count += 1
            
    conn.commit()
    conn.close()
    
    print("-" * 30)
    print(f"Success! Inserted {count} new test queries.")
    print("-" * 30)

if __name__ == "__main__":
    init_test_table()
    insert_queries()
