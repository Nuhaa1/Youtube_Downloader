import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

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

def is_blacklisted(url):
    """Check if a URL is blacklisted."""
    conn = connect_db()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blacklist WHERE url = %s", (url,))
        result = cursor.fetchone()
        return result is not None
    except psycopg2.Error as e:
        print(f"Error checking blacklist: {e}")
        return False
    finally:
        conn.close()

def add_to_blacklist(url):
    """Add a URL to the blacklist."""
    conn = connect_db()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO blacklist (url) VALUES (%s)", (url,))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error adding to blacklist: {e}")
        return False
    finally:
        conn.close()
    return True
