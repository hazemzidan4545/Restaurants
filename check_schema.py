#!/usr/bin/env python3
"""
Check database schema for service requests table
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_schema():
    """Check the service_requests table schema"""
    try:
        from app import create_app
        from app.extensions import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("🔍 Checking service_requests table schema...")
            
            # Check if table exists
            result = db.session.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='service_requests'
            """)).fetchone()
            
            if result:
                print("✅ service_requests table exists")
                
                # Get table schema
                schema = db.session.execute(text("""
                    PRAGMA table_info(service_requests)
                """)).fetchall()
                
                print("📋 Table columns:")
                for column in schema:
                    print(f"   - {column[1]} ({column[2]}) {'NOT NULL' if column[3] else 'NULL'}")
                
                # Check if description column exists
                has_description = any(col[1] == 'description' for col in schema)
                if has_description:
                    print("✅ Description column exists")
                else:
                    print("❌ Description column missing - adding it...")
                    db.session.execute(text("""
                        ALTER TABLE service_requests 
                        ADD COLUMN description TEXT
                    """))
                    db.session.commit()
                    print("✅ Description column added")
                
            else:
                print("❌ service_requests table does not exist")
                print("🔧 Creating table...")
                
                # Create the table
                db.create_all()
                print("✅ Tables created")
            
            return True
            
    except Exception as e:
        print(f"❌ Schema check error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Database Schema Check")
    print("=" * 30)
    check_schema()
