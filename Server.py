import os
from flask import Flask, send_from_directory

app = Flask(__name__)
DOWNLOAD_PATH = "downloads/"

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_PATH, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
