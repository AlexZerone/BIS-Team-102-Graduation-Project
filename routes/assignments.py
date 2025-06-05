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
            assessments = get_records('''                SELECT a.*, c.Title AS CourseTitle,
                       COALESCE(sa.Score, 'N/A') AS Score,
                       sa.SubmissionDate, sa.Status AS SubmissionStatus,
                       sa.Feedback
                FROM assessments a
                JOIN courses c ON a.CourseID = c.CourseID
                JOIN course_registrations cr ON c.CourseID = cr.CourseID                LEFT JOIN student_assessments sa ON a.AssessID = sa.AssessmentID AND sa.StudentID = %s
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
                SELECT a.*, c.Title AS CourseTitle,                       (SELECT COUNT(*) FROM student_assessments WHERE AssessmentID = a.AssessID) AS SubmissionCount
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
            if student:submission = get_record('''
                    SELECT * FROM student_assessments 
                    WHERE AssessmentID = %s AND StudentID = %s
                ''', (AssessID, student['StudentID']))
        
        # Get all submissions if user is instructor
        submissions = None
        if session['user_type'] == 'instructor':
            submissions = get_records('''
                SELECT sa.*, u.First, u.Last
                FROM student_assessments sa
                JOIN students s ON sa.StudentID = s.StudentID
                JOIN users u ON s.UserID = u.UserID
                WHERE sa.AssessmentID = %s
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
        
        instructor_id = instructor['InstructorID']        # Get assessments created by instructor with course info and submission count
        assignments = get_records('''
            SELECT a.AssessID, a.Type AS AssignmentTitle, a.DueDate, 
                   c.Title AS CourseTitle,                   (SELECT COUNT(*) FROM student_assessments sa WHERE sa.AssessmentID = a.AssessID) AS SubmissionCount
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
            return redirect(url_for("dashboard.dashboard"))
        
        student_id = student['StudentID']

        # Get submission content from form
        content = request.form.get('content', '').strip()
        if not content:
            flash('Submission content cannot be empty', 'danger')
            return redirect(url_for('assignments.assessment_detail', AssessID=AssessID))
        
        # Check if assessment exists and is valid for this student
        assessment = get_record('''
            SELECT a.* FROM assessments a
            JOIN courses c ON a.CourseID = c.CourseID
            JOIN course_registrations cr ON c.CourseID = cr.CourseID
            WHERE a.AssessID = %s AND cr.StudentID = %s
        ''', (AssessID, student_id))
        
        if not assessment:
            flash('Assessment not found or you are not enrolled in this course', 'danger')
            return redirect(url_for('assignments.assignments'))
          # Check if already submitted
        existing_submission = get_record('''            SELECT * FROM student_assessments
            WHERE AssessmentID = %s AND StudentID = %s
        ''', (AssessID, student_id))
        
        if existing_submission:
            flash('You have already submitted this assessment', 'warning')
            return redirect(url_for('assignments.assessment_detail', AssessID=AssessID))
          # Create new submission
        execute_query('''
            INSERT INTO student_assessments
            (StudentID, AssessmentID, SubmissionDate, Status, Feedback)
            VALUES (%s, %s, NOW(), 'Submitted', %s)
        ''', (student_id, AssessID, content))
        
        flash('Assessment submitted successfully!', 'success')
        return redirect(url_for('assignments.assessment_detail', AssessID=AssessID))

    except Exception as e:
        flash(f'Error submitting assessment: {str(e)}', 'danger')
        return redirect(url_for('assignments.assessment_detail', AssessID=AssessID))

@assignments_bp.route('/create-assessment', methods=['GET', 'POST'])
@login_required
@role_required(['instructor'])
def create_assessment():
    user_id = session['user_id']
    
    try:
        # Get instructor's ID
        instructor = get_record('SELECT InstructorID FROM instructors WHERE UserID = %s', (user_id,))
        if not instructor:
            flash("Instructor profile not found!", "danger")
            return redirect(url_for("dashboard.dashboard"))
        
        instructor_id = instructor['InstructorID']
        
        # Get courses taught by this instructor
        courses = get_records('''
            SELECT c.* FROM courses c
            JOIN instructor_courses ic ON c.CourseID = ic.CourseID
            WHERE ic.InstructorID = %s
        ''', (instructor_id,))
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('title')
            description = request.form.get('description')
            due_date = request.form.get('due_date')
            course_id = request.form.get('course_id')
            max_score = request.form.get('max_score', 100)
            weight_percent = request.form.get('weight', 10)
            
            # Convert weight percentage to decimal (0-1)
            try:
                # Ensure weight_percent is treated as a float
                weight_percent = float(weight_percent)
                  # Validate percentage is in valid range
                if weight_percent < 0 or weight_percent > 100:
                    flash('Weight must be between 0 and 100%', 'danger')
                    return render_template('create_assessment.html', courses=courses)
                    
                # Convert percentage to decimal (0-1 range) for database storage
                weight = weight_percent / 100.0
                
                # Double check decimal is in valid range for database constraint
                if weight < 0 or weight > 1:
                    flash('Error converting weight to proper format', 'danger')
                    return render_template('create_assessment.html', courses=courses)
            except ValueError:
                flash('Weight must be a valid number', 'danger')
                return render_template('create_assessment.html', courses=courses)
              # Validate required fields
            if not all([title, description, due_date, course_id]):
                flash('All fields are required', 'danger')
                return render_template('create_assessment.html', courses=courses)
            
            # Create the assessment
            execute_query('''
                INSERT INTO assessments 
                (CourseID, Type, Description, DueDate, MaxScore, Weight)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (course_id, title, description, due_date, max_score, weight))
            
            flash('Assessment created successfully!', 'success')
            return redirect(url_for('assignments.assignments'))
        
        return render_template('create_assessment.html', courses=courses)
    
    except Exception as e:
        flash(f'Error creating assessment: {str(e)}', 'danger')
        return redirect(url_for('assignments.assignments'))

@assignments_bp.route('/review-submission/<int:AssessID>/<int:StudentID>', methods=['GET', 'POST'])
@login_required
@role_required(['instructor'])
def review_submission(AssessID, StudentID):
    """Route for instructors to review and grade student submissions"""
    
    try:
        # Check if the instructor teaches the course with this assessment
        instructor = get_record('SELECT InstructorID FROM instructors WHERE UserID = %s', 
                              (session['user_id'],))
        if not instructor:
            flash("Instructor profile not found!", "danger")
            return redirect(url_for("dashboard.dashboard"))
        
        instructor_id = instructor['InstructorID']
        
        # Verify this assessment is for a course taught by this instructor
        assessment_course = get_record('''
            SELECT a.*, c.Title AS CourseTitle, ic.InstructorID 
            FROM assessments a
            JOIN courses c ON a.CourseID = c.CourseID
            JOIN instructor_courses ic ON c.CourseID = ic.CourseID
            WHERE a.AssessID = %s AND ic.InstructorID = %s
        ''', (AssessID, instructor_id))
        
        if not assessment_course:
            flash("You don't have permission to review this assessment", "danger")
            return redirect(url_for('assignments.assignments'))
          # Get student information and submission
        submission = get_record('''
            SELECT sa.*, u.First, u.Last, u.Email
            FROM student_assessments sa
            JOIN students s ON sa.StudentID = s.StudentID
            JOIN users u ON s.UserID = u.UserID
            WHERE sa.AssessmentID = %s AND sa.StudentID = %s
        ''', (AssessID, StudentID))
        
        if not submission:
            flash("Submission not found", "danger")
            return redirect(url_for('assignments.assessment_detail', AssessID=AssessID))
        
        if request.method == 'POST':
            # Update the submission with feedback and score
            score = request.form.get('score')
            feedback = request.form.get('feedback')
            
            try:
                score_float = float(score)
                if score_float < 0 or score_float > assessment_course['MaxScore']:
                    flash(f"Score must be between 0 and {assessment_course['MaxScore']}", "danger")
                    return redirect(url_for('assignments.review_submission', 
                                          AssessID=AssessID, StudentID=StudentID))
            except:
                flash("Score must be a valid number", "danger")
                return redirect(url_for('assignments.review_submission', 
                                       AssessID=AssessID, StudentID=StudentID))
            execute_query('''
                UPDATE student_assessments
                SET Score = %s, Feedback = %s, Status = 'Completed', UpdatedAt = NOW()
                WHERE AssessmentID = %s AND StudentID = %s
            ''', (score, feedback, AssessID, StudentID))
            
            flash("Submission graded successfully!", "success")
            return redirect(url_for('assignments.assessment_detail', AssessID=AssessID))
        
        return render_template('review_submission.html', 
                             assessment=assessment_course,
                             submission=submission)
    
    except Exception as e:
        flash(f"Error reviewing submission: {str(e)}", "danger")
        return redirect(url_for('assignments.assignments'))