from flask_mysqldb import MySQLdb, MySQL
import MySQLdb.cursors
from extensions import mysql
import logging

# Configure logging
logger = logging.getLogger(__name__)

# ✅ *Utility Functions (Optimized)*
def get_record(query, params=()):
    """Fetch a single record with error handling"""
    try:
        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"Database error in get_record: {str(e)}")
        return None

def get_records(query, params=()):
    """Fetch multiple records with error handling"""
    try:
        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Database error in get_records: {str(e)}")
        return []

def execute_query(query, params=()):
    """Execute write operations with transaction handling"""
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute(query, params)
            mysql.connection.commit()
            return cursor.rowcount
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Database error in execute_query: {str(e)}")
        return 0

# Helper Functions (Schema-Aligned)
def get_user_stats(user_id, user_type):
    """Get user statistics aligned with current database schema"""
    stats = {}
    try:
        if user_type == 'student':
            # Get student academic stats
            student = get_record(
                'SELECT StudentID FROM students WHERE UserID = %s', 
                (user_id,)
            )
            if not student:
                return {}
            
            student_id = student['StudentID']
            
            stats.update({
                'enrolled_courses': get_record(
                    '''SELECT COUNT(*) AS count 
                       FROM course_registrations 
                       WHERE StudentID = %s''', 
                    (student_id,)
                )['count'] or 0,
                
                'completed_courses': get_record(
                    '''SELECT COUNT(*) AS count 
                       FROM course_registrations 
                       WHERE StudentID = %s AND Status = 'Completed' ''', 
                    (student_id,)
                )['count'] or 0,
                
                'job_applications': get_record(
                    '''SELECT COUNT(*) AS count 
                       FROM job_applications 
                       WHERE StudentID = %s''', 
                    (student_id,)
                )['count'] or 0
            })

        elif user_type == 'instructor':
            # Get instructor teaching stats
            instructor = get_record(
                'SELECT InstructorID FROM instructors WHERE UserID = %s', 
                (user_id,)
            )
            if not instructor:
                return {}
            
            instructor_id = instructor['InstructorID']
            
            stats.update({
                'teaching_courses': get_record(
                    '''SELECT COUNT(*) AS count 
                       FROM instructor_courses 
                       WHERE InstructorID = %s''', 
                    (instructor_id,)
                )['count'] or 0,
                
                'total_students': get_record(
                    '''SELECT COUNT(DISTINCT cr.StudentID) AS count 
                       FROM course_registrations cr
                       JOIN instructor_courses ic ON cr.CourseID = ic.CourseID
                       WHERE ic.InstructorID = %s''', 
                    (instructor_id,)
                )['count'] or 0,
                
                'total_assessments': get_record(
                    '''SELECT COUNT(*) AS count 
                       FROM assessments 
                       WHERE CourseID IN (
                           SELECT CourseID FROM instructor_courses 
                           WHERE InstructorID = %s
                       )''', 
                    (instructor_id,)
                )['count'] or 0
            })

    except Exception as e:
        logger.error(f"Error in get_user_stats: {str(e)}")
        return {}

    return stats

