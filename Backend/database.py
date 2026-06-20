# database.py - PostgreSQL (Supabase) Connection and Setup

import psycopg2
import psycopg2.extras
from config import Config

def get_connection():
    """Create and return a PostgreSQL connection."""
    try:
        conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print(f"[DB ERROR] Failed to connect to PostgreSQL: {e}")
        return None

def initialize_database():
    """Create tables if they don't exist and seed default admin."""
    conn = get_connection()
    if not conn:
        print("[DB ERROR] Cannot initialize — no connection.")
        return

    try:
        cursor = conn.cursor()

        # users table — role stored as TEXT with CHECK constraint (replaces ENUM)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id        SERIAL PRIMARY KEY,
                username  VARCHAR(100) UNIQUE NOT NULL,
                password  VARCHAR(255) NOT NULL,
                role      TEXT NOT NULL DEFAULT 'worker'
                              CHECK (role IN ('worker', 'admin')),
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # workers table — shift stored as TEXT with CHECK constraint
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id          SERIAL PRIMARY KEY,
                name        VARCHAR(150) NOT NULL,
                phone       VARCHAR(20),
                contractor  VARCHAR(150),
                shift       TEXT DEFAULT 'morning'
                                CHECK (shift IN ('morning', 'afternoon', 'night')),
                username    VARCHAR(100) UNIQUE NOT NULL
                                REFERENCES users(username) ON DELETE CASCADE,
                password    VARCHAR(255) NOT NULL,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # attendance table — status stored as TEXT with CHECK constraint
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id            SERIAL PRIMARY KEY,
                worker_id     INT NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
                date          DATE NOT NULL,
                check_in      TIME,
                check_out     TIME,
                status        TEXT DEFAULT 'present'
                                  CHECK (status IN ('present', 'absent', 'late', 'half_day')),
                working_hours NUMERIC(4,2) DEFAULT 0.00,
                created_at    TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        conn.commit()

        # Seed default admin if not present
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                ('admin', 'admin123', 'admin')
            )
            conn.commit()
            print("[DB] Default admin created: username=admin, password=admin123")

        print("[DB] Database initialized successfully.")
        cursor.close()
    except Exception as e:
        print(f"[DB ERROR] Initialization failed: {e}")
        conn.rollback()
    finally:
        conn.close()
