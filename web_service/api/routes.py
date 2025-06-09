"""
API routes for PP6 Web Service
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.exceptions import BadRequest, NotFound
from pathlib import Path
import logging

from services.workspace import WorkspaceManager
from services.file_manager import FileManager
from services.generator import GenerationService

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize services (will be properly initialized in app context)
workspace_manager = None
file_manager = None
generator_service = None


def init_services(app):
    """Initialize services with app configuration"""
    global workspace_manager, file_manager, generator_service
    
    workspace_manager = WorkspaceManager(
        base_dir=app.config['WORKSPACE_BASE_DIR'],
        default_source_materials=app.config['DEFAULT_SOURCE_MATERIALS'],
        timeout=app.config['WORKSPACE_TIMEOUT']
    )
    
    file_manager = FileManager(
        allowed_extensions=app.config['ALLOWED_EXTENSIONS']
    )
    
    generator_service = GenerationService(
        redis_url=app.config['CELERY_BROKER_URL']
    )


# Workspace management routes
@api_bp.route('/workspace/create', methods=['POST'])
def create_workspace():
    """Create new user workspace"""
    try:
        session_id, workspace_path = workspace_manager.create_workspace()
        
        return jsonify({
            'session_id': session_id,
            'workspace_path': workspace_path,
            'success': True
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create workspace: {e}")
        return jsonify({
            'error': 'Failed to create workspace',
            'message': str(e)
        }), 500


@api_bp.route('/workspace/<session_id>', methods=['GET'])
def get_workspace(session_id):
    """Get workspace information"""
    try:
        info = workspace_manager.get_workspace_info(session_id)
        return jsonify(info)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to get workspace info: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/workspace/<session_id>', methods=['DELETE'])
def delete_workspace(session_id):
    """Delete workspace"""
    try:
        workspace_manager.cleanup_workspace(session_id)
        return jsonify({'success': True, 'deleted': True})
        
    except Exception as e:
        logger.error(f"Failed to delete workspace: {e}")
        return jsonify({'error': 'Failed to delete workspace'}), 500


# File management routes
@api_bp.route('/files/<session_id>', methods=['GET'])
def list_files(session_id):
    """List files in workspace"""
    try:
        workspace_path = workspace_manager.get_workspace_path(session_id)
        path = request.args.get('path', '')
        
        files = file_manager.list_files(workspace_path, path)
        return jsonify({
            'files': files,
            'path': path,
            'success': True
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        return jsonify({'error': 'Failed to list files'}), 500


@api_bp.route('/files/<session_id>/<path:file_path>', methods=['GET'])
def get_file(session_id, file_path):
    """Get file content"""
    try:
        workspace_path = workspace_manager.get_workspace_path(session_id)
        file_data = file_manager.read_file(workspace_path, file_path)
        
        return jsonify(file_data)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        return jsonify({'error': 'Failed to read file'}), 500


@api_bp.route('/files/<session_id>/<path:file_path>', methods=['PUT'])
def update_file(session_id, file_path):
    """Update file content"""
    try:
        workspace_path = workspace_manager.get_workspace_path(session_id)
        
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing content in request'}), 400
            
        result = file_manager.write_file(
            workspace_path, 
            file_path, 
            data['content']
        )
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to update file: {e}")
        return jsonify({'error': 'Failed to update file'}), 500


@api_bp.route('/files/<session_id>/upload', methods=['POST'])
def upload_files(session_id):
    """Upload files to workspace"""
    try:
        workspace_path = workspace_manager.get_workspace_path(session_id)
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        uploaded_files = []
        files = request.files.getlist('file')
        target_dir = request.form.get('path', 'source_materials')
        
        for file in files:
            if file and file.filename:
                # Construct target path
                file_path = Path(target_dir) / file.filename
                
                result = file_manager.upload_file(
                    workspace_path,
                    str(file_path),
                    file
                )
                uploaded_files.append(result)
                
        return jsonify({
            'success': True,
            'files': uploaded_files,
            'count': len(uploaded_files)
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to upload files: {e}")
        return jsonify({'error': 'Failed to upload files'}), 500


@api_bp.route('/files/<session_id>/<path:file_path>', methods=['DELETE'])
def delete_file(session_id, file_path):
    """Delete file or directory"""
    try:
        workspace_path = workspace_manager.get_workspace_path(session_id)
        result = file_manager.delete_file(workspace_path, file_path)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        return jsonify({'error': 'Failed to delete file'}), 500


@api_bp.route('/files/<session_id>/mkdir', methods=['POST'])
def create_directory(session_id):
    """Create directory"""
    try:
        workspace_path = workspace_manager.get_workspace_path(session_id)
        
        data = request.get_json()
        if not data or 'path' not in data:
            return jsonify({'error': 'Missing path in request'}), 400
            
        result = file_manager.create_directory(
            workspace_path,
            data['path']
        )
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to create directory: {e}")
        return jsonify({'error': 'Failed to create directory'}), 500


# Generation routes
@api_bp.route('/generate/<session_id>', methods=['POST'])
def generate_presentation(session_id):
    """Start presentation generation"""
    try:
        workspace_path = workspace_manager.get_workspace_path(session_id)
        
        # Get generation options
        data = request.get_json() or {}
        
        # Queue generation task
        task_id = generator_service.generate_async(workspace_path, data)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Generation started'
        }), 202
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to start generation: {e}")
        return jsonify({'error': 'Failed to start generation'}), 500


@api_bp.route('/generate/<session_id>/status', methods=['GET'])
def get_generation_status(session_id):
    """Check generation status"""
    try:
        task_id = request.args.get('task_id')
        if not task_id:
            return jsonify({'error': 'Missing task_id parameter'}), 400
            
        status = generator_service.get_status(task_id)
        
        # If successful, include file list
        if status['state'] == 'SUCCESS' and status.get('result'):
            workspace_path = workspace_manager.get_workspace_path(session_id)
            status['files'] = generator_service.get_results(
                workspace_path, 
                status['result']
            )
            
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Failed to get generation status: {e}")
        return jsonify({'error': 'Failed to get status'}), 500


@api_bp.route('/generate/<session_id>/download/<path:file_path>', methods=['GET'])
def download_generated_file(session_id, file_path):
    """Download generated file"""
    try:
        workspace_path = workspace_manager.get_workspace_path(session_id)
        full_path = Path(workspace_path) / file_path
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
            
        # Security check
        workspace_path = Path(workspace_path).resolve()
        full_path = full_path.resolve()
        if not str(full_path).startswith(str(workspace_path)):
            return jsonify({'error': 'Invalid file path'}), 403
            
        return send_file(
            str(full_path),
            as_attachment=True,
            download_name=full_path.name
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to download file: {e}")
        return jsonify({'error': 'Failed to download file'}), 500


# Utility routes
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'PP6 Web Service'
    })


@api_bp.route('/cleanup', methods=['POST'])
def cleanup_expired():
    """Trigger cleanup of expired workspaces (admin only)"""
    try:
        # In production, add authentication check here
        count = workspace_manager.cleanup_expired_workspaces()
        
        return jsonify({
            'success': True,
            'cleaned': count,
            'message': f'Cleaned up {count} expired workspaces'
        })
        
    except Exception as e:
        logger.error(f"Failed to cleanup workspaces: {e}")
        return jsonify({'error': 'Cleanup failed'}), 500