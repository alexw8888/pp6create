"""
Configuration for PP6 Web Service
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File Upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'json', 'jpg', 'jpeg', 'png', 'gif', 'bmp'}
    
    # Workspace
    WORKSPACE_BASE_DIR = os.environ.get('WORKSPACE_DIR') or '/tmp/pp6_workspaces'
    WORKSPACE_TIMEOUT = timedelta(hours=24)  # Cleanup after 24 hours
    DEFAULT_SOURCE_MATERIALS = os.environ.get('DEFAULT_SOURCE_MATERIALS') or '/opt/pp6-web-service/source_materials'
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Generation
    GENERATION_TIMEOUT = 300  # 5 minutes max generation time
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/pp6-web.log'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with production values
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production
    
    # Use actual workspace directory
    WORKSPACE_BASE_DIR = '/var/pp6_workspaces'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}