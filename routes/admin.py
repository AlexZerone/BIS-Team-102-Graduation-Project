"""
Admin Routes for Sec Era Platform
Handles admin dashboard, user management, approvals, and system settings
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import get_record, get_records, execute_query
from permissions import login_required, role_required
from datetime import datetime, timedelta
import json
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    """Ensure only admin users can access admin routes"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        # For API endpoints, return JSON error instead of redirect
        if request.path.startswith('/admin/api/'):
            return jsonify({'error': 'Admin authentication required', 'authenticated': False}), 401
        
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('auth.login'))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard with overview statistics"""
    try:
        # Get platform statistics
        stats = {}
        
        # User statistics
        stats['total_users'] = get_record('SELECT COUNT(*) as count FROM users')['count']
        stats['pending_instructors'] = get_record(
            'SELECT COUNT(*) as count FROM instructors WHERE ApprovalStatus = "Pending"'
        )['count']
        stats['pending_companies'] = get_record(
            'SELECT COUNT(*) as count FROM companies WHERE ApprovalStatus = "Pending"'
        )['count']
        stats['pending_courses'] = get_record(
            'SELECT COUNT(*) as count FROM courses WHERE ApprovalStatus = "Pending"'
        )['count']
        
        # Activity statistics
        stats['new_users_today'] = get_record(
            'SELECT COUNT(*) as count FROM users WHERE DATE(CreatedAt) = CURDATE()'
        )['count']
        stats['new_applications_today'] = get_record(
            'SELECT COUNT(*) as count FROM job_applications WHERE DATE(ApplicationDate) = CURDATE()'
        )['count']
        
        # Revenue statistics (for subscription plans)
        stats['monthly_revenue'] = get_record(
            'SELECT COALESCE(SUM(Amount), 0) as revenue FROM subscription_payments WHERE MONTH(PaymentDate) = MONTH(CURDATE()) AND YEAR(PaymentDate) = YEAR(CURDATE()) AND Status = "completed"'
        )['revenue']
        
        # Recent activities
        recent_activities = get_records('''
            SELECT al.*, u.First, u.Last, u.Email
            FROM admin_activity_log al
            JOIN users u ON al.AdminID = u.UserID
            ORDER BY al.CreatedAt DESC
            LIMIT 10
        ''')
        
        # System alerts
        alerts = []
        
        # Check for high number of pending approvals
        if stats['pending_instructors'] > 5:
            alerts.append({
                'type': 'warning',
                'message': f"{stats['pending_instructors']} instructors awaiting approval",
                'action_url': url_for('admin.pending_instructors')
            })
        
        if stats['pending_companies'] > 3:
            alerts.append({
                'type': 'warning',
                'message': f"{stats['pending_companies']} companies awaiting approval",
                'action_url': url_for('admin.pending_companies')
            })
        
        if stats['pending_courses'] > 10:
            alerts.append({
                'type': 'info',
                'message': f"{stats['pending_courses']} courses awaiting approval",
                'action_url': url_for('admin.pending_courses')
            })
        
        return render_template('admin/dashboard.html', 
                             stats=stats, 
                             recent_activities=recent_activities,
                             alerts=alerts)
    except Exception as e:
        flash(f'Error loading admin dashboard: {str(e)}', 'danger')
        return render_template('admin/dashboard.html', stats={}, recent_activities=[], alerts=[])

@admin_bp.route('/users')
def users():
    """Manage all users"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    user_type = request.args.get('type', 'all')
    status = request.args.get('status', 'all')
    
    # Build query with filters
    where_conditions = []
    params = []
    
    if search:
        where_conditions.append('(u.First LIKE %s OR u.Last LIKE %s OR u.Email LIKE %s)')
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param])
    
    if user_type != 'all':
        where_conditions.append('u.UserType = %s')
        params.append(user_type)
    
    if status != 'all':
        where_conditions.append('u.Status = %s')
        params.append(status)
    
    where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
    
    # Get paginated users
    per_page = 20
    offset = (page - 1) * per_page
    
    users = get_records(f'''
        SELECT u.*, 
               CASE 
                   WHEN u.UserType = 'student' THEN s.University
                   WHEN u.UserType = 'instructor' THEN i.Department
                   WHEN u.UserType = 'company' THEN c.Name
                   ELSE NULL
               END as ExtraInfo,
               CASE 
                   WHEN u.UserType = 'instructor' THEN i.ApprovalStatus
                   WHEN u.UserType = 'company' THEN c.ApprovalStatus
                   ELSE 'N/A'
               END as ApprovalStatus
        FROM users u
        LEFT JOIN students s ON u.UserID = s.UserID
        LEFT JOIN instructors i ON u.UserID = i.UserID
        LEFT JOIN companies c ON u.UserID = c.UserID
        {where_clause}
        ORDER BY u.CreatedAt DESC
        LIMIT %s OFFSET %s
    ''', params + [per_page, offset])
    
    # Get total count for pagination
    total_users = get_record(f'''
        SELECT COUNT(*) as count
        FROM users u
        {where_clause}
    ''', params)['count']
    
    total_pages = (total_users + per_page - 1) // per_page
    
    return render_template('admin/users.html', 
                         users=users,
                         page=page,
                         total_pages=total_pages,
                         search=search,
                         user_type=user_type,
                         status=status)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
def toggle_user_status(user_id):
    """Toggle user active/inactive status"""
    try:
        user = get_record('SELECT * FROM users WHERE UserID = %s', (user_id,))
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('admin.users'))
        
        new_status = 'Inactive' if user['Status'] == 'Active' else 'Active'
        execute_query('UPDATE users SET Status = %s WHERE UserID = %s', (new_status, user_id))
        
        # Log the action
        log_admin_action('user_status_change', 'user', user_id, 
                        {'old_status': user['Status'], 'new_status': new_status})
        
        flash(f'User status updated to {new_status}', 'success')
    except Exception as e:
        flash(f'Error updating user status: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/pending-instructors')
def pending_instructors():
    """View and manage pending instructor approvals"""
    instructors = get_records('''
        SELECT i.*, u.First, u.Last, u.Email, u.CreatedAt
        FROM instructors i
        JOIN users u ON i.UserID = u.UserID
        WHERE i.ApprovalStatus = 'Pending'
        ORDER BY u.CreatedAt ASC
    ''')
    
    return render_template('admin/pending_instructors.html', instructors=instructors)

@admin_bp.route('/pending-companies')
def pending_companies():
    """View and manage pending company approvals"""
    companies = get_records('''
        SELECT c.*, u.First, u.Last, u.Email, u.CreatedAt
        FROM companies c
        JOIN users u ON c.UserID = u.UserID
        WHERE c.ApprovalStatus = 'Pending'
        ORDER BY u.CreatedAt ASC
    ''')
    
    return render_template('admin/pending_companies.html', companies=companies)

@admin_bp.route('/pending-courses')
def pending_courses():
    """View and manage pending course approvals"""
    try:
        # Try complex query first
        courses = get_records('''
            SELECT c.*, u.First, u.Last
            FROM courses c
            LEFT JOIN users u ON c.CreatedBy = u.UserID
            WHERE c.ApprovalStatus = 'Pending'
            ORDER BY c.CreatedAt ASC
        ''')
    except:
        # Fallback to simple query
        try:
            courses = get_records('''
                SELECT c.*
                FROM courses c
                WHERE c.ApprovalStatus = 'Pending'
                ORDER BY c.CreatedAt ASC
            ''')
            # Add placeholder user info
            for course in courses:
                course['First'] = 'Unknown'
                course['Last'] = 'User'
        except:
            courses = []
    
    return render_template('admin/pending_courses.html', courses=courses)

@admin_bp.route('/approve-instructor/<int:instructor_id>', methods=['POST'])
def approve_instructor(instructor_id):
    """Approve or reject instructor application"""
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    if not action:
        flash('No action specified', 'danger')
        return redirect(url_for('admin.pending_instructors'))
    
    try:
        # Get instructor record by InstructorID (primary key)
        instructor = get_record('SELECT * FROM instructors WHERE InstructorID = %s', (instructor_id,))
        if not instructor:
            flash('Instructor not found', 'danger')
            return redirect(url_for('admin.pending_instructors'))
        
        user_id = instructor['UserID']
        
        if action == 'approve':
            # Update instructor approval status
            execute_query('''
                UPDATE instructors 
                SET ApprovalStatus = 'Approved', ApprovedBy = %s, ApprovedAt = NOW()
                WHERE InstructorID = %s
            ''', (session['user_id'], instructor_id))
            
            # Activate the user account
            execute_query('''
                UPDATE users 
                SET Status = 'Active', ApprovalStatus = 'Approved' 
                WHERE UserID = %s
            ''', (user_id,))
            
            flash('Instructor approved successfully', 'success')
            
        elif action == 'reject':
            # Update instructor rejection status
            execute_query('''
                UPDATE instructors 
                SET ApprovalStatus = 'Rejected', RejectionReason = %s
                WHERE InstructorID = %s
            ''', (reason, instructor_id))
            
            # Update user status to reflect rejection
            execute_query('''
                UPDATE users 
                SET ApprovalStatus = 'Rejected' 
                WHERE UserID = %s
            ''', (user_id,))
            
            flash('Instructor application rejected', 'info')
        else:
            flash('Invalid action', 'danger')
        
        # Log the action if logging is available
        try:
            log_admin_action(f'instructor_{action}', 'instructor', instructor_id, 
                            {'reason': reason, 'user_id': user_id})
        except:
            pass  # Don't fail if logging fails
        
    except Exception as e:
        flash(f'Error processing instructor approval: {str(e)}', 'danger')
    
    return redirect(url_for('admin.pending_instructors'))

@admin_bp.route('/approve-company/<int:company_id>', methods=['POST'])
def approve_company(company_id):
    """Approve or reject company application"""
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    if not action:
        flash('No action specified', 'danger')
        return redirect(url_for('admin.pending_companies'))
    
    try:
        # Get company record by CompanyID (primary key)
        company = get_record('SELECT * FROM companies WHERE CompanyID = %s', (company_id,))
        if not company:
            flash('Company not found', 'danger')
            return redirect(url_for('admin.pending_companies'))
        
        user_id = company['UserID']
        
        if action == 'approve':
            # Update company approval status
            execute_query('''
                UPDATE companies 
                SET ApprovalStatus = 'Approved', ApprovedBy = %s, ApprovedAt = NOW()
                WHERE CompanyID = %s
            ''', (session['user_id'], company_id))
            
            # Activate the user account
            execute_query('''
                UPDATE users 
                SET Status = 'Active', ApprovalStatus = 'Approved' 
                WHERE UserID = %s
            ''', (user_id,))
            
            flash('Company approved successfully', 'success')
            
        elif action == 'reject':
            # Update company rejection status
            execute_query('''
                UPDATE companies 
                SET ApprovalStatus = 'Rejected', RejectionReason = %s
                WHERE CompanyID = %s
            ''', (reason, company_id))
            
            # Update user status to reflect rejection
            execute_query('''
                UPDATE users 
                SET ApprovalStatus = 'Rejected' 
                WHERE UserID = %s
            ''', (user_id,))
            
            flash('Company application rejected', 'info')
        else:
            flash('Invalid action', 'danger')
        
        # Log the action if logging is available
        try:
            log_admin_action(f'company_{action}', 'company', company_id, 
                            {'reason': reason, 'user_id': user_id})
        except:
            pass  # Don't fail if logging fails
        
    except Exception as e:
        flash(f'Error processing company approval: {str(e)}', 'danger')
    
    return redirect(url_for('admin.pending_companies'))

@admin_bp.route('/approve-course/<int:course_id>', methods=['POST'])
def approve_course(course_id):
    """Approve or reject course"""
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    try:
        if action == 'approve':
            execute_query('''
                UPDATE courses 
                SET ApprovalStatus = 'Approved', ApprovedBy = %s, ApprovedAt = NOW(), IsPublished = 1
                WHERE CourseID = %s
            ''', (session['user_id'], course_id))
            
            flash('Course approved and published successfully', 'success')
            
        elif action == 'reject':
            execute_query('''
                UPDATE courses 
                SET ApprovalStatus = 'Rejected', RejectionReason = %s
                WHERE CourseID = %s
            ''', (reason, course_id))
            
            flash('Course rejected', 'info')
        
        # Log the action
        log_admin_action(f'course_{action}', 'course', course_id, 
                        {'reason': reason})
        
    except Exception as e:
        flash(f'Error processing course approval: {str(e)}', 'danger')
    
    return redirect(url_for('admin.pending_courses'))

@admin_bp.route('/subscriptions')
def subscriptions():
    """Manage subscription plans and payments"""
    plans = get_records('SELECT * FROM subscription_plans ORDER BY Price ASC')
    
    # Get subscription statistics
    stats = {}
    stats['total_subscriptions'] = get_record(
        'SELECT COUNT(*) as count FROM students WHERE SubscriptionTier != "freemium"'
    )['count']
    
    stats['monthly_revenue'] = get_record('''
        SELECT COALESCE(SUM(Amount), 0) as revenue 
        FROM subscription_payments 
        WHERE MONTH(PaymentDate) = MONTH(CURDATE()) 
        AND YEAR(PaymentDate) = YEAR(CURDATE()) 
        AND Status = 'completed'
    ''')['revenue']
    
    # Get recent payments
    recent_payments = get_records('''
        SELECT sp.*, u.First, u.Last, u.Email, spl.Name as PlanName
        FROM subscription_payments sp
        JOIN students s ON sp.StudentID = s.StudentID
        JOIN users u ON s.UserID = u.UserID
        JOIN subscription_plans spl ON sp.PlanID = spl.PlanID
        ORDER BY sp.PaymentDate DESC
        LIMIT 20
    ''')
    
    return render_template('admin/subscriptions.html', 
                         plans=plans, 
                         stats=stats, 
                         recent_payments=recent_payments)

@admin_bp.route('/settings')
def settings():
    """System settings management"""
    settings = get_records('SELECT * FROM system_settings ORDER BY SettingKey')
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/settings/update', methods=['POST'])
def update_settings():
    """Update system settings"""
    try:
        for key, value in request.form.items():
            if key != 'csrf_token':
                execute_query('''
                    UPDATE system_settings 
                    SET SettingValue = %s, UpdatedBy = %s, UpdatedAt = NOW()
                    WHERE SettingKey = %s
                ''', (value, session['user_id'], key))
        
        log_admin_action('settings_update', 'system', 0, dict(request.form))
        flash('Settings updated successfully', 'success')
        
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'danger')
    
    return redirect(url_for('admin.settings'))

@admin_bp.route('/reports')
def reports():
    """Generate various reports"""
    # User registration trends
    user_trends = get_records('''
        SELECT DATE(CreatedAt) as date, UserType, COUNT(*) as count
        FROM users
        WHERE CreatedAt >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY DATE(CreatedAt), UserType
        ORDER BY date DESC
    ''')
    
    # Course enrollment trends
    enrollment_trends = get_records('''
        SELECT DATE(cr.RegistrationDate) as date, COUNT(*) as count
        FROM course_registrations cr
        WHERE cr.RegistrationDate >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY DATE(cr.RegistrationDate)
        ORDER BY date DESC
    ''')
    
    # Job application trends
    application_trends = get_records('''
        SELECT DATE(ApplicationDate) as date, COUNT(*) as count
        FROM job_applications
        WHERE ApplicationDate >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY DATE(ApplicationDate)
        ORDER BY date DESC
    ''')
    
    # Popular courses
    popular_courses = get_records('''
        SELECT c.Title, COUNT(cr.StudentID) as enrollments
        FROM courses c
        LEFT JOIN course_registrations cr ON c.CourseID = cr.CourseID
        WHERE c.IsPublished = 1
        GROUP BY c.CourseID, c.Title
        ORDER BY enrollments DESC
        LIMIT 10
    ''')
    
    return render_template('admin/reports.html', 
                         user_trends=user_trends,
                         enrollment_trends=enrollment_trends,
                         application_trends=application_trends,
                         popular_courses=popular_courses)

@admin_bp.route('/api/notifications')
def get_notifications():
    """Get pending notifications for admin dashboard"""
    try:
        notifications = []
        
        # Pending approvals
        pending_instructors = get_record('SELECT COUNT(*) as count FROM instructors WHERE ApprovalStatus = "Pending"')['count']
        if pending_instructors > 0:
            notifications.append({
                'type': 'approval',
                'message': f'{pending_instructors} instructor{"s" if pending_instructors > 1 else ""} awaiting approval',
                'url': url_for('admin.pending_instructors'),
                'icon': 'fas fa-chalkboard-teacher',
                'badge': pending_instructors
            })
        
        pending_companies = get_record('SELECT COUNT(*) as count FROM companies WHERE ApprovalStatus = "Pending"')['count']
        if pending_companies > 0:
            notifications.append({
                'type': 'approval',
                'message': f'{pending_companies} compan{"ies" if pending_companies > 1 else "y"} awaiting approval',
                'url': url_for('admin.pending_companies'),
                'icon': 'fas fa-building',
                'badge': pending_companies
            })
        
        pending_courses = get_record('SELECT COUNT(*) as count FROM courses WHERE ApprovalStatus = "Pending"')['count']
        if pending_courses > 0:
            notifications.append({
                'type': 'approval',
                'message': f'{pending_courses} course{"s" if pending_courses > 1 else ""} awaiting approval',
                'url': url_for('admin.pending_courses'),
                'icon': 'fas fa-book',
                'badge': pending_courses
            })
        
        # Contact requests
        open_contacts = get_record('SELECT COUNT(*) as count FROM contact_requests WHERE Status = "open"')
        if open_contacts and open_contacts['count'] > 0:
            notifications.append({
                'type': 'contact',
                'message': f'{open_contacts["count"]} new contact request{"s" if open_contacts["count"] > 1 else ""}',
                'url': url_for('help.admin_contact_requests'),
                'icon': 'fas fa-envelope',
                'badge': open_contacts['count']
            })
        
        # Critical issues
        critical_contacts = get_record('SELECT COUNT(*) as count FROM contact_requests WHERE Priority = "critical" AND Status != "resolved"')
        if critical_contacts and critical_contacts['count'] > 0:
            notifications.append({
                'type': 'critical',
                'message': f'{critical_contacts["count"]} critical issue{"s" if critical_contacts["count"] > 1 else ""} need attention',
                'url': url_for('help.admin_contact_requests', priority='critical'),
                'icon': 'fas fa-exclamation-triangle',
                'badge': critical_contacts['count']
            })
        
        # System alerts
        failed_payments = get_record('SELECT COUNT(*) as count FROM subscription_payments WHERE Status = "failed" AND DATE(PaymentDate) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)')
        if failed_payments and failed_payments['count'] > 0:
            notifications.append({
                'type': 'payment',
                'message': f'{failed_payments["count"]} failed payment{"s" if failed_payments["count"] > 1 else ""} this week',
                'url': url_for('admin.subscriptions'),
                'icon': 'fas fa-credit-card',
                'badge': failed_payments['count']
            })
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'total': len(notifications)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/stats')
def get_stats():
    """Get real-time statistics for admin dashboard"""
    try:
        stats = {}
          # User statistics
        stats['total_users'] = get_record('SELECT COUNT(*) as count FROM users')['count']
        
        # Try to get active users with LastLogin, fallback to basic query
        try:
            stats['active_users'] = get_record('SELECT COUNT(*) as count FROM users WHERE LastLogin >= DATE_SUB(NOW(), INTERVAL 30 DAY)')['count']
        except:
            # Fallback: count users created in last 30 days if LastLogin doesn't exist
            try:
                stats['active_users'] = get_record('SELECT COUNT(*) as count FROM users WHERE CreatedAt >= DATE_SUB(NOW(), INTERVAL 30 DAY)')['count']
            except:
                stats['active_users'] = 0
        
        stats['new_users_today'] = get_record('SELECT COUNT(*) as count FROM users WHERE DATE(CreatedAt) = CURDATE()')['count']
        
        # Course statistics
        stats['total_courses'] = get_record('SELECT COUNT(*) as count FROM courses WHERE ApprovalStatus = "Approved"')['count']
        stats['pending_courses'] = get_record('SELECT COUNT(*) as count FROM courses WHERE ApprovalStatus = "Pending"')['count']
          # Enrollment statistics - using course_registrations table
        try:
            stats['total_enrollments'] = get_record('SELECT COUNT(*) as count FROM course_registrations')['count']
            stats['new_enrollments_today'] = get_record('SELECT COUNT(*) as count FROM course_registrations WHERE DATE(RegistrationDate) = CURDATE()')['count']
        except:
            # Fallback if course_registrations doesn't exist
            try:
                stats['total_enrollments'] = get_record('SELECT COUNT(*) as count FROM enrollments')['count']
                stats['new_enrollments_today'] = get_record('SELECT COUNT(*) as count FROM enrollments WHERE DATE(EnrollmentDate) = CURDATE()')['count']
            except:
                stats['total_enrollments'] = 0
                stats['new_enrollments_today'] = 0
        
        # Revenue statistics
        stats['monthly_revenue'] = get_record(
            'SELECT COALESCE(SUM(Amount), 0) as revenue FROM subscription_payments WHERE MONTH(PaymentDate) = MONTH(CURDATE()) AND YEAR(PaymentDate) = YEAR(CURDATE()) AND Status = "completed"'
        )['revenue']
        stats['daily_revenue'] = get_record(
            'SELECT COALESCE(SUM(Amount), 0) as revenue FROM subscription_payments WHERE DATE(PaymentDate) = CURDATE() AND Status = "completed"'
        )['revenue']
        
        # Contact statistics
        stats['open_contacts'] = get_record('SELECT COUNT(*) as count FROM contact_requests WHERE Status = "open"')['count']
        stats['total_contacts'] = get_record('SELECT COUNT(*) as count FROM contact_requests')['count']
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/activity')
def get_recent_activity():
    """Get recent platform activity for admin dashboard"""
    try:
        activities = []
        
        # Recent user registrations
        recent_users = get_records(
            'SELECT First, Last, Email, CreatedAt FROM users ORDER BY CreatedAt DESC LIMIT 5'
        )
        for user in recent_users:
            activities.append({
                'type': 'user_registration',
                'message': f'{user["First"]} {user["Last"]} registered',
                'timestamp': user['CreatedAt'].isoformat() if user['CreatedAt'] else None,
                'icon': 'fas fa-user-plus',
                'color': 'success'
            })        # Recent course submissions - using instructor relationship instead of CreatedBy
        try:
            recent_courses = get_records('''
                SELECT c.Title, u.First, u.Last, c.CreatedAt 
                FROM courses c 
                JOIN instructor_courses ic ON c.CourseID = ic.CourseID
                JOIN instructors i ON ic.InstructorID = i.InstructorID
                JOIN users u ON i.UserID = u.UserID 
                WHERE c.ApprovalStatus = "Pending" 
                ORDER BY c.CreatedAt DESC 
                LIMIT 5
            ''')
        except:
            # Fallback if relationship tables don't exist or have issues
            try:
                recent_courses = get_records(
                    'SELECT c.Title, c.CreatedAt FROM courses c WHERE c.ApprovalStatus = "Pending" ORDER BY c.CreatedAt DESC LIMIT 5'
                )
                # Add placeholder user info
                for course in recent_courses:
                    course['First'] = 'Instructor'
                    course['Last'] = 'User'
            except:
                recent_courses = []
        for course in recent_courses:
            activities.append({
                'type': 'course_submission',
                'message': f'{course["First"]} {course["Last"]} submitted course "{course["Title"]}"',
                'timestamp': course['CreatedAt'].isoformat() if course['CreatedAt'] else None,
                'icon': 'fas fa-book',
                'color': 'info'
            })
        
        # Recent contact requests
        recent_contacts = get_records(
            'SELECT Name, Subject, CreatedAt FROM contact_requests ORDER BY CreatedAt DESC LIMIT 5'
        )
        for contact in recent_contacts:
            activities.append({
                'type': 'contact_request',
                'message': f'{contact["Name"]} submitted contact request: "{contact["Subject"]}"',
                'timestamp': contact['CreatedAt'].isoformat() if contact['CreatedAt'] else None,
                'icon': 'fas fa-envelope',
                'color': 'warning'
            })
        
        # Sort all activities by timestamp
        activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        
        return jsonify({
            'success': True,
            'activities': activities[:10],  # Return top 10 most recent
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def log_admin_action(action, target_type, target_id, details=None):
    """Log admin actions for audit trail"""
    try:
        execute_query('''
            INSERT INTO admin_activity_log 
            (AdminID, Action, TargetType, TargetID, NewValue, IPAddress, CreatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ''', (
            session['user_id'],
            action,
            target_type,
            target_id,
            json.dumps(details) if details else None,
            request.remote_addr
        ))
    except Exception as e:
        print(f"Error logging admin action: {e}")

# Error handlers for admin blueprint
@admin_bp.errorhandler(403)
def forbidden(error):
    return render_template('admin/error.html', 
                         error_code=403, 
                         error_message="Access Forbidden"), 403

@admin_bp.errorhandler(404)
def not_found(error):
    return render_template('admin/error.html', 
                         error_code=404, 
                         error_message="Page Not Found"), 404

@admin_bp.errorhandler(500)
def internal_error(error):
    return render_template('admin/error.html', 
                         error_code=500, 
                         error_message="Internal Server Error"), 500

@admin_bp.route('/fix-passwords', methods=['GET', 'POST'])
def fix_passwords():
    """Admin utility to fix unhashed passwords"""
    if request.method == 'POST':
        try:
            # Get all users with potentially unhashed passwords
            users = get_records('SELECT UserID, Email, Password FROM users WHERE Password IS NOT NULL AND Password != ""')
            
            fixed_count = 0
            for user in users:
                password = user['Password']
                
                # Check if password is not hashed (simple check)
                if password and not any(password.startswith(prefix) for prefix in ['pbkdf2:', 'scrypt:', 'argon2:', '$']):
                    try:
                        # Hash the password
                        hashed_password = generate_password_hash(password)
                        execute_query('UPDATE users SET Password = %s WHERE UserID = %s', 
                                    (hashed_password, user['UserID']))
                        fixed_count += 1
                    except Exception as e:
                        flash(f'Error fixing password for {user["Email"]}: {str(e)}', 'danger')
            
            flash(f'Fixed {fixed_count} user passwords', 'success')
            
        except Exception as e:
            flash(f'Error fixing passwords: {str(e)}', 'danger')
        
        return redirect(url_for('admin.fix_passwords'))
    
    # GET request - show the utility page
    try:
        # Count users with potentially problematic passwords
        users = get_records('SELECT UserID, Email, Password FROM users WHERE Password IS NOT NULL AND Password != ""')
        
        unhashed_count = 0
        for user in users:
            password = user['Password']
            if password and not any(password.startswith(prefix) for prefix in ['pbkdf2:', 'scrypt:', 'argon2:', '$']):
                unhashed_count += 1
        
        return render_template('admin/fix_passwords.html', 
                             total_users=len(users), 
                             unhashed_count=unhashed_count)
    except Exception as e:
        flash(f'Error checking passwords: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/contact-requests')
def contact_requests():
    """Manage contact requests and support tickets"""
    try:
        # Get contact requests with filters
        status_filter = request.args.get('status', 'all')
        priority_filter = request.args.get('priority', 'all')
        
        # Build query with filters
        query = '''
            SELECT ContactID, Name, Email, Subject, Message, Priority, Status, CreatedAt, UpdatedAt
            FROM contact_requests
            WHERE 1=1
        '''
        params = []
        
        if status_filter != 'all':
            query += ' AND Status = %s'
            params.append(status_filter)
            
        if priority_filter != 'all':
            query += ' AND Priority = %s'
            params.append(priority_filter)
        
        query += ' ORDER BY CreatedAt DESC'
        
        if params:
            contact_requests = get_records(query, params)
        else:
            contact_requests = get_records(query)
        
        # Get summary statistics
        stats = {
            'total': get_record('SELECT COUNT(*) as count FROM contact_requests')['count'],
            'open': get_record('SELECT COUNT(*) as count FROM contact_requests WHERE Status = "open"')['count'],
            'in_progress': get_record('SELECT COUNT(*) as count FROM contact_requests WHERE Status = "in_progress"')['count'],
            'resolved': get_record('SELECT COUNT(*) as count FROM contact_requests WHERE Status = "resolved"')['count'],
            'critical': get_record('SELECT COUNT(*) as count FROM contact_requests WHERE Priority = "critical" AND Status != "resolved"')['count']
        }
        
        return render_template('admin/contact_requests.html', 
                             contact_requests=contact_requests,
                             stats=stats,
                             current_status=status_filter,
                             current_priority=priority_filter)
        
    except Exception as e:
        flash(f'Error loading contact requests: {str(e)}', 'danger')
        return render_template('admin/contact_requests.html', 
                             contact_requests=[],
                             stats={'total': 0, 'open': 0, 'in_progress': 0, 'resolved': 0, 'critical': 0})

@admin_bp.route('/contact-requests/<int:contact_id>/update-status', methods=['POST'])
def update_contact_status(contact_id):
    """Update contact request status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        admin_notes = data.get('notes', '')
        
        if new_status not in ['open', 'in_progress', 'resolved']:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Update contact request status
        execute_query('''
            UPDATE contact_requests 
            SET Status = %s, AdminNotes = %s, UpdatedAt = NOW(), AdminID = %s
            WHERE ContactID = %s
        ''', (new_status, admin_notes, session['user_id'], contact_id))
        
        return jsonify({
            'success': True,
            'message': f'Contact request status updated to {new_status}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
