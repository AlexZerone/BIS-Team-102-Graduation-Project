# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, SelectField, DateField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from functools import wraps




# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = '159357'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'

# Security configurations
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize MySQL and CSRF protection
mysql = MySQL(app)
csrf = CSRFProtect(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_type' not in session or session['user_type'] not in allowed_roles:
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ✅ **Forms**
'''class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    user_type = SelectField('User Type', choices=[('student', 'Student'), ('instructor', 'Instructor'), ('company', 'Company')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')'''

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    user_type = SelectField('User Type', 
                          choices=[('student', 'Student'), 
                                 ('instructor', 'Instructor'), 
                                 ('company', 'Company')],
                          validators=[DataRequired()])
    
    # Student fields
    university = StringField('University')
    major = StringField('Major')
    gpa = FloatField('GPA')
    expected_graduation_date = DateField('Expected Graduation Date', format='%Y-%m-%d')
    
    # Instructor fields
    department = StringField('Department')
    specialization = StringField('Specialization')
    experience = IntegerField('Years of Experience')
    
    # Company fields
    company_name = StringField('Company Name')
    industry = StringField('Industry')
    location = StringField('Location')
    company_size = StringField('Company Size')
    founded_date = DateField('Founded Date', format='%Y-%m-%d')

    def validate(self, *args, **kwargs):
        initial_validation = super(RegistrationForm, self).validate(*args, **kwargs)
        if not initial_validation:
            return False

        if self.user_type.data == 'student':
            if not self.university.data:
                self.university.errors.append('University is required for students')
                return False
            if not self.major.data:
                self.major.errors.append('Major is required for students')
                return False
            if not self.gpa.data:
                self.gpa.errors.append('GPA is required for students')
                return False
            if not self.expected_graduation_date.data:
                self.expected_graduation_date.errors.append('Expected graduation date is required for students')
                return False

        elif self.user_type.data == 'instructor':
            if not self.department.data:
                self.department.errors.append('Department is required for instructors')
                return False
            if not self.specialization.data:
                self.specialization.errors.append('Specialization is required for instructors')
                return False
            if not self.experience.data:
                self.experience.errors.append('Years of experience is required for instructors')
                return False

        elif self.user_type.data == 'company':
            if not self.company_name.data:
                self.company_name.errors.append('Company name is required')
                return False
            if not self.industry.data:
                self.industry.errors.append('Industry is required')
                return False
            if not self.location.data:
                self.location.errors.append('Location is required')
                return False
            if not self.company_size.data:
                self.company_size.errors.append('Company size is required')
                return False
            if not self.founded_date.data:
                self.founded_date.errors.append('Founded date is required')
                return False

        return True





class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# ✅ **Utility Functions**
def get_record(query, params=()):
    """ Fetch a single record """
    with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()


def get_records(query, params=()):
    """ Fetch multiple records """
    with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def execute_query(query, params=()):
    """ Execute an INSERT, UPDATE, or DELETE query """
    with mysql.connection.cursor() as cursor:
        cursor.execute(query, params)
        mysql.connection.commit()


# ✅ **Routes**
@app.route('/')
def index():
    # Changed to render home page instead of redirecting to login
    return render_template('home.html')


@app.route('/home')
def home():
    if 'user_id' in session:
        return redirect(url_for('post_home'))
    return render_template('home.html')


@app.route('/Post-home')
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


# ✅ **Login Route**
@app.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or account not active', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            # Rollback in case of error
            mysql.connection.rollback()
            print(f"Registration error: {str(e)}")  # For debugging
            flash('Registration failed. Please try again.', 'danger')
            return render_template('signup.html', form=form)
        
        finally:
            cursor.close()
            
    return render_template('signup.html', form=form)






@app.route('/dashboard')
@login_required
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'warning')
        return redirect(url_for('login'))
    
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
        return redirect(url_for('home'))



# ✅ **Logout**
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# ✅ **Courses Route**
@app.route('/courses')
@login_required
def courses():
    if 'user_id' not in session:
        flash('Please log in to view courses', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_type = session['user_type']
    
    if user_type == 'student':
        registered_courses = get_records('''
            SELECT c.*, cr.Status as RegistrationStatus 
            FROM courses c
            JOIN course_registrations cr ON c.CourseID = cr.CourseID
            WHERE cr.StudentID = (SELECT StudentID FROM students WHERE UserID = %s)
        ''', (user_id,))

    elif user_type == 'instructor':
        registered_courses = get_records('''
            SELECT c.*, COUNT(cr.StudentID) as EnrolledStudents
            FROM courses c
            JOIN instructor_courses ic ON c.CourseID = ic.CourseID
            LEFT JOIN course_registrations cr ON c.CourseID = cr.CourseID
            WHERE ic.InstructorID = (SELECT InstructorID FROM instructors WHERE UserID = %s)
            GROUP BY c.CourseID
        ''', (user_id,))
    
    return render_template('courses.html', courses=registered_courses, user_type=user_type)



# ✅ **Optimized Jobs Route**
@app.route('/jobs')
@login_required
def jobs():
    if 'user_id' not in session:
        flash('Please log in to view jobs', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_type = session['user_type']

    try:
        if user_type == 'student':
            student = get_record('SELECT StudentID FROM students WHERE UserID = %s', (user_id,))
            if not student:
                flash("Student profile not found!", "danger")
                return redirect(url_for("dashboard"))
            
            student_id = student['StudentID']

            # Optimized query: fetch jobs and application status in one go
            jobs = get_records('''
                SELECT j.*, c.Name AS CompanyName, 
                       COALESCE(ja.Status, 'Not Applied') AS ApplicationStatus,
                       ja.ApplicationDate
                FROM jobs j
                JOIN companies c ON j.CompanyID = c.CompanyID
                LEFT JOIN job_applications ja ON j.JobID = ja.JobID AND ja.StudentID = %s
                WHERE j.DeadlineDate >= CURDATE()
                ORDER BY j.PostingDate DESC
            ''', (student_id,))

        elif user_type == 'company':
            # Fetch company's posted jobs
            jobs = get_records('''
                SELECT j.*, 
                       (SELECT COUNT(*) FROM job_applications WHERE JobID = j.JobID) AS ApplicationCount
                FROM jobs j
                JOIN companies c ON j.CompanyID = c.CompanyID
                WHERE c.UserID = %s
                ORDER BY j.PostingDate DESC
            ''', (user_id,))
        
        return render_template('jobs.html', jobs=jobs, user_type=user_type)

    except Exception as e:
        flash(f'Error loading jobs: {str(e)}', 'danger')
        return render_template('jobs.html', jobs=[], user_type=user_type)

# ✅ **Optimized Assignments Route**
@app.route('/assignments')
@login_required
@role_required(['student', 'instructor'])
def assignments():
    if 'user_id' not in session:
        flash('Please log in to view assignments', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_type = session['user_type']

    try:
        if user_type == 'student':
            student = get_record('SELECT StudentID FROM students WHERE UserID = %s', (user_id,))
            if not student:
                flash("Student profile not found!", "danger")
                return redirect(url_for("dashboard"))
            
            student_id = student['StudentID']

            # Optimized query: Fetch assignments along with submission details
            assessments = get_records('''
                SELECT a.*, c.Title AS CourseTitle,
                       COALESCE(sa.Score, 'N/A') AS Score,
                       sa.SubmissionDate, sa.Status AS SubmissionStatus,
                       sa.Feedback
                FROM assessments a
                JOIN courses c ON a.CourseID = c.CourseID
                JOIN course_registrations cr ON c.CourseID = cr.CourseID
                LEFT JOIN student_assessments sa ON a.AssessID = sa.AssessID AND sa.StudentID = %s
                WHERE cr.StudentID = %s
                ORDER BY a.DueDate ASC
            ''', (student_id, student_id))

        elif user_type == 'instructor':
            instructor = get_record('SELECT InstructorID FROM instructors WHERE UserID = %s', (user_id,))
            if not instructor:
                flash("Instructor profile not found!", "danger")
                return redirect(url_for("dashboard"))
            
            instructor_id = instructor['InstructorID']

            assessments = get_records('''
                SELECT a.*, c.Title AS CourseTitle,
                       (SELECT COUNT(*) FROM student_assessments WHERE AssessID = a.AssessID) AS SubmissionCount
                FROM assessments a
                JOIN courses c ON a.CourseID = c.CourseID
                JOIN instructor_courses ic ON c.CourseID = ic.CourseID
                WHERE ic.InstructorID = %s
                ORDER BY a.DueDate ASC
            ''', (instructor_id,))

        return render_template('assignments.html', assessments=assessments, user_type=user_type)

    except Exception as e:
        flash(f'Error loading assignments: {str(e)}', 'danger')
        return render_template('assignments.html', assessments=[], user_type=user_type)

# ✅ **Optimized Enrollment Route**
@app.route('/enrollment', methods=['GET', 'POST'])
@login_required
def enrollment():
    if 'user_id' not in session:
        flash('Please log in to access enrollment', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_type = session['user_type']
    
    if user_type != 'student':
        flash('Only students can access enrollment', 'warning')
        return redirect(url_for('dashboard'))

    try:
        student = get_record('SELECT StudentID FROM students WHERE UserID = %s', (user_id,))
        if not student:
            flash("Student profile not found!", "danger")
            return redirect(url_for("dashboard"))

        student_id = student['StudentID']

        if request.method == 'POST':
            course_id = request.form.get('course_id')

            # Check if already enrolled
            exists = get_record('SELECT * FROM course_registrations WHERE StudentID = %s AND CourseID = %s', (student_id, course_id))
            if exists:
                flash('You are already registered for this course', 'warning')
            else:
                execute_query('''
                    INSERT INTO course_registrations (StudentID, CourseID, RegistrationDate, Status)
                    VALUES (%s, %s, NOW(), 'Enrolled')
                ''', (student_id, course_id))
                flash('Successfully registered for the course', 'success')

        # Fetch available courses
        available_courses = get_records('''
            SELECT c.*, i.First AS InstructorFirst, i.Last AS InstructorLast
            FROM courses c
            JOIN instructor_courses ic ON c.CourseID = ic.CourseID
            JOIN instructors inst ON ic.InstructorID = inst.InstructorID
            JOIN users i ON inst.UserID = i.UserID
            WHERE c.CourseID NOT IN (
                SELECT CourseID FROM course_registrations WHERE StudentID = %s
            )
            AND c.StartDate >= CURDATE()
        ''', (student_id,))

        return render_template('enrollment.html', available_courses=available_courses, user_type=user_type)

    except Exception as e:
        flash(f'Error processing enrollment: {str(e)}', 'danger')
        return render_template('enrollment.html', available_courses=[], user_type=user_type)

# Add these new routes and functions

# Course Management Routes
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        course = get_record('''
            SELECT c.*, u.First as InstructorFirst, u.Last as InstructorLast
            FROM courses c
            JOIN instructor_courses ic ON c.CourseID = ic.CourseID
            JOIN instructors i ON ic.InstructorID = i.InstructorID
            JOIN users u ON i.UserID = u.UserID
            WHERE c.CourseID = %s
        ''', (course_id,))
        
        if not course:
            flash('Course not found', 'danger')
            return redirect(url_for('courses'))
        
        # Get assessments for this course
        assessments = get_records('''
            SELECT * FROM assessments 
            WHERE CourseID = %s 
            ORDER BY DueDate ASC
        ''', (course_id,))
        
        # Get enrolled students if user is instructor
        enrolled_students = None
        if session['user_type'] == 'instructor':
            enrolled_students = get_records('''
                SELECT u.First, u.Last, cr.RegistrationDate, cr.Status
                FROM course_registrations cr
                JOIN students s ON cr.StudentID = s.StudentID
                JOIN users u ON s.UserID = u.UserID
                WHERE cr.CourseID = %s
            ''', (course_id,))
        
        return render_template('course_detail.html', 
                             course=course, 
                             assessments=assessments,
                             enrolled_students=enrolled_students)
    
    except Exception as e:
        flash(f'Error loading course details: {str(e)}', 'danger')
        return redirect(url_for('courses'))

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        job = get_record('''
            SELECT j.*, c.Name as CompanyName, c.Location, c.Industry
            FROM jobs j
            JOIN companies c ON j.CompanyID = c.CompanyID
            WHERE j.JobID = %s
        ''', (job_id,))
        
        if not job:
            flash('Job not found', 'danger')
            return redirect(url_for('jobs'))
        
        # Get application status if user is student
        application = None
        if session['user_type'] == 'student':
            student = get_record('SELECT StudentID FROM students WHERE UserID = %s', 
                               (session['user_id'],))
            if student:
                application = get_record('''
                    SELECT * FROM job_applications 
                    WHERE JobID = %s AND StudentID = %s
                ''', (job_id, student['StudentID']))
        
        return render_template('job_detail.html', job=job, application=application)
    
    except Exception as e:
        flash(f'Error loading job details: {str(e)}', 'danger')
        return redirect(url_for('jobs'))

@app.route('/apply-job/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect(url_for('login'))
    
    try:
        student = get_record('SELECT StudentID FROM students WHERE UserID = %s', 
                           (session['user_id'],))
        if not student:
            flash('Student profile not found', 'danger')
            return redirect(url_for('jobs'))
        
        # Check if already applied
        existing = get_record('''
            SELECT * FROM job_applications 
            WHERE JobID = %s AND StudentID = %s
        ''', (job_id, student['StudentID']))
        
        if existing:
            flash('You have already applied for this job', 'warning')
        else:
            resume = request.form.get('resume', '')
            execute_query('''
                INSERT INTO job_applications 
                (JobID, StudentID, ApplicationDate, Status, Resume)
                VALUES (%s, %s, NOW(), 'Pending', %s)
            ''', (job_id, student['StudentID'], resume))
            flash('Application submitted successfully', 'success')
        
        return redirect(url_for('job_detail', job_id=job_id))
    
    except Exception as e:
        flash(f'Error submitting application: {str(e)}', 'danger')
        return redirect(url_for('jobs'))

@app.route('/assessment/<int:assess_id>')
def assessment_detail(assess_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        assessment = get_record('''
            SELECT a.*, c.Title as CourseTitle
            FROM assessments a
            JOIN courses c ON a.CourseID = c.CourseID
            WHERE a.AssessID = %s
        ''', (assess_id,))
        
        if not assessment:
            flash('Assessment not found', 'danger')
            return redirect(url_for('assignments'))
        
        # Get submission if user is student
        submission = None
        if session['user_type'] == 'student':
            student = get_record('SELECT StudentID FROM students WHERE UserID = %s', 
                               (session['user_id'],))
            if student:
                submission = get_record('''
                    SELECT * FROM student_assessments 
                    WHERE AssessID = %s AND StudentID = %s
                ''', (assess_id, student['StudentID']))
        
        # Get all submissions if user is instructor
        submissions = None
        if session['user_type'] == 'instructor':
            submissions = get_records('''
                SELECT sa.*, u.First, u.Last
                FROM student_assessments sa
                JOIN students s ON sa.StudentID = s.StudentID
                JOIN users u ON s.UserID = u.UserID
                WHERE sa.AssessID = %s
            ''', (assess_id,))
        
        return render_template('assessment_detail.html', 
                             assessment=assessment,
                             submission=submission,
                             submissions=submissions)
    
    except Exception as e:
        flash(f'Error loading assessment details: {str(e)}', 'danger')
        return redirect(url_for('assignments'))

# Profile Management
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
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
            return redirect(url_for('profile'))
        
        return render_template('profile.html', user=user)
    
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)