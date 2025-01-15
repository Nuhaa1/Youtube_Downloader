import logging
from flask import Flask

# Create a Flask app
app = Flask(__name__)

# Set up basic logging configuration
logging.basicConfig(level=logging.DEBUG)

# Debugging message when the server starts
@app.before_first_request
def before_first_request():
    app.logger.debug("App has started and is waiting for requests...")

@app.route('/test')
def test():
    app.logger.debug("Test route accessed.")  # Log when the route is accessed
    return "Minimal test route working!"

# Error handling for 500 and 502 errors
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server error: {error}")
    return "Internal Server Error", 500

@app.errorhandler(502)
def bad_gateway_error(error):
    app.logger.error(f"Bad Gateway error: {error}")
    return "Bad Gateway Error", 502

if __name__ == '__main__':
    # Enable debug mode for Flask during development
    app.run(host='0.0.0.0', port=5000, debug=True)
