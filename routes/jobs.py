from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from models import get_record, get_records, execute_query
from permissions import login_required, role_required
from extensions import mysql

jobs_bp = Blueprint('jobs', __name__)

# ✅ **Optimized Jobs Route**
@jobs_bp.route('/jobs')
@login_required
def jobs():
    if 'user_id' not in session:
        flash('Please log in to view jobs', 'warning')
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

@jobs_bp.route('/job/<int:job_id>')
@login_required
@role_required(['student', 'company'])
def job_detail(job_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        job = get_record('''
            SELECT j.*, c.Name as CompanyName, c.Location, c.Industry
            FROM jobs j
            JOIN companies c ON j.CompanyID = c.CompanyID
            WHERE j.JobID = %s
        ''', (job_id,))
        
        if not job:
            flash('Job not found', 'danger')
            return redirect(url_for('jobs.jobs'))
        
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
        return redirect(url_for('jobs.jobs'))

@jobs_bp.route('/apply-job/<int:job_id>', methods=['POST'])
@login_required
@role_required(['student'])
def apply_job(job_id):
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect(url_for('auth.login'))
    
    try:
        student = get_record('SELECT StudentID FROM students WHERE UserID = %s', 
                           (session['user_id'],))
        if not student:
            flash('Student profile not found', 'danger')
            return redirect(url_for('jobs.jobs'))
        
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
        
        return redirect(url_for('jobs.job_detail', job_id=job_id))
    
    except Exception as e:
        flash(f'Error submitting application: {str(e)}', 'danger')
        return redirect(url_for('jobs.jobs'))

@jobs_bp.route('/manage-jobs', methods=['GET', 'POST'])
@login_required
@role_required(['company'])
def manage_jobs():
    user_id = session['user_id']

    try:
        # Get company ID from the session's user
        company = get_record('SELECT CompanyID FROM companies WHERE UserID = %s', (user_id,))
        if not company:
            flash("Company profile not found!", "danger")
            return redirect(url_for("dashboard.dashboard"))
        company_id = company['CompanyID']

        if request.method == 'POST':
            # Form data for adding/updating
            job_id = request.form.get('job_id')  # present only during editing
            title = request.form['title']
            description = request.form['description']
            location = request.form['location']
            salary = request.form['salary']
            deadline = request.form['deadline']

            if job_id:  # Edit existing job
                execute_query('''
                    UPDATE jobs 
                    SET Title=%s, Description=%s, Location=%s, Salary=%s, DeadlineDate=%s 
                    WHERE JobID=%s AND CompanyID=%s
                ''', (title, description, location, salary, deadline, job_id, company_id))
                flash("Job updated successfully.", "success")
            else:  # Add new job
                execute_query('''
                    INSERT INTO jobs (CompanyID, Title, Description, Location, Salary, PostingDate, DeadlineDate)
                    VALUES (%s, %s, %s, %s, %s, NOW(), %s)
                ''', (company_id, title, description, location, salary, deadline))
                flash("New job posted successfully.", "success")

            return redirect(url_for('jobs.manage_jobs'))

        # GET request: fetch all jobs posted by this company
        jobs = get_records('''
            SELECT * FROM jobs 
            WHERE CompanyID = %s
            ORDER BY PostingDate DESC
        ''', (company_id,))
        return render_template('manage_jobs.html', jobs=jobs)

    except Exception as e:
        flash(f"Error managing jobs: {str(e)}", "danger")
        return render_template('manage_jobs.html', jobs=[])


@jobs_bp.route('/edit-job/<int:job_id>', methods=['GET', 'POST'])
@login_required
@role_required(['company'])
def edit_job(job_id):
    # Ensure company owns this job
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    company = get_record('SELECT CompanyID FROM companies WHERE UserID = %s', (user_id,))
    if not company:
        flash("Company profile not found!", "danger")
        return redirect(url_for("dashboard.dashboard"))
    company_id = company['CompanyID']

    job = get_record('''
        SELECT * FROM jobs
        WHERE JobID = %s AND CompanyID = %s
    ''', (job_id, company_id))
    if not job:
        flash('Job not found or unauthorized access', 'danger')
        return redirect(url_for('jobs.manage_jobs'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        salary = request.form.get('salary')
        deadline = request.form.get('deadline')
        execute_query('''
            UPDATE jobs
            SET Title = %s, Description = %s, Location = %s, Salary = %s, DeadlineDate = %s
            WHERE JobID = %s AND CompanyID = %s
        ''', (title, description, location, salary, deadline, job_id, company_id))
        flash('Job updated successfully', 'success')
        return redirect(url_for('jobs.manage_jobs'))

    return render_template('edit_job.html', job=job)