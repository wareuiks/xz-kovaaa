from database import get_db

def update_prices():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("UPDATE products SET price = 150.0 WHERE duration = '14 DAYS'")
    cur.execute("UPDATE products SET price = 250.0 WHERE duration = '30 DAYS'")
    cur.execute("UPDATE products SET price = 320.0 WHERE duration = '60 DAYS'")
    conn.commit()
    
    cur.execute("SELECT id, name, duration, price FROM products ORDER BY id ASC")
    rows = cur.fetchall()
    print("UPDATED PRODUCTS:")
    for r in rows:
        print(dict(r) if hasattr(r, 'keys') else r)
    conn.close()

if __name__ == '__main__':
    update_prices()
