#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from app import create_app, db

# Load environment variables
load_dotenv()

# Create Flask application
app = create_app()

# Create application context
with app.app_context():
    # Create database tables if they don't exist
    db.create_all()

# Run the application
if __name__ == '__main__':
    # Determine port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(
        host='0.0.0.0',  # Listen on all available interfaces
        port=port,
        debug=os.environ.get('FLASK_DEBUG', 'True') == 'True'
    )
