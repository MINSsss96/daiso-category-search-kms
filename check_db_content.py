import sqlite3
import os

# Define path exact same way as graph.py
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'database', 'products.db')
# Wait, graph.py is in backend/logic.
# os.path.dirname(__file__) in check_db.py (root) -> root.
# Let's just use absolute path logic or relative to root.
# Current CWD is root.
DB_PATH = os.path.abspath("backend/database/products.db")

print(f"Checking DB at: {DB_PATH}")

if not os.path.exists(DB_PATH):
    print("❌ DB file does not exist!")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Searching for '대나무' ---")
    cursor.execute("SELECT * FROM products WHERE name LIKE '%대나무%'")
    rows = cursor.fetchall()
    
    if not rows:
        print("❌ No products found with '대나무'.")
    else:
        for row in rows:
            print(f"✅ Found: {row}")
            
    print("\n--- Total Count ---")
    cursor.execute("SELECT count(*) FROM products")
    print(f"Total rows: {cursor.fetchone()[0]}")
    
    conn.close()
