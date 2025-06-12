"""
Database Schema Fix Utility for Sec Era Platform
This script helps fix common database schema issues
"""
from app import create_app
from models import get_record, get_records, execute_query
from extensions import mysql
from datetime import datetime

def check_and_fix_schema():
    """Check and fix common database schema issues"""
    print("🔍 Checking database schema...")
    issues_found = []
    fixes_applied = []
    
    # Check if LastLogin column exists in users table
    try:
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
    
    # Check for missing instructor_courses relationships
    try:
        # Check if we have any instructor courses without proper relationships
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM instructor_courses ic
            LEFT JOIN instructors i ON ic.InstructorID = i.InstructorID
            WHERE i.InstructorID IS NULL
        """)
        result = cursor.fetchone()
        cursor.close()
        
        if result and result[0] > 0:
            print(f"⚠️  Found {result[0]} orphaned instructor-course relationships")
            issues_found.append("Orphaned instructor-course relationships")
            
            # Clean up orphaned relationships
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("""
                    DELETE ic FROM instructor_courses ic
                    LEFT JOIN instructors i ON ic.InstructorID = i.InstructorID
                    WHERE i.InstructorID IS NULL
                """)
                mysql.connection.commit()
                cursor.close()
                print("✅ Cleaned up orphaned instructor-course relationships")
                fixes_applied.append("Cleaned up orphaned relationships")
            except Exception as e:
                print(f"❌ Failed to clean up relationships: {e}")
        else:
            print("✅ No orphaned instructor-course relationships found")
            
    except Exception as e:
        print(f"❌ Error checking instructor-course relationships: {e}")
    
    # Check for missing API statistics support
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SHOW TABLES LIKE 'user_activity_log'")
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            print("⚠️  Missing user_activity_log table for API statistics")
            issues_found.append("Missing user_activity_log table")
            
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("""
                    CREATE TABLE user_activity_log (
                        LogID INT AUTO_INCREMENT PRIMARY KEY,
                        UserID INT NOT NULL,
                        ActivityType VARCHAR(50) NOT NULL,
                        ActivityDescription TEXT,
                        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        IPAddress VARCHAR(45),
                        UserAgent TEXT,
                        FOREIGN KEY (UserID) REFERENCES users(UserID) ON DELETE CASCADE
                    )
                """)
                mysql.connection.commit()
                cursor.close()
                print("✅ Created user_activity_log table")
                fixes_applied.append("Created user_activity_log table")
            except Exception as e:
                print(f"❌ Failed to create user_activity_log table: {e}")
        else:
            print("✅ user_activity_log table already exists")
            
    except Exception as e:
        print(f"❌ Error checking user_activity_log table: {e}")
    
    return issues_found, fixes_applied

def run_schema_fixes():
    """Main function to run all schema fixes"""
    print("🚀 Sec Era Platform - Database Schema Fix Utility")
    print("=" * 60)
    
    # Initialize statuses first
    from initialize_statuses import initialize_application_statuses
    initialize_application_statuses()
    
    # Run schema checks and fixes
    issues_found, fixes_applied = check_and_fix_schema()
    
    print("=" * 60)
    print("📊 SCHEMA CHECK SUMMARY")
    print("=" * 60)
    print(f"Issues Found: {len(issues_found)}")
    print(f"Fixes Applied: {len(fixes_applied)}")
    
    if fixes_applied:
        print("\n✅ FIXES APPLIED:")
        for fix in fixes_applied:
            print(f"  • {fix}")
    
    if issues_found and not fixes_applied:
        print("\n⚠️  ISSUES FOUND (but not fixed):")
        for issue in issues_found:
            print(f"  • {issue}")
    
    if not issues_found:
        print("✅ No schema fixes needed - database looks good!")
        print("🎯 Database schema is in perfect condition!")
    else:
        print("🔧 Schema fixes completed successfully!")

if __name__ == "__main__":
    # Create app context for database operations
    app = create_app()
    with app.app_context():
        run_schema_fixes()
