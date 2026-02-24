"""
Database operations for prompt history management using SQLite
Replaces Supabase with local file-based database
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import threading

# Database file path
DB_FILE = "genfy.db"
# Use a reentrant lock to prevent deadlocks when calling functions that also acquire the lock
db_lock = threading.RLock()

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize SQLite database with required tables"""
    try:
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            ''')
            
            # Create prompt_history table with user_id NOT NULL
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT,
                user_idea TEXT,
                llm_used TEXT,
                answers_json TEXT,
                final_prompt TEXT,
                visual_settings TEXT,
                generated_image_url TEXT,
                user_id TEXT NOT NULL,
                files_json TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            ''')
            
            # Create sessions table with user_id NOT NULL
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')
            
            conn.commit()
            conn.close()
            print(f"✅ SQLite database initialized at {os.path.abspath(DB_FILE)}")
            
            # Run migrations for existing databases
            migrate_sessions_add_user_id()
            migrate_prompt_history_user_id_required()
            create_database_indexes()
            
            return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

def migrate_sessions_add_user_id():
    """Migration: Add user_id column to sessions table if missing"""
    try:
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check current schema
            cursor.execute("PRAGMA table_info(sessions)")
            columns = {col[1]: col for col in cursor.fetchall()}
            
            # Check if migration is needed
            if 'user_id' not in columns:
                print("🔄 Migrating sessions table: Adding user_id column...")
                
                # Backup old sessions
                cursor.execute("SELECT id, data, updated_at FROM sessions")
                old_sessions = cursor.fetchall()
                
                # Drop and recreate table with new schema
                cursor.execute("DROP TABLE IF EXISTS sessions_old")
                cursor.execute("ALTER TABLE sessions RENAME TO sessions_old")
                
                cursor.execute('''
                    CREATE TABLE sessions (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        data TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT (datetime('now')),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                ''')
                
                # Migrate sessions that have user_id in JSON
                migrated = 0
                for row in old_sessions:
                    try:
                        import json
                        session_data = json.loads(row['data'])
                        user_id = session_data.get('user_id')
                        
                        if user_id:
                            cursor.execute(
                                '''INSERT INTO sessions 
                                   (id, user_id, data, updated_at, created_at)
                                   VALUES (?, ?, ?, ?, ?)''',
                                (row['id'], user_id, row['data'], row['updated_at'], row['updated_at'])
                            )
                            migrated += 1
                    except Exception as e:
                        print(f"⚠️ Skipping session {row['id']}: {e}")
                        continue
                
                # Clean up
                cursor.execute("DROP TABLE sessions_old")
                conn.commit()
                print(f"✅ Sessions migration complete. Migrated {migrated} sessions.")
            else:
                # Check if user_id is NOT NULL
                user_id_col = columns['user_id']
                if user_id_col[3] == 0:  # notnull = 0 means nullable
                    print("🔄 Making sessions.user_id NOT NULL...")
                    # Need to recreate table
                    cursor.execute("ALTER TABLE sessions RENAME TO sessions_old")
                    cursor.execute('''
                        CREATE TABLE sessions (
                            id TEXT PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            data TEXT NOT NULL,
                            updated_at TEXT NOT NULL,
                            created_at TEXT NOT NULL DEFAULT (datetime('now')),
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                    ''')
                    cursor.execute("INSERT INTO sessions SELECT * FROM sessions_old WHERE user_id IS NOT NULL")
                    cursor.execute("DROP TABLE sessions_old")
                    conn.commit()
                    print("✅ sessions.user_id is now NOT NULL")
            
            conn.close()
            return True
    except Exception as e:
        print(f"❌ Sessions migration failed: {e}")
        return False

def migrate_prompt_history_user_id_required():
    """Migration: Make user_id NOT NULL in prompt_history"""
    try:
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check current schema
            cursor.execute("PRAGMA table_info(prompt_history)")
            columns = {col[1]: col for col in cursor.fetchall()}
            
            if 'user_id' in columns:
                user_id_col = columns['user_id']
                if user_id_col[3] == 0:  # notnull = 0 means nullable
                    print("🔄 Migrating prompt_history: Making user_id NOT NULL...")
                    
                    # Delete orphaned records
                    cursor.execute("DELETE FROM prompt_history WHERE user_id IS NULL")
                    deleted = cursor.rowcount
                    print(f"⚠️ Deleted {deleted} orphaned prompts without user_id")
                    
                    # Recreate table with NOT NULL
                    cursor.execute("ALTER TABLE prompt_history RENAME TO prompt_history_old")
                    cursor.execute('''
                        CREATE TABLE prompt_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp TEXT NOT NULL,
                            category TEXT,
                            user_idea TEXT,
                            llm_used TEXT,
                            answers_json TEXT,
                            final_prompt TEXT,
                            visual_settings TEXT,
                            generated_image_url TEXT,
                            user_id TEXT NOT NULL,
                            files_json TEXT,
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                    ''')
                    
                    cursor.execute("INSERT INTO prompt_history SELECT * FROM prompt_history_old")
                    cursor.execute("DROP TABLE prompt_history_old")
                    conn.commit()
                    print("✅ prompt_history.user_id is now NOT NULL")
            
            conn.close()
            return True
    except Exception as e:
        print(f"❌ prompt_history migration failed: {e}")
        return False

def create_database_indexes():
    """Create indexes for performance"""
    try:
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            print("🔄 Creating database indexes...")
            
            # Sessions indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at DESC)")
            
            # Prompt history indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_user_id ON prompt_history(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_timestamp ON prompt_history(user_id, timestamp DESC)")
            
            conn.commit()
            conn.close()
            print("✅ Database indexes created")
            return True
    except Exception as e:
        print(f"❌ Index creation failed: {e}")
        return False

# --- Auth Operations ---

def create_user(user_id, email, password_hash):
    """Create a new user"""
    try:
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (user_id, email, password_hash, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            print(f"Created user: {email}")
            return True
    except sqlite3.IntegrityError:
        print(f"User already exists: {email}")
        return False
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def get_user_by_email(email):
    """Get user by email"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

# --- Prompt History Operations ---

def save_prompt_to_history(category, user_idea, llm_used, answers_json, final_prompt, visual_settings, user_id, generated_image_url=None, files_json=None):
    """
    Save generated prompt to database
    
    Args:
        user_id: REQUIRED - User who owns this prompt
    """
    if not user_id:
        raise ValueError("user_id is required for prompt history")
    
    timestamp = datetime.now().isoformat()
    
    # Ensure JSON fields are strings
    if isinstance(answers_json, (dict, list)):
        answers_json = json.dumps(answers_json)
    if isinstance(visual_settings, (dict, list)):
        visual_settings = json.dumps(visual_settings)
    if isinstance(files_json, (dict, list)):
        files_json = json.dumps(files_json)
        
    print(f"📝 Saving prompt - Category: {category}, User ID: {user_id}")
    
    try:
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO prompt_history 
                (timestamp, category, user_idea, llm_used, answers_json, final_prompt, visual_settings, generated_image_url, user_id, files_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, category, user_idea, llm_used, answers_json, final_prompt, visual_settings, generated_image_url, user_id, files_json))
            
            prompt_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"Saved prompt to history (ID: {prompt_id})")
            return timestamp
    except Exception as e:
        print(f"Error saving to history: {e}")
        return None

def get_prompt_history(user_id, limit=50):
    """
    Retrieve prompt history for a specific user
    
    Args:
        user_id: REQUIRED - User ID to fetch history for
        limit: Maximum number of prompts to return
    
    Returns:
        List of prompts belonging to user_id only
    """
    if not user_id:
        raise ValueError("user_id is required to fetch history")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ALWAYS filter by user_id
        query = "SELECT id, timestamp, category, user_idea, llm_used, final_prompt, generated_image_url, files_json FROM prompt_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?"
        params = (user_id, limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            files_json = json.loads(row['files_json']) if row['files_json'] else []
            results.append({
                "id": row['id'],
                "timestamp": row['timestamp'],
                "category": row['category'],
                "user_idea": row['user_idea'],
                "llm_used": row['llm_used'],
                "final_prompt": row['final_prompt'],
                "generated_image_url": row['generated_image_url'],
                "files_json": files_json
            })
            
        return results
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

def get_prompt_details(prompt_id, user_id):
    """Get detailed information for a specific prompt (hardened)"""
    if not user_id:
        raise ValueError("user_id is required for prompt details")
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prompt_history WHERE id = ? AND user_id = ?", (prompt_id, user_id))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Parse JSON strings back to objects
            answers_json = json.loads(row['answers_json']) if row['answers_json'] else {}
            visual_settings = json.loads(row['visual_settings']) if row['visual_settings'] else {}
            files_json = json.loads(row['files_json']) if row['files_json'] else []
            
            return (
                row['id'],
                row['timestamp'],
                row['category'],
                row['user_idea'],
                row['llm_used'],
                answers_json,
                row['final_prompt'],
                visual_settings,
                row['generated_image_url'],
                files_json
            )
        return None
    except Exception as e:
        print(f"Error fetching prompt details: {e}")
        return None

def delete_prompt_from_history(prompt_id, user_id):
    """Delete a prompt from history (hardened)"""
    if not user_id:
        raise ValueError("user_id is required to delete prompt")
        
    try:
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prompt_history WHERE id = ? AND user_id = ?", (prompt_id, user_id))
            conn.commit()
            conn.close()
            print(f"Deleted prompt ID: {prompt_id} for user: {user_id}")
            return True
    except Exception as e:
        print(f"Error deleting prompt: {e}")
        return False

def clear_all_history_for_user(user_id):
    """Clear all prompt history for a specific user"""
    if not user_id:
        raise ValueError("user_id is required to clear history")
        
    try:
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prompt_history WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            print(f"Cleared all history for user: {user_id}")
            return True
    except Exception as e:
        print(f"Error clearing history: {e}")
        return False

def update_generated_image(prompt_id, image_url):
    """Update the generated image URL for a specific prompt"""
    try:
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE prompt_history SET generated_image_url = ? WHERE id = ?", (image_url, prompt_id))
            conn.commit()
            conn.close()
            print(f"Updated image for prompt ID: {prompt_id}")
            return True
    except Exception as e:
        print(f"Error updating image: {e}")
        return False

def search_prompts_by_category(category, limit=20):
    """Search prompts by category"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, category, user_idea, final_prompt, generated_image_url, files_json FROM prompt_history WHERE category = ? ORDER BY timestamp DESC LIMIT ?", 
            (category, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            files_json = json.loads(row['files_json']) if row['files_json'] else []
            results.append({
                "id": row['id'],
                "timestamp": row['timestamp'],
                "category": row['category'],
                "user_idea": row['user_idea'],
                "final_prompt": row['final_prompt'],
                "generated_image_url": row['generated_image_url'],
                "files_json": files_json
            })
        return results
    except Exception as e:
        print(f"Error searching prompts: {e}")
        return []

def get_recent_prompts_with_images(limit=10):
    """Get recent prompts that have generated images"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM prompt_history WHERE generated_image_url IS NOT NULL ORDER BY timestamp DESC LIMIT ?", 
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching prompts with images: {e}")
        return []

# --- Session Operations ---

def save_session_to_db(session_id: str, data: Dict[str, Any], user_id: str):
    """
    Save/Update session data in database with required user_id
    
    Args:
        session_id: Unique session identifier
        data: Session data dictionary
        user_id: User ID (REQUIRED for security)
    """
    if not user_id:
        raise ValueError("user_id is required for session storage")
    
    try:
        json_data = json.dumps(data)
        updated_at = datetime.now().isoformat()
        
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (id, user_id, data, updated_at, created_at) 
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET 
                user_id = excluded.user_id,
                data = excluded.data,
                updated_at = excluded.updated_at
            ''', (session_id, user_id, json_data, updated_at, updated_at))
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        print(f"Error saving session to DB: {e}")
        return False

def get_session_from_db(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve session data from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row['data'])
        return None
    except Exception as e:
        print(f"Error retrieving session from DB: {e}")
        return None
