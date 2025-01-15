import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
import os
import requests
import json
import logging
import urllib.parse
import threading
import time
from dotenv import load_dotenv
from database import connect_db, get_download_count, increment_download_count
from requests.exceptions import ConnectionError, SSLError
import re
from flask import Flask, jsonify, request, send_from_directory

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_UPLOAD_LIMIT = 50 * 1024 * 1024  # 50 MB
DOWNLOAD_PATH = "/app/downloads/"
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Path to your cookies file in Railway project
COOKIES_PATH = "/app/cookies.txt"

def delete_file_after_delay(file_path, chat_id):
    time.sleep(1800)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.debug(f"Deleted file: {file_path}")
            bot.send_message(chat_id, f"The file {os.path.basename(file_path)} has been deleted from the server after 30 minutes.")
        else:
            logging.error(f"File not found: {file_path} - could not delete")
    except Exception as e:
        logging.error(f"Error deleting file: {file_path}, Error: {e}")

# Define the URL shortening function
def shorten_url(long_url):
    api_token = os.getenv('ADTIVAL_API_TOKEN')
    api_url = f"https://www.adtival.network/api?api={api_token}&url={long_url}&format=json"
    
    response = requests.get(api_url)
    if response.status_code == 200:
        try:
            result = response.json()
            if result['status'] == 'success':
                return result['shortenedUrl']
            else:
                logging.error(f"Error from Adtival: {result['message']}")
                return long_url  # Fallback to the original URL if there's an error
        except json.JSONDecodeError:
            logging.error("Error decoding JSON response from Adtival")
            return long_url  # Fallback to the original URL if there's an error
    else:
        logging.error(f"Error shortening URL: {response.status_code}")
        return long_url  # Fallback to the original URL if there's an error

# Test the URL shortening function
short_url = shorten_url("https://web-production-f9ab3.up.railway.app/downloads/samplefile.mp4")
print("Shortened URL:", short_url)

def get_unique_filepath(base_filepath, ext):
    counter = 1
    filepath = f"{base_filepath}{ext}"
    while os.path.exists(filepath):
        filepath = f"{base_filepath}_{counter}{ext}"
        counter += 1
    return filepath

def send_video_with_retries(file_path, chat_id, retries=3):
    for attempt in range(retries):
        try:
            with open(file_path, 'rb') as video:
                bot.send_video(chat_id, video)
            return True
        except Exception as e:
            logging.error(f"Error uploading video, attempt {attempt + 1}/{retries}: {e}")
            time.sleep(5)
    return False

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = (
        "👋 Welcome to the Video Downloader Bot! 🎉\n\n"
        "📹 **What I Can Do**:\n"
        "Send me any YouTube, Dailymotion, or TikTok link, and I'll help you download the video. If the video file is too large for Telegram, I'll provide you with a convenient download link.\n\n"
        "📅 **Daily Limit**:\n"
        "You can download up to **2 videos per day**. If you reach your limit, you'll need to verify to continue downloading. Some users can download without limits based on their verification status.\n\n"
        "🔍 **Quality Options**:\n"
        "Higher quality downloads, such as 4K and 2K, require verification. Enjoy your videos in the best possible quality after verifying your account!\n\n"
        "🛠️ **Beta Notice**:\n"
        "This bot is currently in beta. If you encounter any problems or bugs, please report them to @Amanadmin69.\n\n"
        "🚀 **Get Started**:\n"
        "Just send me a video link to get started. Enjoy! 🎥"
    )
    
    bot.send_message(message.chat.id, welcome_message)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text
    logging.debug(f"Received URL: {url}")
    bot.reply_to(message, "Fetching available video qualities, please wait...")

    if 'youtube.com' in url or 'youtu.be' in url:
        handle_youtube_video(url, message)
    elif 'dailymotion.com' in url or 'dai.ly' in url:
        handle_dailymotion_video(url, message)
    elif 'tiktok.com' in url:
        handle_tiktok_video(url, message)
    else:
        bot.reply_to(message, "Please send a valid YouTube, Dailymotion, or TikTok link.")

def handle_youtube_video(url, message):
    try:
        ydl_opts = {
            'noplaylist': True,
            'cookies': COOKIES_PATH  # Add the path to your cookies file
        }

        if 'youtube.com' in url:
            url_parts = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(url_parts.query)
            video_id = query_params['v'][0]
        elif 'youtu.be' in url:
            video_id = url.split('/')[-1]
        else:
            bot.reply_to(message, "Invalid YouTube link format.")
            return

        clean_url = f"https://www.youtube.com/watch?v={video_id}"

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            formats = info.get('formats', [])
            keyboard = InlineKeyboardMarkup()
            quality_set = set()
            for f in formats:
                if f['vcodec'] != 'none':
                    quality = str(f.get('format_note'))
                    format_id = f['format_id']
                    if quality and quality.lower() != 'none' and quality.strip():
                        if quality not in quality_set:
                            quality_set.add(quality)
                            callback_data = f'{format_id}|{video_id}|{quality}|youtube'
                            keyboard.add(InlineKeyboardButton(text=quality, callback_data=callback_data))
            callback_data = f'mp3|{video_id}|mp3|youtube'
            keyboard.add(InlineKeyboardButton(text="MP3", callback_data=callback_data))

            if quality_set:
                bot.reply_to(message, "Choose the video quality:", reply_markup=keyboard)
            else:
                bot.reply_to(message, "No video qualities available for this link.")
    except Exception as e:
        logging.error(f"Error fetching video qualities: {e}")
        bot.reply_to(message, f"Failed to fetch video qualities. Error: {e}")

def get_download_link(file_name):
    encoded_file_name = urllib.parse.quote(file_name)
    download_link = f"https://web-production-f9ab3.up.railway.app/downloads/{encoded_file_name}"
    return download_link

def send_download_button(chat_id, file_name):
    original_download_link = get_download_link(file_name)
    short_download_link = shorten_url(original_download_link)
    
    keyboard = InlineKeyboardMarkup()
    download_button = InlineKeyboardButton(text="Download", url=short_download_link)
    keyboard.add(download_button)
    
    bot.send_message(chat_id, (
        "The file is too large to upload to Telegram because the Telegram bot has a 50 MB upload limit. "
        "You can download it using the button below.\n\n"
        "Please download the file within 30 minutes. The file will be deleted from the server after 30 minutes to keep the server clean and efficient."
    ), reply_markup=keyboard)

def handle_dailymotion_video(url, message):
    try:
        ydl_opts = {'quiet': True, 'noplaylist': True, 'force_generic_extractor': True}

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            keyboard = InlineKeyboardMarkup()
            quality_set = set()

            for f in formats:
                if f['vcodec'] != 'none':
                    quality = str(f.get('format_note') or f.get('resolution'))
                    format_id = f['format_id']
                    if quality not in quality_set:
                        quality_set.add(quality)
                        callback_data = f'{format_id}|{info["id"]}|{quality}|dailymotion'
                        keyboard.add(InlineKeyboardButton(text=quality, callback_data=callback_data))
            # Add MP3 option
            callback_data = f'mp3|{info["id"]}|mp3|dailymotion'
            keyboard.add(InlineKeyboardButton(text="MP3", callback_data=callback_data))

            if quality_set:
                bot.reply_to(message, "Choose the video quality:", reply_markup=keyboard)
            else:
                bot.reply_to(message, "No video qualities available for this link.")
    except Exception as e:
        logging.error(f"Error fetching video qualities: {e}")
        bot.reply_to(message, f"Failed to fetch video qualities. Error: {e}")

def handle_tiktok_video(url, message):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{DOWNLOAD_PATH}%(title)s.%(ext)s',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            base_filepath, ext = os.path.splitext(file_path)
            unique_filepath = get_unique_filepath(base_filepath, ext)

            if os.path.exists(file_path):
                os.rename(file_path, unique_filepath)

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

@bot.callback_query_handler(func=lambda call: True)
def handle_quality_callback(call):
    logging.debug(f"Quality callback data: {call.data}")
    try:
        data = call.data.split('|')
        logging.debug(f"Parsed callback data: {data}")

        if len(data) < 4:
            raise ValueError("Incomplete callback data received.")

        format_id, video_id, quality, source = data

        if source == 'dailymotion':
            url = f"https://www.dailymotion.com/video/{video_id}"
        elif source == 'youtube':
            url = f"https://www.youtube.com/watch?v={video_id}"
        else:
            url = f"https://www.tiktok.com/@{video_id}"

        logging.debug(f"Downloading video from URL: {url}")

        if quality == "mp3":
            bot.send_message(call.message.chat.id, "Converting audio to MP3, please wait...")

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'noplaylist': True,
                'cookies': COOKIES_PATH  # Add the path to your cookies file
            }

            with YoutubeDL(ydl_opts) as ydl:
                logging.debug("Downloading and converting audio")
                info = ydl.extract_info(url, download=True)
                logging.debug(f"Downloaded info: {info}")
                file_path = ydl.prepare_filename(info)
                logging.debug(f"Prepared file path: {file_path}")

                # Ensure the MP3 file path is correct
                base_filepath, ext = os.path.splitext(file_path)
                mp3_filepath = base_filepath + ".mp3"
                logging.debug(f"MP3 file path: {mp3_filepath}")

                # Check if the MP3 file exists
                if os.path.exists(mp3_filepath):
                    file_name = os.path.basename(mp3_filepath)
                    file_size = os.path.getsize(mp3_filepath)
                    logging.debug(f"MP3 file size: {file_size}")

                    process_audio(mp3_filepath, file_size, file_name, call)
                else:
                    logging.error(f"File not found: {mp3_filepath}")
                    bot.send_message(call.message.chat.id, "Failed to download audio. File not found after download.")
        else:
            bot.send_message(call.message.chat.id, f"Downloading video in {quality}, please wait...")

            ydl_opts = {
                'format': f'{format_id}+bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s_%(format_id)s.%(ext)s'),
                'noplaylist': True,
                'merge_output_format': 'mp4',
                'cookies': COOKIES_PATH  # Add the path to your cookies file
            }

            with YoutubeDL(ydl_opts) as ydl:
                logging.debug(f"Starting video download with options: {ydl_opts}")
                info = ydl.extract_info(url, download=True)
                logging.debug(f"Downloaded video info: {info}")
                file_path = ydl.prepare_filename(info)
                logging.debug(f"Prepared file path: {file_path}")
                base_filepath, ext = os.path.splitext(file_path)
                logging.debug(f"Base file path: {base_filepath}, Extension: {ext}")
                unique_filepath = get_unique_filepath(base_filepath, ext)
                logging.debug(f"Unique file path: {unique_filepath}")

                if os.path.exists(file_path):
                    os.rename(file_path, unique_filepath)
                    logging.debug(f"Renamed file to unique path: {unique_filepath}")

                file_name = os.path.basename(unique_filepath)

                if os.path.exists(unique_filepath):
                    file_size = os.path.getsize(unique_filepath)
                    logging.debug(f"Downloaded file size: {file_size}")

                    process_file(unique_filepath, file_size, file_name, call)
                else:
                    logging.error(f"File not found after download: {unique_filepath}")
                    bot.send_message(call.message.chat.id, "Failed to download video. File not found after download.")
    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        bot.send_message(call.message.chat.id, f"Error processing video quality: {ve}")
    except Exception as e:
        logging.error(f"Error during video processing: {e}")
        bot.send_message(call.message.chat.id, f"Failed to download video. Error: {e}")

def process_audio(unique_filepath, file_size, file_name, call):
    if os.path.exists(unique_filepath):
        logging.debug(f"File exists: {unique_filepath}")
        
        if file_size <= TELEGRAM_UPLOAD_LIMIT:
            if send_audio_with_retries(unique_filepath, call.message.chat.id):
                if os.path.exists(unique_filepath):
                    os.remove(unique_filepath)
                    logging.debug(f"Deleted file after upload: {unique_filepath}")
            else:
                logging.error("Failed to upload audio after multiple attempts")
                bot.send_message(call.message.chat.id, "Failed to upload audio after multiple attempts.")
        else:
            original_download_link = get_download_link(file_name)
            short_download_link = shorten_url(original_download_link)
            bot.send_message(call.message.chat.id, (
                "The file is too large to upload to Telegram because the Telegram bot has a 50 MB upload limit. "
                "You can download it using the link below.\n\n"
                f"{short_download_link}\n\n"
                "Please download the file within 30 minutes. The file will be deleted from the server after 30 minutes to keep the server clean and efficient."
            ))
            threading.Thread(target=delete_file_after_delay, args=(unique_filepath, call.message.chat.id)).start()
    else:
        logging.error(f"File not found: {unique_filepath}")
        bot.send_message(call.message.chat.id, "Failed to find the MP3 file after conversion.")

def send_audio_with_retries(file_path, chat_id, retries=3):
    for attempt in range(retries):
        try:
            bot.send_audio(chat_id, audio=open(file_path, 'rb'))
            logging.debug(f"Successfully sent audio: {file_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to send audio (Attempt {attempt + 1}): {e}")
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
    return False

def sanitize_and_encode_filename(filename):
    sanitized_filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    encoded_filename = urllib.parse.quote(sanitized_filename)
    return encoded_filename

def setup_database():
    conn = connect_db()
    create_user_downloads_table(conn)

# Call this function at the start of your script
setup_database()

def process_file(unique_filepath, file_size, file_name, call):
    user_id = call.message.chat.id
    conn = connect_db()  # Ensure you establish a database connection
    
    if get_download_count(conn, user_id) >= 2:
        bot.send_message(user_id, "You have reached your download limit of 2 per day. Please try again tomorrow.")
        return
    
    file_name = sanitize_and_encode_filename(file_name)
    if file_size <= TELEGRAM_UPLOAD_LIMIT:
        if send_video_with_retries(unique_filepath, call.message.chat.id):
            os.remove(unique_filepath)
            logging.debug(f"Deleted file after upload: {unique_filepath}")
            increment_download_count(conn, user_id)
        else:
            logging.error("Failed to upload video after multiple attempts")
            bot.send_message(call.message.chat.id, "Failed to upload video after multiple attempts.")
    else:
        send_download_button(call.message.chat.id, file_name)
        bot.send_message(call.message.chat.id, "Please download the file within 30 minutes. The file will be deleted from the server after 30 minutes to keep the server clean and efficient.")
        threading.Thread(target=delete_file_after_delay, args=(unique_filepath, call.message.chat.id)).start()
        increment_download_count(conn, user_id)

def send_video_with_retries(file_path, chat_id, retries=3):
    for attempt in range(retries):
        try:
            with open(file_path, 'rb') as video:
                bot.send_video(chat_id, video)
            return True
        except Exception as e:
            logging.error(f"Error uploading video, attempt {attempt + 1}/{retries}: {e}")
            time.sleep(5)
    return False

# Start polling for the bot
threading.Thread(target=bot.polling, kwargs={'none_stop': True}).start()

# Initialize the Flask app
app = Flask(__name__)

# Flask routes
@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/test')
def test():
    return "Test route working!"

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    quality = request.args.get('quality', 'best')
    source = request.args.get('source', 'youtube')

    if not url:
        return jsonify({"error": "URL parameter is missing"}), 400

    logging.debug(f"Received download request: url={url}, quality={quality}, source={source}")

    try:
        file_path, file_name = download_video(url, quality, source)
        if file_path:
            return jsonify({"status": "success", "file_path": file_path, "file_name": file_name}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to download video"}), 500
    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/downloads/<path:filename>')
def download_file(filename):
    try:
        decoded_filename = urllib.parse.unquote(filename)
        return send_from_directory(DOWNLOAD_PATH, decoded_filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# Flask helper functions
def download_video(url, quality, source):
    try:
        ydl_opts = {
            'format': quality,
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'cookies': COOKIES_PATH  # Ensure the path to the cookies file is correct
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            base_filepath, ext = os.path.splitext(file_path)
            unique_filepath = get_unique_filepath(base_filepath, ext)

            if os.path.exists(file_path):
                os.rename(file_path, unique_filepath)
                logging.debug(f"Renamed file to unique path: {unique_filepath}")
            else:
                logging.error(f"File not found after download: {file_path}")
                return None, None

            file_name = os.path.basename(unique_filepath)
            file_size = os.path.getsize(unique_filepath)
            logging.debug(f"Downloaded file size: {file_size}")

            threading.Thread(target=delete_file_after_delay, args=(unique_filepath,)).start()
            return unique_filepath, file_name
    except Exception as e:
        logging.error(f"Error during video download: {e}")
        return None, None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
