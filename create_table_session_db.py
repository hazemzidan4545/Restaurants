#!/usr/bin/env python3
"""
Create database tables for new TableSession model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db

def create_table_session_table():
    """Create the table_sessions table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables (will only create missing ones)
            db.create_all()
            
            print("Database tables created successfully")
            print("TableSession table is now available")
            
            # Verify the table was created
            from sqlalchemy import text
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='table_sessions'")).fetchone()
            
            if result:
                print("✅ table_sessions table created successfully")
                
                # Show table structure
                columns = db.session.execute(text("PRAGMA table_info(table_sessions)")).fetchall()
                print(f"Table structure ({len(columns)} columns):")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
            else:
                print("❌ table_sessions table was not created")
                
        except Exception as e:
            print(f"Error creating tables: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_table_session_table()
