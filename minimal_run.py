#!/usr/bin/env python3

from app import create_app
import os

if __name__ == '__main__':
    print("Starting Flask application...")
    app = create_app()
    
    print("Flask app created successfully")
    print(f"Debug mode: {app.debug}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
    
    print("Starting server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
