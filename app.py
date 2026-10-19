import os
import base64
import json
import uuid
import hmac
import hashlib
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import requests
from dotenv import load_dotenv

from database import get_db, init_db, hash_password

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-ovk-shop-dev-secret-12345')

# Security & Cookie Configuration
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=86400 * 7 # 7 days
)

# PayMongo Configuration
PAYMONGO_SECRET_KEY = os.getenv('PAYMONGO_SECRET_KEY', '').strip()
PAYMONGO_PUBLIC_KEY = os.getenv('PAYMONGO_PUBLIC_KEY', '').strip()
PAYMONGO_WEBHOOK_SECRET = os.getenv('PAYMONGO_WEBHOOK_SECRET', '').strip()
APP_URL = os.getenv('APP_URL', 'http://localhost:5000').strip()

# Security, Rate Limiting & Master Passkey Configuration
ADMIN_MASTER_PASS = os.getenv('ADMIN_PASSKEY', 'Rovic1925#').strip()
failed_admin_attempts = {}
failed_login_attempts = {}

# Initialize DB on boot
init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required. Please log in.'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_passkey_verified') or session.get('role') != 'admin':
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Master authorization required.'}), 403
            return render_template('admin_gate.html')
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(404)
def handle_404(e):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return redirect(url_for('dashboard_page'))



# ==========================================
# ==========================================
# PAGE ROUTES
# ==========================================

@app.route('/')
def home_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard_page'))
    return redirect(url_for('login_page'))

@app.route('/products')
@login_required
def products_page():
    return render_template('products.html')

@app.route('/product/<int:item_id>')
@login_required
def product_detail_page(item_id):
    return render_template('product_detail.html', item_id=item_id)

@app.route('/tutorial')
@login_required
def tutorial_page():
    return render_template('tutorial.html')

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard_page'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/admin')
@admin_required
def admin_page():
    return render_template('admin.html')

# ==========================================
# MASTER PASSKEY GATEWAY
# ==========================================

@app.route('/api/admin/verify-passkey', methods=['POST'])
def verify_admin_passkey():
    import time
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()
    now = time.time()

    record = failed_admin_attempts.get(ip, {'count': 0, 'lock_until': 0})
    if record['lock_until'] > now:
        remaining_secs = int(record['lock_until'] - now)
        return jsonify({'error': f'Security Lockdown: Too many failed attempts. Try again in {remaining_secs}s.'}), 429

    data = request.get_json() or {}
    passkey = data.get('passkey', '').strip()

    if not passkey:
        return jsonify({'error': 'Master passkey is required.'}), 400

    if hmac.compare_digest(passkey, ADMIN_MASTER_PASS):
        failed_admin_attempts.pop(ip, None)
        session['admin_passkey_verified'] = True
        session['role'] = 'admin'

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, username, email FROM users WHERE role = 'admin' LIMIT 1")
        admin_user = cur.fetchone()
        conn.close()

        if admin_user:
            session['user_id'] = admin_user['id']
            session['username'] = admin_user['username']
        else:
            session['user_id'] = 1
            session['username'] = 'admin'

        return jsonify({'success': True, 'message': 'Access Granted'})
    else:
        new_count = record['count'] + 1
        lock_until = now + 600 if new_count >= 5 else 0
        failed_admin_attempts[ip] = {'count': new_count, 'lock_until': lock_until}

        if new_count >= 5:
            return jsonify({'error': 'Maximum attempts exceeded. IP locked out for 10 minutes.'}), 429

        remaining = 5 - new_count
        return jsonify({'error': f'Access Denied: Invalid Master Passkey ({remaining} attempts remaining)'}), 401

@app.route('/api/admin/lock', methods=['POST'])
def lock_admin():
    session.pop('admin_passkey_verified', None)
    if session.get('role') == 'admin':
        session.clear()
    return jsonify({'success': True, 'message': 'Admin session locked successfully.'})

# ==========================================
# AUTHENTICATION APIS
# ==========================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required.'}), 400

    if len(username) < 3 or len(username) > 30:
        return jsonify({'error': 'Username must be between 3 and 30 characters.'}), 400

    if not username.replace('_', '').replace('-', '').isalnum():
        return jsonify({'error': 'Username can only contain alphanumeric characters, hyphens, and underscores.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Check if already exists
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            return jsonify({'error': 'Username or Email is already registered.'}), 409

        pw_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, balance, role)
            VALUES (?, ?, ?, 0.0, 'user')
        ''', (username, email, pw_hash))
        conn.commit()

        new_user_id = cursor.lastrowid

        # Do NOT set session here - require explicit sign in
        return jsonify({
            'success': True,
            'message': 'Account created successfully! Please sign in with your credentials.',
            'username': username
        }), 201
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    import time
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()
    now = time.time()

    # Rate limiting & Anti-Brute Force Protection
    record = failed_login_attempts.get(ip, {'count': 0, 'lock_until': 0})
    if record['lock_until'] > now:
        remaining_secs = int(record['lock_until'] - now)
        return jsonify({
            'error': f'Too many failed login attempts. IP protected against brute force. Try again in {remaining_secs} seconds.'
        }), 429

    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'error': 'Please enter your username/email and password.'}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        pw_hash = hash_password(password)
        cursor.execute('''
            SELECT id, username, email, password_hash, balance, role 
            FROM users 
            WHERE username = ? OR email = ?
        ''', (identifier, identifier.lower()))
        user = cursor.fetchone()

        # Constant-time comparison to thwart timing attacks
        valid = False
        if user and hmac.compare_digest(user['password_hash'], pw_hash):
            valid = True

        if not valid:
            new_count = record['count'] + 1
            # Progressive lockout: 5 attempts -> 3 minutes, 10+ attempts -> 15 minutes
            if new_count >= 10:
                lock_until = now + 900
            elif new_count >= 5:
                lock_until = now + 180
            else:
                lock_until = 0

            failed_login_attempts[ip] = {'count': new_count, 'lock_until': lock_until}

            if lock_until > 0:
                lock_mins = int((lock_until - now) / 60) or 1
                return jsonify({
                    'error': f'Too many failed attempts. Security lock active for {lock_mins} minute(s).'
                }), 429

            remaining = 5 - (new_count % 5)
            return jsonify({
                'error': f'Invalid credentials. Please verify your details ({remaining} attempt(s) before temporary lockout).'
            }), 401

        # Clear failed attempts on successful login
        failed_login_attempts.pop(ip, None)

        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']

        return jsonify({
            'success': True,
            'message': 'Logged in successfully!',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'balance': float(user['balance']),
                'role': user['role']
            }
        })
    finally:
        conn.close()

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out.'})

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()

    if not email:
        return jsonify({'error': 'Email is required from Google account.'}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT id, username, email, balance, role FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if not user:
            base_username = name.replace(' ', '').lower() if name else email.split('@')[0]
            base_username = ''.join(c for c in base_username if c.isalnum())[:16] or 'user'

            username = base_username
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            suffix = 1
            while cursor.fetchone():
                username = f"{base_username}{suffix}"
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                suffix += 1

            random_pwd = uuid.uuid4().hex + "GGL_SECURE_2026"
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, balance, role)
                VALUES (?, ?, ?, 0.0, 'user')
            ''', (username, email, hash_password(random_pwd)))
            conn.commit()

            new_user_id = cursor.lastrowid
            if not new_user_id:
                cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
                row = cursor.fetchone()
                new_user_id = row['id'] if row else 1

            user = {
                'id': new_user_id,
                'username': username,
                'email': email,
                'balance': 0.0,
                'role': 'user'
            }

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']

        return jsonify({
            'success': True,
            'message': 'Signed in with Google successfully!',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'balance': float(user['balance']),
                'role': user['role']
            }
        })
    except Exception as e:
        return jsonify({'error': f'Google authentication error: {str(e)}'}), 500
    finally:
        conn.close()
@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 200

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, balance, role FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    if not user:
        session.clear()
        return jsonify({'authenticated': False}), 200

    return jsonify({
        'authenticated': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'balance': float(user['balance']),
            'role': user['role']
        }
    })

# ==========================================
# PRODUCTS & STORE CATALOG
# ==========================================

@app.route('/api/products', methods=['GET'])
def list_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.name, p.duration, p.price, p.badge, p.features,
               (SELECT COUNT(*) FROM license_keys WHERE product_id = p.id AND is_used = 0) as in_stock
        FROM products p
        WHERE p.is_active = 1
        ORDER BY p.price ASC
    ''')
    rows = cursor.fetchall()
    conn.close()

    products = []
    for row in rows:
        features_list = []
        try:
            features_list = json.loads(row['features'])
        except Exception:
            features_list = []
        
        products.append({
            'id': row['id'],
            'name': row['name'],
            'duration': row['duration'],
            'price': float(row['price']),
            'badge': row['badge'],
            'features': features_list,
            'stock': row['in_stock']
        })

    return jsonify({'products': products})

@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, title, category, platform, image_url, description FROM catalog_items WHERE is_active = 1 ORDER BY id ASC')
    items = cursor.fetchall()

    catalog = []
    for item in items:
        cursor.execute('''
            SELECT p.id, p.name, p.duration, p.price, p.badge, p.features,
                   (SELECT COUNT(*) FROM license_keys WHERE product_id = p.id AND is_used = 0) as in_stock
            FROM products p
            WHERE p.catalog_id = ? AND p.is_active = 1
            ORDER BY p.price ASC
        ''', (item['id'],))
        prod_rows = cursor.fetchall()

        options = []
        min_p = 999999
        max_p = 0
        total_stock = 0

        for pr in prod_rows:
            price = float(pr['price'])
            if price < min_p: min_p = price
            if price > max_p: max_p = price
            stock = pr['in_stock']
            total_stock += stock

            try:
                features_list = json.loads(pr['features'])
            except Exception:
                features_list = []

            options.append({
                'id': pr['id'],
                'name': pr['name'],
                'duration': pr['duration'],
                'price': price,
                'badge': pr['badge'],
                'features': features_list,
                'stock': stock
            })

        catalog.append({
            'id': item['id'],
            'title': item['title'],
            'category': item['category'],
            'platform': item['platform'],
            'image_url': item['image_url'],
            'description': item['description'],
            'options_count': len(options),
            'min_price': min_p if min_p != 999999 else 70.0,
            'max_price': max_p if max_p != 0 else 700.0,
            'total_stock': total_stock,
            'options': options
        })

    conn.close()
    return jsonify({'catalog': catalog})

@app.route('/api/catalog/<int:item_id>', methods=['GET'])
def get_catalog_item(item_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, title, category, platform, image_url, description FROM catalog_items WHERE id = ? AND is_active = 1', (item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        return jsonify({'error': 'Product not found'}), 404

    cursor.execute('''
        SELECT p.id, p.name, p.duration, p.price, p.badge, p.features,
               (SELECT COUNT(*) FROM license_keys WHERE product_id = p.id AND is_used = 0) as in_stock
        FROM products p
        WHERE p.catalog_id = ? AND p.is_active = 1
        ORDER BY p.price ASC
    ''', (item['id'],))
    prod_rows = cursor.fetchall()

    options = []
    total_stock = 0
    for pr in prod_rows:
        stock = pr['in_stock']
        total_stock += stock
        try:
            features_list = json.loads(pr['features'])
        except Exception:
            features_list = []

        options.append({
            'id': pr['id'],
            'name': pr['name'],
            'duration': pr['duration'],
            'price': float(pr['price']),
            'badge': pr['badge'],
            'features': features_list,
            'stock': stock
        })

    product_data = {
        'id': item['id'],
        'title': item['title'],
        'category': item['category'],
        'platform': item['platform'],
        'image_url': item['image_url'],
        'description': item['description'],
        'total_stock': total_stock,
        'options': options
    }

    conn.close()
    return jsonify({'product': product_data})

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def dashboard_stats():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # User balance & profile
    cursor.execute('SELECT username, email, balance, role FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    # Auto-sync any pending PayMongo transactions for this user
    cursor.execute('''
        SELECT reference_id, amount 
        FROM transactions 
        WHERE user_id = ? AND status = 'pending' AND reference_id LIKE 'cs_%'
    ''', (user_id,))
    pending_txs = cursor.fetchall()
    
    if pending_txs and PAYMONGO_SECRET_KEY and 'demo_key' not in PAYMONGO_SECRET_KEY:
        auth_header = base64.b64encode(f"{PAYMONGO_SECRET_KEY}:".encode('utf-8')).decode('utf-8')
        headers = {'Authorization': f'Basic {auth_header}'}
        
        for ptx in pending_txs:
            sid = ptx['reference_id']
            try:
                pm_res = requests.get(f'https://api.paymongo.com/v1/checkout_sessions/{sid}', headers=headers, timeout=5)
                if pm_res.status_code == 200:
                    pm_data = pm_res.json().get('data', {}).get('attributes', {})
                    pm_payments = pm_data.get('payments', [])
                    pm_status = pm_data.get('status')
                    if (pm_payments and pm_payments[0].get('attributes', {}).get('status') == 'paid') or pm_status == 'paid':
                        amt = ptx['amount']
                        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amt, user_id))
                        cursor.execute('''
                            UPDATE transactions 
                            SET status = 'completed', description = ? 
                            WHERE reference_id = ?
                        ''', (f"PayMongo Paid via GCash/Card (₱{amt:.2f})", sid))
                        conn.commit()
            except Exception:
                pass

    # Fetch updated user balance
    cursor.execute('SELECT username, email, balance, role FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    # Total orders & Credits spent
    cursor.execute('SELECT COUNT(*) as total_orders, COALESCE(SUM(price), 0.0) as credits_spent FROM orders WHERE user_id = ?', (user_id,))
    order_data = cursor.fetchone()

    # Total active keys for this user
    cursor.execute('SELECT COUNT(*) as total_keys FROM orders WHERE user_id = ?', (user_id,))
    keys_data = cursor.fetchone()
    total_keys = keys_data['total_keys'] if keys_data else 0

    # Total registered users across the entire web/system
    cursor.execute('SELECT COUNT(*) as registered_users FROM users')
    users_data = cursor.fetchone()
    registered_users = users_data['registered_users'] if users_data else 0

    # Total global products count
    cursor.execute('SELECT COUNT(*) as total_products FROM catalog_items WHERE is_active = 1')
    products_data = cursor.fetchone()
    total_products = products_data['total_products'] if products_data else 0

    # Total global orders count across the platform
    cursor.execute('SELECT COUNT(*) as global_orders FROM orders')
    global_orders_data = cursor.fetchone()
    global_orders = global_orders_data['global_orders'] if global_orders_data else 0

    # Recent orders
    cursor.execute('''
        SELECT order_id, product_name, price, license_key, created_at 
        FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 5
    ''', (user_id,))
    recent_orders = [dict(r) for r in cursor.fetchall()]

    # Recent transactions
    cursor.execute('''
        SELECT reference_id, type, amount, status, description, created_at 
        FROM transactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 5
    ''', (user_id,))
    recent_txs = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return jsonify({
        'username': user['username'],
        'email': user['email'],
        'balance': float(user['balance']),
        'role': user['role'],
        'total_orders': order_data['total_orders'],
        'credits_spent': float(order_data['credits_spent']),
        'total_keys': total_keys,
        'registered_users': registered_users,
        'total_products': total_products,
        'global_orders': global_orders,
        'recent_orders': recent_orders,
        'recent_transactions': recent_txs
    })

# ==========================================
# PURCHASING / KEY DELIVERY
# ==========================================

@app.route('/api/purchase', methods=['POST'])
@login_required
def purchase_product():
    data = request.get_json() or {}
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'error': 'Product ID is required.'}), 400

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    try:
        # 1. Fetch user balance
        cursor.execute('SELECT id, username, balance FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found.'}), 404

        # 2. Fetch product
        cursor.execute('SELECT id, name, duration, price FROM products WHERE id = ? AND is_active = 1', (product_id,))
        product = cursor.fetchone()
        if not product:
            return jsonify({'error': 'Selected tier does not exist.'}), 404

        price = float(product['price'])
        user_balance = float(user['balance'])

        if user_balance < price:
            needed = price - user_balance
            return jsonify({
                'error': f'Insufficient balance! You need ₱{needed:.2f} more.',
                'code': 'INSUFFICIENT_FUNDS',
                'current_balance': user_balance,
                'price': price,
                'needed': needed
            }), 400

        # 3. Retrieve an unused key
        cursor.execute('''
            SELECT id, license_key 
            FROM license_keys 
            WHERE product_id = ? AND is_used = 0 
            LIMIT 1
        ''', (product_id,))
        key_record = cursor.fetchone()

        # If stock ran out, do NOT auto-generate. Block purchase!
        if not key_record:
            return jsonify({
                'error': f'Sorry, {product["name"]} is currently out of stock! Please contact support or check back soon.',
                'code': 'OUT_OF_STOCK'
            }), 400

        delivered_key = key_record['license_key']
        cursor.execute('''
            UPDATE license_keys 
            SET is_used = 1, assigned_to_user_id = ?, used_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (user_id, key_record['id']))

        # 4. Deduct user balance
        new_balance = user_balance - price
        cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))

        # 5. Create Order record
        order_id = f"ORD-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        cursor.execute('''
            INSERT INTO orders (order_id, user_id, product_id, product_name, price, license_key)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (order_id, user_id, product['id'], product['name'], price, delivered_key))

        # 6. Record transaction
        cursor.execute('''
            INSERT INTO transactions (reference_id, user_id, type, amount, status, description)
            VALUES (?, ?, 'purchase', ?, 'completed', ?)
        ''', (order_id, user_id, price, f"Purchased {product['name']} ({product['duration']})"))

        conn.commit()

        return jsonify({
            'success': True,
            'message': 'Purchase completed! Your license key is ready.',
            'order_id': order_id,
            'product_name': product['name'],
            'duration': product['duration'],
            'license_key': delivered_key,
            'new_balance': new_balance
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Purchase failed: {str(e)}'}), 500
    finally:
        conn.close()

# ==========================================
# PAYMONGO INTEGRATION (ADD FUNDS)
# ==========================================

@app.route('/api/wallet/create-checkout', methods=['POST'])
@login_required
def create_paymongo_checkout():
    """
    Creates a PayMongo Checkout Session for adding funds to the user's wallet.
    Supports GCash, Maya, GrabPay, Credit/Debit Cards, BillEase, etc.
    """
    data = request.get_json() or {}
    amount = data.get('amount')

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({'error': 'Please enter a valid numeric amount.'}), 400

    ALLOWED_DEPOSIT_AMOUNTS = [70.0, 100.0, 150.0, 200.0, 250.0, 300.0, 320.0, 500.0, 700.0, 1000.0]
    if amount not in ALLOWED_DEPOSIT_AMOUNTS:
        return jsonify({'error': 'Please select a valid preset deposit amount.'}), 400

    user_id = session['user_id']
    username = session.get('username', f'User #{user_id}')
    amount_in_centavos = int(round(amount * 100))

    # Check if PayMongo key is configured
    is_demo_key = not PAYMONGO_SECRET_KEY or 'demo_key' in PAYMONGO_SECRET_KEY or 'paste_your' in PAYMONGO_SECRET_KEY

    if is_demo_key:
        return jsonify({
            'demo_mode': True,
            'message': 'PayMongo Secret Key is currently in Demo/Sandbox mode. Use the Instant Deposit Simulator below or add your PayMongo key in .env!',
            'amount': amount
        })

    # Call PayMongo Checkout Session API
    auth_header = base64.b64encode(f"{PAYMONGO_SECRET_KEY}:".encode('utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_header}'
    }

    payload = {
        'data': {
            'attributes': {
                'send_email_receipt': True,
                'show_description': True,
                'show_line_items': True,
                'description': f"Wallet Deposit for {username} (ID: {user_id})",
                'line_items': [
                    {
                        'currency': 'PHP',
                        'amount': amount_in_centavos,
                        'name': f"Wallet Deposit (₱{amount:.2f})",
                        'quantity': 1,
                        'description': f"Balance top-up for {username}"
                    }
                ],
                'payment_method_types': ['gcash', 'paymaya', 'card', 'qrph', 'grab_pay'],
                'success_url': f"{APP_URL}/dashboard?deposit=success&session_id={{CHECKOUT_SESSION_ID}}&amount={amount}",
                'cancel_url': f"{APP_URL}/dashboard?deposit=cancelled",
                'metadata': {
                    'userId': str(user_id),
                    'type': 'wallet_deposit',
                    'amountPhp': f"{amount:.2f}",
                    'username': username
                }
            }
        }
    }

    try:
        response = requests.post(
            'https://api.paymongo.com/v1/checkout_sessions',
            headers=headers,
            json=payload,
            timeout=15
        )
        resp_data = response.json()

        if response.status_code not in (200, 201):
            err_msg = 'PayMongo Error: '
            if 'errors' in resp_data and len(resp_data['errors']) > 0:
                err_msg += resp_data['errors'][0].get('detail', 'Unknown error')
            else:
                err_msg += str(resp_data)
            return jsonify({'error': err_msg}), 400

        checkout_data = resp_data.get('data', {})
        checkout_url = checkout_data.get('attributes', {}).get('checkout_url')
        session_id = checkout_data.get('id')

        # Log pending transaction in database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM transactions WHERE reference_id = ?', (session_id,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO transactions (reference_id, user_id, type, amount, status, description)
                VALUES (?, ?, 'deposit', ?, 'pending', ?)
            ''', (session_id, user_id, amount, f"PayMongo Checkout Session ({amount:.2f} PHP)"))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'checkout_url': checkout_url,
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'error': f'Failed to reach PayMongo: {str(e)}'}), 500

@app.route('/api/wallet/verify-checkout', methods=['POST'])
@login_required
def verify_paymongo_checkout():
    """
    Called automatically when the customer redirects back from PayMongo.
    Verifies payment with PayMongo API directly so credits are added INSTANTLY
    without waiting for webhooks or admin manual approval!
    """
    data = request.get_json() or {}
    session_id = data.get('session_id')
    user_id = session['user_id']

    if not session_id:
        return jsonify({'error': 'session_id required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Check if already completed locally
    cursor.execute('SELECT id, status, amount FROM transactions WHERE reference_id = ? AND user_id = ?', (session_id, user_id))
    tx = cursor.fetchone()

    if tx and tx['status'] == 'completed':
        conn.close()
        return jsonify({'success': True, 'status': 'completed', 'already_credited': True})

    # Query PayMongo Checkout Session API
    auth_header = base64.b64encode(f"{PAYMONGO_SECRET_KEY}:".encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': f'Basic {auth_header}'
    }

    try:
        res = requests.get(f'https://api.paymongo.com/v1/checkout_sessions/{session_id}', headers=headers, timeout=12)
        if res.status_code != 200:
            conn.close()
            return jsonify({'error': 'Unable to retrieve checkout from PayMongo.'}), 400

        data = res.json().get('data', {})
        attributes = data.get('attributes', {})
        payments = attributes.get('payments', [])
        status = attributes.get('status')

        # Check if paid
        is_paid = (len(payments) > 0 and payments[0].get('attributes', {}).get('status') == 'paid') or status == 'paid'
        
        # In test mode or when redirect arrives with success, if payment exists or status is paid:
        if is_paid:
            amount = tx['amount'] if tx else (attributes.get('line_items', [{}])[0].get('amount', 0) / 100.0)

            # Credit user balance immediately!
            cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))

            if tx:
                cursor.execute('''
                    UPDATE transactions 
                    SET status = 'completed', description = ? 
                    WHERE reference_id = ?
                ''', (f"PayMongo Instant Paid (₱{amount:.2f})", session_id))
            else:
                cursor.execute('''
                    INSERT INTO transactions (reference_id, user_id, type, amount, status, description)
                    VALUES (?, ?, 'deposit', ?, 'completed', ?)
                ''', (session_id, user_id, amount, f"PayMongo Instant Paid (₱{amount:.2f})"))

            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'status': 'completed',
                'credited': amount,
                'message': f"Successfully credited ₱{amount:.2f} to your wallet!"
            })
        else:
            conn.close()
            return jsonify({'success': False, 'status': 'pending', 'message': 'Payment is still processing.'})

    except Exception as e:
        conn.close()
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500

@app.route('/api/wallet/simulate-deposit', methods=['POST'])
@login_required
def simulate_deposit():
    """
    Development & Sandbox helper:
    Instantly credit funds so you can test purchasing without waiting for live webhook delivery!
    """
    data = request.get_json() or {}
    try:
        amount = float(data.get('amount', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid amount.'}), 400

    ALLOWED_DEPOSIT_AMOUNTS = [100.0, 200.0, 300.0, 500.0, 700.0, 1000.0]
    if amount not in ALLOWED_DEPOSIT_AMOUNTS:
        return jsonify({'error': 'Credits that can be added are: ₱100, ₱200, ₱300, ₱500, ₱700, or ₱1,000.'}), 400

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    try:
        ref_id = f"DEP-SIM-{uuid.uuid4().hex[:8].upper()}"
        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
        cursor.execute('''
            INSERT INTO transactions (reference_id, user_id, type, amount, status, description)
            VALUES (?, ?, 'deposit', ?, 'completed', ?)
        ''', (ref_id, user_id, amount, f"Instant Top-Up Sandbox (₱{amount:.2f})"))
        conn.commit()

        cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
        updated_balance = cursor.fetchone()['balance']

        return jsonify({
            'success': True,
            'message': f'Successfully added ₱{amount:.2f} to your wallet!',
            'new_balance': float(updated_balance)
        })
    finally:
        conn.close()

@app.route('/api/webhooks/paymongo', methods=['POST'])
def paymongo_webhook():
    """
    PayMongo Webhook listener:
    Receives automated notifications when a user pays via GCash, Maya, Card, etc.
    """
    raw_body = request.get_data()
    signature_header = request.headers.get('Paymongo-Signature', '')

    try:
        event = json.loads(raw_body.decode('utf-8'))
    except Exception:
        return jsonify({'error': 'Invalid JSON body'}), 400

    # Optional signature verification if WEBHOOK_SECRET is set
    if PAYMONGO_WEBHOOK_SECRET and not 'demo' in PAYMONGO_WEBHOOK_SECRET and signature_header:
        # PayMongo signature header format: t=timestamp,te=test_signature,li=live_signature
        parts = dict(item.split('=', 1) for item in signature_header.split(',') if '=' in item)
        timestamp = parts.get('t', '')
        test_sig = parts.get('te', '')
        live_sig = parts.get('li', '')
        received_sig = live_sig or test_sig

        if timestamp and received_sig:
            signed_payload = f"{timestamp}.{raw_body.decode('utf-8')}"
            expected_sig = hmac.new(
                PAYMONGO_WEBHOOK_SECRET.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(expected_sig, received_sig):
                return jsonify({'error': 'Invalid signature'}), 401

    event_type = event.get('data', {}).get('attributes', {}).get('type')
    event_data = event.get('data', {}).get('attributes', {}).get('data', {})

    # We listen for checkout_session.payment.paid or payment.paid
    if event_type in ('checkout_session.payment.paid', 'payment.paid'):
        attributes = event_data.get('attributes', {})
        metadata = attributes.get('metadata', {})
        session_id = event_data.get('id')

        user_id = metadata.get('userId')
        amount_php_str = metadata.get('amountPhp')

        if not user_id and 'payments' in attributes and len(attributes['payments']) > 0:
            payment_meta = attributes['payments'][0].get('attributes', {}).get('metadata', {})
            user_id = payment_meta.get('userId')
            amount_php_str = payment_meta.get('amountPhp')

        if user_id:
            try:
                user_id = int(user_id)
                amount = float(amount_php_str) if amount_php_str else (attributes.get('amount', 0) / 100.0)

                conn = get_db()
                cursor = conn.cursor()

                # Check idempotency to prevent double-crediting
                cursor.execute('SELECT id, status FROM transactions WHERE reference_id = ?', (session_id,))
                existing_tx = cursor.fetchone()

                if existing_tx and existing_tx['status'] == 'completed':
                    conn.close()
                    return jsonify({'status': 'already_processed'}), 200

                # Credit user balance
                cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))

                if existing_tx:
                    cursor.execute('''
                        UPDATE transactions 
                        SET status = 'completed', description = ? 
                        WHERE reference_id = ?
                    ''', (f"PayMongo Paid via GCash/Card (₱{amount:.2f})", session_id))
                else:
                    cursor.execute('''
                        INSERT INTO transactions (reference_id, user_id, type, amount, status, description)
                        VALUES (?, ?, 'deposit', ?, 'completed', ?)
                    ''', (session_id, user_id, amount, f"PayMongo Paid via GCash/Card (₱{amount:.2f})"))

                conn.commit()
                conn.close()
                print(f"[PayMongo Webhook] Successfully credited PHP {amount:.2f} to User ID {user_id}")
            except Exception as e:
                print(f"[PayMongo Webhook Error] {str(e)}")
                return jsonify({'error': f'Database update failed: {str(e)}'}), 500

    return jsonify({'received': True}), 200

# ==========================================
# USER ORDERS & TRANSACTIONS
# ==========================================

@app.route('/api/user/orders', methods=['GET'])
@login_required
def get_user_orders():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT order_id, product_name, price, license_key, created_at 
        FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()

    orders = [dict(row) for row in rows]
    return jsonify({'orders': orders})

@app.route('/api/user/transactions', methods=['GET'])
@login_required
def get_user_transactions():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # Sync any pending PayMongo transactions for this user
    cursor.execute('''
        SELECT reference_id, amount 
        FROM transactions 
        WHERE user_id = ? AND status = 'pending' AND reference_id LIKE 'cs_%'
    ''', (user_id,))
    pending_txs = cursor.fetchall()
    
    if pending_txs and PAYMONGO_SECRET_KEY and 'demo_key' not in PAYMONGO_SECRET_KEY:
        auth_header = base64.b64encode(f"{PAYMONGO_SECRET_KEY}:".encode('utf-8')).decode('utf-8')
        headers = {'Authorization': f'Basic {auth_header}'}
        for ptx in pending_txs:
            sid = ptx['reference_id']
            try:
                pm_res = requests.get(f'https://api.paymongo.com/v1/checkout_sessions/{sid}', headers=headers, timeout=5)
                if pm_res.status_code == 200:
                    pm_data = pm_res.json().get('data', {}).get('attributes', {})
                    pm_payments = pm_data.get('payments', [])
                    pm_status = pm_data.get('status')
                    if (pm_payments and pm_payments[0].get('attributes', {}).get('status') == 'paid') or pm_status == 'paid':
                        amt = ptx['amount']
                        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amt, user_id))
                        cursor.execute('''
                            UPDATE transactions 
                            SET status = 'completed', description = ? 
                            WHERE reference_id = ?
                        ''', (f"PayMongo Paid via GCash/Card (₱{amt:.2f})", sid))
                        conn.commit()
            except Exception:
                pass

    cursor.execute('''
        SELECT reference_id, type, amount, status, description, created_at 
        FROM transactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()

    transactions = [dict(row) for row in rows]
    return jsonify({'transactions': transactions})

# ==========================================
# ADMIN MANAGEMENT APIS
# ==========================================

@app.route('/api/admin/overview', methods=['GET'])
@admin_required
def admin_overview():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total_users FROM users')
    total_users = cursor.fetchone()['total_users']

    cursor.execute('SELECT COUNT(*) as total_orders, COALESCE(SUM(price), 0) as total_revenue FROM orders')
    order_stats = cursor.fetchone()

    cursor.execute('SELECT COUNT(*) as available_keys FROM license_keys WHERE is_used = 0')
    available_keys = cursor.fetchone()['available_keys']

    cursor.execute('SELECT COUNT(*) as used_keys FROM license_keys WHERE is_used = 1')
    used_keys = cursor.fetchone()['used_keys']

    cursor.execute('''
        SELECT u.id, u.username, u.email, u.balance, u.role, u.created_at
        FROM users u
        ORDER BY u.id DESC
        LIMIT 20
    ''')
    users = [dict(row) for row in cursor.fetchall()]

    cursor.execute('''
        SELECT p.id, p.name, p.duration, p.price,
               (SELECT COUNT(*) FROM license_keys WHERE product_id = p.id AND is_used = 0) as stock
        FROM products p
        ORDER BY p.price ASC
    ''')
    products = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        'total_users': total_users,
        'total_orders': order_stats['total_orders'],
        'total_revenue': float(order_stats['total_revenue']),
        'available_keys': available_keys,
        'used_keys': used_keys,
        'users': users,
        'products': products
    })

@app.route('/api/admin/keys/add', methods=['POST'])
@admin_required
def admin_add_keys():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    raw_keys = data.get('keys', '')

    if not product_id or not raw_keys:
        return jsonify({'error': 'Product and keys are required.'}), 400

    key_list = [k.strip() for k in raw_keys.split('\n') if k.strip()]
    if not key_list:
        return jsonify({'error': 'No valid keys provided.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    added = 0

    for key_text in key_list:
        try:
            cursor.execute('''
                INSERT INTO license_keys (product_id, license_key, is_used)
                VALUES (?, ?, 0)
            ''', (product_id, key_text))
            added += 1
        except Exception:
            pass # duplicate key ignored

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'added': added, 'message': f'Successfully imported {added} keys!'})

@app.route('/api/admin/keys', methods=['GET'])
@admin_required
def admin_get_keys():
    status = request.args.get('status', 'all')
    product_id = request.args.get('product_id', 'all')
    
    query = '''
        SELECT k.id, k.license_key, k.is_used, k.created_at, k.used_at,
               p.name as product_name, p.duration,
               u.username as claimed_by_user,
               o.order_id
        FROM license_keys k
        JOIN products p ON k.product_id = p.id
        LEFT JOIN users u ON k.assigned_to_user_id = u.id
        LEFT JOIN orders o ON o.license_key = k.license_key
        WHERE 1=1
    '''
    params = []
    if status == 'available':
        query += ' AND k.is_used = 0'
    elif status == 'used':
        query += ' AND k.is_used = 1'
        
    if product_id != 'all' and product_id.isdigit():
        query += ' AND k.product_id = ?'
        params.append(int(product_id))
        
    query += ' ORDER BY k.id DESC LIMIT 100'

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    keys = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({'keys': keys})

@app.route('/api/admin/keys/delete', methods=['POST'])
@admin_required
def admin_delete_key():
    data = request.get_json() or {}
    key_ids = data.get('ids', [])
    single_id = data.get('id')
    
    if single_id is not None:
        if isinstance(key_ids, list):
            if single_id not in key_ids:
                key_ids.append(single_id)
        else:
            key_ids = [single_id]

    if not key_ids or not isinstance(key_ids, list):
        return jsonify({'error': 'Please select at least one key to delete.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    placeholders = ', '.join(['?'] * len(key_ids))
    cursor.execute(f'DELETE FROM license_keys WHERE id IN ({placeholders})', tuple(key_ids))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    return jsonify({
        'success': True, 
        'message': f'Deleted {len(key_ids)} key(s) from inventory.',
        'deleted_count': deleted
    })

@app.route('/api/admin/keys/bring-back', methods=['POST'])
@admin_required
def admin_bring_back_key():
    data = request.get_json() or {}
    key_id = data.get('id')
    bring_all = data.get('all', False)

    conn = get_db()
    cursor = conn.cursor()

    if bring_all:
        cursor.execute('''
            UPDATE license_keys 
            SET is_used = 0, assigned_to_user_id = NULL, used_at = NULL
            WHERE is_used = 1
        ''')
        restored = cursor.rowcount
    elif key_id:
        cursor.execute('''
            UPDATE license_keys 
            SET is_used = 0, assigned_to_user_id = NULL, used_at = NULL
            WHERE id = ? AND is_used = 1
        ''', (key_id,))
        restored = cursor.rowcount
    else:
        conn.close()
        return jsonify({'error': 'Key ID or all parameter is required'}), 400

    conn.commit()
    conn.close()

    if restored == 0 and not bring_all:
        return jsonify({'error': 'Key is already available in stock or not found.'}), 400

    return jsonify({
        'success': True, 
        'restored': restored, 
        'message': f'Brought back {restored} key(s) to stock successfully!'
    })

@app.route('/api/admin/users/balance', methods=['POST'])
@admin_required
def admin_adjust_balance():
    data = request.get_json() or {}
    target_user_id = data.get('user_id')
    amount = data.get('amount')
    reason = data.get('reason', 'Admin adjustment')

    try:
        amount = float(amount)
        target_user_id = int(target_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid user ID or amount.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, target_user_id))
    ref_id = f"ADM-ADJ-{uuid.uuid4().hex[:6].upper()}"
    cursor.execute('''
        INSERT INTO transactions (reference_id, user_id, type, amount, status, description)
        VALUES (?, ?, 'admin_adjustment', ?, 'completed', ?)
    ''', (ref_id, target_user_id, amount, reason))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'Balance adjusted by ₱{amount:+.2f}'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f">> OVK Shop running at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
