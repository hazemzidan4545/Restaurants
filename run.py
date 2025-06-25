#!/usr/bin/env python3
"""
Restaurant Management System
Main application entry point
"""

import os
from app import create_app
from app.extensions import db, socketio
from flask_migrate import upgrade

def deploy():
    """Run deployment tasks."""
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Run database migrations
        upgrade()

if __name__ == '__main__':
    try:
        print("Starting Restaurant Management System...")
        print("Initializing application...")
        app = create_app(os.getenv('FLASK_CONFIG') or 'development')
        
        print("Creating database tables...")
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
        
        print("Starting server...")
        # Run the application with SocketIO support
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"ERROR: Failed to start the application: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease fix the above error and try again.")
