import os
from flask import Flask, send_from_directory

app = Flask(__name__)
DOWNLOAD_PATH = "downloads/"

@app.route('/downloads/<filename>')
def download_file(filename):
    # Debugging: print the absolute path and check if the file exists
    abs_path = os.path.join(os.getcwd(), DOWNLOAD_PATH, filename)
    print(f"Looking for file at {abs_path}")
    if not os.path.exists(abs_path):
        return f"File {filename} not found", 404
    return send_from_directory(DOWNLOAD_PATH, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
