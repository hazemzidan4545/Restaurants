#!/usr/bin/env python3
"""Migrate database schema to fix OrderItem table"""

from app import create_app
from app.models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        print("=== MIGRATING DATABASE SCHEMA ===")
        
        # Check current schema
        result = db.session.execute(text("PRAGMA table_info(order_items)"))
        columns = result.fetchall()
        
        print("Current order_items table schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check if menu_item_id column exists
        column_names = [col[1] for col in columns]
        
        if 'menu_item_id' not in column_names and 'item_id' in column_names:
            print("\n🔧 Need to rename item_id to menu_item_id")
            
            # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
            print("Creating backup of order_items...")
            
            # Create backup table
            db.session.execute(text("""
                CREATE TABLE order_items_backup AS 
                SELECT * FROM order_items
            """))
            
            # Drop the old table
            print("Dropping old order_items table...")
            db.session.execute(text("DROP TABLE order_items"))
            
            # Create new table with correct schema
            print("Creating new order_items table...")
            db.session.execute(text("""
                CREATE TABLE order_items (
                    order_item_id INTEGER PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    menu_item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    note VARCHAR(255),
                    unit_price DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (order_id),
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items (item_id)
                )
            """))
            
            # Copy data back with column rename
            print("Copying data back...")
            db.session.execute(text("""
                INSERT INTO order_items (order_item_id, order_id, menu_item_id, quantity, note, unit_price)
                SELECT order_item_id, order_id, item_id, quantity, note, unit_price
                FROM order_items_backup
            """))
            
            # Drop backup table
            db.session.execute(text("DROP TABLE order_items_backup"))
            
            db.session.commit()
            print("✅ Successfully migrated order_items table")
            
        elif 'menu_item_id' in column_names:
            print("✅ order_items table already has correct schema")
            
        else:
            print("❌ Unexpected table schema")
        
        # Verify new schema
        result = db.session.execute(text("PRAGMA table_info(order_items)"))
        columns = result.fetchall()
        
        print("\nFinal order_items table schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        print("\n🎉 Database migration completed!")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
