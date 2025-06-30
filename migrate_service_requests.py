#!/usr/bin/env python3
"""
Database migration script to add service_id column to service_requests table
"""

from app import create_app
from app.extensions import db

def migrate_service_requests():
    """Add service_id column to service_requests table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if service_id column already exists
            result = db.engine.execute("PRAGMA table_info(service_requests)")
            columns = [row[1] for row in result]
            
            if 'service_id' in columns:
                print("✓ service_id column already exists in service_requests table")
                return
            
            print("Adding service_id column to service_requests table...")
            
            # Add the service_id column
            db.engine.execute("""
                ALTER TABLE service_requests 
                ADD COLUMN service_id INTEGER 
                REFERENCES services(service_id)
            """)
            
            # Update existing records to have a default service_id (if any services exist)
            services = db.engine.execute("SELECT service_id FROM services LIMIT 1").fetchone()
            if services:
                default_service_id = services[0]
                db.engine.execute(f"""
                    UPDATE service_requests 
                    SET service_id = {default_service_id} 
                    WHERE service_id IS NULL
                """)
                print(f"✓ Updated existing service requests to use service_id: {default_service_id}")
            
            print("✓ service_id column added successfully!")
            
            # Verify the column was added
            result = db.engine.execute("PRAGMA table_info(service_requests)")
            print("\nUpdated service_requests table structure:")
            for row in result:
                print(f"  {row[1]} ({row[2]})")
                
        except Exception as e:
            print(f"✗ Error during migration: {e}")

if __name__ == "__main__":
    migrate_service_requests()
