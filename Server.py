import os
from flask import Flask

app = Flask(__name__)

@app.route('/test')
def test():
    return "Minimal test route working!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Railway's PORT environment variable
    app.run(host='0.0.0.0', port=port)
