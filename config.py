import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '159357'

    # MySQL Configuration
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'flask'

    # Security configurations
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_SAMESITE = 'Lax'