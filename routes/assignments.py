from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from models import get_record, get_records, execute_query
from permissions import login_required, role_required
from extensions import mysql

assignments_bp = Blueprint('assignments', __name__)

# ✅ **Optimized Assignments Route**
@assignments_bp.route('/assignments')
@login_required
@role_required(['student', 'instructor'])
def assignments():
    if 'user_id' not in session:
        flash('Please log in to view assignments', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    user_type = session['user_type']

    try:
        if user_type == 'student':
            student = get_record('SELECT StudentID FROM students WHERE UserID = %s', (user_id,))
            if not student:
                flash("Student profile not found!", "danger")
                return redirect(url_for("dashboard.dashboard"))
            
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
                return redirect(url_for("dashboard.dashboard"))
            
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

@assignments_bp.route('/assessment/<int:AssessID>')
@login_required
@role_required(['student', 'instructor'])
def assessment_detail(AssessID):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        assessment = get_record('''
            SELECT a.*, c.Title as CourseTitle
            FROM assessments a
            JOIN courses c ON a.CourseID = c.CourseID
            WHERE a.AssessID = %s
        ''', (AssessID,))
        
        if not assessment:
            flash('Assessment not found', 'danger')
            return redirect(url_for('assignments.assignments'))
        
        # Get submission if user is student
        submission = None
        if session['user_type'] == 'student':
            student = get_record('SELECT StudentID FROM students WHERE UserID = %s', 
                               (session['user_id'],))
            if student:
                submission = get_record('''
                    SELECT * FROM student_assessments 
                    WHERE AssessID = %s AND StudentID = %s
                ''', (AssessID, student['StudentID']))
        
        # Get all submissions if user is instructor
        submissions = None
        if session['user_type'] == 'instructor':
            submissions = get_records('''
                SELECT sa.*, u.First, u.Last
                FROM student_assessments sa
                JOIN students s ON sa.StudentID = s.StudentID
                JOIN users u ON s.UserID = u.UserID
                WHERE sa.AssessID = %s
            ''', (AssessID,))
        
        return render_template('assessment_detail.html', 
                             assessment=assessment,
                             submission=submission,
                             submissions=submissions)
    
    except Exception as e:
        flash(f'Error loading assessment details: {str(e)}', 'danger')
        return redirect(url_for('assignments.assignments'))

@assignments_bp.route('/assignment/manage_assignments')
@login_required
@role_required(['instructor'])
def manage_assignments():
    user_id = session['user_id']
    
    try:
        # Get instructor's ID
        instructor = get_record('SELECT InstructorID FROM instructors WHERE UserID = %s', (user_id,))
        if not instructor:
            flash("Instructor profile not found!", "danger")
            return redirect(url_for("dashboard.dashboard"))
        
        instructor_id = instructor['InstructorID']

        # Get assessments created by instructor with course info and submission count
        assignments = get_records('''
            SELECT a.AssessID, a.Title AS AssignmentTitle, a.DueDate, 
                   c.Title AS CourseTitle,
                   (SELECT COUNT(*) FROM student_assessments sa WHERE sa.AssessID = a.AssessID) AS SubmissionCount
            FROM assessments a
            JOIN courses c ON a.CourseID = c.CourseID
            JOIN instructor_courses ic ON c.CourseID = ic.CourseID
            WHERE ic.InstructorID = %s
            ORDER BY a.DueDate ASC
        ''', (instructor_id,))
        
        return render_template('manage_assignments.html', assignments=assignments)

    except Exception as e:
        flash(f"Error loading instructor assignments: {str(e)}", "danger")
        return render_template('manage_assignments.html', assignments=[])


@assignments_bp.route('/submit-assessment/<int:AssessID>', methods=['POST'])
@login_required
@role_required(['student'])
def submit_assessment(AssessID):
    if 'user_id' not in session:
        flash('Please log in to submit the assignment', 'warning')
        return redirect(url_for('auth.login'))

    try:
        # Get current student ID
        student = get_record('SELECT StudentID FROM students WHERE UserID = %s', (session['user_id'],))
        if not student:
            flash("Student profile not found", "danger")
            return redirect(url_for("assignments.assignments"))
        
        student_id = student['StudentID']

        # Get submission content from form
        content = request.form.get('content', '').strip()
        if not content:
            flash('Submission content is required', 'danger')
            return redirect(url_for('assignments.assessment_detail', AssessID=AssessID))

        # Check if already submitted
        existing = get_record('''
            SELECT * FROM student_assessments
            WHERE StudentID = %s AND AssessID = %s
        ''', (student_id, AssessID))

        if existing:
            # Update existing submission
            execute_query('''
                UPDATE student_assessments
                SET Content = %s, SubmissionDate = NOW(), Status = 'Submitted'
                WHERE StudentID = %s AND AssessID = %s
            ''', (content, student_id, AssessID))
            flash('Assignment updated successfully', 'success')
        else:
            # Insert new submission
            execute_query('''
                INSERT INTO student_assessments
                (StudentID, AssessID, SubmissionDate, Status, Content)
                VALUES (%s, %s, NOW(), 'Submitted', %s)
            ''', (student_id, AssessID, content))
            flash('Assignment submitted successfully', 'success')

        return redirect(url_for('assignments.assessment_detail', AssessID=AssessID))

    except Exception as e:
        flash(f'Error submitting assignment: {str(e)}', 'danger')
        return redirect(url_for('assignments.assessment_detail', AssessID=AssessID))

@assignments_bp.route('/create-assessment', methods=['GET', 'POST'])
@login_required
@role_required(['instructor'])
def create_assessment():
    if 'user_id' not in session:
        flash('Please log in to create an assessment', 'warning')
        return redirect(url_for('auth.login'))

    try:
        # Get instructor's ID
        instructor = get_record('SELECT InstructorID FROM instructors WHERE UserID = %s', (session['user_id'],))
        if not instructor:
            flash("Instructor profile not found", "danger")
            return redirect(url_for("dashboard.dashboard"))

        instructor_id = instructor['InstructorID']

        # Fetch courses assigned to the instructor
        courses = get_records('''
            SELECT c.CourseID, c.Title 
            FROM courses c
            JOIN instructor_courses ic ON c.CourseID = ic.CourseID
            WHERE ic.InstructorID = %s
        ''', (instructor_id,))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            due_date = request.form.get('due_date')
            course_id = request.form.get('course_id')

            if not (title and description and due_date and course_id):
                flash('All fields are required', 'danger')
                return redirect(url_for('assignments.create_assessment'))

            # Insert the assessment
            execute_query('''
                INSERT INTO assessments (Title, Description, DueDate, CourseID)
                VALUES (%s, %s, %s, %s)
            ''', (title, description, due_date, course_id))

            flash('Assessment created successfully', 'success')
            return redirect(url_for('assignments.assignments'))

        return render_template('create_assessment.html', courses=courses)

    except Exception as e:
        flash(f'Error creating assessment: {str(e)}', 'danger')
        return redirect(url_for('assignments.assignments'))