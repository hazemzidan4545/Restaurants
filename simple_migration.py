"""
Simple migration script to add special option columns
"""

import sys
import os
import sqlite3

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_migration():
    """Run the migration to add special option columns"""
    try:
        from app import create_app
        from app.extensions import db
        
        print("Creating Flask app...")
        app = create_app()
        
        with app.app_context():
            print("Initializing database...")
            # First, create all tables
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Get database path
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
            else:
                db_path = db_uri.replace('sqlite://', '')
            
            print(f"Using database: {db_path}")
            
            # Connect directly to SQLite
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if menu_items table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menu_items'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                print("❌ menu_items table does not exist")
                conn.close()
                return False
            
            print("✅ menu_items table found")
            
            # Check current columns
            cursor.execute("PRAGMA table_info(menu_items)")
            columns = cursor.fetchall()
            existing_columns = [col[1] for col in columns]
            
            print(f"Existing columns: {len(existing_columns)}")
            
            # Add new columns if they don't exist
            columns_to_add = [
                ('is_featured', 'INTEGER DEFAULT 0'),
                ('is_spicy', 'INTEGER DEFAULT 0'),
                ('is_vegetarian', 'INTEGER DEFAULT 0'),
                ('is_vegan', 'INTEGER DEFAULT 0')
            ]
            
            for column_name, column_def in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE menu_items ADD COLUMN {column_name} {column_def}"
                        cursor.execute(sql)
                        print(f"✅ Added column: {column_name}")
                    except Exception as e:
                        print(f"❌ Error adding {column_name}: {e}")
                else:
                    print(f"⏭️  Column {column_name} already exists")
            
            conn.commit()
            conn.close()
            
            print("🎉 Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Simple Migration Script")
    print("=" * 40)
    
    success = run_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
