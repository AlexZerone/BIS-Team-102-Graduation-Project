# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, blueprints
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from functools import wraps

from config import Config
from extensions import mysql
from permissions import login_required, role_required

from routes.auth import auth_bp
from routes.home import home_bp
from routes.courses import courses_bp
from routes.dashboard import dashboard_bp
from routes.enrollments import enrollments_bp
from routes.jobs import jobs_bp
from routes.assignments import assignments_bp
from routes.profile import profile_bp



# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize MySQL and CSRF protection
mysql.init_app(app)  # ✅ Initialize MySQL here
csrf = CSRFProtect(app)


# Routes
# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp, url_prefix="/")
app.register_blueprint(courses_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(enrollments_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(assignments_bp)
app.register_blueprint(profile_bp)


if __name__ == '__main__':
    app.run(debug=True)