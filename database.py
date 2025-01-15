import psycopg2
from datetime import datetime
import os
from flask import Flask, jsonify, request, send_from_directory
import telebot
import logging
import urllib.parse

# Load environment variables
DB_HOST = os.getenv('PGHOST')
DB_NAME = os.getenv('PGDATABASE')
DB_USER = os.getenv('PGUSER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_PORT = os.getenv('PGPORT')

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
admin_user_ids = [123456789, 987654321]

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def connect_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

def create_user_downloads_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_downloads (
        user_id BIGINT PRIMARY KEY,
        download_count INTEGER DEFAULT 0,
        last_download_date DATE
    );
    ''')
    conn.commit()

def reset_database():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_downloads")
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Error resetting database: {e}")
        return False

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

@app.route('/reset', methods=['POST'])
def reset_database_route():
    try:
        if reset_database():
            return jsonify({"status": "success", "message": "Database has been reset successfully."}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to reset the database."}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bot.message_handler(commands=['reset'])
def reset_database_command(message):
    user_id = message.chat.id
    if user_id in admin_user_ids:
        if reset_database():
            bot.send_message(user_id, "Database has been reset successfully.")
        else:
            bot.send_message(user_id, "Failed to reset the database. Please try again later.")
    else:
        bot.send_message(user_id, "You don't have the required permissions to reset the database.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
