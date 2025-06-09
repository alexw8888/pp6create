"""
PP6 Web Service - Flask Application
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, render_template, jsonify
from flask_cors import CORS

from config import config
from api.routes import api_bp, init_services


def create_app(config_name=None):
    """Application factory"""
    
    # Determine config
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Set up logging
    setup_logging(app)
    
    # Initialize services
    init_services(app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Main routes
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check"""
        return jsonify({
            'status': 'healthy',
            'service': 'PP6 Web Service',
            'version': '1.0.0'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


def setup_logging(app):
    """Set up application logging"""
    if not app.debug and not app.testing:
        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Set up file handler
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        # Add handler to app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info('PP6 Web Service startup')


# Create app instance
app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )