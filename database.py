import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from yt_dlp import YoutubeDL

# Load environment variables
load_dotenv()
PGUSER = os.getenv('PGUSER')
PGPASSWORD = os.getenv('PGPASSWORD')
PGHOST = os.getenv('PGHOST')
PGDATABASE = os.getenv('PGDATABASE')
PGPORT = os.getenv('PGPORT')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_UPLOAD_LIMIT = 50 * 1024 * 1024  # 50 MB
DOWNLOAD_PATH = "/app/downloads/"
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def connect_db():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            user=PGUSER,
            password=PGPASSWORD,
            host=PGHOST,
            database=PGDATABASE,
            port=PGPORT,
            cursor_factory=DictCursor
        )
        logging.debug("Database connection established successfully")
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error connecting to database: {e}")
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
        logging.error(f"Error resetting database: {e}")
        return False

def get_unique_filepath(base_filepath, ext):
    counter = 1
    unique_filepath = base_filepath + ext
    while os.path.exists(unique_filepath):
        unique_filepath = f"{base_filepath}_{counter}{ext}"
        counter += 1
    return unique_filepath

def handle_tiktok_video(url, message):
    try:
        logging.debug(f"Starting to download TikTok video: {url}")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{DOWNLOAD_PATH}%(title)s.%(ext)s',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'http_headers': {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Pragma': 'no-cache',
            }
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            logging.debug(f"Video info: {info}")

            file_path = ydl.prepare_filename(info)
            logging.debug(f"File path: {file_path}")

            base_filepath, ext = os.path.splitext(file_path)
            unique_filepath = get_unique_filepath(base_filepath, ext)

            if os.path.exists(file_path):
                os.rename(file_path, unique_filepath)
                logging.debug(f"File renamed to: {unique_filepath}")

            file_name = os.path.basename(unique_filepath)

            if os.path.exists(unique_filepath):
                file_size = os.path.getsize(unique_filepath)
                logging.debug(f"Downloaded file size: {file_size}")

                if file_size <= TELEGRAM_UPLOAD_LIMIT:
                    if send_video_with_retries(unique_filepath, message.chat.id):
                        os.remove(unique_filepath)
                        logging.debug(f"Deleted file after upload: {unique_filepath}")
                    else:
                        logging.error("Failed to upload video after multiple attempts")
                        bot.send_message(message.chat.id, "Failed to upload video after multiple attempts.")
                else:
                    send_download_button(message.chat.id, file_name)
                    threading.Thread(target=delete_file_after_delay, args=(unique_filepath, message.chat.id)).start()
            else:
                logging.error(f"File not found: {unique_filepath}")
                bot.send_message(message.chat.id, "Failed to download video. File not found after download.")
    except Exception as e:
        logging.error(f"Error during video processing: {e}")
        bot.send_message(message.chat.id, f"Failed to download video. Error: {e}")

if __name__ == "__main__":
    conn = connect_db()
    if conn:
        create_user_downloads_table(conn)
        # Example usage: handle a TikTok video and increment download count
        user_id = 123456789  # Example user ID
        ensure_user_in_db(conn, user_id)
        increment_download_count(conn, user_id)
        # handle_tiktok_video('https://www.tiktok.com/@user/video/123456789', message)  # Example TikTok URL
        conn.close()
