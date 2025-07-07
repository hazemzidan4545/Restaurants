"""
Simple script to initialize the database
"""

import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_db():
    """Initialize the database with all tables"""
    try:
        from app import create_app
        from app.extensions import db
        
        print("Creating Flask app...")
        app = create_app()
        
        print("Initializing database...")
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if tables exist
            from sqlalchemy import text
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = result.fetchall()

            print(f"Created {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
                
            return True
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Database Initialization Script")
    print("=" * 40)
    
    success = init_db()
    
    if success:
        print("\n🎉 Database initialization completed successfully!")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)
