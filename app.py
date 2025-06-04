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

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)



    # Initialize extensions
    mysql.init_app(app)
    csrf = CSRFProtect(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(courses_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(enrollments_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(profile_bp, url_prefix='/profile')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)