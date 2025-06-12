"""
Simple File Upload Routes for Sec Era Platform
Basic file upload without image processing
"""
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import uuid
from datetime import datetime
import mimetypes

uploads_bp = Blueprint('uploads', __name__, url_prefix='/uploads')

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
    """Check if the file extension is allowed for the given type"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS.get(file_type, set())

def get_file_type(filename):
    """Determine file type based on extension"""
    if '.' not in filename:
        return 'unknown'
    
    extension = filename.rsplit('.', 1)[1].lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return file_type
    return 'unknown'

def generate_unique_filename(filename):
    """Generate a unique filename with timestamp and UUID"""
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{secure_filename(name)}_{timestamp}_{unique_id}.{ext}"
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{secure_filename(filename)}_{timestamp}_{unique_id}"

@uploads_bp.route('/profile-image', methods=['POST'])
def upload_profile_image():
    """Upload and process profile image"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename, 'image'):
        return jsonify({'error': 'Invalid file type. Only images are allowed.'}), 400
    
    try:
        # Check file size
        file_data = file.read()
        if len(file_data) > MAX_FILE_SIZES['image']:
            return jsonify({'error': 'File too large. Maximum size is 5MB.'}), 400
        
        # Generate unique filename
        filename = generate_unique_filename(file.filename)
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'profiles')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Return success response
        file_url = f'/static/uploads/profiles/{filename}'
        return jsonify({
            'success': True,
            'file_url': file_url,
            'filename': filename,
            'message': 'Profile image uploaded successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error uploading profile image: {str(e)}")
        return jsonify({'error': 'Upload failed. Please try again.'}), 500

@uploads_bp.route('/course-material', methods=['POST'])
def upload_course_material():
    """Upload course materials (documents, videos, etc.)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Determine file type
    file_type = get_file_type(file.filename)
    if file_type == 'unknown':
        return jsonify({'error': 'Unsupported file type'}), 400
    
    try:
        # Check file size
        file_data = file.read()
        if len(file_data) > MAX_FILE_SIZES.get(file_type, MAX_FILE_SIZES['document']):
            max_size_mb = MAX_FILE_SIZES.get(file_type, MAX_FILE_SIZES['document']) // (1024 * 1024)
            return jsonify({'error': f'File too large. Maximum size is {max_size_mb}MB.'}), 400
        
        # Generate unique filename
        filename = generate_unique_filename(file.filename)
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'courses')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Return success response
        file_url = f'/static/uploads/courses/{filename}'
        return jsonify({
            'success': True,
            'file_url': file_url,
            'filename': filename,
            'file_type': file_type,
            'original_name': file.filename,
            'message': 'Course material uploaded successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error uploading course material: {str(e)}")
        return jsonify({'error': 'Upload failed. Please try again.'}), 500

@uploads_bp.route('/admin-document', methods=['POST'])
def upload_admin_document():
    """Upload administrative documents"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check if user is admin (you may want to implement proper admin check)
    # For now, we'll allow any logged-in user
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Only allow documents for admin uploads
    if not allowed_file(file.filename, 'document'):
        return jsonify({'error': 'Invalid file type. Only documents are allowed.'}), 400
    
    try:
        # Check file size
        file_data = file.read()
        if len(file_data) > MAX_FILE_SIZES['document']:
            return jsonify({'error': 'File too large. Maximum size is 10MB.'}), 400
        
        # Generate unique filename
        filename = generate_unique_filename(file.filename)
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'admin')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Return success response
        file_url = f'/static/uploads/admin/{filename}'
        return jsonify({
            'success': True,
            'file_url': file_url,
            'filename': filename,
            'original_name': file.filename,
            'message': 'Administrative document uploaded successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error uploading admin document: {str(e)}")
        return jsonify({'error': 'Upload failed. Please try again.'}), 500

@uploads_bp.route('/delete', methods=['POST'])
def delete_file():
    """Delete an uploaded file"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    if not data or 'filename' not in data or 'file_type' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    filename = data['filename']
    file_type = data['file_type']
    
    # Determine upload directory based on file type
    if file_type == 'profile':
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'profiles')
    elif file_type == 'course':
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'courses')
    elif file_type == 'admin':
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'admin')
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        file_path = os.path.join(upload_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({
                'success': True,
                'message': 'File deleted successfully'
            })
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        current_app.logger.error(f"Error deleting file: {str(e)}")
        return jsonify({'error': 'Delete failed. Please try again.'}), 500

@uploads_bp.route('/list/<file_type>')
def list_files(file_type):
    """List uploaded files of a specific type"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Determine upload directory based on file type
    if file_type == 'profiles':
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'profiles')
    elif file_type == 'courses':
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'courses')
    elif file_type == 'admin':
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'admin')
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        if not os.path.exists(upload_dir):
            return jsonify({'files': []})
        
        files = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'url': f'/static/uploads/{file_type}/{filename}'
                })
        
        return jsonify({'files': files})
        
    except Exception as e:
        current_app.logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': 'Failed to list files'}), 500

@uploads_bp.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Please choose a smaller file.'}), 413
