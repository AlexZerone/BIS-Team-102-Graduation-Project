from flask_mysqldb import MySQLdb
import MySQLdb.cursors
from extensions import mysql

# ✅ Utility Functions


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
            return True
    except Exception as e:
        print(f"DB Error in execute_query: {e}")
        mysql.connection.rollback()
        return False

# Helper Functions
def get_user_stats(user_id, user_type):
    stats = {}
    try:
        if user_type == 'student':
            # Get enrolled courses (use course_registrations and StudentID)
            student = get_record('SELECT StudentID FROM students WHERE UserID = %s', (user_id,))
            student_id = student['StudentID'] if student else None

            stats['enrolled_courses'] = get_record(
                'SELECT COUNT(*) as count FROM course_registrations WHERE StudentID = %s',
                (student_id,)
            )['count'] if student_id else 0

            stats['completed_courses'] = get_record(
                'SELECT COUNT(*) as count FROM course_registrations WHERE StudentID = %s AND Status = "Completed"',
                (student_id,)
            )['count'] if student_id else 0

            stats['job_applications'] = get_record(
                'SELECT COUNT(*) as count FROM job_applications WHERE StudentID = %s',
                (student_id,)
            )['count'] if student_id else 0

        elif user_type == 'instructor':
            # Get instructor's ID
            instructor = get_record('SELECT InstructorID FROM instructors WHERE UserID = %s', (user_id,))
            instructor_id = instructor['InstructorID'] if instructor else None

            # Get teaching courses
            stats['teaching_courses'] = get_record(
                'SELECT COUNT(*) as count FROM instructor_courses WHERE InstructorID = %s',
                (instructor_id,)
            )['count'] if instructor_id else 0

            # Get total students (distinct students in instructor's courses)
            stats['total_students'] = get_record(
                '''
                SELECT COUNT(DISTINCT cr.StudentID) as count
                FROM instructor_courses ic
                JOIN course_registrations cr ON ic.CourseID = cr.CourseID
                WHERE ic.InstructorID = %s
                ''',
                (instructor_id,)
            )['count'] if instructor_id else 0

            # Get total assessments in instructor's courses
            stats['total_assessments'] = get_record(
                '''
                SELECT COUNT(*) as count
                FROM assessments a
                JOIN instructor_courses ic ON a.CourseID = ic.CourseID
                WHERE ic.InstructorID = %s
                ''',
                (instructor_id,)
            )['count'] if instructor_id else 0

    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {}

    return stats