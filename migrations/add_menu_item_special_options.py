"""
Migration script to add special options to MenuItem model
Run this script to add is_featured, is_spicy, is_vegetarian, is_vegan columns

Usage:
    python migrations/add_menu_item_special_options.py          # Run upgrade
    python migrations/add_menu_item_special_options.py check    # Check if columns exist
"""

import sys
import os
import sqlite3

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def check_column_exists(table_name, column_name):
    """Check if a column exists in the table"""
    app = create_app()

    with app.app_context():
        try:
            # Get database file path
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
            else:
                db_path = db_uri.replace('sqlite://', '')

            print(f"Checking database: {db_path}")

            # Connect directly to SQLite to check schema
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # First check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                print(f"Table {table_name} does not exist")
                conn.close()
                return False

            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # Check if column exists
            column_exists = any(col[1] == column_name for col in columns)

            conn.close()
            return column_exists

        except Exception as e:
            print(f"Error checking column {column_name}: {e}")
            return False

def check_all_columns():
    """Check if all special option columns exist"""
    columns_to_check = ['is_featured', 'is_spicy', 'is_vegetarian', 'is_vegan']
    results = {}

    for column in columns_to_check:
        exists = check_column_exists('menu_items', column)
        results[column] = exists
        print(f"Column '{column}': {'EXISTS' if exists else 'MISSING'}")

    return results

def upgrade():
    """Add special option columns to menu_items table"""
    print("Starting migration: Adding special option columns to menu_items table")

    # Check current state
    print("\nChecking current column state:")
    column_status = check_all_columns()

    columns_to_add = [
        ('is_featured', 'INTEGER DEFAULT 0'),
        ('is_spicy', 'INTEGER DEFAULT 0'),
        ('is_vegetarian', 'INTEGER DEFAULT 0'),
        ('is_vegan', 'INTEGER DEFAULT 0')
    ]

    app = create_app()

    with app.app_context():
        try:
            # Get database file path
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
            else:
                db_path = db_uri.replace('sqlite://', '')

            print(f"Using database: {db_path}")

            # Use direct SQLite connection for more reliable ALTER TABLE
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            for column_name, column_def in columns_to_add:
                if not column_status.get(column_name, False):
                    try:
                        sql = f"ALTER TABLE menu_items ADD COLUMN {column_name} {column_def}"
                        cursor.execute(sql)
                        print(f"✅ Added column: {column_name}")
                    except Exception as e:
                        print(f"❌ Error adding {column_name}: {e}")
                else:
                    print(f"⏭️  Column {column_name} already exists, skipping")

            conn.commit()
            conn.close()

            print("\n🎉 Migration completed successfully!")

            # Verify the changes
            print("\nVerifying changes:")
            check_all_columns()

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            return False

    return True

def downgrade():
    """Remove special option columns from menu_items table"""
    app = create_app()

    with app.app_context():
        try:
            # SQLite doesn't support DROP COLUMN, so we'll recreate the table
            print("Note: SQLite doesn't support DROP COLUMN. Manual table recreation required for downgrade.")
            print("Columns to remove: is_featured, is_spicy, is_vegetarian, is_vegan")

        except Exception as e:
            print(f"Error during downgrade: {e}")
            raise

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'check':
            print("Checking column status:")
            check_all_columns()
        elif command == 'downgrade':
            downgrade()
        elif command == 'upgrade':
            upgrade()
        else:
            print("Usage:")
            print("  python migrations/add_menu_item_special_options.py          # Run upgrade")
            print("  python migrations/add_menu_item_special_options.py check    # Check column status")
            print("  python migrations/add_menu_item_special_options.py upgrade  # Run upgrade")
            print("  python migrations/add_menu_item_special_options.py downgrade # Run downgrade")
    else:
        upgrade()
