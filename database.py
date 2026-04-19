import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "users.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User configs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_configs (
            user_id INTEGER PRIMARY KEY,
            chat_id TEXT DEFAULT '',
            name_prefix TEXT DEFAULT '',
            delay INTEGER DEFAULT 30,
            cookies TEXT DEFAULT '',
            messages TEXT DEFAULT 'Hello!\nHow are you?\nNice to meet you!',
            automation_running BOOLEAN DEFAULT 0,
            admin_e2ee_thread_id TEXT,
            chat_type TEXT DEFAULT 'INSTAGRAM',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    """Create a new user"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username already exists!"
        
        hashed_pwd = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_pwd)
        )
        user_id = cursor.lastrowid
        
        # Create default config for user
        cursor.execute('''
            INSERT INTO user_configs (user_id, chat_id, name_prefix, delay, cookies, messages, automation_running)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, "", "", 30, "", "Hello!\nHow are you?\nNice to meet you!", 0))
        
        conn.commit()
        return True, "Account created successfully!"
        
    except sqlite3.IntegrityError:
        return False, "Username already exists!"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def verify_user(username, password):
    """Verify user credentials"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        hashed_pwd = hash_password(password)
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, hashed_pwd)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def get_user_config(user_id):
    """Get user configuration"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT chat_id, name_prefix, delay, cookies, messages, automation_running, admin_e2ee_thread_id, chat_type
            FROM user_configs WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        
        if result:
            return {
                'chat_id': result[0] or '',
                'name_prefix': result[1] or '',
                'delay': result[2] or 30,
                'cookies': result[3] or '',
                'messages': result[4] or 'Hello!\nHow are you?\nNice to meet you!',
                'automation_running': bool(result[5]),
                'admin_e2ee_thread_id': result[6],
                'chat_type': result[7] or 'INSTAGRAM'
            }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
    """Update user configuration"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE user_configs 
            SET chat_id = ?, name_prefix = ?, delay = ?, cookies = ?, messages = ?
            WHERE user_id = ?
        ''', (chat_id, name_prefix, delay, cookies, messages, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def set_automation_running(user_id, status):
    """Set automation running status"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE user_configs SET automation_running = ? WHERE user_id = ?
        ''', (1 if status else 0, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def get_automation_running(user_id):
    """Get automation running status"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT automation_running FROM user_configs WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return bool(result[0]) if result else False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def get_username(user_id):
    """Get username by user_id"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def get_admin_e2ee_thread_id(user_id):
    """Get admin thread ID"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT admin_e2ee_thread_id FROM user_configs WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def set_admin_e2ee_thread_id(user_id, thread_id, cookies, chat_type):
    """Set admin thread ID"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE user_configs 
            SET admin_e2ee_thread_id = ?, cookies = ?, chat_type = ? 
            WHERE user_id = ?
        ''', (thread_id, cookies, chat_type, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()
