from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistrationForm
from models import get_record, execute_query
from permissions import login_required, role_required
from extensions import mysql



auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if request.method == 'POST':
        try:
            # Start transaction
            cursor = mysql.connection.cursor()
            
            # Insert user
            insert_user_sql = """
                INSERT INTO users (First, Last, Email, Password, UserType)
                VALUES (%s, %s, %s, %s, %s)
            """
            user_data = (
                request.form['first_name'],
                request.form['last_name'],
                request.form['email'],
                generate_password_hash(request.form['password']),
                request.form['user_type']
            )
            
            cursor.execute(insert_user_sql, user_data)
            user_id = cursor.lastrowid
            
            # Handle role-specific registration
            user_type = request.form['user_type']
            
            if user_type == 'student':
                insert_student_sql = """
                    INSERT INTO students (UserID, University, Major, GPA, ExpectedGraduationDate)
                    VALUES (%s, %s, %s, %s, %s)
                """
                student_data = (
                    user_id,
                    request.form.get('university'),
                    request.form.get('major'),
                    request.form.get('gpa'),
                    request.form.get('expected_graduation_date')
                )
                cursor.execute(insert_student_sql, student_data)
                
            elif user_type == 'instructor':
                insert_instructor_sql = """
                    INSERT INTO instructors (UserID, Department, Specialization, Experience)
                    VALUES (%s, %s, %s, %s)
                """
                instructor_data = (
                    user_id,
                    request.form.get('department'),
                    request.form.get('specialization'),
                    request.form.get('experience')
                )
                cursor.execute(insert_instructor_sql, instructor_data)
                
            elif user_type == 'company':
                insert_company_sql = """
                    INSERT INTO companies (UserID, Name, Industry, Location, CompanySize, FoundedDate)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                company_data = (
                    user_id,
                    request.form.get('company_name'),
                    request.form.get('industry'),
                    request.form.get('location'),
                    request.form.get('company_size'),
                    request.form.get('founded_date')
                )
                cursor.execute(insert_company_sql, company_data)
            
            # Commit the transaction
            mysql.connection.commit()
            
            # Set session
            session['user_id'] = user_id
            session['user_type'] = user_type
            
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
            
        except Exception as e:
            # Rollback in case of error
            mysql.connection.rollback()
            print(f"Registration error: {str(e)}")  # For debugging
            flash('Registration failed. Please try again.', 'danger')
            return render_template('signup.html', form=form)
        
        finally:
            cursor.close()
            
    return render_template('signup.html', form=form)



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = get_record('SELECT * FROM users WHERE Email = %s AND Status = "Active"', (email,))

        if user and check_password_hash(user['Password'], password):
            session['user_id'] = user['UserID']
            session['user_type'] = user['UserType']

            try:
                execute_query('UPDATE users SET LastLoginDate = NOW() WHERE UserID = %s', (user['UserID'],))
            except Exception as e:
                flash(f"Database error: {str(e)}", "danger")

            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        
        flash('Invalid email or account not active', 'danger')
    
    return render_template('login.html', form=form)



@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

