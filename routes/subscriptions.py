"""
Subscription Routes for Sec Era Platform
Handles subscription plans, payments, and billing
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import get_record, get_records, execute_query
from permissions import login_required, role_required
from datetime import datetime, timedelta
import json
import uuid

subscriptions_bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')

@subscriptions_bp.route('/')
def plans():
    """Display available subscription plans"""
    plans = get_records('''
        SELECT * FROM subscription_plans 
        WHERE IsActive = 1 
        ORDER BY Price ASC
    ''')
    
    # Parse features JSON for each plan
    for plan in plans:
        if plan['Features']:
            plan['Features'] = json.loads(plan['Features'])
    
    return render_template('subscriptions/plans.html', plans=plans)

@subscriptions_bp.route('/current')
@login_required
@role_required(['student'])
def current_subscription():
    """Show current subscription details"""
    try:
        user_id = session['user_id']
        
        # Get student subscription info
        student = get_record('''
            SELECT s.*, sp.Name as PlanName, sp.Description, sp.Price, sp.BillingCycle, sp.Features
            FROM students s
            LEFT JOIN subscription_plans sp ON s.SubscriptionTier = sp.Name
            WHERE s.UserID = %s
        ''', (user_id,))
        
        if not student:
            flash('Student profile not found', 'danger')
            return redirect(url_for('dashboard.dashboard'))
        
        # Parse features if available
        if student['Features']:
            student['Features'] = json.loads(student['Features'])
        
        # Get payment history
        payment_history = get_records('''
            SELECT sp.*, spl.Name as PlanName
            FROM subscription_payments sp
            JOIN subscription_plans spl ON sp.PlanID = spl.PlanID
            WHERE sp.StudentID = %s
            ORDER BY sp.PaymentDate DESC
        ''', (student['StudentID'],))
        
        # Check for active installment plan
        installment_info = None
        if student['SubscriptionTier'] == 'premium_annual':
            installment_info = get_record('''
                SELECT COUNT(*) as paid_installments, 
                       MAX(InstallmentNumber) as last_installment,
                       MAX(TotalInstallments) as total_installments
                FROM subscription_payments
                WHERE StudentID = %s AND IsInstallment = 1 AND Status = 'completed'
            ''', (student['StudentID'],))
        
        return render_template('subscriptions/current.html', 
                             student=student,
                             payment_history=payment_history,
                             installment_info=installment_info)
    
    except Exception as e:
        flash(f'Error loading subscription details: {str(e)}', 'danger')
        return redirect(url_for('dashboard.dashboard'))

@subscriptions_bp.route('/upgrade/<plan_name>')
@login_required
@role_required(['student'])
def upgrade(plan_name):
    """Show upgrade options for a specific plan"""
    try:
        user_id = session['user_id']
        
        # Get student info
        student = get_record('SELECT * FROM students WHERE UserID = %s', (user_id,))
        if not student:
            flash('Student profile not found', 'danger')
            return redirect(url_for('subscriptions.plans'))
        
        # Get target plan
        plan = get_record('SELECT * FROM subscription_plans WHERE Name = %s AND IsActive = 1', (plan_name,))
        if not plan:
            flash('Invalid subscription plan', 'danger')
            return redirect(url_for('subscriptions.plans'))
        
        # Parse features
        plan['Features'] = json.loads(plan['Features']) if plan['Features'] else {}
        
        # Check if already on this plan
        if student['SubscriptionTier'] == plan_name:
            flash('You are already subscribed to this plan', 'info')
            return redirect(url_for('subscriptions.current_subscription'))
        
        # Calculate proration if upgrading mid-cycle
        proration_info = calculate_proration(student, plan)
        
        return render_template('subscriptions/upgrade.html', 
                             plan=plan,
                             student=student,
                             proration_info=proration_info)
    
    except Exception as e:
        flash(f'Error loading upgrade options: {str(e)}', 'danger')
        return redirect(url_for('subscriptions.plans'))

@subscriptions_bp.route('/checkout', methods=['POST'])
@login_required
@role_required(['student'])
def checkout():
    """Process subscription checkout"""
    try:
        user_id = session['user_id']
        plan_id = request.form.get('plan_id')
        payment_method = request.form.get('payment_method', 'credit_card')
        is_installment = request.form.get('is_installment') == 'true'
        
        # Get student and plan info
        student = get_record('SELECT * FROM students WHERE UserID = %s', (user_id,))
        plan = get_record('SELECT * FROM subscription_plans WHERE PlanID = %s', (plan_id,))
        
        if not student or not plan:
            flash('Invalid checkout request', 'danger')
            return redirect(url_for('subscriptions.plans'))
        
        # Calculate payment amount
        if is_installment and plan['Name'] == 'premium_annual':
            amount = plan['Price'] / 12  # Monthly installment
            total_installments = 12
        else:
            amount = plan['Price']
            total_installments = 1
        
        # Create payment record
        transaction_id = str(uuid.uuid4())
        
        execute_query('''
            INSERT INTO subscription_payments 
            (StudentID, PlanID, Amount, PaymentMethod, TransactionID, Status, 
             IsInstallment, InstallmentNumber, TotalInstallments)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            student['StudentID'], plan_id, amount, payment_method, 
            transaction_id, 'pending', is_installment, 1 if is_installment else None, 
            total_installments if is_installment else None
        ))
        
        # In a real implementation, you would integrate with a payment processor here
        # For now, we'll simulate a successful payment
        if simulate_payment_processing(transaction_id, amount):
            # Update payment status
            execute_query('''
                UPDATE subscription_payments 
                SET Status = 'completed', PaymentDate = NOW()
                WHERE TransactionID = %s
            ''', (transaction_id,))
            
            # Update student subscription
            subscription_start = datetime.now().date()
            if plan['BillingCycle'] == 'monthly':
                subscription_end = subscription_start + timedelta(days=30)
            else:  # annual
                subscription_end = subscription_start + timedelta(days=365)
            
            execute_query('''
                UPDATE students 
                SET SubscriptionTier = %s, SubscriptionStatus = 'active',
                    SubscriptionStart = %s, SubscriptionEnd = %s
                WHERE StudentID = %s
            ''', (plan['Name'], subscription_start, subscription_end, student['StudentID']))
            
            flash(f'Successfully subscribed to {plan["Name"]}!', 'success')
            
            # Set up recurring payments for installments
            if is_installment:
                flash('Your installment plan has been set up. You will be charged monthly.', 'info')
            
            return redirect(url_for('subscriptions.current_subscription'))
        else:
            # Payment failed
            execute_query('''
                UPDATE subscription_payments 
                SET Status = 'failed'
                WHERE TransactionID = %s
            ''', (transaction_id,))
            
            flash('Payment processing failed. Please try again.', 'danger')
            return redirect(url_for('subscriptions.upgrade', plan_name=plan['Name']))
    
    except Exception as e:
        flash(f'Error processing payment: {str(e)}', 'danger')
        return redirect(url_for('subscriptions.plans'))

@subscriptions_bp.route('/cancel', methods=['POST'])
@login_required
@role_required(['student'])
def cancel_subscription():
    """Cancel current subscription"""
    try:
        user_id = session['user_id']
        reason = request.form.get('cancellation_reason', '')
        
        student = get_record('SELECT * FROM students WHERE UserID = %s', (user_id,))
        if not student:
            flash('Student profile not found', 'danger')
            return redirect(url_for('dashboard.dashboard'))
        
        if student['SubscriptionTier'] == 'freemium':
            flash('You are already on the free plan', 'info')
            return redirect(url_for('subscriptions.current_subscription'))
        
        # Update subscription status
        execute_query('''
            UPDATE students 
            SET SubscriptionStatus = 'cancelled'
            WHERE StudentID = %s
        ''', (student['StudentID'],))
        
        # Log cancellation reason
        execute_query('''
            INSERT INTO admin_activity_log 
            (AdminID, Action, TargetType, TargetID, NewValue, CreatedAt)
            VALUES (%s, %s, %s, %s, %s, NOW())
        ''', (
            user_id, 'subscription_cancelled', 'student', student['StudentID'],
            json.dumps({'reason': reason, 'previous_tier': student['SubscriptionTier']})
        ))
        
        flash('Your subscription has been cancelled. You will retain access until the end of your billing period.', 'info')
        return redirect(url_for('subscriptions.current_subscription'))
    
    except Exception as e:
        flash(f'Error cancelling subscription: {str(e)}', 'danger')
        return redirect(url_for('subscriptions.current_subscription'))

@subscriptions_bp.route('/process-installment/<int:student_id>')
def process_installment(student_id):
    """Process monthly installment payment (called by scheduled job)"""
    try:
        # Get student with active installment plan
        student = get_record('''
            SELECT s.*, sp.PlanID, sp.Price
            FROM students s
            JOIN subscription_plans sp ON s.SubscriptionTier = sp.Name
            WHERE s.StudentID = %s 
            AND s.SubscriptionTier = 'premium_annual'
            AND s.SubscriptionStatus = 'active'
        ''', (student_id,))
        
        if not student:
            return jsonify({'error': 'Invalid student or no active installment plan'}), 400
        
        # Check how many installments have been paid
        installment_info = get_record('''
            SELECT COUNT(*) as paid_count, MAX(InstallmentNumber) as last_number
            FROM subscription_payments
            WHERE StudentID = %s AND IsInstallment = 1 AND Status = 'completed'
        ''', (student_id,))
        
        next_installment = (installment_info['last_number'] or 0) + 1
        
        if next_installment > 12:
            return jsonify({'message': 'All installments completed'}), 200
        
        # Process installment payment
        amount = student['Price'] / 12
        transaction_id = str(uuid.uuid4())
        
        execute_query('''
            INSERT INTO subscription_payments 
            (StudentID, PlanID, Amount, PaymentMethod, TransactionID, Status,
             IsInstallment, InstallmentNumber, TotalInstallments)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            student_id, student['PlanID'], amount, 'auto_charge',
            transaction_id, 'pending', True, next_installment, 12
        ))
        
        # Simulate payment processing
        if simulate_payment_processing(transaction_id, amount):
            execute_query('''
                UPDATE subscription_payments 
                SET Status = 'completed', PaymentDate = NOW()
                WHERE TransactionID = %s
            ''', (transaction_id,))
            
            return jsonify({'message': f'Installment {next_installment} processed successfully'}), 200
        else:
            execute_query('''
                UPDATE subscription_payments 
                SET Status = 'failed'
                WHERE TransactionID = %s
            ''', (transaction_id,))
            
            return jsonify({'error': 'Payment processing failed'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_proration(student, new_plan):
    """Calculate proration for mid-cycle upgrades"""
    # This is a simplified implementation
    # In practice, you'd calculate based on remaining days in current cycle
    proration_info = {
        'current_plan_refund': 0.00,
        'new_plan_charge': new_plan['Price'],
        'total_due': new_plan['Price']
    }
    
    if student['SubscriptionEnd'] and student['SubscriptionEnd'] > datetime.now().date():
        # Calculate remaining days
        remaining_days = (student['SubscriptionEnd'] - datetime.now().date()).days
        if remaining_days > 0:
            # Simple proration calculation
            current_plan = get_record(
                'SELECT * FROM subscription_plans WHERE Name = %s', 
                (student['SubscriptionTier'],)
            )
            if current_plan:
                daily_rate = current_plan['Price'] / 30  # Assuming 30-day month
                proration_info['current_plan_refund'] = daily_rate * remaining_days
                proration_info['total_due'] = new_plan['Price'] - proration_info['current_plan_refund']
    
    return proration_info

def simulate_payment_processing(transaction_id, amount):
    """Simulate payment processing (replace with real payment gateway)"""
    # In a real implementation, integrate with Stripe, PayPal, etc.
    # For demo purposes, we'll simulate a 95% success rate
    import random
    return random.random() < 0.95

@subscriptions_bp.route('/invoice/<int:payment_id>')
@login_required
@role_required(['student'])
def invoice(payment_id):
    """Generate invoice for a payment"""
    try:
        user_id = session['user_id']
        
        # Get payment details with plan info
        payment = get_record('''
            SELECT sp.*, spl.Name as PlanName, spl.Description,
                   u.First, u.Last, u.Email
            FROM subscription_payments sp
            JOIN subscription_plans spl ON sp.PlanID = spl.PlanID
            JOIN students s ON sp.StudentID = s.StudentID
            JOIN users u ON s.UserID = u.UserID
            WHERE sp.PaymentID = %s AND u.UserID = %s
        ''', (payment_id, user_id))
        
        if not payment:
            flash('Invoice not found', 'danger')
            return redirect(url_for('subscriptions.current_subscription'))
        
        return render_template('subscriptions/invoice.html', payment=payment)
    
    except Exception as e:
        flash(f'Error generating invoice: {str(e)}', 'danger')
        return redirect(url_for('subscriptions.current_subscription'))
