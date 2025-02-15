import os
from datetime import timedelta

class Config:
    # Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-key-here'
    
    # Database Configuration
    MYSQL_USER = os.environ.get('MYSQL_USER', 'Kelvin')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Rukeratabaro2$')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'transactions_db')
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Application Directories
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    
    # Logging Configuration
    LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO')
    
    # CORS Configuration
    CORS_HEADERS = 'Content-Type'
    
    # Pagination
    DEFAULT_PAGE_SIZE = 10
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Ensure directories exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings"""
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError("Database URI must be configured")
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY must be set in environment variables")

class DevelopmentConfig(Config):
    """Configuration for Development Environment"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuration for Production Environment"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configuration for Testing Environment"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

def get_config(config_name='development'):
    """
    Returns the appropriate configuration based on the environment
    
    Args:
        config_name (str): Name of the configuration to use
        
    Returns:
        Config: Configuration class
    """
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(config_name, DevelopmentConfig)
