"""
Workspace management service for user isolation
"""
import os
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class WorkspaceManager:
    """Manages isolated user workspaces"""
    
    def __init__(self, base_dir: str, default_source_materials: str, timeout: timedelta):
        self.base_dir = Path(base_dir)
        self.default_source_materials = Path(default_source_materials)
        self.timeout = timeout
        
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def create_workspace(self, session_id: str = None) -> tuple[str, str]:
        """
        Create isolated workspace with default source_materials
        
        Args:
            session_id: Optional session ID, generates UUID if not provided
            
        Returns:
            Tuple of (session_id, workspace_path)
        """
        if not session_id:
            session_id = str(uuid.uuid4())
            
        workspace_path = self.base_dir / session_id
        
        try:
            # Create workspace directory
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            # Copy default source_materials if available
            if self.default_source_materials.exists():
                source_materials_dest = workspace_path / 'source_materials'
                shutil.copytree(self.default_source_materials, source_materials_dest)
                logger.info(f"Created workspace for session {session_id} with default materials")
            else:
                # Create empty source_materials directory
                (workspace_path / 'source_materials').mkdir(exist_ok=True)
                logger.warning(f"Default source materials not found at {self.default_source_materials}")
                
            # Create metadata file
            metadata_file = workspace_path / '.metadata'
            metadata = {
                'session_id': session_id,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + self.timeout).isoformat()
            }
            
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)
                
            return session_id, str(workspace_path)
            
        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            # Clean up on failure
            if workspace_path.exists():
                shutil.rmtree(workspace_path)
            raise
            
    def get_workspace_path(self, session_id: str) -> str:
        """
        Get path to user's workspace
        
        Args:
            session_id: Session identifier
            
        Returns:
            Workspace path
            
        Raises:
            ValueError: If workspace doesn't exist
        """
        workspace_path = self.base_dir / session_id
        
        if not workspace_path.exists():
            raise ValueError(f"Workspace {session_id} not found")
            
        return str(workspace_path)
        
    def cleanup_workspace(self, session_id: str):
        """
        Clean up workspace after timeout or completion
        
        Args:
            session_id: Session identifier
        """
        workspace_path = self.base_dir / session_id
        
        if workspace_path.exists():
            try:
                shutil.rmtree(workspace_path)
                logger.info(f"Cleaned up workspace {session_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup workspace {session_id}: {e}")
                
    def cleanup_expired_workspaces(self):
        """Clean up all expired workspaces based on timeout"""
        current_time = datetime.utcnow()
        cleaned_count = 0
        
        for workspace_dir in self.base_dir.iterdir():
            if not workspace_dir.is_dir():
                continue
                
            metadata_file = workspace_dir / '.metadata'
            
            # If no metadata, check directory modification time
            if not metadata_file.exists():
                dir_age = current_time - datetime.fromtimestamp(workspace_dir.stat().st_mtime)
                if dir_age > self.timeout:
                    self.cleanup_workspace(workspace_dir.name)
                    cleaned_count += 1
                continue
                
            # Check metadata for expiration
            try:
                import json
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    
                expires_at = datetime.fromisoformat(metadata.get('expires_at', ''))
                if current_time > expires_at:
                    self.cleanup_workspace(workspace_dir.name)
                    cleaned_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to read metadata for {workspace_dir.name}: {e}")
                # Clean up corrupted workspace
                self.cleanup_workspace(workspace_dir.name)
                cleaned_count += 1
                
        logger.info(f"Cleaned up {cleaned_count} expired workspaces")
        return cleaned_count
        
    def get_workspace_info(self, session_id: str) -> dict:
        """
        Get workspace information including metadata
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with workspace info
        """
        workspace_path = self.base_dir / session_id
        
        if not workspace_path.exists():
            raise ValueError(f"Workspace {session_id} not found")
            
        info = {
            'session_id': session_id,
            'path': str(workspace_path),
            'exists': True
        }
        
        # Read metadata if available
        metadata_file = workspace_path / '.metadata'
        if metadata_file.exists():
            try:
                import json
                with open(metadata_file) as f:
                    metadata = json.load(f)
                info.update(metadata)
            except Exception:
                pass
                
        # Get workspace size
        total_size = 0
        file_count = 0
        for path in workspace_path.rglob('*'):
            if path.is_file():
                total_size += path.stat().st_size
                file_count += 1
                
        info['size_bytes'] = total_size
        info['file_count'] = file_count
        
        return info