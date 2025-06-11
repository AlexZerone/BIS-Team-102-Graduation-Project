"""
Database Schema Fix Utility for Sec Era Platform
This script helps fix common database schema issues
"""
from app import create_app
from models import get_record, get_records, execute_query
from datetime import datetime

def check_and_fix_schema():
    """Check and fix common database schema issues"""
    print("🔍 Checking database schema...")
    issues_found = []
    fixes_applied = []
      # Check if LastLogin column exists
    try:
        # Use raw query to get table structure
        from extensions import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("DESCRIBE users")
        columns_info = cursor.fetchall()
        columns = [row[0] for row in columns_info] if columns_info else []
        cursor.close()
        
        if 'LastLogin' not in columns:
            print("⚠️  Missing LastLogin column in users table")
            issues_found.append("Missing LastLogin column")
            
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("ALTER TABLE users ADD COLUMN LastLogin DATETIME DEFAULT NULL")
                mysql.connection.commit()
                cursor.close()
                print("✅ Added LastLogin column to users table")
                fixes_applied.append("Added LastLogin column")
            except Exception as e:
                print(f"❌ Failed to add LastLogin column: {e}")
        else:
            print("✅ LastLogin column already exists in users table")
                
    except Exception as e:
        print(f"❌ Error checking users table: {e}")
      # Check instructors table structure
    try:
        from extensions import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("DESCRIBE instructors")
        instructor_info = cursor.fetchall()
        cursor.close()
        
        if instructor_info:
            instructor_columns = [row[0] for row in instructor_info]
            print(f"📋 Instructors table columns: {instructor_columns}")
            
            # Check if we need to add missing columns
            required_columns = ['ApprovalStatus', 'ApprovedBy', 'ApprovedAt', 'RejectionReason']
            for col in required_columns:
                if col not in instructor_columns:
                    print(f"⚠️  Missing {col} column in instructors table")
                    issues_found.append(f"Missing {col} column in instructors")
                    
                    try:
                        cursor = mysql.connection.cursor()
                        if col == 'ApprovalStatus':
                            cursor.execute(f"ALTER TABLE instructors ADD COLUMN {col} VARCHAR(20) DEFAULT 'Pending'")
                        elif col == 'ApprovedBy':
                            cursor.execute(f"ALTER TABLE instructors ADD COLUMN {col} INT DEFAULT NULL")
                        elif col == 'ApprovedAt':
                            cursor.execute(f"ALTER TABLE instructors ADD COLUMN {col} DATETIME DEFAULT NULL")
                        elif col == 'RejectionReason':
                            cursor.execute(f"ALTER TABLE instructors ADD COLUMN {col} TEXT DEFAULT NULL")
                        mysql.connection.commit()
                        cursor.close()
                        print(f"✅ Added {col} column to instructors table")
                        fixes_applied.append(f"Added {col} column to instructors")
                    except Exception as e:
                        print(f"❌ Failed to add {col} column: {e}")
        else:
            print("⚠️  Instructors table not found")
            
    except Exception as e:
        print(f"❌ Error checking instructors table: {e}")
                            execute_query(f"ALTER TABLE instructors ADD COLUMN {col} INT DEFAULT NULL")
                        elif col == 'ApprovedAt':
                            execute_query(f"ALTER TABLE instructors ADD COLUMN {col} DATETIME DEFAULT NULL")
                        elif col == 'RejectionReason':
                            execute_query(f"ALTER TABLE instructors ADD COLUMN {col} TEXT DEFAULT NULL")
                        
                        print(f"✅ Added {col} column to instructors table")
                        fixes_applied.append(f"Added {col} column to instructors")
                    except Exception as e:
                        print(f"❌ Failed to add {col} column: {e}")
        else:
            print("❌ Could not describe instructors table")
            
    except Exception as e:
        print(f"❌ Error checking instructors table: {e}")
    
    # Check companies table structure
    try:
        result = execute_query("DESCRIBE companies")
        if result:
            company_columns = [row[0] for row in result]
            print(f"📋 Companies table columns: {company_columns}")
            
            # Check if we need to add missing columns
            required_columns = ['ApprovalStatus', 'ApprovedBy', 'ApprovedAt', 'RejectionReason']
            for col in required_columns:
                if col not in company_columns:
                    print(f"⚠️  Missing {col} column in companies table")
                    issues_found.append(f"Missing {col} column in companies")
                    
                    try:
                        if col == 'ApprovalStatus':
                            execute_query(f"ALTER TABLE companies ADD COLUMN {col} VARCHAR(20) DEFAULT 'Pending'")
                        elif col == 'ApprovedBy':
                            execute_query(f"ALTER TABLE companies ADD COLUMN {col} INT DEFAULT NULL")
                        elif col == 'ApprovedAt':
                            execute_query(f"ALTER TABLE companies ADD COLUMN {col} DATETIME DEFAULT NULL")
                        elif col == 'RejectionReason':
                            execute_query(f"ALTER TABLE companies ADD COLUMN {col} TEXT DEFAULT NULL")
                        
                        print(f"✅ Added {col} column to companies table")
                        fixes_applied.append(f"Added {col} column to companies")
                    except Exception as e:
                        print(f"❌ Failed to add {col} column: {e}")
        else:
            print("❌ Could not describe companies table")
            
    except Exception as e:
        print(f"❌ Error checking companies table: {e}")
    
    # Check courses table structure
    try:
        result = execute_query("DESCRIBE courses")
        if result:
            course_columns = [row[0] for row in result]
            print(f"📋 Courses table columns: {course_columns}")
            
            # Check if we need to add missing columns
            required_columns = ['ApprovalStatus', 'ApprovedBy', 'ApprovedAt', 'RejectionReason', 'CreatedBy']
            for col in required_columns:
                if col not in course_columns:
                    print(f"⚠️  Missing {col} column in courses table")
                    issues_found.append(f"Missing {col} column in courses")
                    
                    try:
                        if col == 'ApprovalStatus':
                            execute_query(f"ALTER TABLE courses ADD COLUMN {col} VARCHAR(20) DEFAULT 'Pending'")
                        elif col in ['ApprovedBy', 'CreatedBy']:
                            execute_query(f"ALTER TABLE courses ADD COLUMN {col} INT DEFAULT NULL")
                        elif col == 'ApprovedAt':
                            execute_query(f"ALTER TABLE courses ADD COLUMN {col} DATETIME DEFAULT NULL")
                        elif col == 'RejectionReason':
                            execute_query(f"ALTER TABLE courses ADD COLUMN {col} TEXT DEFAULT NULL")
                        
                        print(f"✅ Added {col} column to courses table")
                        fixes_applied.append(f"Added {col} column to courses")
                    except Exception as e:
                        print(f"❌ Failed to add {col} column: {e}")
        else:
            print("❌ Could not describe courses table")
            
    except Exception as e:
        print(f"❌ Error checking courses table: {e}")
    
    # Check for contact_requests table
    try:
        result = execute_query("DESCRIBE contact_requests")
        if not result:
            print("⚠️  Missing contact_requests table")
            issues_found.append("Missing contact_requests table")
            
            try:
                execute_query('''
                    CREATE TABLE contact_requests (
                        ContactID INT AUTO_INCREMENT PRIMARY KEY,
                        Name VARCHAR(100) NOT NULL,
                        Email VARCHAR(100) NOT NULL,
                        Subject VARCHAR(200) NOT NULL,
                        Message TEXT NOT NULL,
                        Priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
                        Status ENUM('open', 'in_progress', 'resolved') DEFAULT 'open',
                        AdminID INT DEFAULT NULL,
                        AdminNotes TEXT DEFAULT NULL,
                        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (AdminID) REFERENCES users(UserID)
                    )
                ''')
                print("✅ Created contact_requests table")
                fixes_applied.append("Created contact_requests table")
            except Exception as e:
                print(f"❌ Failed to create contact_requests table: {e}")
    except Exception as e:
        print(f"❌ Error checking contact_requests table: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SCHEMA CHECK SUMMARY")
    print("="*60)
    print(f"Issues Found: {len(issues_found)}")
    for issue in issues_found:
        print(f"  - {issue}")
    
    print(f"\nFixes Applied: {len(fixes_applied)}")
    for fix in fixes_applied:
        print(f"  ✅ {fix}")
    
    if len(fixes_applied) > 0:
        print("\n🎉 Schema fixes applied successfully!")
        print("ℹ️  You may need to restart the application for changes to take effect.")
    else:
        print("\n✅ No schema fixes needed - database looks good!")
    
    return len(issues_found), len(fixes_applied)

if __name__ == "__main__":
    print("🚀 Sec Era Platform - Database Schema Fix Utility")
    print("="*60)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            issues, fixes = check_and_fix_schema()
            
            if issues == 0:
                print("\n🎯 Database schema is in perfect condition!")
            elif fixes > 0:
                print(f"\n🔧 Fixed {fixes} out of {issues} schema issues.")
            else:
                print(f"\n⚠️  Found {issues} issues but couldn't fix them automatically.")
                print("Please check the database connection and permissions.")
                
        except Exception as e:
            print(f"\n❌ Error running schema check: {e}")
            print("Please ensure the database is accessible and try again.")
