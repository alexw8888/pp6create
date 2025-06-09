# Web Service Implementation Plan
## ProPresenter 6 & PowerPoint Generator Web Application

### Overview
Transform the existing `generate_presentation.py` CLI tool into a web-based service with a user-friendly interface for generating ProPresenter 6 playlists and PowerPoint presentations. This implementation is optimized for deployment on Amazon Linux 2023 AMI 2023.7.20250527.1 x86_64 HVM kernel-6.1.

## Architecture

### Backend Service (Amazon Linux 2023)
- **Framework**: Flask or FastAPI (Python)
- **Core**: Existing `generate_presentation.py` as backend service
- **File Management**: User workspace isolation with temporary directories
- **Queue System**: Celery + Redis for background generation tasks
- **Storage**: Local filesystem with user session management

### Frontend Web UI
- **Framework**: Vue.js, React, or vanilla HTML/JS
- **Features**: File management, text/JSON editing, upload interface
- **Real-time**: WebSocket for generation progress updates

## Implementation Plan

### Phase 1: Backend API Service

#### 1.1 Create Flask/FastAPI Application
```
web_service/
├── app.py                 # Main Flask application
├── api/
│   ├── __init__.py
│   ├── routes.py          # API endpoints
│   ├── models.py          # Data models
│   └── utils.py           # Helper functions
├── services/
│   ├── __init__.py
│   ├── workspace.py       # User workspace management
│   ├── generator.py       # Wrapper for generate_presentation.py
│   └── file_manager.py    # File operations
├── templates/             # HTML templates
├── static/               # CSS, JS, assets
├── requirements.txt      # Python dependencies
└── config.py            # Configuration
```

#### 1.2 API Endpoints Design
```python
# User workspace management
POST   /api/workspace/create           # Create new user workspace
GET    /api/workspace/{session_id}     # Get workspace info
DELETE /api/workspace/{session_id}     # Clean up workspace

# File management
GET    /api/files/{session_id}         # List files in workspace
POST   /api/files/{session_id}/upload  # Upload files
GET    /api/files/{session_id}/{path}  # Get file content
PUT    /api/files/{session_id}/{path}  # Update file content
DELETE /api/files/{session_id}/{path}  # Delete file

# Generation
POST   /api/generate/{session_id}      # Start generation task
GET    /api/generate/{session_id}/status # Check generation status
GET    /api/generate/{session_id}/download/{file} # Download result
```

#### 1.3 User Workspace Management
```python
class WorkspaceManager:
    def create_workspace(self, session_id: str) -> str:
        """Create isolated workspace with default source_materials"""
        workspace_path = f"/tmp/pp6_workspaces/{session_id}"
        # Copy default source_materials as template
        # Return workspace path
    
    def cleanup_workspace(self, session_id: str):
        """Clean up workspace after timeout or completion"""
        
    def get_workspace_path(self, session_id: str) -> str:
        """Get path to user's workspace"""
```

#### 1.4 Generation Service
```python
class GenerationService:
    def generate_async(self, workspace_path: str, options: dict) -> str:
        """Queue generation task and return task_id"""
        
    def get_status(self, task_id: str) -> dict:
        """Get generation status and progress"""
        
    def get_results(self, task_id: str) -> list:
        """Get list of generated files"""
```

### Phase 2: Frontend Web Interface

#### 2.1 Main Dashboard
- **Workspace Overview**: Show current source_materials structure
- **Session Management**: New Session button to refresh workspace with latest template
- **Quick Actions**: Generate PP6, Generate PowerPoint, Generate Both
- **Settings Panel**: Environment variables (.env editor)
- **Progress Indicator**: Real-time generation status

#### 2.2 File Manager Interface
```html
<!-- File tree view -->
<div class="file-tree">
  <div class="folder" data-path="source_materials">
    <div class="folder" data-path="1-worship">
      <div class="file" data-path="1.jpg">1.jpg</div>
      <div class="file editable" data-path="1.json">1.json</div>
    </div>
    <div class="folder" data-path="2-song1">
      <div class="file editable" data-path="song1.txt">song1.txt</div>
      <div class="file" data-path="bg2.png">bg2.png</div>
    </div>
  </div>
</div>

<!-- File editor panel -->
<div class="editor-panel">
  <div class="editor-tabs"></div>
  <div class="editor-content">
    <!-- CodeMirror or Monaco Editor for text/JSON -->
  </div>
</div>
```

#### 2.3 Upload Interface
- **Drag & Drop**: Upload files to specific directories
- **Batch Upload**: Multiple file selection
- **Progress Indicators**: Upload progress bars
- **File Validation**: Check file types and sizes

#### 2.4 Session Management & Generation Interface
```html
<div class="control-panel">
  <div class="session-controls">
    <button class="new-session-btn" onclick="app.createNewSession()">
      🔄 New Session (Refresh Template)
    </button>
    <span class="session-info">Session: <span id="session-id">Loading...</span></span>
  </div>
  
  <div class="generation-panel">
    <div class="format-selection">
      <input type="radio" name="format" value="both" checked> Both Formats
      <input type="radio" name="format" value="pro6"> ProPresenter 6 Only
      <input type="radio" name="format" value="pptx"> PowerPoint Only
    </div>
    
    <div class="options">
      <input type="text" name="output_name" placeholder="Output name">
      <input type="number" name="width" value="1024" placeholder="Width">
      <input type="number" name="height" value="768" placeholder="Height">
    </div>
    
    <button class="generate-btn">Generate Presentation</button>
    
    <div class="progress-container" style="display: none;">
      <div class="progress-bar"></div>
      <div class="progress-text">Processing...</div>
    </div>
  </div>
</div>
```

### Phase 3: Advanced Features

#### 3.1 Environment Configuration Editor
- **Visual .env Editor**: Form-based interface for all environment variables
- **Live Preview**: Show how changes affect output
- **Presets**: Save/load configuration presets
- **Validation**: Check value formats and ranges

#### 3.2 Template System
- **Default Templates**: Multiple source_materials templates
- **Template Gallery**: Pre-made worship service templates
- **Custom Templates**: Save user workspaces as templates
- **Import/Export**: Share templates between users

#### 3.3 Real-time Collaboration
- **Session Sharing**: Share workspace URLs with team members
- **Live Editing**: Multiple users editing same workspace
- **Change History**: Track file modifications
- **Conflict Resolution**: Handle simultaneous edits

## Technical Implementation Details

### Backend Service Setup

#### Dependencies (requirements.txt)
```txt
flask==2.3.3
flask-cors==4.0.0
celery==5.3.1
redis==4.6.0
python-dotenv==1.0.0
Pillow==10.0.0
python-pptx==0.6.21
lxml==4.9.3
gunicorn==21.2.0
```

#### Flask Application Structure
```python
# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from services.workspace import WorkspaceManager
from services.generator import GenerationService
import uuid

app = Flask(__name__)
CORS(app)

workspace_manager = WorkspaceManager()
generator_service = GenerationService()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/workspace/create', methods=['POST'])
def create_workspace():
    session_id = str(uuid.uuid4())
    workspace_path = workspace_manager.create_workspace(session_id)
    return jsonify({
        'session_id': session_id,
        'workspace_path': workspace_path
    })

# Additional routes...
```

#### Background Task Processing
```python
# services/generator.py
from celery import Celery
from generate_presentation import UnifiedPresentationGenerator
import os

celery = Celery('pp6_generator', broker='redis://localhost:6379')

@celery.task(bind=True)
def generate_presentation_task(self, workspace_path, options):
    """Background task for presentation generation"""
    try:
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Starting generation...'})
        
        # Run generation
        generator = UnifiedPresentationGenerator()
        results = generator.generate(
            source_dir=workspace_path,
            output_format=options.get('format', 'both'),
            output_path=options.get('output_name'),
            **options
        )
        
        return {
            'status': 'SUCCESS',
            'results': results
        }
    except Exception as e:
        return {
            'status': 'FAILURE',
            'error': str(e)
        }
```

### Frontend Implementation

#### Main JavaScript Application
```javascript
// static/js/app.js
class PP6WebApp {
    constructor() {
        this.sessionId = null;
        this.workspacePath = null;
        this.socket = null;
        
        this.initializeWorkspace();
        this.setupEventHandlers();
    }
    
    async initializeWorkspace() {
        const response = await fetch('/api/workspace/create', {
            method: 'POST'
        });
        const data = await response.json();
        
        this.sessionId = data.session_id;
        this.workspacePath = data.workspace_path;
        
        this.loadFileTree();
    }
    
    async loadFileTree() {
        const response = await fetch(`/api/files/${this.sessionId}`);
        const files = await response.json();
        
        this.renderFileTree(files);
    }
    
    async createNewSession() {
        // Clean up current workspace
        if (this.sessionId) {
            await fetch(`/api/workspace/${this.sessionId}`, {
                method: 'DELETE'
            });
        }
        
        // Create new workspace
        await this.initializeWorkspace();
        
        // Update UI
        this.clearEditor();
        this.showNotification('New session created with latest template');
    }
    
    async generatePresentation(options) {
        const response = await fetch(`/api/generate/${this.sessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(options)
        });
        
        const data = await response.json();
        this.pollGenerationStatus(data.task_id);
    }
    
    pollGenerationStatus(taskId) {
        const interval = setInterval(async () => {
            const response = await fetch(`/api/generate/${this.sessionId}/status?task_id=${taskId}`);
            const status = await response.json();
            
            this.updateProgress(status);
            
            if (status.state === 'SUCCESS' || status.state === 'FAILURE') {
                clearInterval(interval);
                this.handleGenerationComplete(status);
            }
        }, 1000);
    }
    
    setupEventHandlers() {
        // Add event listeners for UI elements
        document.addEventListener('DOMContentLoaded', () => {
            // Update session ID display
            this.updateSessionDisplay();
        });
    }
    
    updateSessionDisplay() {
        const sessionElement = document.getElementById('session-id');
        if (sessionElement && this.sessionId) {
            sessionElement.textContent = this.sessionId.substring(0, 8) + '...';
        }
    }
    
    clearEditor() {
        // Clear any open file editors
        console.log('Editor cleared for new session');
    }
    
    showNotification(message) {
        // Simple notification - could be enhanced with a proper notification system
        alert(message);
    }
}

// Initialize app
const app = new PP6WebApp();
```

#### File Editor Integration
```html
<!-- CodeMirror for text/JSON editing -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/javascript/javascript.min.js"></script>

<script>
class FileEditor {
    constructor(container) {
        this.editor = CodeMirror(container, {
            lineNumbers: true,
            mode: 'javascript',
            theme: 'default'
        });
    }
    
    async loadFile(filePath) {
        const response = await fetch(`/api/files/${app.sessionId}/${filePath}`);
        const content = await response.text();
        
        this.editor.setValue(content);
        this.currentFile = filePath;
    }
    
    async saveFile() {
        const content = this.editor.getValue();
        
        await fetch(`/api/files/${app.sessionId}/${this.currentFile}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'text/plain'
            },
            body: content
        });
    }
}
</script>
```

## Deployment Guide (Amazon Linux 2023)

This guide is specifically tailored for Amazon Linux 2023 AMI 2023.7.20250527.1 x86_64 HVM kernel-6.1, commonly used on AWS EC2 instances.

### Server Setup (Amazon Linux 2023)

#### 1. Install Dependencies
```bash
# Update system
sudo dnf update -y

# Install Python and dependencies
# Note: Amazon Linux 2023 includes these packages without needing EPEL
sudo dnf install python3 python3-pip python3-devel nginx redis6 -y

# Install system packages for image processing
sudo dnf install libjpeg-devel zlib-devel freetype-devel -y

# Enable and start Redis service (service name is redis6 in Amazon Linux 2023)
sudo systemctl enable redis6
sudo systemctl start redis6
```

#### 2. Application Setup
```bash
# Create app directory
sudo mkdir -p /opt/pp6-web-service
cd /opt/pp6-web-service

# Copy application files
sudo cp -r /home/ec2-user/pp6create/web_service/* .

# Create virtual environment
sudo python3 -m venv venv
sudo ./venv/bin/pip install -r requirements.txt

# Copy core generator files
sudo cp /path/to/generate_presentation.py .
sudo cp /path/to/generate_pp6_doc.py .
sudo cp /path/to/generate_pp6_playlist.py .
sudo cp /path/to/pptx_generator.py .
# ... other required files

# Create workspace directory
sudo mkdir -p /tmp/pp6_workspaces
sudo chown nginx:nginx /tmp/pp6_workspaces

# Configure SELinux context for web service (Amazon Linux 2023 specific)
sudo semanage fcontext -a -t httpd_sys_content_t "/opt/pp6-web-service(/.*)?"
sudo restorecon -Rv /opt/pp6-web-service
sudo setsebool -P httpd_can_network_connect 1

# Allow nginx to write to workspace directory
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/tmp/pp6_workspaces(/.*)?"
sudo restorecon -Rv /tmp/pp6_workspaces
```

#### 3. Service Configuration

Create the systemd service file for the web application:
```bash
sudo nano /etc/systemd/system/pp6-web.service
```

Add the following content to the file:
```ini
[Unit]
Description=PP6 Web Service
After=network.target

[Service]
Type=notify
User=nginx
Group=nginx
WorkingDirectory=/opt/pp6-web-service
Environment=PATH=/opt/pp6-web-service/venv/bin
ExecStart=/opt/pp6-web-service/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

Create the systemd service file for the Celery worker:
```bash
sudo nano /etc/systemd/system/pp6-worker.service
```

Add the following content to the file:
```ini
[Unit]
Description=PP6 Celery Worker
After=network.target redis6.service

[Service]
Type=simple
User=nginx
Group=nginx
WorkingDirectory=/opt/pp6-web-service
Environment=PATH=/opt/pp6-web-service/venv/bin
Environment=CELERY_BROKER_URL=redis://localhost:6379/0
Environment=CELERY_RESULT_BACKEND=redis://localhost:6379/0
ExecStart=/opt/pp6-web-service/venv/bin/celery -A services.generator worker --loglevel=info --broker=redis://localhost:6379/0
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4. Nginx Configuration

Create the sites-available and sites-enabled directories (Amazon Linux 2023 doesn't create these by default):
```bash
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled
```

Edit the main nginx configuration to include sites-enabled:
```bash
sudo nano /etc/nginx/nginx.conf
```

Add this line in the `http` block (before the closing brace):
```nginx
include /etc/nginx/sites-enabled/*;
```

Create the site configuration file:
```bash
sudo nano /etc/nginx/sites-available/pp6-web
```

Add the following content:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /api/files/upload {
        proxy_pass http://127.0.0.1:5000;
        proxy_request_buffering off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /opt/pp6-web-service/static;
        expires 1d;
    }
}
```

#### 5. Configure AWS Security Groups
Configure your EC2 Security Group to allow web traffic:
- **Port 80 (HTTP)** - for web access
- **Port 443 (HTTPS)** - for SSL (optional)
- **Port 22 (SSH)** - for administration

In AWS Console: EC2 → Security Groups → Select your instance's security group → Add inbound rules

#### 6. Start Services
```bash
# Enable and start services
sudo systemctl enable redis6
sudo systemctl enable pp6-web
sudo systemctl enable pp6-worker
sudo systemctl enable nginx

sudo systemctl start redis6
sudo systemctl start pp6-web
sudo systemctl start pp6-worker
sudo systemctl restart nginx

# Enable nginx site
sudo ln -s /etc/nginx/sites-available/pp6-web /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

#### 7. Test the Installation
```bash
# Check service status
sudo systemctl status redis6
sudo systemctl status nginx
sudo systemctl status pp6-web
sudo systemctl status pp6-worker

# Test Redis connection
redis-cli ping

# Test nginx configuration
sudo nginx -t

# Check if services are listening on correct ports
sudo netstat -tlnp | grep :80    # nginx
sudo netstat -tlnp | grep :5000  # Flask app
sudo netstat -tlnp | grep :6379  # Redis

# Test web service locally
curl http://localhost
curl http://localhost/api/workspace/create -X POST

# Test from your browser (replace with your EC2 public IP)
# http://YOUR-EC2-PUBLIC-IP
```

#### 8. View Logs (if something isn't working)
```bash
# Check service logs
sudo journalctl -u pp6-web -f
sudo journalctl -u pp6-worker -f
sudo journalctl -u nginx -f
sudo journalctl -u redis6 -f

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check application logs (if configured)
sudo tail -f /opt/pp6-web-service/logs/pp6-web.log
```

## Security Considerations (Amazon Linux 2023)

### SELinux Configuration
- **Policy Management**: Amazon Linux 2023 has SELinux enabled by default in enforcing mode
- **Context Labels**: Ensure proper SELinux contexts for web files and directories
- **Boolean Settings**: Configure necessary SELinux booleans for web service functionality
- **Troubleshooting**: Use `sealert` and `audit2allow` for debugging SELinux denials

### File Upload Security
- **File Type Validation**: Only allow specific file types (.txt, .json, .jpg, .png, etc.)
- **File Size Limits**: Prevent large file uploads (max 50MB per file)
- **Path Traversal Protection**: Sanitize file paths and names
- **Virus Scanning**: Consider ClamAV integration for uploaded files

### User Isolation
- **Workspace Isolation**: Each user gets isolated temporary directory
- **Resource Limits**: Limit CPU/memory usage per generation task
- **Session Management**: Implement session timeouts and cleanup
- **Rate Limiting**: Prevent abuse with request rate limiting

### Network Security
- **HTTPS**: Use SSL certificates (Let's Encrypt)
- **Firewall**: Configure iptables/firewalld to limit access
- **SELinux**: Configure SELinux policies for web service (Amazon Linux 2023 has SELinux enabled by default)
- **CORS**: Proper CORS configuration for API endpoints
- **Input Validation**: Sanitize all user inputs
- **EC2 Security Groups**: Configure appropriate inbound/outbound rules if running on EC2

## Monitoring and Maintenance

### Logging
```python
# Configure logging in app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/pp6-web.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### Health Checks
- **Service Status**: Monitor Flask app, Celery workers, Redis
- **Disk Space**: Monitor workspace directory usage
- **Memory Usage**: Track memory consumption during generation
- **Generation Success Rate**: Monitor task failure rates
- **EC2 CloudWatch**: Integrate with AWS CloudWatch for monitoring (if on EC2)
- **SELinux Denials**: Monitor audit logs for SELinux issues: `sudo ausearch -m avc -ts recent`

### Cleanup Tasks
```bash
# Cron job for workspace cleanup
# /etc/cron.d/pp6-cleanup
0 2 * * * nginx find /tmp/pp6_workspaces -type d -mtime +1 -exec rm -rf {} \;
```

## EC2-Specific Considerations

### Instance Recommendations
- **Instance Type**: t3.medium or larger for production workloads
- **Storage**: Use EBS GP3 volumes for better performance
- **Auto Scaling**: Configure Auto Scaling Groups for high availability
- **Load Balancer**: Use Application Load Balancer (ALB) for HTTPS termination

### AWS Integration
- **S3 Storage**: Consider storing generated files in S3 instead of local disk
- **CloudFront**: Use CloudFront CDN for serving static assets
- **RDS**: Use Amazon RDS for PostgreSQL if migrating from filesystem
- **ElastiCache**: Use ElastiCache for Redis instead of local Redis
- **Systems Manager**: Use Parameter Store for environment variables
- **IAM Roles**: Use EC2 instance profiles instead of hardcoded credentials

## Future Enhancements

### Performance Optimizations
- **Caching**: Cache generated presentations for identical inputs
- **CDN Integration**: Serve static assets from CDN
- **Database**: Move from filesystem to PostgreSQL for metadata
- **Load Balancing**: Multiple app servers behind load balancer

### Feature Additions
- **User Authentication**: Login system with user accounts
- **Presentation History**: Save and recall previous generations
- **API Keys**: Allow programmatic access via API
- **Webhooks**: Notify external systems when generation completes
- **Preview Mode**: Generate preview images before full generation
- **Batch Processing**: Process multiple workspaces simultaneously

### Mobile Support
- **Responsive Design**: Mobile-friendly interface
- **Progressive Web App**: Offline capability
- **Touch Gestures**: Mobile file management
- **Photo Upload**: Direct camera integration

## Implementation Status

### ✅ Completed Features (Phase 1 & 2)

**Backend Services**:
- ✅ Flask application with complete API endpoints
- ✅ Workspace management with session isolation 
- ✅ File upload, edit, and management system
- ✅ Celery + Redis background task processing
- ✅ Complete presentation generation (PP6 + PowerPoint)
- ✅ SELinux and Amazon Linux 2023 compatibility

**Frontend Interface**:
- ✅ Responsive web UI with file tree navigation
- ✅ CodeMirror-based text/JSON editor with syntax highlighting
- ✅ Drag & drop file upload interface
- ✅ Real-time generation progress tracking
- ✅ **New Session functionality** - refresh workspace with latest template
- ✅ **Download buttons** - direct download of generated PP6 and PowerPoint files
- ✅ Session management and workspace cleanup

**Deployment**:
- ✅ Amazon Linux 2023 systemd service configuration
- ✅ Nginx reverse proxy setup
- ✅ Redis6 integration for task queue
- ✅ Production-ready error handling and logging

### 🎯 Key Features

1. **Multi-format Generation**: Creates both ProPresenter 6 (.pro6plx) and PowerPoint (.pptx) files
2. **Template Management**: Users can refresh their workspace to get latest source_materials updates
3. **Real-time Processing**: Background tasks with live progress updates
4. **File Management**: Full upload, edit, create folder capabilities
5. **Direct Downloads**: Dedicated buttons for downloading generated presentations
6. **Session Isolation**: Each user gets isolated workspace in `/tmp/pp6_workspaces/`

### 🚀 Production Deployment

The web service is successfully deployed and operational on Amazon Linux 2023 with:
- **URL**: `http://alex.zetakey.com` 
- **Backend**: Flask + Gunicorn on port 5000
- **Task Queue**: Celery workers with Redis
- **Web Server**: Nginx reverse proxy
- **File Storage**: User workspaces in `/tmp/pp6_workspaces/`
- **Template Source**: `/opt/pp6-web-service/source_materials/`

### 📋 Usage Workflow

1. **Access**: Navigate to web interface
2. **Edit**: Modify source materials using built-in editors
3. **Upload**: Add new images, text files, or JSON configurations
4. **Generate**: Click "🚀 Generate" to create presentations
5. **Download**: Use dedicated download buttons for PP6 or PowerPoint files
6. **Refresh**: Click "🔄 New Session" to get latest template updates

## Conclusion

The PP6 Web Service successfully transforms the CLI-based generator into a modern, user-friendly web application. The implementation provides all the powerful features of the original command-line tool while adding:

- **Ease of Use**: Intuitive web interface eliminates need for command-line knowledge
- **Real-time Feedback**: Live progress updates and immediate download access
- **Multi-user Support**: Isolated workspaces and session management
- **Template Management**: Easy refresh mechanism for updated source materials
- **Production Ready**: Robust error handling, logging, and deployment configuration

The service maintains the full functionality of the original CLI tool while providing a significantly improved user experience through its web interface.