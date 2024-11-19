import os
from datetime import timedelta

class Config:
    ENV = os.environ.get('FLASK_ENV', 'development')
    if ENV == 'development':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'  # Example for local SQLite DB
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/dbname')  # Production database

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    SESSION_COOKIE_SECURE = ENV != 'development'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # Define session lifetime
    SESSION_LIFETIME = timedelta(days=7)  # Sessions will last 7 days
