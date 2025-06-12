"""
Help and Support Routes for Sec Era Platform
Handles FAQ, contact forms, privacy policy, and terms of service
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import execute_query, get_records, get_record
from permissions import login_required


help_bp = Blueprint('help', __name__, url_prefix='/help')

@help_bp.route('/faq')
def faq():
    """Display frequently asked questions"""
    # In a real implementation, this would come from a database
    faqs = [
        {
            'category': 'General',
            'questions': [
                {
                    'question': 'What is Sec Era Platform?',
                    'answer': 'Sec Era is a comprehensive cybersecurity learning platform offering courses, certifications, and hands-on training for security professionals and enthusiasts.'
                },
                {
                    'question': 'How do I get started?',
                    'answer': 'Simply create an account and choose your learning path. You can start with our free courses or upgrade to premium for full access.'
                },
                {
                    'question': 'Is there a mobile app?',
                    'answer': 'Currently, we offer a fully responsive web platform. A mobile app is in development and will be available soon.'
                }
            ]
        },
        {
            'category': 'Subscriptions',
            'questions': [
                {
                    'question': 'What subscription plans are available?',
                    'answer': 'We offer Freemium (free), Standard ($29/month), and Premium ($99/year) plans with different levels of access to courses and features.'
                },
                {
                    'question': 'Can I cancel my subscription anytime?',
                    'answer': 'Yes, you can cancel your subscription at any time. You\'ll retain access until the end of your billing period.'
                },
                {
                    'question': 'Do you offer refunds?',
                    'answer': 'We offer a 30-day money-back guarantee for all paid subscriptions. Contact support for refund requests.'
                },
                {
                    'question': 'Can I upgrade or downgrade my plan?',
                    'answer': 'Yes, you can change your subscription plan at any time. Changes take effect immediately with prorated billing.'
                }
            ]
        },
        {
            'category': 'Courses & Certifications',
            'questions': [
                {
                    'question': 'Are the certifications industry-recognized?',
                    'answer': 'Our certifications are recognized by leading cybersecurity organizations and employers worldwide.'
                },
                {
                    'question': 'Do I need prior experience?',
                    'answer': 'We offer courses for all skill levels, from complete beginners to advanced professionals.'
                },
                {
                    'question': 'How long do courses take to complete?',
                    'answer': 'Course duration varies from 2-40 hours depending on the complexity and depth of the subject matter.'
                },
                {
                    'question': 'Can I access courses offline?',
                    'answer': 'Premium subscribers can download course materials for offline viewing on supported devices.'
                }
            ]
        },
        {
            'category': 'Technical Support',
            'questions': [
                {
                    'question': 'I\'m having trouble accessing my account',
                    'answer': 'Try resetting your password. If the issue persists, contact our support team with your email address.'
                },
                {
                    'question': 'The platform is running slowly',
                    'answer': 'Clear your browser cache and cookies. If issues continue, try using a different browser or contact support.'
                },
                {
                    'question': 'I can\'t submit my assignments',
                    'answer': 'Ensure your files meet the size and format requirements. Check your internet connection and try again.'
                }
            ]
        }
    ]
    
    return render_template('help/faq.html', faqs=faqs)

@help_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form for support requests"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            priority = request.form.get('priority', 'normal')
            category = request.form.get('category', 'general')
            
            # Basic validation
            if not all([name, email, subject, message]):
                flash('Please fill in all required fields', 'danger')
                return render_template('help/contact.html')
            
            # Get user ID if logged in
            user_id = session.get('user_id')
            
            # Store contact request
            execute_query('''
                INSERT INTO contact_requests 
                (UserID, Name, Email, Subject, Message, Priority, Category, Status, CreatedAt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ''', (user_id, name, email, subject, message, priority, category, 'open'))
            
            flash('Your message has been sent successfully! We\'ll get back to you within 24 hours.', 'success')
            return redirect(url_for('help.contact'))
            
        except Exception as e:
            flash(f'Error sending message: {str(e)}', 'danger')
    
    return render_template('help/contact.html')

@help_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('help/privacy.html')

@help_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('help/terms.html')

@help_bp.route('/about')
def about():
    """About us page"""
    return render_template('help/about.html')

# Admin Contact Management Routes
@help_bp.route('/admin/contact-requests')
@login_required
def admin_contact_requests():
    """Admin view for managing contact requests"""
    # Check admin access
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        category_filter = request.args.get('category', 'all')
        priority_filter = request.args.get('priority', 'all')
        search = request.args.get('search', '')
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if status_filter != 'all':
            where_conditions.append('cr.Status = %s')
            params.append(status_filter)
        
        if category_filter != 'all':
            where_conditions.append('cr.Category = %s')
            params.append(category_filter)
        
        if priority_filter != 'all':
            where_conditions.append('cr.Priority = %s')
            params.append(priority_filter)
        
        if search:
            where_conditions.append('(cr.Name LIKE %s OR cr.Email LIKE %s OR cr.Subject LIKE %s OR cr.Message LIKE %s)')
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param, search_param])
        
        where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        # Get contact requests with admin assignment info
        requests = get_records(f'''
            SELECT cr.*, 
                   u_assigned.First AS AssignedToName, 
                   u_assigned.Last AS AssignedToLastName
            FROM contact_requests cr
            LEFT JOIN users u_assigned ON cr.AssignedTo = u_assigned.UserID
            {where_clause}
            ORDER BY 
                CASE cr.Priority 
                    WHEN 'critical' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'normal' THEN 3 
                    WHEN 'low' THEN 4 
                END,
                cr.CreatedAt DESC
        ''', params)
        
        # Get admin users for assignment dropdown
        admin_users = get_records('''
            SELECT UserID, First, Last, Email 
            FROM users 
            WHERE UserType = 'admin' AND Status = 'Active'
            ORDER BY First, Last
        ''')
        
        # Get statistics
        stats = {
            'total': len(requests),
            'open': len([r for r in requests if r['Status'] == 'open']),
            'in_progress': len([r for r in requests if r['Status'] == 'in_progress']),
            'resolved': len([r for r in requests if r['Status'] == 'resolved']),
            'closed': len([r for r in requests if r['Status'] == 'closed'])
        }
        
        return render_template('admin/contact_requests.html', 
                             requests=requests,
                             admin_users=admin_users,
                             stats=stats,
                             status_filter=status_filter,
                             category_filter=category_filter,
                             priority_filter=priority_filter,
                             search=search)
    
    except Exception as e:
        flash(f'Error loading contact requests: {str(e)}', 'danger')
        return render_template('admin/contact_requests.html', 
                             requests=[], admin_users=[], stats={})

@help_bp.route('/admin/contact-requests/<int:request_id>/status', methods=['PATCH'])
@login_required
def update_contact_status(request_id):
    """Update contact request status"""
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['open', 'in_progress', 'resolved', 'closed']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        execute_query('''
            UPDATE contact_requests 
            SET Status = %s, UpdatedAt = NOW()
            WHERE RequestID = %s
        ''', (new_status, request_id))
        
        return jsonify({'success': True, 'message': f'Status updated to {new_status}'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_bp.route('/admin/contact-requests/<int:request_id>/assign', methods=['PATCH'])
@login_required
def assign_contact_request(request_id):
    """Assign contact request to admin"""
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        admin_id = data.get('admin_id')
        
        # Validate admin exists
        admin = get_record('SELECT UserID FROM users WHERE UserID = %s AND UserType = "admin"', (admin_id,))
        if not admin:
            return jsonify({'success': False, 'error': 'Invalid admin user'}), 400
        
        execute_query('''
            UPDATE contact_requests 
            SET AssignedTo = %s, UpdatedAt = NOW()
            WHERE RequestID = %s
        ''', (admin_id, request_id))
        
        return jsonify({'success': True, 'message': 'Request assigned successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@help_bp.route('/admin/contact-requests/<int:request_id>/respond', methods=['POST'])
@login_required
def respond_to_contact(request_id):
    """Admin response to contact request"""
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    try:
        response_message = request.form.get('response_message', '').strip()
        new_status = request.form.get('status', 'in_progress')
        assign_to = request.form.get('assign_to')
        
        if not response_message:
            flash('Response message is required', 'danger')
            return redirect(url_for('help.admin_contact_requests'))
        
        # Get the original request
        contact_request = get_record('SELECT * FROM contact_requests WHERE RequestID = %s', (request_id,))
        if not contact_request:
            flash('Contact request not found', 'danger')
            return redirect(url_for('help.admin_contact_requests'))
        
        # Update the request
        execute_query('''
            UPDATE contact_requests 
            SET Status = %s, AssignedTo = %s, AdminResponse = %s, 
                RespondedAt = NOW(), UpdatedAt = NOW()
            WHERE RequestID = %s
        ''', (new_status, assign_to if assign_to else None, response_message, request_id))
        
        # Log admin action
        execute_query('''
            INSERT INTO admin_activity_log 
            (AdminID, Action, TargetType, TargetID, Details, CreatedAt)
            VALUES (%s, %s, %s, %s, %s, NOW())
        ''', (session['user_id'], 'contact_response', 'contact_request', request_id, 
              f'Responded to contact request from {contact_request["Name"]}'))
        
        # TODO: Send email notification to user
        
        flash('Response sent successfully', 'success')
        return redirect(url_for('help.admin_contact_requests'))
    
    except Exception as e:
        flash(f'Error sending response: {str(e)}', 'danger')
        return redirect(url_for('help.admin_contact_requests'))

@help_bp.route('/admin/contact-requests/bulk-update', methods=['PATCH'])
@login_required
def bulk_update_contacts():
    """Bulk update contact requests"""
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        request_ids = data.get('request_ids', [])
        status = data.get('status')
        assign_to = data.get('assign_to')
        
        if not request_ids:
            return jsonify({'success': False, 'error': 'No requests selected'}), 400
        
        # Build update query
        update_fields = ['UpdatedAt = NOW()']
        params = []
        
        if status:
            update_fields.append('Status = %s')
            params.append(status)
        
        if assign_to:
            update_fields.append('AssignedTo = %s')
            params.append(assign_to)
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No updates specified'}), 400
        
        # Create placeholders for IN clause
        placeholders = ','.join(['%s'] * len(request_ids))
        params.extend(request_ids)
        
        execute_query(f'''
            UPDATE contact_requests 
            SET {', '.join(update_fields)}
            WHERE RequestID IN ({placeholders})
        ''', params)
        
        return jsonify({'success': True, 'message': f'Updated {len(request_ids)} requests'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
