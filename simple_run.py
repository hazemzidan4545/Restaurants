#!/usr/bin/env python3
"""
Simple Flask runner without SocketIO for testing
"""

import os
from app import create_app
from app.extensions import db

if __name__ == '__main__':
    try:
        print("Starting Restaurant Management System (Simple Mode)...")
        app = create_app(os.getenv('FLASK_CONFIG') or 'development')
        
        print("Creating database tables...")
        with app.app_context():
            db.create_all()
        
        print("Starting server on port 5001...")
        # Run without SocketIO
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
