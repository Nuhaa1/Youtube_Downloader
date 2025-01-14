from flask import Flask, send_file, Response
import os

app = Flask(__name__)
DOWNLOAD_PATH = "downloads/"

@app.route('/downloads/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_PATH, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

def generate_file(file_path):
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            yield chunk

@app.route('/downloads/large/<filename>')
def download_large_file(filename):
    file_path = os.path.join(DOWNLOAD_PATH, filename)
    if os.path.exists(file_path):
        return Response(generate_file(file_path), headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'application/octet-stream'
        })
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
