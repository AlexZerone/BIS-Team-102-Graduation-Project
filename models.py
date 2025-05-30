from flask_mysqldb import MySQLdb, MySQL
import MySQLdb.cursors
from extensions import mysql



# ✅ **Utility Functions**

# Fetch a single record 
def get_record(query, params=()):
    try:
        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    except Exception as e:
        print(f"DB Error in get_record: {e}")
        return None


# Fetch multiple records
def get_records(query, params=()):
    try:
        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        print(f"DB Error in get_records: {e}")
        return None

# Execute an INSERT, UPDATE, or DELETE query
def execute_query(query, params=()):
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute(query, params)
            mysql.connection.commit()
    except Exception as e:
        print(f"DB Error in execute_query: {e}")
        return None



# Helper Functions
def get_user_stats(user_id, user_type):
    stats = {}
    try:
        if user_type == 'student':
            # Get enrolled courses
            stats['enrolled_courses'] = get_record(
                'SELECT COUNT(*) as count FROM enrollments WHERE UserID = %s', 
                (user_id,)
            )['count']
            
            # Get completed courses
            stats['completed_courses'] = get_record(
                'SELECT COUNT(*) as count FROM enrollments WHERE UserID = %s AND Status = "completed"', 
                (user_id,)
            )['count']
            
            # Get job applications
            stats['job_applications'] = get_record(
                'SELECT COUNT(*) as count FROM job_applications WHERE UserID = %s', 
                (user_id,)
            )['count']
            
        elif user_type == 'instructor':
            # Get teaching courses
            stats['teaching_courses'] = get_record(
                'SELECT COUNT(*) as count FROM courses WHERE InstructorID = %s', 
                (user_id,)
            )['count']
            
            # Get total students
            stats['total_students'] = get_record(
                '''SELECT COUNT(DISTINCT e.UserID) as count 
                   FROM enrollments e 
                   JOIN courses c ON e.CourseID = c.CourseID 
                   WHERE c.InstructorID = %s''', 
                (user_id,)
            )['count']
            
            # Get total assessments
            stats['total_assessments'] = get_record(
                '''SELECT COUNT(*) as count 
                   FROM assignments 
                   WHERE CourseID IN (SELECT CourseID FROM courses WHERE InstructorID = %s)''', 
                (user_id,)
            )['count']
            
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {}
    
    return stats


