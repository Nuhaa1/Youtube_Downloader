from flask import Flask, send_from_directory
import os

app = Flask(__name__)
DOWNLOAD_PATH = "downloads/"

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_PATH, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
