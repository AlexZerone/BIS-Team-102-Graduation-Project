#!/usr/bin/env python3
"""
Create an admin user for testing the admin approval functionality
"""

import sqlite3
from werkzeug.security import generate_password_hash
import sys

def create_admin_user():
    """Create an admin user in the database"""
    
    try:
        # Connect to the database
        conn = sqlite3.connect('database/flask0.db')
        cursor = conn.cursor()
        
        # Check if admin user already exists
        cursor.execute("SELECT * FROM users WHERE Email = ?", ('admin@secera.com',))
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            print("✓ Admin user already exists!")
            print(f"   Email: admin@secera.com")
            print(f"   UserID: {existing_admin[0]}")
            print(f"   User Type: {existing_admin[5]}")
            print(f"   Status: {existing_admin[6]}")
            return existing_admin[0]
        
        # Create admin user
        print("Creating admin user...")
        
        password_hash = generate_password_hash('admin123')
        
        cursor.execute('''
            INSERT INTO users (First, Last, Email, Password, UserType, Status, ApprovalStatus, CreatedAt, UpdatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', ('Admin', 'User', 'admin@secera.com', password_hash, 'admin', 'Active', 'Approved'))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        print("✓ Admin user created successfully!")
        print(f"   Email: admin@secera.com")
        print(f"   Password: admin123")
        print(f"   UserID: {user_id}")
        
        return user_id
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return None
    finally:
        if conn:
            conn.close()

def verify_pending_users():
    """Check if there are pending instructors and companies to approve"""
    
    try:
        conn = sqlite3.connect('database/flask0.db')
        cursor = conn.cursor()
        
        # Check pending instructors
        cursor.execute('''
            SELECT COUNT(*) FROM instructors WHERE ApprovalStatus = 'Pending'
        ''')
        pending_instructors = cursor.fetchone()[0]
        
        # Check pending companies  
        cursor.execute('''
            SELECT COUNT(*) FROM companies WHERE ApprovalStatus = 'Pending'
        ''')
        pending_companies = cursor.fetchone()[0]
        
        print(f"\n📊 Pending Approvals:")
        print(f"   Instructors: {pending_instructors}")
        print(f"   Companies: {pending_companies}")
        
        if pending_instructors == 0 and pending_companies == 0:
            print("\n⚠️  No pending approvals found!")
            print("   Consider creating test instructor/company accounts for testing")
        
        return pending_instructors, pending_companies
        
    except Exception as e:
        print(f"❌ Error checking pending users: {e}")
        return 0, 0
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 Admin User Setup")
    print("=" * 20)
    
    admin_id = create_admin_user()
    if admin_id:
        verify_pending_users()
        
        print(f"\n🎯 Ready for Testing!")
        print(f"   1. Login with: admin@secera.com / admin123")
        print(f"   2. Navigate to: http://127.0.0.1:5000/admin/pending-instructors")
        print(f"   3. Test approve/reject functionality")
    else:
        print("❌ Failed to create admin user")
        sys.exit(1)
