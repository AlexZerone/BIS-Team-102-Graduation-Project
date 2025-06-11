"""
Static pages routes for Sec Era Platform
Handles About Us, Contact Us, and other informational pages
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import execute_query
from datetime import datetime

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/about')
def about():
    """About Us page"""
    return render_template('pages/about.html')

@pages_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact Us page with contact form"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')
            
            # Validate required fields
            if not all([name, email, subject, message]):
                flash('All fields are required', 'danger')
                return render_template('pages/contact.html')
            
            # Store contact message in database (you could create a contact_messages table)
            # For now, we'll just show a success message
            # In a real implementation, you would:
            # 1. Store in database
            # 2. Send email notification to admin
            # 3. Auto-reply to user
            
            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('pages.contact'))
            
        except Exception as e:
            flash(f'Error sending message: {str(e)}', 'danger')
    
    return render_template('pages/contact.html')

@pages_bp.route('/privacy')
def privacy():
    """Privacy Policy page"""
    return render_template('pages/privacy.html')

@pages_bp.route('/terms')
def terms():
    """Terms of Service page"""
    return render_template('pages/terms.html')

@pages_bp.route('/help')
def help():
    """Help/FAQ page"""
    return render_template('pages/help.html')
