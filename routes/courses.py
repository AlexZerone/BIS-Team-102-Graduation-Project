from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from models import get_record, get_records, execute_query
from permissions import login_required, role_required



courses_bp = Blueprint('courses', __name__)


# ✅ **Courses Route**
@courses_bp.route('/courses')
@login_required
def courses():
    if 'user_id' not in session:
        flash('Please log in to view courses', 'warning')
        return redirect(url_for('auth.login'))
    
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



@courses_bp.route('/course/<int:course_id>')
@login_required
def course_detail(course_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
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
            return redirect(url_for('courses.courses'))
        
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
        return redirect(url_for('courses.courses'))
