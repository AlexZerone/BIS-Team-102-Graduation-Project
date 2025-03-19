from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from models import get_record, get_records, execute_query
from permissions import login_required, role_required
from extensions import mysql



enrollments_bp = Blueprint('enrollments', __name__)



# ✅ **Optimized Enrollment Route**
@enrollments_bp.route('/enrollment', methods=['GET', 'POST'])
@login_required
def enrollment():
    if 'user_id' not in session:
        flash('Please log in to access enrollment', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    user_type = session['user_type']
    
    if user_type != 'student':
        flash('Only students can access enrollment', 'warning')
        return redirect(url_for('dashboard.dashboard'))

    try:
        student = get_record('SELECT StudentID FROM students WHERE UserID = %s', (user_id,))
        if not student:
            flash("Student profile not found!", "danger")
            return redirect(url_for("dashboard.dashboard"))

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

