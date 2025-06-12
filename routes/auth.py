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
        
        # Determine approval status and user status based on user type
        if form.user_type.data == 'student':
            approval_status = 'Approved'
            user_status = 'Active'
        else:  # instructor or company
            approval_status = 'Pending'
            user_status = 'Inactive'
        
        # Insert user with proper approval status
        password_hash = generate_password_hash(form.password.data)
        execute_query('''
            INSERT INTO users (First, Last, Email, Password, UserType, ApprovalStatus, Status, CreatedAt, UpdatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ''', (form.first_name.data, form.last_name.data, form.email.data, password_hash, form.user_type.data, approval_status, user_status))
        
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
        
        if form.user_type.data == 'student':
            flash('Account created successfully! You can now log in.', 'success')
        else:
            flash('Account created successfully! Your account is pending approval.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Fetch user by email first (don't filter by status yet)
        user = get_record('SELECT * FROM users WHERE Email = %s', (email,))
        
        if user:
            # Check approval status first
            if user.get('ApprovalStatus') == 'Pending':
                flash('Your account is pending approval. Please wait for admin approval.', 'warning')
                return render_template('login.html', form=form)
            
            # Check if user status is active
            if user.get('Status') != 'Active':
                flash('Your account is not active. Please contact administrator.', 'danger')
                return render_template('login.html', form=form)
            
            stored_password = user['Password']
            
            # Check if password exists and is not empty
            if not stored_password:
                flash('Account password not set. Please contact administrator.', 'danger')
                return render_template('login.html', form=form)
            
            # Check if password is hashed (starts with hash method indicators)
            password_valid = False
            
            try:
                # Try to check as hashed password first
                password_valid = check_password_hash(stored_password, password)
            except ValueError:
                # If hash check fails, check if it's a plain text password (legacy)
                if stored_password == password:
                    password_valid = True
                    # Update to hashed password for security
                    try:
                        hashed_password = generate_password_hash(password)
                        execute_query('UPDATE users SET Password = %s WHERE UserID = %s', 
                                    (hashed_password, user['UserID']))
                        flash('Password security updated.', 'info')
                    except Exception as e:
                        # Log error but don't prevent login
                        pass
            
            if password_valid:
                session['user_id'] = user['UserID']
                session['user_type'] = user['UserType']
                session['user_name'] = user['First'] + " " + user['Last']

                try:
                    # Try to update LastLogin if column exists, otherwise just update UpdatedAt
                    execute_query('UPDATE users SET UpdatedAt = NOW() WHERE UserID = %s', (user['UserID'],))
                except Exception as e:
                    # Log error but don't prevent login
                    pass

                flash('Login successful!', 'success')
                return redirect(url_for('dashboard.dashboard'))

        # Generic error message for user
        if not user:
            flash('Email not found. Please check your email or register.', 'danger')
        elif user.get('ApprovalStatus') == 'Pending':
            flash('Your account is pending approval. Please wait for admin approval.', 'warning')
        elif user.get('Status') != 'Active':
            flash('Your account is not active. Please contact administrator.', 'danger')
        else:
            flash('Invalid password. Please try again.', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def adminlogin():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Fetch user by email first (don't filter by status yet)
        user = get_record('SELECT * FROM users WHERE Email = %s', (email,))
        
        if user:
            # Ensure only admin users can log in here
            if user.get('UserType').lower() != 'admin':
                flash('Access denied. Only admins can log in here.', 'danger')
                return render_template('login.html', form=form)

            # Check approval status first
            if user.get('ApprovalStatus') == 'Pending':
                flash('Your account is pending approval. Please wait for admin approval.', 'warning')
                return render_template('login.html', form=form)
            
            # Check if user status is active
            if user.get('Status') != 'Active':
                flash('Your account is not active. Please contact administrator.', 'danger')
                return render_template('login.html', form=form)
            
            stored_password = user['Password']
            
            # Check if password exists and is not empty
            if not stored_password:
                flash('Account password not set. Please contact administrator.', 'danger')
                return render_template('login.html', form=form)
            
            # Check if password is hashed (starts with hash method indicators)
            password_valid = False
            
            try:
                # Try to check as hashed password first
                password_valid = check_password_hash(stored_password, password)
            except ValueError:
                # If hash check fails, check if it's a plain text password (legacy)
                if stored_password == password:
                    password_valid = True
                    # Update to hashed password for security
                    try:
                        hashed_password = generate_password_hash(password)
                        execute_query('UPDATE users SET Password = %s WHERE UserID = %s', 
                                    (hashed_password, user['UserID']))
                        flash('Password security updated.', 'info')
                    except Exception as e:
                        # Log error but don't prevent login
                        pass
            
            if password_valid:
                session['user_id'] = user['UserID']
                session['user_type'] = user['UserType']
                session['user_name'] = user['First'] + " " + user['Last']

                try:
                    # Try to update LastLogin if column exists, otherwise just update UpdatedAt
                    execute_query('UPDATE users SET UpdatedAt = NOW() WHERE UserID = %s', (user['UserID'],))
                except Exception as e:
                    # Log error but don't prevent login
                    pass

                flash('Login successful!', 'success')
                return redirect(url_for('admin.dashboard'))

        # Generic error message for user
        flash('Invalid email or password, or account not approved.', 'danger')

    return render_template('login.html', form=form)



@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
