import sqlite3

DB_PATH = "cybersathi_pro.db"

def create_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT,
            emotion TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
