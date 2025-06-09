"""
Generator service wrapper for presentation generation
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from celery import Celery
import logging
import json
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery('pp6_generator')

class GenerationService:
    """Wrapper service for presentation generation"""
    
    def __init__(self, redis_url: str):
        """
        Initialize generation service
        
        Args:
            redis_url: Redis connection URL for Celery
        """
        celery_app.conf.broker_url = redis_url
        celery_app.conf.result_backend = redis_url
        
    def generate_async(self, workspace_path: str, options: Dict[str, Any]) -> str:
        """
        Queue generation task asynchronously
        
        Args:
            workspace_path: Path to user workspace
            options: Generation options (format, output_name, etc.)
            
        Returns:
            Task ID for tracking
        """
        # Queue the task
        task = generate_presentation_task.delay(workspace_path, options)
        
        logger.info(f"Queued generation task {task.id} for workspace {workspace_path}")
        return task.id
        
    def get_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get generation task status
        
        Args:
            task_id: Celery task ID
            
        Returns:
            Dictionary with task status and metadata
        """
        task = generate_presentation_task.AsyncResult(task_id)
        
        result = {
            'task_id': task_id,
            'state': task.state,
            'ready': task.ready()
        }
        
        if task.state == 'PENDING':
            result['status'] = 'Task is waiting to start'
        elif task.state == 'PROGRESS':
            result['status'] = task.info.get('status', 'Processing...')
            result['current'] = task.info.get('current', 0)
            result['total'] = task.info.get('total', 100)
        elif task.state == 'SUCCESS':
            result['status'] = 'Generation completed'
            result['result'] = task.result
        elif task.state == 'FAILURE':
            result['status'] = 'Generation failed'
            result['error'] = str(task.info)
            
        return result
        
    def get_results(self, workspace_path: str, task_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get list of generated files
        
        Args:
            workspace_path: Path to user workspace
            task_result: Result from successful task
            
        Returns:
            List of generated file information
        """
        logger.info(f"Getting results for task_result: {task_result}")
        
        if not task_result or 'files' not in task_result:
            logger.warning("No task result or files key missing")
            return []
            
        files = []
        workspace = Path(workspace_path)
        
        for file_path in task_result['files']:
            full_path = workspace / file_path
            logger.info(f"Checking file: {file_path} -> {full_path}")
            if full_path.exists():
                file_info = {
                    'path': file_path,
                    'name': full_path.name,
                    'size': full_path.stat().st_size,
                    'created': full_path.stat().st_mtime
                }
                files.append(file_info)
                logger.info(f"Added file info: {file_info}")
            else:
                logger.warning(f"File does not exist: {full_path}")
                
        logger.info(f"Returning {len(files)} files")
        return files
        
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task
        
        Args:
            task_id: Celery task ID
            
        Returns:
            True if cancelled successfully
        """
        try:
            celery_app.control.revoke(task_id, terminate=True)
            logger.info(f"Cancelled task {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False


@celery_app.task(bind=True)
def generate_presentation_task(self, workspace_path: str, options: Dict[str, Any]):
    """
    Background task for presentation generation
    
    Args:
        workspace_path: Path to user workspace
        options: Generation options
        
    Returns:
        Dictionary with generation results
    """
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Starting generation...', 'current': 0, 'total': 100}
        )
        
        # Import here to avoid circular imports
        # Add the parent directory to sys.path to find generate_presentation
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        from generate_presentation import UnifiedPresentationGenerator
        
        # Prepare source directory
        source_dir = Path(workspace_path) / 'source_materials'
        if not source_dir.exists():
            raise ValueError("source_materials directory not found in workspace")
            
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Initializing generator...', 'current': 10, 'total': 100}
        )
        
        # Create generator instance
        generator = UnifiedPresentationGenerator()
        
        # Prepare generation options
        gen_options = {
            'source_dir': str(source_dir),
            'output_format': options.get('format', 'both'),
            'output_path': options.get('output_name'),
            'width': options.get('width', 1024),
            'height': options.get('height', 768),
            'font_size': options.get('font_size'),
            'lines_per_slide': options.get('lines_per_slide'),
            'title': options.get('title'),
            'process_all_subdirs': True  # Always process subdirs for web
        }
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Generating presentation...', 'current': 30, 'total': 100}
        )
        
        # Change to workspace directory for output
        original_cwd = os.getcwd()
        os.chdir(workspace_path)
        
        try:
            # Generate presentations
            generated_files = generator.generate(**gen_options)
        finally:
            # Always restore original directory
            os.chdir(original_cwd)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Finalizing...', 'current': 90, 'total': 100}
        )
        
        # Prepare result
        result = {
            'success': True,
            'files': [],
            'format': options.get('format', 'both'),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Get relative paths for generated files
        workspace = Path(workspace_path)
        logger.info(f"Generated files from generator: {generated_files}")
        logger.info(f"Workspace path: {workspace}")
        
        # If no files returned from generator, scan workspace for common output files
        if not generated_files:
            logger.info("No files returned from generator, scanning workspace")
            # Look for common output files in workspace
            for pattern in ['*.pro6plx', '*.pptx']:
                for file_path in workspace.glob(pattern):
                    if file_path.exists():
                        relative_path = file_path.relative_to(workspace)
                        result['files'].append(str(relative_path))
                        logger.info(f"Found output file: {relative_path}")
        else:
            # Process returned file paths
            for file_path in generated_files:
                file_obj = Path(file_path)
                
                # Check if file exists in workspace
                if file_obj.is_absolute():
                    full_path = file_obj
                else:
                    # Relative path - check in workspace
                    full_path = workspace / file_obj
                
                logger.info(f"Checking file path: {file_path} -> {full_path}")
                
                if full_path.exists():
                    try:
                        if file_obj.is_absolute():
                            relative_path = full_path.relative_to(workspace)
                        else:
                            # Already relative
                            relative_path = file_obj
                        result['files'].append(str(relative_path))
                        logger.info(f"Added file to result: {relative_path}")
                    except ValueError:
                        # File is outside workspace, use filename only
                        result['files'].append(full_path.name)
                        logger.info(f"Added external file: {full_path.name}")
                else:
                    logger.warning(f"Generated file does not exist: {full_path}")
                    
        # Log generation details
        logger.info(f"Generated {len(result['files'])} files in workspace {workspace_path}")
        
        return result
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise  # Re-raise to mark task as failed