#!/usr/bin/env python3
"""
Check database structure
"""

import sqlite3
import os

def check_database(db_path):
    """Check database structure"""
    print(f"\n📍 Checking {db_path}:")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        # Check menu_items table specifically
        if 'menu_items' in tables:
            cursor.execute("PRAGMA table_info(menu_items)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"menu_items columns: {columns}")
            
            # Check if discount columns exist
            has_discount = 'discount_percentage' in columns
            has_original = 'original_price' in columns
            print(f"Has discount_percentage: {has_discount}")
            print(f"Has original_price: {has_original}")
        else:
            print("❌ menu_items table not found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check both databases
    check_database("instance/restaurant.db")
    check_database("instance/restaurant_dev.db")
