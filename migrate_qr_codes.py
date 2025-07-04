#!/usr/bin/env python3
"""
Database Migration: Add qr_image_data column to qr_codes table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate_qr_codes_table():
    """Add qr_image_data column to existing qr_codes table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(qr_codes)")).fetchall()
            columns = [row[1] for row in result]
            
            if 'qr_image_data' in columns:
                print("✅ qr_image_data column already exists")
                return True
            
            print("Adding qr_image_data column to qr_codes table...")
            
            # Add the new column
            db.session.execute(text("ALTER TABLE qr_codes ADD COLUMN qr_image_data TEXT"))
            db.session.commit()
            
            print("✅ Successfully added qr_image_data column")
            
            # Verify the column was added
            result = db.session.execute(text("PRAGMA table_info(qr_codes)")).fetchall()
            columns = [row[1] for row in result]
            
            if 'qr_image_data' in columns:
                print("✅ Column verified in database")
                print(f"QR Codes table now has {len(columns)} columns:")
                for col in result:
                    print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
                return True
            else:
                print("❌ Column was not added successfully")
                return False
                
        except Exception as e:
            print(f"❌ Error migrating database: {e}")
            db.session.rollback()
            return False

def main():
    """Run the migration"""
    print("🔄 DATABASE MIGRATION: Adding QR Image Data Column")
    print("=" * 50)
    
    if migrate_qr_codes_table():
        print("\n🎉 Migration completed successfully!")
        print("You can now run the QR code generation system.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above.")

if __name__ == '__main__':
    main()
