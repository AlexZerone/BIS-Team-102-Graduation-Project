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
            stats['enrolled_courses'] = course_count['count'] if course_count else 0            # Example: Get upcoming assignments
            raw_upcoming_items = get_records('''
                SELECT a.Type as Title, a.DueDate, c.Title as CourseTitle
                FROM assessments a
                JOIN courses c ON a.CourseID = c.CourseID
                JOIN course_registrations cr ON c.CourseID = cr.CourseID
                WHERE cr.StudentID = %s AND a.DueDate >= CURDATE()
                ORDER BY a.DueDate ASC
                LIMIT 5
            ''', (student_id,))
            
            # Process upcoming items to match template expectations
            upcoming_items = []
            for item in raw_upcoming_items:
                due_date = item['DueDate']
                # Safely calculate days_left
                try:
                    days_left = (due_date - datetime.now().date()).days if due_date else 0
                except (TypeError, AttributeError):
                    days_left = 0
                
                upcoming_items.append({
                    'title': item['Title'],
                    'subtitle': item['CourseTitle'],
                    'date': due_date.strftime('%Y-%m-%d') if due_date else 'No date',
                    'days_left': days_left
                })# Example: Get recent activities (e.g., submissions)
            raw_activities = get_records('''
                SELECT sa.SubmissionDate, a.Type AS AssessTitle, c.Title AS CourseTitle, sa.Score, sa.Status
                FROM student_assessments sa
                JOIN assessments a ON sa.AssessmentID = a.AssessID
                JOIN courses c ON a.CourseID = c.CourseID
                WHERE sa.StudentID = %s
                ORDER BY sa.SubmissionDate DESC
                LIMIT 5
            ''', (student_id,))
            
            # Process activities to match template expectations
            activities = []
            for activity in raw_activities:
                description = f"Submitted '{activity['AssessTitle']}' for {activity['CourseTitle']}"
                score_text = f" - Score: {activity['Score']}" if activity['Score'] is not None else f" - {activity['Status']}"
                activities.append({
                    'type': 'assignment',
                    'description': description + score_text,
                    'timestamp': activity['SubmissionDate'].strftime('%Y-%m-%d') if activity['SubmissionDate'] else 'N/A'
                })

    elif user_type == 'instructor':
        instructor = get_record('SELECT InstructorID FROM instructors WHERE UserID = %s', (user_id,))
        if instructor:
            instructor_id = instructor['InstructorID']
            # Number of assigned courses
            course_count = get_record('SELECT COUNT(*) as count FROM instructor_courses WHERE InstructorID = %s', (instructor_id,))
            stats['assigned_courses'] = course_count['count'] if course_count else 0            # Example: Get upcoming assessments to grade
            raw_upcoming_items = get_records('''
                SELECT a.Type as Title, a.DueDate, c.Title as CourseTitle
                FROM assessments a
                JOIN courses c ON a.CourseID = c.CourseID
                JOIN instructor_courses ic ON c.CourseID = ic.CourseID
                WHERE ic.InstructorID = %s AND a.DueDate >= CURDATE()
                ORDER BY a.DueDate ASC
                LIMIT 5
            ''', (instructor_id,))
            
            # Process upcoming items to match template expectations
            upcoming_items = []
            for item in raw_upcoming_items:
                due_date = item['DueDate']
                # Safely calculate days_left
                try:
                    days_left = (due_date - datetime.now().date()).days if due_date else 0
                except (TypeError, AttributeError):
                    days_left = 0
                
                upcoming_items.append({
                    'title': item['Title'],
                    'subtitle': item['CourseTitle'],
                    'date': due_date.strftime('%Y-%m-%d') if due_date else 'No date',
                    'days_left': days_left
                })# Example: Get recent grading activities
            raw_activities = get_records('''
                SELECT sa.SubmissionDate, a.Type AS AssessTitle, c.Title AS CourseTitle, sa.Score,
                       u.First, u.Last
                FROM student_assessments sa
                JOIN assessments a ON sa.AssessmentID = a.AssessID
                JOIN courses c ON a.CourseID = c.CourseID
                JOIN students s ON sa.StudentID = s.StudentID
                JOIN users u ON s.UserID = u.UserID
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
            
            # Process activities to match template expectations
            activities = []
            for activity in raw_activities:
                description = f"Graded {activity['First']} {activity['Last']}'s '{activity['AssessTitle']}' - {activity['CourseTitle']}"
                activities.append({
                    'type': 'assignment',
                    'description': description,
                    'timestamp': activity['SubmissionDate'].strftime('%Y-%m-%d') if activity['SubmissionDate'] else 'N/A'
                })

    elif user_type == 'company':
        company = get_record('SELECT CompanyID FROM companies WHERE UserID = %s', (user_id,))
        if company:
            company_id = company['CompanyID']
            # Number of active job postings
            job_count = get_record('SELECT COUNT(*) as count FROM jobs WHERE CompanyID = %s AND (ExpirationDate IS NULL OR ExpirationDate >= CURDATE())', (company_id,))
            stats['active_jobs'] = job_count['count'] if job_count else 0            # Recent job applications to company's jobs
            raw_activities = get_records('''
                SELECT ja.ApplicationDate, ja.Status, j.Title AS JobTitle, u.First, u.Last
                FROM job_applications ja
                JOIN jobs j ON ja.JobID = j.JobID
                JOIN students s ON ja.StudentID = s.StudentID
                JOIN users u ON s.UserID = u.UserID
                WHERE j.CompanyID = %s
                ORDER BY ja.ApplicationDate DESC
                LIMIT 5
            ''', (company_id,))
            
            # Process activities to match template expectations
            activities = []
            for activity in raw_activities:
                description = f"{activity['First']} {activity['Last']} applied for '{activity['JobTitle']}' - {activity['Status']}"
                activities.append({
                    'type': 'job',
                    'description': description,
                    'timestamp': activity['ApplicationDate'].strftime('%Y-%m-%d') if activity['ApplicationDate'] else 'N/A'
                })            # Upcoming job post expirations
            raw_upcoming_items = get_records('''
                SELECT Title, ExpirationDate
                FROM jobs
                WHERE CompanyID = %s AND ExpirationDate >= CURDATE()
                ORDER BY ExpirationDate ASC
                LIMIT 5
            ''', (company_id,))
            
            # Process upcoming items to match template expectations
            upcoming_items = []
            for item in raw_upcoming_items:
                expiration_date = item['ExpirationDate']
                # Safely calculate days_left
                try:
                    days_left = (expiration_date - datetime.now().date()).days if expiration_date else 0
                except (TypeError, AttributeError):
                    days_left = 0
                
                upcoming_items.append({
                    'title': item['Title'],
                    'subtitle': 'Job Posting',
                    'date': expiration_date.strftime('%Y-%m-%d') if expiration_date else 'No date',
                    'days_left': days_left
                })

    # Additional logic for other user types can be added similarly

    return render_template('Post-Login Home.html', 
                          user=user, 
                          user_type=user_type,
                          current_date=datetime.now(),
                          activities=activities,
                          upcoming_items=upcoming_items,
                          **stats)