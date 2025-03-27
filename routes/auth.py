from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistrationForm
from models import get_record, execute_query
from permissions import login_required
from extensions import mysql
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Get user type ID from database
            user_type = get_record(
                "SELECT TypeID FROM user_types WHERE Name = %s",
                (form.user_type.data.lower(),)
            )
            
            if not user_type:
                flash('Invalid user type selected', 'danger')
                return render_template('signup.html', form=form)

            # Start transaction
            with mysql.connection.cursor() as cursor:
                # Insert user
                user_query = """
                    INSERT INTO users 
                    (First, Last, Email, Password, TypeID)
                    VALUES (%s, %s, %s, %s, %s)
                """
                user_data = (
                    form.first_name.data.strip(),
                    form.last_name.data.strip(),
                    form.email.data.lower(),
                    generate_password_hash(form.password.data),
                    user_type['TypeID']
                )
                cursor.execute(user_query, user_data)
                user_id = cursor.lastrowid

                # Handle role-specific registration
                if form.user_type.data.lower() == 'student':
                    student_query = """
                        INSERT INTO students 
                        (UserID, University, Major, GPA, ExpectedGraduationDate)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    student_data = (
                        user_id,
                        form.university.data.strip(),
                        form.major.data.strip(),
                        float(form.gpa.data),
                        form.expected_graduation.data
                    )
                    cursor.execute(student_query, student_data)

                elif form.user_type.data.lower() == 'instructor':
                    instructor_query = """
                        INSERT INTO instructors 
                        (UserID, Department, Specialization, Experience)
                        VALUES (%s, %s, %s, %s)
                    """
                    instructor_data = (
                        user_id,
                        form.department.data.strip(),
                        form.specialization.data.strip(),
                        int(form.experience.data)
                    )
                    cursor.execute(instructor_query, instructor_data)

                elif form.user_type.data.lower() == 'company':
                    company_query = """
                        INSERT INTO companies 
                        (UserID, Name, Industry, Location, SizeID, FoundedDate)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    company_data = (
                        user_id,
                        form.company_name.data.strip(),
                        form.industry.data.strip(),
                        form.location.data.strip(),
                        int(form.company_size.data),
                        form.founded_date.data
                    )
                    cursor.execute(company_query, company_data)

                mysql.connection.commit()
                
                # Set session with additional validation
                session.permanent = True
                session['user_id'] = user_id
                session['user_type'] = form.user_type.data.lower()
                session['fresh'] = True  # For sensitive operations

                flash('Registration successful!', 'success')
                return redirect(url_for('dashboard.dashboard'))

        except Exception as e:
            mysql.connection.rollback()
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            flash('Registration failed due to a system error. Please try again.', 'danger')
        finally:
            cursor.close()

    elif request.method == 'POST':
        flash('Form validation failed. Please correct the errors.', 'warning')

    return render_template('signup.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # Get user with type information
            user_query = """
                SELECT u.*, ut.Name AS user_type 
                FROM users u
                JOIN user_types ut ON u.TypeID = ut.TypeID
                WHERE u.Email = %s AND u.Status = 'Active'
            """
            user = get_record(user_query, (form.email.data.lower(),))

            if user and check_password_hash(user['Password'], form.password.data):
                # Update last login
                execute_query(
                    "UPDATE users SET LastLoginDate = NOW() WHERE UserID = %s",
                    (user['UserID'],)
                )

                # Regenerate session to prevent fixation
                session.clear()
                session['user_id'] = user['UserID']
                session['user_type'] = user['user_type']
                session['fresh'] = True
                session.permanent = True

                flash('Login successful!', 'success')
                return redirect(url_for('dashboard.dashboard'))

            flash('Invalid credentials or inactive account', 'danger')

        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            flash('Login temporarily unavailable. Please try again later.', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    try:
        # Clear server-side session data if needed
        execute_query(
            "UPDATE users SET LastLoginDate = NOW() WHERE UserID = %s",
            (session['user_id'],)
        )
    except Exception as e:
        logger.error(f"Logout error: {str(e)}", exc_info=True)

    # Client-side session cleanup
    session.clear()
    flash('You have been securely logged out', 'info')
    return redirect(url_for('auth.login'))