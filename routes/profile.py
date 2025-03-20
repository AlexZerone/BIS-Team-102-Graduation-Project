from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import get_record, execute_query, get_user_stats
from permissions import login_required
from extensions import mysql
from forms import ProfileForm, PasswordChangeForm
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename




profile_bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    password_form = PasswordChangeForm()
    
    try:
        user_id = session['user_id']
        user_type = session['user_type']

        # Get user details
        user = get_record('SELECT * FROM users WHERE UserID = %s', (user_id,))
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('auth.logout'))

        # Get user type specific profile
        profile = None
        if user_type == 'student':
            profile = get_record('SELECT * FROM students WHERE UserID = %s', (user_id,))
        elif user_type == 'instructor':
            profile = get_record('SELECT * FROM instructors WHERE UserID = %s', (user_id,))
        elif user_type == 'company':
            profile = get_record('SELECT * FROM companies WHERE UserID = %s', (user_id,))

        # Get user stats
        stats = get_user_stats(user_id, user_type)

        if request.method == 'POST':
            if form.validate_on_submit():
                # Update user basic information
                execute_query('''
                    UPDATE users 
                    SET First = %s, Last = %s, Email = %s
                    WHERE UserID = %s
                ''', (form.first_name.data, form.last_name.data, form.email.data, user_id))

                # Update profile based on user type
                if user_type == 'student':
                    execute_query('''
                        UPDATE students 
                        SET University = %s, Major = %s, GPA = %s
                        WHERE UserID = %s
                    ''', (
                        request.form.get('university'),
                        request.form.get('major'),
                        request.form.get('gpa'),
                        user_id
                    ))

                flash('Profile updated successfully', 'success')
                return redirect(url_for('profile.profile'))

        # For GET request, populate form with current data
        if request.method == 'GET':
            form.first_name.data = user['First']
            form.last_name.data = user['Last']
            form.email.data = user['Email']

        return render_template('profile.html', 
                             user=user,
                             profile=profile,
                             form=form,
                             password_form=password_form,
                             **stats)

    except Exception as e:
        flash(f'Error accessing profile: {str(e)}', 'danger')
        return redirect(url_for('dashboard.dashboard'))

@profile_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        try:
            user = get_record('SELECT * FROM users WHERE UserID = %s', (session['user_id'],))
            
            if check_password_hash(user['Password'], form.current_password.data):
                new_password_hash = generate_password_hash(form.new_password.data)
                
                execute_query('''
                    UPDATE users 
                    SET Password = %s 
                    WHERE UserID = %s
                ''', (new_password_hash, session['user_id']))
                
                
                flash('Password changed successfully', 'success')
            else:
                flash('Current password is incorrect', 'danger')
        except Exception as e:
            flash(f'Error changing password: {str(e)}', 'danger')
    
    return redirect(url_for('profile.profile'))

@profile_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    if request.form.get('confirm_delete') == 'DELETE':
        try:
            user_id = session['user_id']
            
            # Delete user and related records
            execute_query('DELETE FROM users WHERE UserID = %s', (user_id,))
            
            session.clear()
            flash('Your account has been deleted', 'success')
            return redirect(url_for('home.home'))
        except Exception as e:
            flash(f'Error deleting account: {str(e)}', 'danger')
    else:
        flash('Please type DELETE to confirm account deletion', 'danger')
    
    return redirect(url_for('profile.profile'))

# File upload route (if needed)
@profile_bp.route('/upload-resume', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('profile.profile'))
    
    file = request.files['resume']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('profile.profile'))
    
    if file and allowed_file(file.filename):
        try:
            # Add your file upload logic here
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            
            # Update database with resume information
            execute_query('''
                UPDATE students 
                SET ResumeFile = %s 
                WHERE UserID = %s
            ''', (filename, session['user_id']))
            
            flash('Resume uploaded successfully', 'success')
        except Exception as e:
            flash(f'Error uploading resume: {str(e)}', 'danger')
    else:
        flash('Invalid file type', 'danger')
    
    return redirect(url_for('profile.profile'))


# User Settings Route
@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    try:
        user_id = session['user_id']

        if request.method == 'POST':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if new_password and new_password == confirm_password:
                execute_query('''
                    UPDATE users 
                    SET Password = %s
                    WHERE UserID = %s
                ''', (new_password, user_id))
                flash('Password updated successfully', 'success')
            else:
                flash('Passwords do not match', 'danger')

        return render_template('settings.html')

    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'danger')
        return redirect(url_for('profile.settings'))
