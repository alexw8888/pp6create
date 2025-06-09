# PP6 Web Service

A production-ready web-based interface for generating ProPresenter 6 and PowerPoint presentations from source materials.

## Status: Production Ready ✅

The web service is fully operational and deployed with complete functionality:
- ✅ **Multi-format Generation**: Creates both PP6 (.pro6plx) and PowerPoint (.pptx) files
- ✅ **Real-time Processing**: Background tasks with live progress updates
- ✅ **File Management**: Upload, edit, create folders, and manage source materials
- ✅ **Session Management**: Isolated user workspaces with template refresh
- ✅ **Direct Downloads**: Dedicated buttons for generated presentations
- ✅ **Production Deployment**: Running on Amazon Linux 2023 with nginx + Redis

## 🌐 Live Demo

**URL**: http://alex.zetakey.com

## Project Structure

```
web_service/
├── app.py                     # Main Flask application
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── api/
│   ├── __init__.py
│   └── routes.py              # REST API endpoints
├── services/
│   ├── __init__.py
│   ├── workspace.py           # User workspace management
│   ├── file_manager.py        # File operations & security
│   └── generator.py           # Background generation tasks
├── templates/
│   └── index.html             # Complete web interface
└── static/                    # CSS, JS, assets
    ├── css/app.css           # Responsive styles
    └── js/app.js             # Full-featured JavaScript app
```

## Quick Start (Development)

### 1. Install Dependencies
```bash
cd web_service
pip install -r requirements.txt
```

### 2. Start Redis (Required for Background Tasks)
```bash
# macOS with Homebrew
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# Amazon Linux 2023
sudo dnf install redis6
sudo systemctl start redis6
```

### 3. Start Celery Worker
```bash
# In a separate terminal
celery -A services.generator worker --loglevel=info
```

### 4. Run the Application
```bash
# Development mode
python app.py

# Production mode with Gunicorn
gunicorn app:app
```

### 5. Access Web Interface
Open http://localhost:5000 in your browser

## 🎯 Key Features

### ✅ Web Interface
- **File Manager**: Full file tree navigation with breadcrumbs
- **Code Editor**: Syntax-highlighted editing with CodeMirror
- **Upload Interface**: Drag & drop with progress indicators
- **Real-time Generation**: Live progress updates via polling
- **Download Management**: Dedicated buttons for PP6 and PowerPoint files
- **Session Control**: "New Session" button to refresh workspace templates

### ✅ Backend Services
- **Multi-format Output**: Generates both .pro6plx and .pptx files
- **Background Processing**: Celery + Redis for non-blocking tasks
- **Workspace Isolation**: Each user gets isolated directory
- **Template Management**: Source materials refreshed from server
- **Security**: Path validation, file type checking, size limits

### ✅ Production Features
- **Amazon Linux 2023**: Full deployment configuration
- **Systemd Services**: Managed Flask app and Celery workers
- **Nginx Proxy**: Reverse proxy with proper headers
- **SELinux Support**: Compatible with security-enhanced Linux
- **Logging**: Comprehensive error tracking and debugging

## 🚀 Usage Workflow

1. **Access**: Navigate to the web interface
2. **Edit Files**: Use the built-in editor to modify text files and JSON configurations
3. **Upload Media**: Drag & drop images and other media files
4. **Organize**: Create folders and organize your source materials
5. **Generate**: Click "🚀 Generate" to create presentations in background
6. **Monitor**: Watch real-time progress updates
7. **Download**: Use dedicated buttons to download PP6 or PowerPoint files
8. **Refresh**: Click "🔄 New Session" to get latest template updates

## API Endpoints

### Workspace Management
- `POST /api/workspace/create` - Create new user workspace
- `GET /api/workspace/{session_id}` - Get workspace info
- `DELETE /api/workspace/{session_id}` - Delete workspace

### File Management
- `GET /api/files/{session_id}` - List files in workspace
- `GET /api/files/{session_id}/{path}` - Get file content
- `PUT /api/files/{session_id}/{path}` - Update file content
- `POST /api/files/{session_id}/upload` - Upload files
- `DELETE /api/files/{session_id}/{path}` - Delete file/directory
- `POST /api/files/{session_id}/mkdir` - Create directory

### Generation
- `POST /api/generate/{session_id}` - Start generation task
- `GET /api/generate/{session_id}/status` - Check status
- `GET /api/generate/{session_id}/download/{file}` - Download results

### Utility
- `GET /api/health` - Service health check
- `POST /api/cleanup` - Cleanup expired workspaces

## Configuration

Environment variables (optional):
```bash
# Workspace settings
WORKSPACE_DIR=/tmp/pp6_workspaces
DEFAULT_SOURCE_MATERIALS=/opt/pp6-web-service/source_materials

# Redis settings
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/pp6-web.log
```

## Security Features

- **Path Traversal Protection**: All file operations validate paths
- **File Type Validation**: Only allowed file types can be uploaded
- **Workspace Isolation**: Each user gets isolated directory
- **Input Sanitization**: All user inputs are validated
- **File Size Limits**: 50MB max upload size
- **Session Management**: Automatic workspace cleanup

## Production Deployment

### Amazon Linux 2023 Setup
See the complete deployment guide in `../web_service_implementation_plan.md` for:
- System dependencies installation
- Systemd service configuration
- Nginx reverse proxy setup
- Redis configuration
- SELinux compatibility
- Firewall/Security Groups

### Key Production Commands
```bash
# Install dependencies
sudo dnf install python3 python3-pip nginx redis6

# Deploy application
sudo cp -r web_service/* /opt/pp6-web-service/

# Start services
sudo systemctl enable --now redis6 nginx pp6-web pp6-worker

# Check status
sudo systemctl status pp6-web pp6-worker redis6 nginx
```

## Testing the Service

### Web Interface
Visit the deployed URL to access the full web interface with:
- File manager and editor
- Upload capabilities
- Generation controls
- Download buttons

### API Testing
```bash
# Health check
curl http://localhost:5000/api/health

# Create workspace
curl -X POST http://localhost:5000/api/workspace/create

# Generate presentation
curl -X POST http://localhost:5000/api/generate/SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"format":"both","output_name":"TestPresentation"}'
```

## Troubleshooting

### Common Issues
1. **Celery worker not starting**: Check Redis connection and service status
2. **File upload fails**: Verify directory permissions and SELinux contexts
3. **Generation fails**: Check source_materials path and file permissions
4. **Download buttons not showing**: Check browser console for API errors

### Log Locations
- **Flask app**: `sudo journalctl -u pp6-web -f`
- **Celery worker**: `sudo journalctl -u pp6-worker -f`
- **Nginx**: `sudo tail -f /var/log/nginx/error.log`
- **Application**: `/opt/pp6-web-service/logs/pp6-web.log`

## Support

For deployment assistance or feature requests, see the comprehensive implementation plan at `../web_service_implementation_plan.md`.