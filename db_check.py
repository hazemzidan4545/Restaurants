import sqlite3
import os

# Change to the correct directory
os.chdir(r'c:\Users\zezo_\OneDrive\Desktop\WORK\Resturant\Restaurants')

try:
    # Connect to the database
    conn = sqlite3.connect('instance/restaurant_dev.db')
    cursor = conn.cursor()
    
    print("Successfully connected to database")
    
    # Check order_items table schema
    cursor.execute("PRAGMA table_info(order_items)")
    columns = cursor.fetchall()
    
    print("\norder_items table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
        
    # Look for the specific columns we care about
    column_names = [col[1] for col in columns]
    
    if 'item_id' in column_names:
        print("\n✅ Database has 'item_id' column")
    
    if 'menu_item_id' in column_names:
        print("\n✅ Database has 'menu_item_id' column")
        
    if 'item_id' not in column_names and 'menu_item_id' not in column_names:
        print("\n❌ Database missing both item_id and menu_item_id columns!")
    
    # Check menu_items table too
    cursor.execute("PRAGMA table_info(menu_items)")
    menu_columns = cursor.fetchall()
    
    print("\nmenu_items table columns:")
    for col in menu_columns:
        print(f"  {col[1]} ({col[2]})")
    
    conn.close()
    print("\nDatabase schema check complete")
    
except Exception as e:
    print(f"Error: {e}")
    
input("Press Enter to continue...")
