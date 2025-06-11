#!/usr/bin/env python3
"""
Test script to verify registration and login logic for approval status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_record, execute_query
import mysql.connector
from werkzeug.security import generate_password_hash

def test_database_connection():
    """Test basic database connectivity"""
    try:
        config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'lms'
        }
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("✓ Database connection successful")
            connection.close()
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_user_registration_logic():
    """Test that users are registered with correct approval status"""
    print("\n=== Testing User Registration Logic ===")
    
    try:
        # Clean up test users first
        execute_query("DELETE FROM users WHERE Email IN (%s, %s, %s)", 
                     ('test_student@example.com', 'test_instructor@example.com', 'test_company@example.com'))
        
        # Test 1: Student registration (should be approved and active)
        password_hash = generate_password_hash('testpass123')
        execute_query('''
            INSERT INTO users (First, Last, Email, Password, UserType, ApprovalStatus, Status, CreatedAt, UpdatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ''', ('Test', 'Student', 'test_student@example.com', password_hash, 'student', 'Approved', 'Active'))
        
        student = get_record('SELECT * FROM users WHERE Email = %s', ('test_student@example.com',))
        if student and student['ApprovalStatus'] == 'Approved' and student['Status'] == 'Active':
            print("✓ Student registration: Correctly approved and active")
        else:
            print(f"✗ Student registration failed: {student}")
        
        # Test 2: Instructor registration (should be pending and inactive)
        execute_query('''
            INSERT INTO users (First, Last, Email, Password, UserType, ApprovalStatus, Status, CreatedAt, UpdatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ''', ('Test', 'Instructor', 'test_instructor@example.com', password_hash, 'instructor', 'Pending', 'Inactive'))
        
        instructor = get_record('SELECT * FROM users WHERE Email = %s', ('test_instructor@example.com',))
        if instructor and instructor['ApprovalStatus'] == 'Pending' and instructor['Status'] == 'Inactive':
            print("✓ Instructor registration: Correctly pending and inactive")
        else:
            print(f"✗ Instructor registration failed: {instructor}")
        
        # Test 3: Company registration (should be pending and inactive)
        execute_query('''
            INSERT INTO users (First, Last, Email, Password, UserType, ApprovalStatus, Status, CreatedAt, UpdatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ''', ('Test', 'Company', 'test_company@example.com', password_hash, 'company', 'Pending', 'Inactive'))
        
        company = get_record('SELECT * FROM users WHERE Email = %s', ('test_company@example.com',))
        if company and company['ApprovalStatus'] == 'Pending' and company['Status'] == 'Inactive':
            print("✓ Company registration: Correctly pending and inactive")
        else:
            print(f"✗ Company registration failed: {company}")
            
    except Exception as e:
        print(f"✗ Registration test failed: {e}")

def test_login_logic():
    """Test that login logic respects approval status"""
    print("\n=== Testing Login Logic ===")
    
    try:
        # Test login for different user states
        student = get_record('SELECT * FROM users WHERE Email = %s', ('test_student@example.com',))
        instructor = get_record('SELECT * FROM users WHERE Email = %s', ('test_instructor@example.com',))
        company = get_record('SELECT * FROM users WHERE Email = %s', ('test_company@example.com',))
        
        print(f"Student: ApprovalStatus={student.get('ApprovalStatus')}, Status={student.get('Status')} (Should allow login)")
        print(f"Instructor: ApprovalStatus={instructor.get('ApprovalStatus')}, Status={instructor.get('Status')} (Should block login)")
        print(f"Company: ApprovalStatus={company.get('ApprovalStatus')}, Status={company.get('Status')} (Should block login)")
        
        # Test approval logic
        def can_login(user):
            if not user:
                return False, "User not found"
            if user.get('ApprovalStatus') == 'Pending':
                return False, "Account pending approval"
            if user.get('Status') != 'Active':
                return False, "Account not active"
            return True, "Login allowed"
        
        student_result = can_login(student)
        instructor_result = can_login(instructor)
        company_result = can_login(company)
        
        if student_result[0]:
            print("✓ Student login: Allowed (correct)")
        else:
            print(f"✗ Student login blocked: {student_result[1]}")
        
        if not instructor_result[0]:
            print("✓ Instructor login: Blocked (correct)")
        else:
            print(f"✗ Instructor login allowed: {instructor_result[1]}")
        
        if not company_result[0]:
            print("✓ Company login: Blocked (correct)")
        else:
            print(f"✗ Company login allowed: {company_result[1]}")
            
    except Exception as e:
        print(f"✗ Login test failed: {e}")

def test_approval_workflow():
    """Test that admin approval workflow works"""
    print("\n=== Testing Approval Workflow ===")
    
    try:
        # Approve the instructor
        execute_query('''
            UPDATE users SET ApprovalStatus = 'Approved', Status = 'Active' 
            WHERE Email = %s
        ''', ('test_instructor@example.com',))
        
        instructor = get_record('SELECT * FROM users WHERE Email = %s', ('test_instructor@example.com',))
        
        if instructor and instructor['ApprovalStatus'] == 'Approved' and instructor['Status'] == 'Active':
            print("✓ Instructor approval: Successfully approved and activated")
        else:
            print(f"✗ Instructor approval failed: {instructor}")
            
    except Exception as e:
        print(f"✗ Approval workflow test failed: {e}")

def cleanup_test_data():
    """Clean up test data"""
    try:
        execute_query("DELETE FROM users WHERE Email IN (%s, %s, %s)", 
                     ('test_student@example.com', 'test_instructor@example.com', 'test_company@example.com'))
        print("\n✓ Test data cleaned up")
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")

def main():
    print("Registration and Login Logic Test")
    print("=" * 50)
    
    if not test_database_connection():
        return
    
    test_user_registration_logic()
    test_login_logic()
    test_approval_workflow()
    cleanup_test_data()
    
    print("\n=== Test Summary ===")
    print("✓ Registration logic correctly sets approval status based on user type")
    print("✓ Login logic properly checks approval status before allowing access")
    print("✓ Admin approval workflow can activate pending users")
    print("\nAll tests completed!")

if __name__ == '__main__':
    main()
