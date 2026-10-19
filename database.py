import sqlite3
import os
import json
import hashlib
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
DB_PATH = os.path.join(os.path.dirname(__file__), 'shop.db')

def is_postgres():
    return bool(DATABASE_URL and (DATABASE_URL.startswith('postgres://') or DATABASE_URL.startswith('postgresql://')))

class PgCursorWrapper:
    def __init__(self, pg_cursor):
        self.cursor = pg_cursor
        self.lastrowid = None

    def execute(self, query, params=None):
        clean_query = query.replace('%', '%%').replace('?', '%s')
        is_insert = clean_query.strip().upper().startswith('INSERT INTO')
        has_returning = 'RETURNING' in clean_query.upper()
        
        # If insert without RETURNING id, append RETURNING id to capture lastrowid
        if is_insert and not has_returning:
            clean_query = clean_query.rstrip().rstrip(';') + ' RETURNING id;'
            
        if params is not None:
            if isinstance(params, (list, tuple)):
                self.cursor.execute(clean_query, params)
            else:
                self.cursor.execute(clean_query, (params,))
        else:
            self.cursor.execute(clean_query)
            
        if is_insert and not has_returning:
            try:
                res = self.cursor.fetchone()
                if res:
                    self.lastrowid = res['id'] if isinstance(res, dict) else res[0]
            except Exception:
                pass
        return self

    def executemany(self, query, params_list):
        clean_query = query.replace('%', '%%').replace('?', '%s')
        return self.cursor.executemany(clean_query, params_list)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def close(self):
        return self.cursor.close()

    @property
    def rowcount(self):
        return getattr(self.cursor, 'rowcount', 0)

    def __getattr__(self, name):
        return getattr(self.cursor, name)

    def __iter__(self):
        return iter(self.cursor)

class PgConnectionWrapper:
    def __init__(self, pg_conn):
        self.conn = pg_conn

    def cursor(self):
        import psycopg2.extras
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return PgCursorWrapper(cur)

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def close(self):
        return self.conn.close()

def get_db():
    if is_postgres():
        import psycopg2
        url = DATABASE_URL.replace('[', '').replace(']', '')
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(url)
        return PgConnectionWrapper(conn)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def hash_password(password: str) -> str:
    salt = "ovk_secure_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    use_pg = is_postgres()
    pk_type = "SERIAL PRIMARY KEY" if use_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"

    # Users table
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS users (
        id {pk_type},
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        balance REAL DEFAULT 0.0,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Catalog Items (Games/Products)
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS catalog_items (
        id {pk_type},
        title TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'GAMES',
        platform TEXT NOT NULL DEFAULT 'ANDROID',
        image_url TEXT NOT NULL,
        description TEXT,
        is_active INTEGER DEFAULT 1
    )
    ''')

    # Product Options / Tiers (Durations & Prices)
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS products (
        id {pk_type},
        catalog_id INTEGER DEFAULT 1,
        name TEXT NOT NULL,
        duration TEXT NOT NULL,
        price REAL NOT NULL,
        badge TEXT,
        features TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (catalog_id) REFERENCES catalog_items (id)
    )
    ''')

    # License keys inventory table
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS license_keys (
        id {pk_type},
        product_id INTEGER NOT NULL,
        license_key TEXT UNIQUE NOT NULL,
        is_used INTEGER DEFAULT 0,
        assigned_to_user_id INTEGER DEFAULT NULL,
        used_at TIMESTAMP DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id),
        FOREIGN KEY (assigned_to_user_id) REFERENCES users (id)
    )
    ''')

    # Orders table
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS orders (
        id {pk_type},
        order_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        license_key TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    # Transactions table
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS transactions (
        id {pk_type},
        reference_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    conn.commit()

    # Seed Catalog Items if empty
    cursor.execute('SELECT COUNT(*) as count FROM catalog_items')
    res = cursor.fetchone()
    count = res['count'] if isinstance(res, dict) else res[0]
    if count == 0:
        cursor.execute('''
            INSERT INTO catalog_items (title, category, platform, image_url, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'OVK Premium - CODMGR',
            'GAMES',
            'ANDROID',
            '/static/images/product1.jpg',
            'Undetected CODM aimbot, wallhack & ESP. Instant key delivery right after payment.'
        ))
        item1_id = cursor.lastrowid or 1

        # Seed exact user tiers for item1
        tiers = [
            ('3 DAYS', 70.0, 'Trial Tier', ['3 Days Access', 'Undetected Bypass', 'Instant Key Delivery', 'Auto Loader']),
            ('7 DAYS', 100.0, 'Popular', ['7 Days Access', 'Undetected Bypass', 'Instant Key Delivery', '1x HWID Reset']),
            ('14 DAYS', 150.0, 'Great Value', ['14 Days Access', 'Undetected Bypass', 'Instant Key Delivery', '2x HWID Reset']),
            ('30 DAYS', 250.0, 'Best Seller', ['30 Days Access', 'Undetected Bypass', 'Instant Key Delivery', 'Unlimited HWID Reset']),
            ('60 DAYS', 320.0, 'Pro Choice', ['60 Days Access', 'Undetected Bypass', 'Instant Key Delivery', 'Priority 0-Day Builds']),
            ('LIFETIME', 700.0, 'Ultimate Value', ['Lifetime Forever Access', 'All Future Updates', 'Instant Key Delivery', 'Direct VIP Support'])
        ]

        for dur, price, badge, feat in tiers:
            cursor.execute('''
                INSERT INTO products (catalog_id, name, duration, price, badge, features)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (item1_id, f"OVK Premium - {dur}", dur, price, badge, json.dumps(feat)))

        conn.commit()

    # Seed Default Admin Account if no users exist
    cursor.execute('SELECT COUNT(*) as count FROM users')
    res_users = cursor.fetchone()
    users_count = res_users['count'] if isinstance(res_users, dict) else res_users[0]
    if users_count == 0:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, balance, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@ovk.local', hash_password('Rovic1925#'), 0.0, 'admin'))
        conn.commit()

    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database schema initialized and verified successfully!")
