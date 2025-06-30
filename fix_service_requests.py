#!/usr/bin/env python3
"""
Database migration script to fix service_requests table
"""

from app import create_app
from app.extensions import db
from sqlalchemy import text

def check_and_fix_database():
    """Check and fix the service_requests table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check current table structure
            result = db.session.execute(text("PRAGMA table_info(service_requests)"))
            columns = [row[1] for row in result]
            
            print("Current service_requests columns:")
            for col in columns:
                print(f"  - {col}")
            
            if 'service_id' not in columns:
                print("\nAdding service_id column...")
                
                # Add service_id column
                db.session.execute(text("""
                    ALTER TABLE service_requests 
                    ADD COLUMN service_id INTEGER
                """))
                
                # Get the first service ID to use as default
                service_result = db.session.execute(text("SELECT service_id FROM services LIMIT 1"))
                first_service = service_result.fetchone()
                
                if first_service:
                    default_service_id = first_service[0]
                    print(f"Setting default service_id to: {default_service_id}")
                    
                    # Update existing records
                    db.session.execute(text(f"""
                        UPDATE service_requests 
                        SET service_id = {default_service_id} 
                        WHERE service_id IS NULL
                    """))
                
                db.session.commit()
                print("✓ service_id column added successfully!")
            else:
                print("✓ service_id column already exists")
                
            # Verify final structure
            result = db.session.execute(text("PRAGMA table_info(service_requests)"))
            print("\nFinal service_requests structure:")
            for row in result:
                print(f"  {row[1]} ({row[2]})")
                
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    check_and_fix_database()
