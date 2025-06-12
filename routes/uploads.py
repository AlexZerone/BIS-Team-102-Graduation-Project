"""
File Upload Routes for Sec Era Platform
Handles file uploads for course materials, profile images, and admin uploads
"""
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import uuid
from datetime import datetime
from models import get_file_type, allowed_file, optimize_image, create_upload_folder, ALLOWED_EXTENSIONS, MAX_FILE_SIZES


uploads_bp = Blueprint('uploads', __name__, url_prefix='/uploads')

@uploads_bp.route('/profile-image', methods=['POST'])
def upload_profile_image():
    """Upload and process profile image"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename, 'image'):
        return jsonify({'success': False, 'error': 'Invalid file type. Only images are allowed.'}), 400
    
    try:
        # Read file data
        file_data = file.read()
        
        # Check file size
        if len(file_data) > MAX_FILE_SIZES['image']:
            return jsonify({'success': False, 'error': 'File too large. Maximum size is 5MB.'}), 400
        
        # Optimize image
        optimized_data = optimize_image(file_data, max_width=500, max_height=500)
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"profile_{session['user_id']}_{uuid.uuid4().hex[:8]}.jpg"
        
        # Create upload directory
        upload_folder = create_upload_folder(os.path.join(current_app.static_folder, 'uploads', 'profiles'))
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Save optimized image
        with open(file_path, 'wb') as f:
            f.write(optimized_data)
        
        # Return success response with file URL
        file_url = f"/static/uploads/profiles/{unique_filename}"
        
        return jsonify({
            'success': True,
            'message': 'Profile image uploaded successfully',
            'file_url': file_url,
            'filename': unique_filename
        })
    
    except RequestEntityTooLarge:
        return jsonify({'success': False, 'error': 'File too large'}), 413
    except Exception as e:
        current_app.logger.error(f"Error uploading profile image: {str(e)}")
        return jsonify({'success': False, 'error': 'Upload failed. Please try again.'}), 500

@uploads_bp.route('/course-material', methods=['POST'])
def upload_course_material():
    """Upload course material (documents, videos, etc.)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    # Check if user is instructor or admin
    user_type = session.get('user_type')
    if user_type not in ['instructor', 'admin']:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    course_id = request.form.get('course_id')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not course_id:
        return jsonify({'success': False, 'error': 'Course ID required'}), 400
    
    # Determine file type
    file_type = get_file_type(file.filename)
    if not file_type:
        return jsonify({'success': False, 'error': 'File type not supported'}), 400
    
    try:
        # Read file data
        file_data = file.read()
        
        # Check file size
        if len(file_data) > MAX_FILE_SIZES.get(file_type, MAX_FILE_SIZES['document']):
            max_size = MAX_FILE_SIZES.get(file_type) // (1024 * 1024)
            return jsonify({'success': False, 'error': f'File too large. Maximum size is {max_size}MB.'}), 400
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        safe_filename = secure_filename(file.filename.rsplit('.', 1)[0])
        unique_filename = f"course_{course_id}_{uuid.uuid4().hex[:8]}_{safe_filename}.{file_extension}"
        
        # Create upload directory
        upload_folder = create_upload_folder(os.path.join(current_app.static_folder, 'uploads', 'courses', course_id))
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Return success response
        file_url = f"/static/uploads/courses/{course_id}/{unique_filename}"
        
        return jsonify({
            'success': True,
            'message': 'Course material uploaded successfully',
            'file_url': file_url,
            'filename': unique_filename,
            'file_type': file_type,
            'file_size': len(file_data)
        })
    
    except RequestEntityTooLarge:
        return jsonify({'success': False, 'error': 'File too large'}), 413
    except Exception as e:
        current_app.logger.error(f"Error uploading course material: {str(e)}")
        return jsonify({'success': False, 'error': 'Upload failed. Please try again.'}), 500

@uploads_bp.route('/admin-document', methods=['POST'])
def upload_admin_document():
    """Upload administrative documents"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    document_type = request.form.get('document_type', 'general')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Determine file type
    file_type = get_file_type(file.filename)
    if file_type not in ['document', 'image']:
        return jsonify({'success': False, 'error': 'Only documents and images are allowed'}), 400
    
    try:
        # Read file data
        file_data = file.read()
        
        # Check file size
        if len(file_data) > MAX_FILE_SIZES.get(file_type, MAX_FILE_SIZES['document']):
            max_size = MAX_FILE_SIZES.get(file_type) // (1024 * 1024)
            return jsonify({'success': False, 'error': f'File too large. Maximum size is {max_size}MB.'}), 400
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        safe_filename = secure_filename(file.filename.rsplit('.', 1)[0])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"admin_{document_type}_{timestamp}_{safe_filename}.{file_extension}"
        
        # Create upload directory
        upload_folder = create_upload_folder(os.path.join(current_app.static_folder, 'uploads', 'admin'))
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Return success response
        file_url = f"/static/uploads/admin/{unique_filename}"
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'file_url': file_url,
            'filename': unique_filename,
            'file_type': file_type,
            'file_size': len(file_data)
        })
    
    except RequestEntityTooLarge:
        return jsonify({'success': False, 'error': 'File too large'}), 413
    except Exception as e:
        current_app.logger.error(f"Error uploading admin document: {str(e)}")
        return jsonify({'success': False, 'error': 'Upload failed. Please try again.'}), 500

@uploads_bp.route('/delete', methods=['DELETE'])
def delete_file():
    """Delete uploaded file (admin only)"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    
    file_path = request.json.get('file_path')
    if not file_path:
        return jsonify({'success': False, 'error': 'File path required'}), 400
    
    try:
        # Ensure file is within allowed directories
        allowed_paths = ['static/uploads/']
        if not any(file_path.startswith(path) for path in allowed_paths):
            return jsonify({'success': False, 'error': 'Invalid file path'}), 400
        
        full_path = os.path.join(current_app.static_folder, file_path.replace('static/', ''))
        
        if os.path.exists(full_path):
            os.remove(full_path)
            return jsonify({'success': True, 'message': 'File deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    
    except Exception as e:
        current_app.logger.error(f"Error deleting file: {str(e)}")
        return jsonify({'success': False, 'error': 'Delete failed. Please try again.'}), 500

@uploads_bp.route('/list/<path:folder>')
def list_files(folder):
    """List files in upload folder (admin only)"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    
    try:
        folder_path = os.path.join(current_app.static_folder, 'uploads', folder)
        
        if not os.path.exists(folder_path):
            return jsonify({'success': True, 'files': []})
        
        files = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'url': f"/static/uploads/{folder}/{filename}"
                })
        
        return jsonify({'success': True, 'files': files})
    
    except Exception as e:
        current_app.logger.error(f"Error listing files: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to list files'}), 500
