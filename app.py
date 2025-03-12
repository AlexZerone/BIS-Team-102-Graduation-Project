# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = '159357'

# Add this line to initialize CSRF protection
csrf = CSRFProtect(app)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
# app.config['MYSQL_PORT'] = 3306  # Default port, uncomment if needed

# Initialize MySQL
mysql = MySQL(app)

# Registration form
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

# Login form
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        # Create cursor for database connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE Email = %s', (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['Password'], password):
            session['user_id'] = user['UserID']
            session['user_type'] = user['UserType']
            
            # Update last login date
            cursor.execute(
                'UPDATE users SET LastLoginDate = %s WHERE UserID = %s',
                (datetime.utcnow(), user['UserID'])
            )
            mysql.connection.commit()
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    form_errors = []
    
    if request.method == 'POST':
        # Get common user data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        # Create cursor for database connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if email already exists
        cursor.execute('SELECT * FROM users WHERE Email = %s', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        try:
            # Create new user
            hashed_password = generate_password_hash(password)
            created_date = datetime.utcnow()
            
            cursor.execute(
                'INSERT INTO users (First, Last, Email, Password, UserType, CreatedDate, Status) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (first_name, last_name, email, hashed_password, user_type, created_date, 'Active')
            )
            mysql.connection.commit()
            
            # Get the newly created user ID
            user_id = cursor.lastrowid
            
            # Create profile based on user type
            if user_type == 'student':
                university = request.form.get('university')
                major = request.form.get('major')
                gpa = request.form.get('gpa')
                expected_graduation_date = request.form.get('expected_graduation_date')
                
                enrollment_date = datetime.utcnow()
                updated_date = datetime.utcnow()
                
                cursor.execute(
                    'INSERT INTO students (UserID, University, Major, GPA, EnrollmentDate, ExpectedGraduationDate, UpdatedDate) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (user_id, university, major, gpa, enrollment_date, expected_graduation_date, updated_date)
                )
                
            elif user_type == 'instructor':
                department = request.form.get('department')
                specialization = request.form.get('specialization')
                experience = request.form.get('experience')
                hire_date = datetime.utcnow()
                
                cursor.execute(
                    'INSERT INTO instructors (UserID, Department, Specialization, Experience, HireDate) VALUES (%s, %s, %s, %s, %s)',
                    (user_id, department, specialization, experience, hire_date)
                )
                
            elif user_type == 'company':
                company_name = request.form.get('company_name')
                location = request.form.get('location')
                industry = request.form.get('industry')
                company_size = request.form.get('company_size')
                founded_date = request.form.get('founded_date')
                
                cursor.execute(
                    'INSERT INTO companies (UserID, Name, Location, Industry, CompanySize, FoundedDate) VALUES (%s, %s, %s, %s, %s, %s)',
                    (user_id, company_name, location, industry, company_size, founded_date)
                )
            
            mysql.connection.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('register'))
        
        finally:
            cursor.close()
    
    return render_template('signup.html', form=form, form_errors=form_errors)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_type = session['user_type']
    
    # Create cursor for database connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get user information
    cursor.execute('SELECT * FROM users WHERE UserID = %s', (user_id,))
    user = cursor.fetchone()
    
    # Get profile information based on user type
    profile = None
    if user_type == 'student':
        cursor.execute('SELECT * FROM students WHERE UserID = %s', (user_id,))
        profile = cursor.fetchone()
    elif user_type == 'instructor':
        cursor.execute('SELECT * FROM instructors WHERE UserID = %s', (user_id,))
        profile = cursor.fetchone()
    elif user_type == 'company':
        cursor.execute('SELECT * FROM companies WHERE UserID = %s', (user_id,))
        profile = cursor.fetchone()
    
    cursor.close()
    
    return render_template('dashboard.html', user=user, profile=profile, user_type=user_type)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)