"""
Database Handler - SQLite for FirmwareShop Bot
"""

import sqlite3
import json
from datetime import datetime
from difflib import SequenceMatcher


class Database:
    def __init__(self, db_path="firmware_shop.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_conn()
        c = conn.cursor()
        
        # Users table
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                language TEXT DEFAULT 'en',
                credits INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Categories table
        c.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                icon TEXT DEFAULT '📦'
            )
        """)
        
        # Products table
        c.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                category_id INTEGER,
                price INTEGER DEFAULT 0,
                description TEXT,
                download_link TEXT,
                license_key TEXT,
                instructions TEXT,
                version TEXT DEFAULT '1.0',
                tags TEXT DEFAULT '[]',
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        
        # Purchases table
        c.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                price_paid INTEGER,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Payments table
        c.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                method TEXT,
                transaction_code TEXT UNIQUE,
                amount REAL,
                credits INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                verified_at TEXT
            )
        """)
        
        # Seed default categories
        for cat in ["Firmware", "Solution", "Source Code", "Tools", "Other"]:
            c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))
        
        # Seed sample products
        self._seed_sample_products(c)
        
        conn.commit()
        conn.close()
    
    def _seed_sample_products(self, c):
        """Add sample products for demonstration"""
        products = [
            ("Samsung A51 Firmware", "Firmware", 200, "Official Samsung A51 firmware SM-A515F", "https://example.com/samsung_a51.zip", "v4.0.0"),
            ("Samsung A21s Firmware", "Firmware", 200, "Samsung A21s SM-A217F official firmware", "https://example.com/samsung_a21s.zip", "v3.0.0"),
            ("Tecno Spark 7 Firmware", "Firmware", 150, "Tecno Spark 7 KF6j flash file", "https://example.com/tecno_spark7.zip", "v1.0"),
            ("iPhone 12 iCloud Bypass", "Solution", 500, "iPhone 12 iCloud activation bypass - permanent", "https://example.com/icloud_bypass.zip", "2024"),
            ("FRP Remove Tool", "Tools", 0, "Universal FRP bypass tool for Android", "https://example.com/frp_tool.zip", "v5.1 Free"),
            ("MTK Auth Bypass", "Solution", 300, "MediaTek auth bypass for flash", "https://example.com/mtk_auth.zip", "v2.0"),
            ("Huawei Bootloader Unlock", "Solution", 400, "Huawei bootloader unlock solution", "https://example.com/huawei_bl.zip", "v1.5"),
            ("Samsung FRP Tool Source", "Source Code", 1000, "Samsung FRP bypass tool full source code - Python", "https://example.com/src_frp.zip", "v3.0"),
            ("Android Flash Tool", "Source Code", 800, "Android SP Flash tool source code", "https://example.com/src_flash.zip", "v2.5"),
            ("Universal FRP Bypass APK", "Tools", 0, "Works on Android 9/10/11/12", "https://example.com/frp_apk.apk", "v2024"),
            ("Xiaomi Mi 11 Firmware", "Firmware", 200, "MIUI 14 official firmware for Xiaomi Mi 11", "https://example.com/xiaomi_mi11.zip", "MIUI14"),
            ("Oppo A54 Firmware", "Firmware", 180, "Oppo A54 CPH2239 flash file", "https://example.com/oppo_a54.zip", "v1.0"),
            ("iCloud MDM Bypass Source", "Source Code", 1500, "iOS MDM bypass full source code", "https://example.com/src_mdm.zip", "v4.0"),
            ("Vivo Y21 Firmware", "Firmware", 150, "Vivo Y21 V2111 firmware", "https://example.com/vivo_y21.zip", "v1.0"),
        ]
        
        for name, cat, price, desc, link, ver in products:
            c.execute("SELECT id FROM categories WHERE name=?", (cat,))
            cat_row = c.fetchone()
            if cat_row:
                c.execute("""
                    INSERT OR IGNORE INTO products (name, category_id, price, description, download_link, version)
                    VALUES (?,?,?,?,?,?)
                """, (name, cat_row[0], price, desc, link, ver))
    
    # ─── USER METHODS ───
    
    def register_user(self, user_id, username, full_name, language="en"):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        exists = c.fetchone()
        
        if not exists:
            # New user bonus: 50 free credits
            c.execute("""
                INSERT INTO users (user_id, username, full_name, language, credits)
                VALUES (?,?,?,?,?)
            """, (user_id, username, full_name, language, 50))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def get_user(self, user_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else {}
    
    def get_user_language(self, user_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else "en"
    
    def update_user_language(self, user_id, language):
        conn = self.get_conn()
        conn.execute("UPDATE users SET language=? WHERE user_id=?", (language, user_id))
        conn.commit()
        conn.close()
    
    def get_credits(self, user_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT credits FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0
    
    def add_credits(self, user_id, amount):
        conn = self.get_conn()
        conn.execute("UPDATE users SET credits = credits + ? WHERE user_id=?", (amount, user_id))
        conn.commit()
        conn.close()
    
    def deduct_credits(self, user_id, amount):
        conn = self.get_conn()
        conn.execute("UPDATE users SET credits = credits - ? WHERE user_id=?", (amount, user_id))
        conn.commit()
        conn.close()
    
    # ─── PRODUCT METHODS ───
    
    def search_products(self, query):
        conn = self.get_conn()
        c = conn.cursor()
        q = f"%{query.lower()}%"
        c.execute("""
            SELECT p.*, cat.name as category 
            FROM products p 
            JOIN categories cat ON p.category_id = cat.id
            WHERE (LOWER(p.name) LIKE ? OR LOWER(p.description) LIKE ? OR LOWER(p.tags) LIKE ?)
            AND p.active = 1
            ORDER BY p.price ASC
            LIMIT 15
        """, (q, q, q))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    
    def get_suggestions(self, query, limit=5):
        """Fuzzy search for suggestions when exact match fails"""
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT p.*, cat.name as category 
            FROM products p 
            JOIN categories cat ON p.category_id = cat.id
            WHERE p.active = 1
        """)
        all_products = [dict(r) for r in c.fetchall()]
        conn.close()
        
        # Score each product
        scored = []
        query_lower = query.lower()
        for p in all_products:
            score = SequenceMatcher(None, query_lower, p['name'].lower()).ratio()
            # Also check word by word
            for word in query_lower.split():
                if word in p['name'].lower() or word in p['description'].lower():
                    score += 0.3
            scored.append((score, p))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for score, p in scored[:limit] if score > 0.2]
    
    def get_product(self, product_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT p.*, cat.name as category 
            FROM products p 
            JOIN categories cat ON p.category_id = cat.id
            WHERE p.id = ?
        """, (product_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_categories(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM categories")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    
    def get_category(self, cat_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM categories WHERE id=?", (cat_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else {}
    
    def get_products_by_category(self, cat_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT p.*, cat.name as category 
            FROM products p 
            JOIN categories cat ON p.category_id = cat.id
            WHERE p.category_id = ? AND p.active = 1
            ORDER BY p.price ASC
        """, (cat_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    
    def count_products_in_category(self, cat_name):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT COUNT(*) FROM products p
            JOIN categories cat ON p.category_id = cat.id
            WHERE cat.name = ? AND p.active = 1
        """, (cat_name,))
        count = c.fetchone()[0]
        conn.close()
        return count
    
    def add_product(self, name, category, price, description, download_link, version="1.0"):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT id FROM categories WHERE name=?", (category,))
        cat = c.fetchone()
        if not cat:
            c.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            cat_id = c.lastrowid
        else:
            cat_id = cat[0]
        
        c.execute("""
            INSERT INTO products (name, category_id, price, description, download_link, version)
            VALUES (?,?,?,?,?,?)
        """, (name, cat_id, price, description, download_link, version))
        product_id = c.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    # ─── PURCHASE METHODS ───
    
    def record_purchase(self, user_id, product_id):
        conn = self.get_conn()
        c = conn.cursor()
        product = self.get_product(product_id)
        c.execute("""
            INSERT INTO purchases (user_id, product_id, price_paid)
            VALUES (?,?,?)
        """, (user_id, product_id, product['price'] if product else 0))
        conn.commit()
        conn.close()
    
    def get_user_purchases(self, user_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT pu.*, p.name as product_name, p.price, pu.date
            FROM purchases pu
            JOIN products p ON pu.product_id = p.id
            WHERE pu.user_id = ?
            ORDER BY pu.date DESC
        """, (user_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    
    def get_total_spent(self, user_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT SUM(price_paid) FROM purchases WHERE user_id=?", (user_id,))
        result = c.fetchone()[0]
        conn.close()
        return result or 0
    
    # ─── PAYMENT METHODS ───
    
    def is_payment_code_used(self, code):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT id FROM payments WHERE transaction_code=?", (code,))
        result = c.fetchone()
        conn.close()
        return result is not None
    
    def record_payment(self, user_id, method, code, amount, credits):
        conn = self.get_conn()
        conn.execute("""
            INSERT INTO payments (user_id, method, transaction_code, amount, credits, status, verified_at)
            VALUES (?,?,?,?,?,'verified',CURRENT_TIMESTAMP)
        """, (user_id, method, code, amount, credits))
        conn.commit()
        conn.close()
    
    def queue_payment_verification(self, user_id, method, code, amount, credits):
        conn = self.get_conn()
        conn.execute("""
            INSERT OR IGNORE INTO payments (user_id, method, transaction_code, amount, credits, status)
            VALUES (?,?,?,?,?,'pending')
        """, (user_id, method, code, amount, credits))
        conn.commit()
        conn.close()
    
    # ─── ADMIN METHODS ───
    
    def get_admin_stats(self):
        conn = self.get_conn()
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM purchases")
        total_sales = c.fetchone()[0]
        
        c.execute("SELECT SUM(price_paid) FROM purchases")
        total_revenue = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM products WHERE active=1")
        total_products = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM payments WHERE status='pending'")
        pending_payments = c.fetchone()[0]
        
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COUNT(*) FROM purchases WHERE date LIKE ?", (f"{today}%",))
        today_sales = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE created_at LIKE ?", (f"{today}%",))
        new_users_today = c.fetchone()[0]
        
        conn.close()
        
        return {
            "total_users": total_users,
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_products": total_products,
            "pending_payments": pending_payments,
            "today_sales": today_sales,
            "new_users_today": new_users_today
        }
