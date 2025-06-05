from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from models import get_record, get_records, execute_query
from permissions import login_required, role_required
from forms import CourseForm
from extensions import mysql  # Ensure you import your mysql instance

courses_bp = Blueprint('courses', __name__)

def get_student_id(user_id):
    student = get_record("SELECT StudentID FROM students WHERE UserID = %s", (user_id,))
    return student["StudentID"] if student else None

def get_instructor_id(user_id):
    instructor = get_record("SELECT InstructorID FROM instructors WHERE UserID = %s", (user_id,))
    return instructor["InstructorID"] if instructor else None

@courses_bp.route('/courses')
@login_required
def courses():
    user_id = session.get('user_id')
    user_type = session.get('user_type')

    if user_type == 'student':
        student_id = get_student_id(user_id)
        registered_courses = get_records('''
            SELECT c.*, cr.Status as RegistrationStatus 
            FROM courses c
            JOIN course_registrations cr ON c.CourseID = cr.CourseID
            WHERE cr.StudentID = %s
        ''', (student_id,))
    elif user_type == 'instructor':
        instructor_id = get_instructor_id(user_id)
        registered_courses = get_records('''
            SELECT c.*, COUNT(cr.StudentID) as EnrolledStudents
            FROM courses c
            JOIN instructor_courses ic ON c.CourseID = ic.CourseID
            LEFT JOIN course_registrations cr ON c.CourseID = cr.CourseID
            WHERE ic.InstructorID = %s
            GROUP BY c.CourseID
        ''', (instructor_id,))
    else:
        registered_courses = []

    return render_template('courses.html', courses=registered_courses, user_type=user_type)

@courses_bp.route('/course/<int:course_id>')
@login_required
def course_detail(course_id):
    user_type = session.get('user_type')
    try:
        # Get basic course info plus instructor name(s)
        course = get_record('''
            SELECT c.*, GROUP_CONCAT(u.First, ' ', u.Last) AS InstructorNames
            FROM courses c
            JOIN instructor_courses ic ON c.CourseID = ic.CourseID
            JOIN instructors i ON ic.InstructorID = i.InstructorID
            JOIN users u ON i.UserID = u.UserID
            WHERE c.CourseID = %s
            GROUP BY c.CourseID
        ''', (course_id,))

        if not course:
            flash('Course not found', 'danger')
            return redirect(url_for('courses.courses'))

        # Get assessments for this course
        assessments = get_records('''
            SELECT * FROM assessments 
            WHERE CourseID = %s 
            ORDER BY DueDate ASC
        ''', (course_id,))

        # If instructor, get enrolled students
        enrolled_students = None
        if user_type == 'instructor':
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
        return redirect(url_for('courses.courses'))

@courses_bp.route('/course/enrolled_courses')
@login_required
@role_required(['student'])
def enrolled_courses():
    user_id = session.get('user_id')
    student_id = get_student_id(user_id)
    registered_courses = get_records('''
        SELECT c.*, cr.Status as RegistrationStatus 
        FROM courses c
        JOIN course_registrations cr ON c.CourseID = cr.CourseID
        WHERE cr.StudentID = %s
    ''', (student_id,))
    return render_template('courses.html', courses=registered_courses, user_type='student')

@courses_bp.route('/course/create', methods=['GET', 'POST'])
@login_required
@role_required(['instructor'])
def create_course():
    form = CourseForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        start_date = form.start_date.data.strftime('%Y-%m-%d')
        end_date = form.end_date.data.strftime('%Y-%m-%d')
        duration = form.duration.data

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO courses (Title, Description, StartDate, EndDate, Duration)
                VALUES (%s, %s, %s, %s, %s)
            ''', (title, description, start_date, end_date, duration))
            course_id = cursor.lastrowid

            instructor_id = get_instructor_id(session['user_id'])
            if not instructor_id:
                raise Exception("Instructor profile not found.")

            cursor.execute('''
                INSERT INTO instructor_courses (InstructorID, CourseID)
                VALUES (%s, %s)
            ''', (instructor_id, course_id))

            mysql.connection.commit()
            flash('Course created successfully!', 'success')
            return redirect(url_for('courses.courses'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating course: {str(e)}', 'danger')
        finally:
            cursor.close()
    return render_template('create_course.html', form=form)

@courses_bp.route('/course/manage_courses')
@login_required
@role_required(['instructor'])
def manage_courses():
    user_id = session.get('user_id')
    instructor_id = get_instructor_id(user_id)
    courses = get_records('''
        SELECT c.*, COUNT(DISTINCT cr.StudentID) AS EnrolledCount
        FROM courses c
        JOIN instructor_courses ic ON c.CourseID = ic.CourseID
        LEFT JOIN course_registrations cr ON c.CourseID = cr.CourseID
        WHERE ic.InstructorID = %s
        GROUP BY c.CourseID
        ORDER BY c.Title
    ''', (instructor_id,))
    return render_template('manage_courses.html', courses=courses)