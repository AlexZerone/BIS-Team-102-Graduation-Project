from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from datetime import datetime
from models import get_record, get_records, execute_query
from permissions import login_required, role_required
from extensions import mysql



home_bp = Blueprint('home', __name__)


@home_bp.route('/')
@home_bp.route('/home')
def home():
    if 'user_id' in session:
        return redirect(url_for('home.post_home'))
    return render_template('home.html')


@home_bp.route('/Post-home')
@login_required
def post_home():
    user_id = session['user_id']
    user_type = session['user_type']
    user = get_record('SELECT * FROM users WHERE UserID = %s', (user_id,))
    
    # Fetch role-specific data
    activities = []
    upcoming_items = []
    stats = {}
    
    # Example for student stats
    if user_type == 'student':
        student = get_record('SELECT StudentID FROM students WHERE UserID = %s', (user_id,))
        if student:
            student_id = student['StudentID']
            
            # Get course count
            course_count = get_record('SELECT COUNT(*) as count FROM course_registrations WHERE StudentID = %s', (student_id,))
            stats['enrolled_courses'] = course_count['count'] if course_count else 0
            
            # Additional student-specific data fetching can be added here

    # Similar logic can be added for other user types (e.g., instructor, company)

    return render_template('Post-Login Home.html', 
                          user=user, 
                          user_type=user_type,
                          current_date=datetime.now(),
                          activities=activities,
                          upcoming_items=upcoming_items,
                          **stats)







