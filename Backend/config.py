# config.py - Application Configuration

import os

class Config:
    # Flask secret key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'myattendancesystem2024-dev-only')

    # Supabase / PostgreSQL connection string
    # Format: postgresql://user:password@host:port/dbname
    DATABASE_URL = os.environ.get('DATABASE_URL', '')

    # OpenAI API Key for GenAI features (optional)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

    # ML Model path
    MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ML', 'attendance_model.pkl')

    # CORS - comma-separated list of allowed origins, or * for all
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
