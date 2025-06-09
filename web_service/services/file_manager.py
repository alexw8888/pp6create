"""
File management service for workspace files
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import mimetypes
import logging

logger = logging.getLogger(__name__)

class FileManager:
    """Manages files within user workspaces"""
    
    def __init__(self, allowed_extensions: set):
        self.allowed_extensions = allowed_extensions
        
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in self.allowed_extensions
        
    def list_files(self, workspace_path: str, relative_path: str = '') -> List[Dict[str, Any]]:
        """
        List files in workspace directory
        
        Args:
            workspace_path: Base workspace path
            relative_path: Relative path within workspace
            
        Returns:
            List of file/directory information
        """
        base_path = Path(workspace_path)
        target_path = base_path / relative_path if relative_path else base_path
        
        # Security check - ensure we're within workspace
        try:
            target_path = target_path.resolve()
            base_path = base_path.resolve()
            if not str(target_path).startswith(str(base_path)):
                raise ValueError("Path traversal detected")
        except Exception as e:
            logger.error(f"Path validation failed: {e}")
            raise ValueError("Invalid path")
            
        if not target_path.exists():
            return []
            
        files = []
        try:
            for item in target_path.iterdir():
                # Skip hidden files and metadata
                if item.name.startswith('.'):
                    continue
                    
                file_info = {
                    'name': item.name,
                    'path': str(item.relative_to(base_path)),
                    'is_directory': item.is_dir(),
                    'size': item.stat().st_size if item.is_file() else 0,
                    'modified': item.stat().st_mtime,
                    'editable': self._is_editable(item.name) if item.is_file() else False
                }
                
                if item.is_file():
                    file_info['mime_type'] = mimetypes.guess_type(item.name)[0] or 'application/octet-stream'
                    
                files.append(file_info)
                
            # Sort: directories first, then by name
            files.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            raise
            
        return files
        
    def read_file(self, workspace_path: str, file_path: str) -> Dict[str, Any]:
        """
        Read file content
        
        Args:
            workspace_path: Base workspace path
            file_path: Relative file path
            
        Returns:
            Dictionary with file content and metadata
        """
        base_path = Path(workspace_path)
        target_file = base_path / file_path
        
        # Security check
        try:
            target_file = target_file.resolve()
            base_path = base_path.resolve()
            if not str(target_file).startswith(str(base_path)):
                raise ValueError("Path traversal detected")
        except Exception:
            raise ValueError("Invalid file path")
            
        if not target_file.exists() or not target_file.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        result = {
            'path': file_path,
            'name': target_file.name,
            'size': target_file.stat().st_size,
            'mime_type': mimetypes.guess_type(target_file.name)[0] or 'application/octet-stream',
            'editable': self._is_editable(target_file.name)
        }
        
        # Read text files
        if result['editable']:
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    result['content'] = f.read()
                result['type'] = 'text'
            except UnicodeDecodeError:
                result['error'] = 'File is not valid UTF-8 text'
                result['type'] = 'binary'
        else:
            result['type'] = 'binary'
            
        return result
        
    def write_file(self, workspace_path: str, file_path: str, content: str) -> Dict[str, Any]:
        """
        Write file content
        
        Args:
            workspace_path: Base workspace path
            file_path: Relative file path
            content: File content to write
            
        Returns:
            Dictionary with operation result
        """
        base_path = Path(workspace_path)
        target_file = base_path / file_path
        
        # Security check
        try:
            # Ensure parent directory exists
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            target_file = target_file.resolve()
            base_path = base_path.resolve()
            if not str(target_file).startswith(str(base_path)):
                raise ValueError("Path traversal detected")
        except Exception as e:
            raise ValueError(f"Invalid file path: {e}")
            
        # Check file extension
        if not self.is_allowed_file(target_file.name):
            raise ValueError(f"File type not allowed: {target_file.suffix}")
            
        # Write file
        try:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return {
                'success': True,
                'path': file_path,
                'size': len(content.encode('utf-8'))
            }
        except Exception as e:
            logger.error(f"Failed to write file: {e}")
            raise
            
    def upload_file(self, workspace_path: str, file_path: str, file_data) -> Dict[str, Any]:
        """
        Handle file upload
        
        Args:
            workspace_path: Base workspace path
            file_path: Relative destination path
            file_data: File data (werkzeug FileStorage or similar)
            
        Returns:
            Dictionary with upload result
        """
        base_path = Path(workspace_path)
        target_file = base_path / file_path
        
        # Security check
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            target_file = target_file.resolve()
            base_path = base_path.resolve()
            if not str(target_file).startswith(str(base_path)):
                raise ValueError("Path traversal detected")
        except Exception:
            raise ValueError("Invalid file path")
            
        # Check file extension
        if not self.is_allowed_file(target_file.name):
            raise ValueError(f"File type not allowed: {target_file.suffix}")
            
        # Save file
        try:
            file_data.save(str(target_file))
            
            return {
                'success': True,
                'path': file_path,
                'name': target_file.name,
                'size': target_file.stat().st_size,
                'mime_type': mimetypes.guess_type(target_file.name)[0] or 'application/octet-stream'
            }
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise
            
    def delete_file(self, workspace_path: str, file_path: str) -> Dict[str, Any]:
        """
        Delete file or directory
        
        Args:
            workspace_path: Base workspace path
            file_path: Relative file/directory path
            
        Returns:
            Dictionary with deletion result
        """
        base_path = Path(workspace_path)
        target_path = base_path / file_path
        
        # Security check
        try:
            target_path = target_path.resolve()
            base_path = base_path.resolve()
            if not str(target_path).startswith(str(base_path)):
                raise ValueError("Path traversal detected")
        except Exception:
            raise ValueError("Invalid path")
            
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {file_path}")
            
        # Don't delete the workspace root or source_materials root
        if target_path == base_path or (
            target_path.name == 'source_materials' and 
            target_path.parent == base_path
        ):
            raise ValueError("Cannot delete protected directory")
            
        try:
            if target_path.is_dir():
                import shutil
                shutil.rmtree(target_path)
            else:
                target_path.unlink()
                
            return {
                'success': True,
                'path': file_path,
                'deleted': True
            }
        except Exception as e:
            logger.error(f"Failed to delete: {e}")
            raise
            
    def create_directory(self, workspace_path: str, dir_path: str) -> Dict[str, Any]:
        """
        Create directory
        
        Args:
            workspace_path: Base workspace path
            dir_path: Relative directory path
            
        Returns:
            Dictionary with creation result
        """
        base_path = Path(workspace_path)
        target_dir = base_path / dir_path
        
        # Security check
        try:
            target_dir = target_dir.resolve()
            base_path = base_path.resolve()
            if not str(target_dir).startswith(str(base_path)):
                raise ValueError("Path traversal detected")
        except Exception:
            raise ValueError("Invalid directory path")
            
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            
            return {
                'success': True,
                'path': dir_path,
                'created': True
            }
        except Exception as e:
            logger.error(f"Failed to create directory: {e}")
            raise
            
    def _is_editable(self, filename: str) -> bool:
        """Check if file is editable (text-based)"""
        editable_extensions = {'txt', 'json', 'md', 'yml', 'yaml', 'xml', 'html', 'css', 'js'}
        
        if '.' not in filename:
            return False
            
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in editable_extensions