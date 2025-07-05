#!/usr/bin/env python3
"""
Quick server start script for testing
"""

import os
import sys
from app import create_app
from app.extensions import db

if __name__ == '__main__':
    try:
        print("Creating Flask app...")
        app = create_app('development')
        
        print("Setting up database...")
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
        
        print("Starting server on http://localhost:5000...")
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
