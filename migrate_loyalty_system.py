#!/usr/bin/env python3
"""
Database migration script to add new loyalty system fields
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def run_migration():
    """Run database migration for loyalty system updates"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Starting loyalty system database migration...")
            
            # Add new fields to loyalty_programs table
            print("Adding new fields to loyalty_programs table...")
            
            # Check if points_value column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('loyalty_programs') 
                WHERE name = 'points_value'
            """)).fetchone()
            
            if result[0] == 0:
                db.session.execute(text("""
                    ALTER TABLE loyalty_programs 
                    ADD COLUMN points_value REAL NOT NULL DEFAULT 1.0
                """))
                print("✓ Added points_value column")
            else:
                print("✓ points_value column already exists")
            
            # Check if min_redemption column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('loyalty_programs') 
                WHERE name = 'min_redemption'
            """)).fetchone()
            
            if result[0] == 0:
                db.session.execute(text("""
                    ALTER TABLE loyalty_programs 
                    ADD COLUMN min_redemption INTEGER NOT NULL DEFAULT 100
                """))
                print("✓ Added min_redemption column")
            else:
                print("✓ min_redemption column already exists")
            
            # Check if max_redemption_percentage column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('loyalty_programs') 
                WHERE name = 'max_redemption_percentage'
            """)).fetchone()
            
            if result[0] == 0:
                db.session.execute(text("""
                    ALTER TABLE loyalty_programs 
                    ADD COLUMN max_redemption_percentage INTEGER NOT NULL DEFAULT 50
                """))
                print("✓ Added max_redemption_percentage column")
            else:
                print("✓ max_redemption_percentage column already exists")
            
            # Add new fields to point_transactions table
            print("Adding new fields to point_transactions table...")
            
            # Check if balance_after column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('point_transactions') 
                WHERE name = 'balance_after'
            """)).fetchone()
            
            if result[0] == 0:
                db.session.execute(text("""
                    ALTER TABLE point_transactions 
                    ADD COLUMN balance_after INTEGER
                """))
                print("✓ Added balance_after column")
            else:
                print("✓ balance_after column already exists")
            
            # Update transaction_type enum to include 'adjustment'
            print("Updating transaction types...")
            
            # SQLite doesn't support modifying ENUMs directly, so we'll handle this in the application
            # The new enum values will be available when the model is used
            
            db.session.commit()
            print("✓ Migration completed successfully!")
            
        except Exception as e:
            print(f"✗ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    run_migration()
