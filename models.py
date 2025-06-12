from flask_mysqldb import MySQLdb
import MySQLdb.cursors
from extensions import mysql
from flask import current_app
import os
from PIL import Image  # Temporarily disabled
import io

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





# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'document': {'pdf', 'doc', 'docx', 'txt', 'md'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv'},
    'archive': {'zip', 'rar', '7z', 'tar', 'gz'}
}

# Maximum file sizes (in bytes)
MAX_FILE_SIZES = {
    'image': 5 * 1024 * 1024,  # 5MB
    'document': 10 * 1024 * 1024,  # 10MB
    'video': 100 * 1024 * 1024,  # 100MB
    'archive': 50 * 1024 * 1024  # 50MB
}

def allowed_file(filename, file_type):
    """Check if file extension is allowed for the given type"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS.get(file_type, set())

def get_file_type(filename):
    """Determine file type based on extension"""
    if '.' not in filename:
        return None
    extension = filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return file_type
    return None

def create_upload_folder(folder_path):
    """Create upload folder if it doesn't exist"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def optimize_image(image_data, max_width=1920, max_height=1080, quality=85):
    """Optimize image for web use"""
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Resize if too large
        if image.width > max_width or image.height > max_height:
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save optimized image
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    
    except Exception as e:
        current_app.logger.error(f"Error optimizing image: {str(e)}")
        return image_data
