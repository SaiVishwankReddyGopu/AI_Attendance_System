# app.py - Flask Application Entry Point
# Run with: python app.py

from flask import Flask
from flask_cors import CORS
from config import Config
from database import initialize_database
from routes import api

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Enable CORS for frontend communication
CORS(app, supports_credentials=True, origins=Config.CORS_ORIGINS)

# Register API routes with /api prefix
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    return {"message": "AI Attendance Management System API", "status": "running"}, 200

if __name__ == '__main__':
    print("=" * 50)
    print("  AI Attendance Management System - Backend")
    print("=" * 50)
    # Initialize database tables on startup
    initialize_database()
    print("[APP] Starting Flask server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
