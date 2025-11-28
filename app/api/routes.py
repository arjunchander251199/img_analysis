from flask import Blueprint, request, jsonify, current_app, url_for
from app.utils.file_handler import allowed_file, save_file, cleanup_file
from app.services.gemini_service import GeminiService
import traceback

api_bp = Blueprint('api', __name__)

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and return file info"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload an image.'}), 400
        
        # Save file
        filepath, unique_filename = save_file(file)
        
        if not filepath:
            return jsonify({'error': 'Error saving file'}), 500
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'file_url': url_for('static', filename=f'uploads/{unique_filename}', _external=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@api_bp.route('/analyze', methods=['POST'])
def analyze_file():
    """Analyze uploaded image with Gemini AI"""
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data:
            return jsonify({'error': 'Filename not provided'}), 400
        
        filename = data['filename']
        filepath = current_app.config['UPLOAD_FOLDER'] + '/' + filename
        
        # Check if file exists
        import os
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Initialize Gemini service
        gemini_service = GeminiService()
        
        # Analyze file with timeout handling
        result = gemini_service.analyze_file(filepath)
        
        if not result or 'content' not in result:
            return jsonify({'error': 'No content extracted from image'}), 500
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except TimeoutError:
        traceback.print_exc()
        return jsonify({'error': 'Analysis timed out. Please try again with a smaller or clearer image.'}), 504
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        
        # Return appropriate status codes
        if 'quota' in error_msg.lower() or '429' in error_msg:
            return jsonify({'error': 'API quota exceeded. Please try again later.'}), 429
        elif 'timeout' in error_msg.lower() or 'deadline' in error_msg.lower():
            return jsonify({'error': 'Analysis timed out. Please try again.'}), 504
        else:
            return jsonify({'error': f'Analysis failed: {error_msg}'}), 500

@api_bp.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete uploaded file"""
    try:
        filepath = current_app.config['UPLOAD_FOLDER'] + '/' + filename
        
        if cleanup_file(filepath):
            return jsonify({'success': True, 'message': 'File deleted'}), 200
        else:
            return jsonify({'error': 'File not found or could not be deleted'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Deletion failed: {str(e)}'}), 500
