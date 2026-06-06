import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fintrack.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # Password expiry (days)
    PASSWORD_EXPIRY_DAYS = 45
    
    # Pagination
    ITEMS_PER_PAGE = 20