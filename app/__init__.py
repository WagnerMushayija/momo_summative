from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config, get_config
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='development'):
    """
    Application factory for creating Flask application
    
    Args:
        config_name (str): Configuration environment name
    
    Returns:
        Flask application instance
    """
    # Determine the base directory of the application
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Create Flask app instance with explicit template and static folders
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Enable CORS for the entire application
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configure logging
    configure_logging(app)
    
    # Import and register blueprints
    from app.route import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app

def configure_logging(app):
    """
    Configure application logging
    
    Args:
        app (Flask): Flask application instance
    """
    # Ensure log directory exists
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a file handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'financial_dashboard.log'), 
        maxBytes=10240, 
        backupCount=10
    )
    
    # Set logging format
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # Set logging level based on configuration
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Log application startup
    app.logger.info('Financial Dashboard startup')

# Import models to ensure they are recognized by Flask-Migrate
from app.models import Transaction