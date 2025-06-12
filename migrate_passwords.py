#!/usr/bin/env python3
"""
Password Migration Script for Sec Era Platform
This script updates any plain text passwords in the database to properly hashed passwords.
Run this once to migrate existing user passwords to secure hashed format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash, check_password_hash
from models import get_records, execute_query, get_record
from extensions import mysql
from app import create_app

def is_password_hashed(password):
    """Check if a password is already hashed"""
    if not password:
        return False
    
    # Hashed passwords typically start with method identifiers
    hash_indicators = ['pbkdf2:', 'scrypt:', 'argon2:', '$']
    return any(password.startswith(indicator) for indicator in hash_indicators)

def migrate_passwords():
    """Migrate plain text passwords to hashed passwords"""
    print("🔐 Starting password migration...")
    
    try:
        # Get all users with passwords
        users = get_records('SELECT UserID, Email, Password FROM users WHERE Password IS NOT NULL AND Password != ""')
        
        if not users:
            print("ℹ️  No users found with passwords.")
            return
        
        migrated_count = 0
        already_hashed_count = 0
        error_count = 0
        
        for user in users:
            user_id = user['UserID']
            email = user['Email']
            password = user['Password']
            
            if is_password_hashed(password):
                already_hashed_count += 1
                print(f"✅ User {email} already has hashed password")
                continue
            
            try:
                # Hash the plain text password
                hashed_password = generate_password_hash(password)
                
                # Update the database
                execute_query('UPDATE users SET Password = %s WHERE UserID = %s', 
                            (hashed_password, user_id))
                
                migrated_count += 1
                print(f"🔄 Migrated password for user: {email}")
                
                # Verify the migration worked
                test_user = get_record('SELECT Password FROM users WHERE UserID = %s', (user_id,))
                if test_user and check_password_hash(test_user['Password'], password):
                    print(f"✅ Verification successful for user: {email}")
                else:
                    print(f"⚠️  Verification failed for user: {email}")
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Error migrating password for user {email}: {str(e)}")
        
        print(f"\n📊 Migration Summary:")
        print(f"   ✅ Already hashed: {already_hashed_count}")
        print(f"   🔄 Migrated: {migrated_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📈 Total processed: {len(users)}")
        
        if error_count == 0:
            print("🎉 Password migration completed successfully!")
        else:
            print(f"⚠️  Migration completed with {error_count} errors. Please review.")
            
    except Exception as e:
        print(f"💥 Critical error during migration: {str(e)}")
        return False
    
    return True

def create_test_users():
    """Create test users with proper hashed passwords"""
    print("\n👥 Creating test users...")
    
    test_users = [
        {
            'first': 'Admin',
            'last': 'User',
            'email': 'admin@secera.com',
            'password': 'admin123',
            'user_type': 'admin'
        },
        {
            'first': 'John',
            'last': 'Student',
            'email': 'student@example.com',
            'password': 'student123',
            'user_type': 'student'
        },
        {
            'first': 'Jane',
            'last': 'Instructor',
            'email': 'instructor@example.com',
            'password': 'instructor123',
            'user_type': 'instructor'
        },
        {
            'first': 'Tech',
            'last': 'Company',
            'email': 'company@example.com',
            'password': 'company123',
            'user_type': 'company'
        }
    ]
    
    created_count = 0
    
    for user_data in test_users:
        try:
            # Check if user already exists
            existing = get_record('SELECT UserID FROM users WHERE Email = %s', (user_data['email'],))
            if existing:
                print(f"⚠️  User {user_data['email']} already exists, skipping...")
                continue
            
            # Hash the password
            hashed_password = generate_password_hash(user_data['password'])
            
            # Create the user
            execute_query('''
                INSERT INTO users (First, Last, Email, Password, UserType, CreatedAt, UpdatedAt, Status)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), 'Active')
            ''', (user_data['first'], user_data['last'], user_data['email'], 
                  hashed_password, user_data['user_type']))
            
            created_count += 1
            print(f"✅ Created test user: {user_data['email']} (password: {user_data['password']})")
            
        except Exception as e:
            print(f"❌ Error creating user {user_data['email']}: {str(e)}")
    
    print(f"\n📊 Test User Creation Summary:")
    print(f"   ✅ Created: {created_count}")
    print(f"   📈 Total attempted: {len(test_users)}")

def verify_login_functionality():
    """Test login functionality with migrated passwords"""
    print("\n🧪 Testing login functionality...")
    
    # Test with a known user (if exists)
    test_email = "admin@secera.com"
    test_password = "admin123"
    
    try:
        user = get_record('SELECT * FROM users WHERE Email = %s AND Status = "Active"', (test_email,))
        
        if user:
            stored_password = user['Password']
            if check_password_hash(stored_password, test_password):
                print(f"✅ Login test successful for {test_email}")
                return True
            else:
                print(f"❌ Login test failed for {test_email}")
                return False
        else:
            print(f"⚠️  Test user {test_email} not found")
            return None
            
    except Exception as e:
        print(f"❌ Error testing login: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("🚀 Sec Era Platform - Password Migration Tool")
    print("=" * 50)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Step 1: Migrate existing passwords
            if not migrate_passwords():
                print("💥 Migration failed, exiting...")
                return
            
            # Step 2: Create test users (optional)
            choice = input("\n❓ Do you want to create test users? (y/n): ").lower().strip()
            if choice == 'y':
                create_test_users()
            
            # Step 3: Verify functionality
            print("\n🔍 Verifying login functionality...")
            verify_login_functionality()
            
            print("\n🎉 Migration process completed!")
            print("📝 You can now use the application with properly hashed passwords.")
            
        except Exception as e:
            print(f"💥 Unexpected error: {str(e)}")
            print("🔧 Please check your database connection and try again.")

if __name__ == "__main__":
    main()
