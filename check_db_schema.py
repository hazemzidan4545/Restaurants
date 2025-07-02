#!/usr/bin/env python3

from flask import Flask
import sqlite3

def check_database_schema():
    """Check the actual database schema to understand the current state"""
    
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/restaurant_dev.db')
        cursor = conn.cursor()
        
        print("🔍 Checking actual database schema...")
        
        # Check order_items table schema
        cursor.execute("PRAGMA table_info(order_items)")
        columns = cursor.fetchall()
        
        print("\n📋 order_items table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
        # Check if item_id or menu_item_id exists
        column_names = [col[1] for col in columns]
        
        if 'item_id' in column_names:
            print("✅ Found 'item_id' column")
        if 'menu_item_id' in column_names:
            print("✅ Found 'menu_item_id' column")
            
        if 'item_id' not in column_names and 'menu_item_id' not in column_names:
            print("❌ Neither 'item_id' nor 'menu_item_id' found!")
            
        # Check foreign key constraints
        cursor.execute("PRAGMA foreign_key_list(order_items)")
        foreign_keys = cursor.fetchall()
        
        print("\n🔗 Foreign key constraints:")
        for fk in foreign_keys:
            print(f"  - {fk[3]} -> {fk[2]}.{fk[4]}")
            
        conn.close()
        
        return 'item_id' in column_names, 'menu_item_id' in column_names
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False, False

if __name__ == "__main__":
    has_item_id, has_menu_item_id = check_database_schema()
    
    if has_item_id and not has_menu_item_id:
        print("\n✅ Database uses 'item_id' - code should match this")
    elif has_menu_item_id and not has_item_id:
        print("\n✅ Database uses 'menu_item_id' - code should match this")
    elif has_item_id and has_menu_item_id:
        print("\n⚠️  Database has both columns - this might cause confusion")
    else:
        print("\n❌ Database schema is unclear or missing columns")
