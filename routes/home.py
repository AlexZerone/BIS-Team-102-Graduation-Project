from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from datetime import datetime
from models import get_record, get_records, execute_query
from permissions import login_required, role_required
from extensions import mysql

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
@home_bp.route('/home')
def home():
    if 'user_id' in session:
        return redirect(url_for('home.post_home'))
    return render_template('home.html')

@home_bp.route('/Post-home')
@login_required
def post_home():
    user_id = session['user_id']
    user_type = session['user_type']
    user = get_record('SELECT * FROM users WHERE UserID = %s', (user_id,))
    
    # Fetch role-specific data
    activities = []
    upcoming_items = []
    stats = {}

    if user_type == 'student':
        student = get_record('SELECT StudentID FROM students WHERE UserID = %s', (user_id,))
        if student:
            student_id = student['StudentID']
            # Number of enrolled courses
            course_count = get_record('SELECT COUNT(*) as count FROM course_registrations WHERE StudentID = %s', (student_id,))
            stats['enrolled_courses'] = course_count['count'] if course_count else 0
            # Example: Get upcoming assignments
            upcoming_items = get_records('''
                SELECT a.Title, a.DueDate, c.Title as CourseTitle
                FROM assessments a
                JOIN courses c ON a.CourseID = c.CourseID
                JOIN course_registrations cr ON c.CourseID = cr.CourseID
                WHERE cr.StudentID = %s AND a.DueDate >= CURDATE()
                ORDER BY a.DueDate ASC
                LIMIT 5
            ''', (student_id,))
            # Example: Get recent activities (e.g., submissions)
            activities = get_records('''
                SELECT sa.SubmissionDate, a.Title AS AssessTitle, c.Title AS CourseTitle, sa.Score
                FROM student_assessments sa
                JOIN assessments a ON sa.AssessID = a.AssessID
                JOIN courses c ON a.CourseID = c.CourseID
                WHERE sa.StudentID = %s
                ORDER BY sa.SubmissionDate DESC
                LIMIT 5
            ''', (student_id,))

    elif user_type == 'instructor':
        instructor = get_record('SELECT InstructorID FROM instructors WHERE UserID = %s', (user_id,))
        if instructor:
            instructor_id = instructor['InstructorID']
            # Number of assigned courses
            course_count = get_record('SELECT COUNT(*) as count FROM instructor_courses WHERE InstructorID = %s', (instructor_id,))
            stats['assigned_courses'] = course_count['count'] if course_count else 0
            # Example: Get upcoming assessments to grade
            upcoming_items = get_records('''
                SELECT a.Title, a.DueDate, c.Title as CourseTitle
                FROM assessments a
                JOIN courses c ON a.CourseID = c.CourseID
                JOIN instructor_courses ic ON c.CourseID = ic.CourseID
                WHERE ic.InstructorID = %s AND a.DueDate >= CURDATE()
                ORDER BY a.DueDate ASC
                LIMIT 5
            ''', (instructor_id,))
            # Example: Get recent grading activities
            activities = get_records('''
                SELECT sa.SubmissionDate, a.Title AS AssessTitle, c.Title AS CourseTitle, sa.Score
                FROM student_assessments sa
                JOIN assessments a ON sa.AssessID = a.AssessID
                JOIN courses c ON a.CourseID = c.CourseID
                WHERE a.AssessID IN (
                    SELECT a2.AssessID
                    FROM assessments a2
                    JOIN courses c2 ON a2.CourseID = c2.CourseID
                    JOIN instructor_courses ic2 ON c2.CourseID = ic2.CourseID
                    WHERE ic2.InstructorID = %s
                ) AND sa.Score IS NOT NULL
                ORDER BY sa.SubmissionDate DESC
                LIMIT 5
            ''', (instructor_id,))

    elif user_type == 'company':
        company = get_record('SELECT CompanyID FROM companies WHERE UserID = %s', (user_id,))
        if company:
            company_id = company['CompanyID']
            # Number of active job postings
            job_count = get_record('SELECT COUNT(*) as count FROM jobs WHERE CompanyID = %s AND (ExpirationDate IS NULL OR ExpirationDate >= CURDATE())', (company_id,))
            stats['active_jobs'] = job_count['count'] if job_count else 0
            # Recent job applications to company's jobs
            activities = get_records('''
                SELECT ja.ApplicationDate, ja.Status, j.Title AS JobTitle, u.First, u.Last
                FROM job_applications ja
                JOIN jobs j ON ja.JobID = j.JobID
                JOIN students s ON ja.StudentID = s.StudentID
                JOIN users u ON s.UserID = u.UserID
                WHERE j.CompanyID = %s
                ORDER BY ja.ApplicationDate DESC
                LIMIT 5
            ''', (company_id,))
            # Upcoming job post expirations
            upcoming_items = get_records('''
                SELECT Title, ExpirationDate
                FROM jobs
                WHERE CompanyID = %s AND ExpirationDate >= CURDATE()
                ORDER BY ExpirationDate ASC
                LIMIT 5
            ''', (company_id,))

    # Additional logic for other user types can be added similarly

    return render_template('Post-Login Home.html', 
                          user=user, 
                          user_type=user_type,
                          current_date=datetime.now(),
                          activities=activities,
                          upcoming_items=upcoming_items,
                          **stats)