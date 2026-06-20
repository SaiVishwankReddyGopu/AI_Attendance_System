# wsgi.py - Gunicorn entry point for Render deployment

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database import initialize_database

initialize_database()

if __name__ == "__main__":
    app.run()
