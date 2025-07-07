#!/usr/bin/env python3
"""
Check promotional_campaigns table schema
"""

import sqlite3

def check_campaigns_schema():
    """Check the promotional_campaigns table schema"""
    
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/restaurant_dev.db')
        cursor = conn.cursor()
        
        print("🔍 Checking promotional_campaigns table schema...")
        
        # Check promotional_campaigns table schema
        cursor.execute("PRAGMA table_info(promotional_campaigns)")
        columns = cursor.fetchall()
        
        print("\n📋 promotional_campaigns table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
        # Check if new columns exist
        column_names = [col[1] for col in columns]
        
        new_columns = [
            'minimum_order_amount',
            'maximum_uses_per_customer', 
            'total_usage_limit',
            'target_customer_tier',
            'applicable_days',
            'specific_menu_categories',
            'discount_type',
            'discount_value',
            'updated_at'
        ]
        
        print("\n🔍 Checking for new columns:")
        missing_columns = []
        for col in new_columns:
            if col in column_names:
                print(f"  ✅ {col} - EXISTS")
            else:
                print(f"  ❌ {col} - MISSING")
                missing_columns.append(col)
                
        conn.close()
        
        return missing_columns
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []

if __name__ == "__main__":
    missing = check_campaigns_schema()
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} columns: {', '.join(missing)}")
        print("🔧 Need to run migration to add these columns")
    else:
        print("\n✅ All campaign enhancement columns exist in database")
