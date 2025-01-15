import psycopg2
from datetime import datetime
import os

def connect_db():
    conn = psycopg2.connect(
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT")
    )
    return conn

def reset_download_count(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE user_downloads
    SET download_count = 0,
        last_download_date = %s
    WHERE user_id = %s
    ''', (datetime.now().date(), user_id))
    conn.commit()

def get_download_count(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT download_count, last_download_date
    FROM user_downloads
    WHERE user_id = %s
    ''', (user_id,))
    result = cursor.fetchone()
    
    if result:
        download_count, last_download_date = result
        if last_download_date != datetime.now().date():
            reset_download_count(conn, user_id)
            return 0
        return download_count
    else:
        cursor.execute('''
        INSERT INTO user_downloads (user_id, download_count, last_download_date)
        VALUES (%s, %s, %s)
        ''', (user_id, 0, datetime.now().date()))
        conn.commit()
        return 0

def increment_download_count(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE user_downloads
    SET download_count = download_count + 1,
        last_download_date = %s
    WHERE user_id = %s
    ''', (datetime.now().date(), user_id))
    conn.commit()
