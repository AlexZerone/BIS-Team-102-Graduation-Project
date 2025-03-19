from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from models import get_record, get_records, execute_query
from permissions import login_required, role_required
from extensions import mysql



profile_bp = Blueprint('profile', __name__)




# Profile Management
@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        user = get_record('SELECT * FROM users WHERE UserID = %s', 
                         (session['user_id'],))
        
        if request.method == 'POST':
            # Update user information
            execute_query('''
                UPDATE users 
                SET First = %s, Last = %s, Email = %s
                WHERE UserID = %s
            ''', (request.form['first_name'], 
                 request.form['last_name'],
                 request.form['email'],
                 session['user_id']))
            
            # Update profile based on user type
            if session['user_type'] == 'student':
                execute_query('''
                    UPDATE students 
                    SET University = %s, Major = %s, GPA = %s
                    WHERE UserID = %s
                ''', (request.form['university'],
                     request.form['major'],
                     request.form['gpa'],
                     session['user_id']))
            
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile.profile'))
        
        return render_template('profile.html', user=user)
    
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'danger')
        return redirect(url_for('dashboard.dashboard'))





