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
    app = create_app(os.getenv('FLASK_CONFIG') or 'development')
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    
    # Run the application with SocketIO support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
