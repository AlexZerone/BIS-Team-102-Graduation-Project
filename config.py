import os
from flask import current_app

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '159357'

    # MySQL Configuration
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'flask'

    # Security configurations
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # Change this to False during development
    SESSION_COOKIE_SAMESITE = 'Lax'
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Define a function to set paths that need the app instance
    @staticmethod
    def init_app(app):
        app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'resumes')
