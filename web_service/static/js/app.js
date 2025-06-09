/**
 * PP6 Web Service - Main Application JavaScript
 */

class PP6WebApp {
    constructor() {
        this.sessionId = null;
        this.workspacePath = null;
        this.currentPath = '';
        this.selectedFile = null;
        this.currentTaskId = null;
        this.refreshInterval = null;
        this.generatedFiles = {};
        
        this.initializeApp();
    }
    
    async initializeApp() {
        try {
            console.log('Starting app initialization...');
            this.showStatus('Initializing workspace...', 'info');
            
            console.log('Creating workspace...');
            await this.createWorkspace();
            
            console.log('Loading file tree...');
            await this.loadFileTree();
            
            console.log('Setting up event handlers...');
            this.setupEventHandlers();
            
            console.log('App initialization complete');
            this.showStatus('Ready to work!', 'success');
        } catch (error) {
            console.error('App initialization failed:', error);
            this.showStatus(`Failed to initialize: ${error.message}`, 'error');
        }
    }
    
    async createWorkspace() {
        console.log('Creating workspace...');
        const response = await fetch('/api/workspace/create', {
            method: 'POST'
        });
        
        console.log('Workspace creation response:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`Failed to create workspace: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Workspace created:', data);
        
        this.sessionId = data.session_id;
        this.workspacePath = data.workspace_path;
        
        // Update UI
        document.getElementById('session-id').textContent = this.sessionId;
        document.getElementById('workspace-path').textContent = this.workspacePath;
    }
    
    async loadFileTree() {
        try {
            const url = `/api/files/${this.sessionId}?path=${this.currentPath}`;
            console.log('Loading file tree from:', url);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                console.error('File tree request failed:', response.status, response.statusText);
                throw new Error(`Failed to load files: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('File tree data received:', data);
            
            if (data.files && Array.isArray(data.files)) {
                console.log(`Found ${data.files.length} files/folders`);
                data.files.forEach(file => {
                    console.log(`  ${file.is_directory ? 'DIR' : 'FILE'}: ${file.name} (${file.path})`);
                });
            } else {
                console.warn('Unexpected file tree response format:', data);
            }
            
            this.renderFileTree(data.files || []);
            this.updateBreadcrumb();
            
        } catch (error) {
            console.error('File tree loading error:', error);
            this.showStatus(`Failed to load files: ${error.message}`, 'error');
        }
    }
    
    async createNewSession() {
        try {
            this.showStatus('Creating new session...', 'info');
            
            // Clean up current workspace
            if (this.sessionId) {
                await fetch(`/api/workspace/${this.sessionId}`, {
                    method: 'DELETE'
                });
            }
            
            // Create new workspace
            await this.createWorkspace();
            
            // Reset current path and clear editor
            this.currentPath = '';
            this.clearEditor();
            
            // Reload file tree with fresh template
            await this.loadFileTree();
            
            // Update UI
            this.updateSessionDisplay();
            this.showStatus('New session created with latest template!', 'success');
            
        } catch (error) {
            this.showStatus(`Failed to create new session: ${error.message}`, 'error');
        }
    }
    
    updateSessionDisplay() {
        const sessionElement = document.getElementById('session-id');
        if (sessionElement && this.sessionId) {
            sessionElement.textContent = this.sessionId.substring(0, 8) + '...';
        }
    }
    
    renderFileTree(files) {
        const container = document.getElementById('file-tree');
        container.innerHTML = '';
        
        // Add back button if not at root
        if (this.currentPath) {
            const backItem = this.createFileItem({
                name: '..',
                is_directory: true,
                path: this.getParentPath()
            }, true);
            container.appendChild(backItem);
        }
        
        // Sort: directories first, then files
        files.sort((a, b) => {
            if (a.is_directory !== b.is_directory) {
                return b.is_directory - a.is_directory;
            }
            return a.name.localeCompare(b.name);
        });
        
        files.forEach(file => {
            const item = this.createFileItem(file);
            container.appendChild(item);
        });
    }
    
    createFileItem(file, isBack = false) {
        const item = document.createElement('div');
        item.className = file.is_directory ? 'folder-item' : 'file-item';
        item.dataset.path = file.path;
        item.dataset.isDirectory = file.is_directory;
        
        const icon = document.createElement('span');
        icon.className = file.is_directory ? 'folder-icon' : 'file-icon';
        icon.innerHTML = file.is_directory ? '📁' : this.getFileIcon(file.name);
        
        const name = document.createElement('span');
        name.className = 'file-name';
        name.textContent = file.name;
        
        item.appendChild(icon);
        item.appendChild(name);
        
        if (!file.is_directory && !isBack) {
            const size = document.createElement('span');
            size.className = 'file-size';
            size.textContent = this.formatFileSize(file.size);
            item.appendChild(size);
            
            if (file.editable) {
                const badge = document.createElement('span');
                badge.className = 'editable-badge';
                badge.textContent = 'Edit';
                item.appendChild(badge);
            }
        }
        
        // Add click handler
        item.addEventListener('click', () => {
            if (file.is_directory) {
                this.navigateToFolder(isBack ? file.path : file.path);
            } else {
                this.selectFile(item, file);
            }
        });
        
        return item;
    }
    
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'txt': '📄',
            'json': '📋',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️',
            'gif': '🖼️'
        };
        return icons[ext] || '📄';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    async navigateToFolder(path) {
        this.currentPath = path;
        await this.loadFileTree();
        this.clearEditor();
    }
    
    getParentPath() {
        if (!this.currentPath) return '';
        const parts = this.currentPath.split('/');
        parts.pop();
        return parts.join('/');
    }
    
    updateBreadcrumb() {
        const breadcrumb = document.getElementById('breadcrumb');
        if (!breadcrumb) return;
        
        const parts = this.currentPath ? this.currentPath.split('/') : [];
        let path = '';
        let html = '<a href="#" onclick="app.navigateToFolder(\'\')">📁 workspace</a>';
        
        parts.forEach(part => {
            if (part) {
                path += (path ? '/' : '') + part;
                html += ` / <a href="#" onclick="app.navigateToFolder('${path}')">${part}</a>`;
            }
        });
        
        breadcrumb.innerHTML = html;
    }
    
    selectFile(item, file) {
        // Remove previous selection
        document.querySelectorAll('.file-item.selected').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Select current item
        item.classList.add('selected');
        this.selectedFile = file;
        
        // Load file content if editable
        if (file.editable) {
            this.loadFileContent(file);
        } else {
            this.showFileInfo(file);
        }
    }
    
    async loadFileContent(file) {
        try {
            document.getElementById('editor-title').textContent = file.name;
            document.getElementById('editor-content').style.display = 'block';
            document.getElementById('file-info').style.display = 'none';
            
            const response = await fetch(`/api/files/${this.sessionId}/${file.path}`);
            
            if (!response.ok) {
                throw new Error('Failed to load file');
            }
            
            const data = await response.json();
            
            if (data.type === 'text') {
                // Initialize CodeMirror if not already done
                if (!this.codeEditor) {
                    this.initCodeMirror();
                }
                
                // Set mode based on file extension
                const mode = this.getEditorMode(file.name);
                this.codeEditor.setOption('mode', mode);
                
                // Set content
                this.codeEditor.setValue(data.content);
                document.getElementById('save-btn').style.display = 'inline-flex';
            } else {
                // Show plain textarea for non-editable files
                if (this.codeEditor) {
                    this.codeEditor.toTextArea();
                    this.codeEditor = null;
                }
                document.getElementById('code-editor').value = 'This file cannot be edited (binary or invalid UTF-8)';
                document.getElementById('save-btn').style.display = 'none';
            }
            
        } catch (error) {
            this.showStatus(`Failed to load file: ${error.message}`, 'error');
        }
    }
    
    initCodeMirror() {
        const textarea = document.getElementById('code-editor');
        this.codeEditor = CodeMirror.fromTextArea(textarea, {
            lineNumbers: true,
            mode: 'javascript',
            theme: 'default',
            lineWrapping: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            indentUnit: 2,
            tabSize: 2,
            extraKeys: {
                'Ctrl-S': () => this.saveFile(),
                'Cmd-S': () => this.saveFile()
            }
        });
        
        // Style the CodeMirror instance
        this.codeEditor.setSize('100%', '100%');
    }
    
    getEditorMode(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const modes = {
            'json': 'application/json',
            'js': 'javascript',
            'txt': 'text/plain',
            'md': 'markdown',
            'html': 'htmlmixed',
            'xml': 'xml',
            'css': 'css'
        };
        return modes[ext] || 'text/plain';
    }
    
    showFileInfo(file) {
        document.getElementById('editor-title').textContent = file.name;
        document.getElementById('editor-content').style.display = 'none';
        document.getElementById('file-info').style.display = 'block';
        
        document.getElementById('file-info').innerHTML = `
            <div class="file-details">
                <h4>File Information</h4>
                <p><strong>Name:</strong> ${file.name}</p>
                <p><strong>Size:</strong> ${this.formatFileSize(file.size)}</p>
                <p><strong>Type:</strong> ${file.mime_type || 'Unknown'}</p>
                <p><strong>Path:</strong> ${file.path}</p>
                ${file.is_directory ? '' : '<p><em>This file cannot be edited online.</em></p>'}
            </div>
        `;
    }
    
    clearEditor() {
        document.getElementById('editor-title').textContent = 'No file selected';
        document.getElementById('editor-content').style.display = 'none';
        document.getElementById('file-info').style.display = 'block';
        document.getElementById('file-info').innerHTML = '<p class="text-muted">Select a file to view or edit</p>';
        this.selectedFile = null;
    }
    
    async saveFile() {
        if (!this.selectedFile) return;
        
        // Get content from CodeMirror or fallback to textarea
        const content = this.codeEditor ? this.codeEditor.getValue() : document.getElementById('code-editor').value;
        const saveBtn = document.getElementById('save-btn');
        
        try {
            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';
            
            const response = await fetch(`/api/files/${this.sessionId}/${this.selectedFile.path}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content })
            });
            
            if (!response.ok) {
                throw new Error('Failed to save file');
            }
            
            this.showStatus('File saved successfully!', 'success');
            
        } catch (error) {
            this.showStatus(`Failed to save file: ${error.message}`, 'error');
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = '💾 Save';
        }
    }
    
    setupEventHandlers() {
        console.log('Setting up event handlers...');
        
        // Helper function to safely add event listener
        const safeAddEventListener = (id, event, handler) => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener(event, handler);
                console.log(`✓ Added ${event} listener to ${id}`);
            } else {
                console.warn(`⚠️ Element with id '${id}' not found`);
            }
        };
        
        // Save button
        safeAddEventListener('save-btn', 'click', () => {
            this.saveFile();
        });
        
        // Upload handling
        const uploadZone = document.getElementById('upload-zone');
        const fileInput = document.getElementById('file-input');
        
        if (uploadZone) {
            uploadZone.addEventListener('click', () => {
                if (fileInput) fileInput.click();
            });
            
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('drag-over');
            });
            
            uploadZone.addEventListener('dragleave', () => {
                uploadZone.classList.remove('drag-over');
            });
            
            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('drag-over');
                this.handleFiles(e.dataTransfer.files);
            });
            console.log('✓ Added upload zone listeners');
        } else {
            console.warn('⚠️ Upload zone not found');
        }
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFiles(e.target.files);
            });
            console.log('✓ Added file input listener');
        } else {
            console.warn('⚠️ File input not found');
        }
        
        // Generation button
        safeAddEventListener('generate-btn', 'click', () => {
            this.startGeneration();
        });
        
        // Refresh button
        safeAddEventListener('refresh-btn', 'click', () => {
            this.loadFileTree();
        });
        
        // Create folder button
        safeAddEventListener('create-folder-btn', 'click', () => {
            this.createFolder();
        });
        
        // New session button
        safeAddEventListener('new-session-btn', 'click', () => {
            this.createNewSession();
        });
        
        // Download buttons
        safeAddEventListener('download-pp6-btn', 'click', () => {
            this.downloadFile(this.generatedFiles.pp6);
        });
        
        safeAddEventListener('download-pptx-btn', 'click', () => {
            this.downloadFile(this.generatedFiles.pptx);
        });
        
        console.log('Event handlers setup complete');
    }
    
    async handleFiles(files) {
        if (files.length === 0) return;
        
        const uploadStatus = document.getElementById('upload-status');
        uploadStatus.style.display = 'block';
        uploadStatus.innerHTML = '<div class="spinner"></div> Uploading files...';
        
        try {
            const formData = new FormData();
            
            for (let file of files) {
                formData.append('file', file);
            }
            
            // Upload to current directory
            formData.append('path', this.currentPath || 'source_materials');
            
            const response = await fetch(`/api/files/${this.sessionId}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Upload failed');
            }
            
            const result = await response.json();
            this.showStatus(`Successfully uploaded ${result.count} file(s)`, 'success');
            
            // Refresh file tree
            await this.loadFileTree();
            
        } catch (error) {
            this.showStatus(`Upload failed: ${error.message}`, 'error');
        } finally {
            uploadStatus.style.display = 'none';
        }
    }
    
    async createFolder() {
        const name = prompt('Enter folder name:');
        if (!name) return;
        
        try {
            const path = this.currentPath ? `${this.currentPath}/${name}` : name;
            
            const response = await fetch(`/api/files/${this.sessionId}/mkdir`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ path })
            });
            
            if (!response.ok) {
                throw new Error('Failed to create folder');
            }
            
            this.showStatus('Folder created successfully!', 'success');
            await this.loadFileTree();
            
        } catch (error) {
            this.showStatus(`Failed to create folder: ${error.message}`, 'error');
        }
    }
    
    async startGeneration() {
        const generateBtn = document.getElementById('generate-btn');
        const progressContainer = document.getElementById('progress-container');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        try {
            generateBtn.disabled = true;
            generateBtn.textContent = 'Starting...';
            
            // Hide download buttons from previous generation
            this.hideDownloadButtons();
            
            // Get options
            const format = document.querySelector('input[name="format"]:checked').value;
            const outputName = document.getElementById('output-name').value;
            const width = document.getElementById('width').value;
            const height = document.getElementById('height').value;
            
            const options = {
                format,
                output_name: outputName || 'GeneratedPresentation',
                width: parseInt(width) || 1024,
                height: parseInt(height) || 768
            };
            
            const response = await fetch(`/api/generate/${this.sessionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(options)
            });
            
            if (!response.ok) {
                throw new Error('Failed to start generation');
            }
            
            const result = await response.json();
            this.currentTaskId = result.task_id;
            
            // Show progress
            progressContainer.style.display = 'block';
            progressFill.style.width = '0%';
            progressText.textContent = 'Starting generation...';
            
            // Start polling for status
            this.pollGenerationStatus();
            
        } catch (error) {
            this.showStatus(`Failed to start generation: ${error.message}`, 'error');
            generateBtn.disabled = false;
            generateBtn.textContent = '🚀 Generate';
        }
    }
    
    async pollGenerationStatus() {
        if (!this.currentTaskId) return;
        
        try {
            const response = await fetch(`/api/generate/${this.sessionId}/status?task_id=${this.currentTaskId}`);
            
            if (!response.ok) {
                throw new Error('Failed to get status');
            }
            
            const status = await response.json();
            this.updateProgress(status);
            
            if (status.state === 'SUCCESS') {
                console.log('SUCCESS state detected, calling handleGenerationComplete');
                this.handleGenerationComplete(status);
            } else if (status.state === 'FAILURE') {
                console.log('FAILURE state detected');
                this.handleGenerationError(status);
            } else {
                console.log('Status polling:', status.state, status.status);
                // Continue polling
                setTimeout(() => this.pollGenerationStatus(), 1000);
            }
            
        } catch (error) {
            this.showStatus(`Failed to check status: ${error.message}`, 'error');
            this.resetGenerationUI();
        }
    }
    
    updateProgress(status) {
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        let percentage = 0;
        let text = status.status || 'Processing...';
        
        if (status.current && status.total) {
            percentage = (status.current / status.total) * 100;
        } else if (status.state === 'PROGRESS') {
            percentage = 50; // Default progress
        }
        
        progressFill.style.width = percentage + '%';
        progressText.textContent = text;
    }
    
    handleGenerationComplete(status) {
        console.log('Generation completed! Status:', status);
        
        const progressText = document.getElementById('progress-text');
        const progressFill = document.getElementById('progress-fill');
        
        progressFill.style.width = '100%';
        progressText.textContent = 'Generation completed!';
        
        this.showStatus('Presentation generated successfully!', 'success');
        
        // Process generated files and show download buttons
        if (status.files && status.files.length > 0) {
            console.log('Processing files...');
            this.processGeneratedFiles(status.files);
            this.showDownloadButtons();
            this.showDownloadLinks(status.files);
        } else {
            console.log('No files in status:', status);
        }
        
        this.resetGenerationUI();
    }
    
    handleGenerationError(status) {
        this.showStatus(`Generation failed: ${status.error || 'Unknown error'}`, 'error');
        this.resetGenerationUI();
    }
    
    processGeneratedFiles(files) {
        console.log('Processing generated files:', files);
        
        // Reset generated files
        this.generatedFiles = {};
        
        // Categorize files by extension
        files.forEach(file => {
            console.log('Processing file:', file.name, file.path);
            if (file.name.endsWith('.pro6plx')) {
                this.generatedFiles.pp6 = file.path;
                console.log('Found PP6 file:', file.path);
            } else if (file.name.endsWith('.pptx')) {
                this.generatedFiles.pptx = file.path;
                console.log('Found PPTX file:', file.path);
            }
        });
        
        console.log('Final generatedFiles:', this.generatedFiles);
    }
    
    showDownloadButtons() {
        console.log('Showing download buttons...');
        const pp6Btn = document.getElementById('download-pp6-btn');
        const pptxBtn = document.getElementById('download-pptx-btn');
        
        console.log('PP6 button element:', pp6Btn);
        console.log('PPTX button element:', pptxBtn);
        console.log('Generated files:', this.generatedFiles);
        
        // Show buttons based on available files
        if (this.generatedFiles.pp6) {
            console.log('Showing PP6 download button');
            pp6Btn.style.display = 'inline-flex';
        }
        if (this.generatedFiles.pptx) {
            console.log('Showing PPTX download button');
            pptxBtn.style.display = 'inline-flex';
        }
    }
    
    hideDownloadButtons() {
        document.getElementById('download-pp6-btn').style.display = 'none';
        document.getElementById('download-pptx-btn').style.display = 'none';
    }
    
    downloadFile(filePath) {
        if (!filePath) {
            this.showStatus('File not available for download', 'error');
            return;
        }
        
        // Create download URL
        const downloadUrl = `/api/generate/${this.sessionId}/download/${filePath}`;
        
        // Trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = '';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showStatus('Download started!', 'success');
    }
    
    resetGenerationUI() {
        const generateBtn = document.getElementById('generate-btn');
        const progressContainer = document.getElementById('progress-container');
        
        generateBtn.disabled = false;
        generateBtn.textContent = '🚀 Generate';
        
        setTimeout(() => {
            progressContainer.style.display = 'none';
        }, 3000);
        
        this.currentTaskId = null;
        
        // DON'T hide download buttons here - they should stay visible after generation
    }
    
    showDownloadLinks(files) {
        const resultsPanel = document.getElementById('results-panel');
        resultsPanel.style.display = 'block';
        
        let html = '<h4>Generated Files:</h4>';
        files.forEach(file => {
            html += `
                <div class="result-item">
                    <div class="file-info">
                        <div class="file-name-result">${file.name}</div>
                        <div class="file-meta">${this.formatFileSize(file.size)} • Created just now</div>
                    </div>
                    <a href="/api/generate/${this.sessionId}/download/${file.path}" 
                       class="btn btn-sm btn-success" download>
                        📥 Download
                    </a>
                </div>
            `;
        });
        
        resultsPanel.innerHTML = html;
    }
    
    showStatus(message, type = 'info') {
        const statusContainer = document.getElementById('status-container');
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" style="border: none; background: none; float: right; cursor: pointer;">×</button>
        `;
        
        statusContainer.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new PP6WebApp();
});