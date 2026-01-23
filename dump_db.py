import sqlite3
import os

# Absolute path to DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Project root
DB_PATH = os.path.join(BASE_DIR, 'backend', 'database', 'products.db')

print(f"Dumping DB from: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT id, name, category_major, category_middle FROM products")
rows = cursor.fetchall()
conn.close()

with open("db_dump.txt", "w", encoding="utf-8") as f:
    f.write(f"Total Products: {len(rows)}\n")
    f.write("-" * 50 + "\n")
    for row in rows:
        f.write(f"[{row[0]}] {row[1]} | {row[2]}/{row[3]}\n")

print(f"Dumped {len(rows)} products to db_dump.txt")
