import sqlite3
import os

DB_PATH = os.path.join("backend", "database", "products.db")

def inspect_db_pretty():
    if not os.path.exists(DB_PATH):
        print(f"File not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n🔍 DAISO PRODUCT DATABASE INSPECTION 🔍\n")

    # Get formatting width
    col_widths = {
        "ID": 5,
        "Name": 30,
        "Price": 10,
        "Category": 15,
        "Image": 30
    }
    
    header = f"| {'ID':<{col_widths['ID']}} | {'Name':<{col_widths['Name']}} | {'Price':<{col_widths['Price']}} | {'Image':<{col_widths['Image']}} |"
    separator = f"|{'-' * (col_widths['ID']+2)}|{'-' * (col_widths['Name']+2)}|{'-' * (col_widths['Price']+2)}|{'-' * (col_widths['Image']+2)}|"

    try:
        cursor.execute("SELECT * FROM products ORDER BY id LIMIT 20")
        rows = cursor.fetchall()
        
        if not rows:
            print("No products found in the database.")
        else:
            print(separator)
            print(header)
            print(separator)
            
            for row in rows:
                p_id = str(row['id'])
                name = row['name'] or ""
                # Truncate long names
                if len(name) > 28:
                    name = name[:25] + "..."
                
                price = f"{row['price']:,} KRW" if row['price'] else "N/A"
                
                img = row['image_name'] or ""
                if len(img) > 28:
                    img = img[:25] + "..."

                print(f"| {p_id:<{col_widths['ID']}} | {name:<{col_widths['Name']}} | {price:<{col_widths['Price']}} | {img:<{col_widths['Image']}} |")
            
            print(separator)
            
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total Products: {count}")
        
    except Exception as e:
        print(f"Error querying products: {e}")

    conn.close()

if __name__ == "__main__":
    inspect_db_pretty()
