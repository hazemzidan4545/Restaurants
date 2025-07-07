#!/usr/bin/env python3
"""
Migration script to add missing fields to ServiceRequest table
"""

from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate_service_request_fields():
    """Add missing fields to service_requests table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Checking ServiceRequest table structure...")
            
            # Check current table structure
            result = db.session.execute(text("PRAGMA table_info(service_requests)"))
            columns = [row[1] for row in result]
            print(f"Current columns: {columns}")
            
            # Add missing columns if they don't exist
            if 'handled_by' not in columns:
                print("Adding handled_by column...")
                db.session.execute(text("""
                    ALTER TABLE service_requests
                    ADD COLUMN handled_by INTEGER
                """))
                print("✅ Added handled_by column")
            else:
                print("✓ handled_by column already exists")

            if 'created_at' not in columns:
                print("Adding created_at column...")
                db.session.execute(text("""
                    ALTER TABLE service_requests
                    ADD COLUMN created_at DATETIME
                """))
                print("✅ Added created_at column")
            else:
                print("✓ created_at column already exists")

            if 'updated_at' not in columns:
                print("Adding updated_at column...")
                db.session.execute(text("""
                    ALTER TABLE service_requests
                    ADD COLUMN updated_at DATETIME
                """))
                print("✅ Added updated_at column")
            else:
                print("✓ updated_at column already exists")
            
            # Update existing records to have created_at = timestamp if null
            db.session.execute(text("""
                UPDATE service_requests 
                SET created_at = timestamp 
                WHERE created_at IS NULL
            """))
            
            # Update existing records to have updated_at = timestamp if null
            db.session.execute(text("""
                UPDATE service_requests 
                SET updated_at = timestamp 
                WHERE updated_at IS NULL
            """))
            
            db.session.commit()
            print("✅ ServiceRequest table migration completed successfully!")
            
            # Verify the changes
            result = db.session.execute(text("PRAGMA table_info(service_requests)"))
            new_columns = [row[1] for row in result]
            print(f"Updated columns: {new_columns}")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = migrate_service_request_fields()
    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n💥 Migration failed!")
