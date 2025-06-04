from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm
from models import get_record, execute_query
from permissions import login_required
from extensions import mysql


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing = get_record('SELECT * FROM users WHERE Email = %s', (form.email.data,))
        if existing:
            flash('Email already registered.', 'danger')
            return render_template('register.html', form=form)
        # Insert user
        password_hash = generate_password_hash(form.password.data)
        execute_query('''
            INSERT INTO users (First, Last, Email, Password, UserType, CreatedAt, UpdatedAt, Status)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), 'Active')
        ''', (form.first_name.data, form.last_name.data, form.email.data, password_hash, form.user_type.data))
        user = get_record('SELECT * FROM users WHERE Email = %s', (form.email.data,))
        user_id = user['UserID']
        # Insert profile data based on user type
        if form.user_type.data == 'student':
            execute_query('''
                INSERT INTO students (UserID, University, Major, GPA, ExpectedGraduationDate, CreatedAt, UpdatedAt)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            ''', (user_id, form.university.data, form.major.data, form.gpa.data, form.expected_graduation_date.data))
        elif form.user_type.data == 'instructor':
            execute_query('''
                INSERT INTO instructors (UserID, Department, Specialization, Experience, CreatedAt, UpdatedAt)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            ''', (user_id, form.department.data, form.specialization.data, form.experience.data))
        elif form.user_type.data == 'company':
            execute_query('''
                INSERT INTO companies (UserID, Name, Industry, Location, CompanySize, FoundedDate, CreatedAt, UpdatedAt)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            ''', (user_id, form.company_name.data, form.industry.data, form.location.data, form.company_size.data, form.founded_date.data))
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Fetch only active users
        user = get_record('SELECT * FROM users WHERE Email = %s AND Status = "Active"', (email,))
        
        if user and check_password_hash(user['Password'], password):
            session['user_id'] = user['UserID']
            session['user_type'] = user['UserType']
            session['user_name'] = user['First'] + " " + user['Last']

            try:
                execute_query('UPDATE users SET UpdatedAt = NOW() WHERE UserID = %s', (user['UserID'],))
            except Exception as e:
                flash(f"Database error: {str(e)}", "danger")

            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))

        # Generic error message for user
        flash('Invalid email or password, or account not active.', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))