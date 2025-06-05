from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from models import get_record, get_records, execute_query
from permissions import login_required, role_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'warning')
        return redirect(url_for('auth.login'))
    
    try:
        user_id = session['user_id']
        user_type = session['user_type']

        user = get_record('SELECT * FROM users WHERE UserID = %s', (user_id,))
        profile = None

        if user_type == 'student':
            profile = get_record('SELECT * FROM students WHERE UserID = %s', (user_id,))
        elif user_type == 'instructor':
            profile = get_record('SELECT * FROM instructors WHERE UserID = %s', (user_id,))
        elif user_type == 'company':
            profile = get_record('SELECT * FROM companies WHERE UserID = %s', (user_id,))
        
        return render_template('dashboard.html', user=user, profile=profile, user_type=user_type)
    
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return redirect(url_for('home.home'))