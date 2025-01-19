import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def connect_db():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_user_downloads_table(conn):
    """Create the user_downloads table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_downloads (
            user_id BIGINT PRIMARY KEY,
            download_count INTEGER NOT NULL,
            last_download_date DATE NOT NULL
        )
    """)
    conn.commit()

def ensure_user_in_db(conn, user_id):
    """Ensure the user exists in the database."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_downloads (user_id, download_count, last_download_date)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, 0, datetime.now().date()))
    conn.commit()

def get_download_count(conn, user_id):
    """Get the download count for a user."""
    cursor = conn.cursor()
    cursor.execute("SELECT download_count FROM user_downloads WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    return result['download_count'] if result else 0

def increment_download_count(conn, user_id):
    """Increment the download count for a user."""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_downloads
        SET download_count = download_count + 1,
            last_download_date = %s
        WHERE user_id = %s
    """, (datetime.now().date(), user_id))
    conn.commit()

def reset_database():
    """Reset the user_downloads table in the database."""
    try:
        conn = connect_db()
        if conn is None:
            return False
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS user_downloads")
        create_user_downloads_table(conn)
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"Error resetting database: {e}")
        return False
