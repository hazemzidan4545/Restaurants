#!/usr/bin/env python3
"""
Database Migration Script
Adds discount_percentage and original_price columns to menu_items table
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add discount columns to menu_items table"""
    
    # Check multiple possible database paths - prioritize dev database
    db_paths = [
        os.path.join('instance', 'restaurant_dev.db'),
        os.path.join('instance', 'restaurant.db'),
        'restaurant_dev.db',
        'restaurant.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ Database file not found in any of these locations: {db_paths}")
        return False
    
    print(f"📍 Using database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Starting database migration...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(menu_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns in menu_items: {columns}")
        
        # Add discount_percentage column if it doesn't exist
        if 'discount_percentage' not in columns:
            print("Adding discount_percentage column...")
            cursor.execute("""
                ALTER TABLE menu_items 
                ADD COLUMN discount_percentage DECIMAL(5,2) DEFAULT 0.00
            """)
            print("✅ Added discount_percentage column")
        else:
            print("✅ discount_percentage column already exists")
        
        # Add original_price column if it doesn't exist
        if 'original_price' not in columns:
            print("Adding original_price column...")
            cursor.execute("""
                ALTER TABLE menu_items 
                ADD COLUMN original_price DECIMAL(10,2)
            """)
            print("✅ Added original_price column")
        else:
            print("✅ original_price column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(menu_items)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns in menu_items: {new_columns}")
        
        conn.close()
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def migrate_system_settings():
    """Create system_settings table if it doesn't exist"""
    
    # Check multiple possible database paths - prioritize dev database
    db_paths = [
        os.path.join('instance', 'restaurant_dev.db'),
        os.path.join('instance', 'restaurant.db'),
        'restaurant_dev.db',
        'restaurant.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ Database file not found in any of these locations: {db_paths}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if system_settings table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='system_settings'
        """)
        
        if not cursor.fetchone():
            print("Creating system_settings table...")
            cursor.execute("""
                CREATE TABLE system_settings (
                    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key VARCHAR(100) UNIQUE NOT NULL,
                    value TEXT,
                    description TEXT,
                    setting_type VARCHAR(20) DEFAULT 'string' CHECK (setting_type IN ('string', 'integer', 'boolean', 'float')),
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add default currency setting
            cursor.execute("""
                INSERT INTO system_settings (key, value, description, setting_type)
                VALUES ('currency', 'EGP', 'System currency for price display', 'string')
            """)
            
            conn.commit()
            print("✅ Created system_settings table with default currency")
        else:
            print("✅ system_settings table already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ System settings migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("RESTAURANT DATABASE MIGRATION")
    print("=" * 60)
    print(f"Migration started at: {datetime.now()}")
    
    # Run migrations
    success1 = migrate_database()
    success2 = migrate_system_settings()
    
    if success1 and success2:
        print("\n🎉 All migrations completed successfully!")
        print("The server should now work without database errors.")
    else:
        print("\n❌ Some migrations failed. Please check the errors above.")
    
    print("=" * 60)
