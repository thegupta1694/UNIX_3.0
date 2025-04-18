from flask import Flask, request, jsonify
import os
import sys

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app modules after adding to path
from app.api.routes_vercel import api, initialize_resources
from app.config import settings

app = Flask(__name__)
app.register_blueprint(api)

# Initialize resources when the app starts
try:
    initialize_resources()
except Exception as e:
    print(f"Warning: Could not initialize resources: {e}")

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Unix Commands API is running"})

# This is the entry point for Vercel
def handler(request):
    """Handle incoming requests for Vercel serverless functions."""
    # Convert Vercel request to Flask request
    if request.method == 'GET':
        return app.handle_request()
    elif request.method == 'POST':
        return app.handle_request()
    else:
        return jsonify({"error": "Method not allowed"}), 405

# For local development
if __name__ == '__main__':
    app.run(
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG
    ) 