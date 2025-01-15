import os
import time
import threading
import logging
import urllib.parse
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from yt_dlp import YoutubeDL

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()
TELEGRAM_UPLOAD_LIMIT = 50 * 1024 * 1024  # 50 MB
DOWNLOAD_PATH = "/app/downloads/"
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

# Initialize the Flask app
app = Flask(__name__)

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

def download_video(url, quality, source):
    try:
        ydl_opts = {
            'format': quality,
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'cookies': '/app/cookies.txt'  # Add the path to your cookies file
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

def get_unique_filepath(base_filepath, ext):
    counter = 1
    filepath = f"{base_filepath}{ext}"
    while os.path.exists(filepath):
        filepath = f"{base_filepath}_{counter}{ext}"
        counter += 1
    return filepath

def delete_file_after_delay(file_path):
    time.sleep(1800)  # 30 minutes
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.debug(f"Deleted file: {file_path}")
        else:
            logging.error(f"File not found: {file_path} - could not delete")
    except Exception as e:
        logging.error(f"Error deleting file: {file_path}, Error: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
