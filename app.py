from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import Config
from extensions import mysql
from routes.auth import auth_bp
from routes.home import home_bp
from routes.courses import courses_bp
from routes.dashboard import dashboard_bp
from routes.enrollments import enrollments_bp
from routes.jobs import jobs_bp
from routes.assignments import assignments_bp
from routes.profile import profile_bp
from routes.admin import admin_bp
from routes.subscriptions import subscriptions_bp
from routes.pages import pages_bp
from routes.help import help_bp
from routes.uploads import uploads_bp
from initialize_statuses import initialize_application_statuses

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    
    # Set MySQL configuration
    app.config['MYSQL_UNIX_SOCKET'] = None  # Use TCP instead of Unix socket
    
    # Initialize extensions
    mysql.init_app(app)
      # Initialize app extensions and data - after MySQL is connected
    with app.app_context():
        initialize_application_statuses()
    
    # Setup CSRF protection
    csrf = CSRFProtect(app)
      # Make csrf token available in all templates
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(courses_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(enrollments_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(admin_bp)
    app.register_blueprint(subscriptions_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(uploads_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)