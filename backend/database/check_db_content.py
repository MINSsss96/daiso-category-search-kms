import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'products.db')

def check():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Checking for specific new items...")
    targets = ["유리컵", "키티", "리필", "3단", "샤워볼"]
    
    for t in targets:
        cursor.execute("SELECT id, name, category_major FROM products WHERE name LIKE ?", (f"%{t}%",))
        rows = cursor.fetchall()
        print(f"[{t}] Found {len(rows)} items:")
        for r in rows:
            print(f"  - {r}")
            
    conn.close()

if __name__ == "__main__":
    check()
