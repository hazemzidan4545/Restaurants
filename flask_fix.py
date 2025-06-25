from app import create_app
from app.extensions import db
from app.models import Order
import os

def fix_preparing_status():
    app = create_app(os.getenv('FLASK_CONFIG') or 'development')
    
    with app.app_context():
        print("Fixing preparing status values...")
        
        # Use raw SQL to fix the issue
        try:
            result = db.session.execute("UPDATE orders SET status = 'processing' WHERE status = 'preparing'")
            affected_rows = result.rowcount
            print(f"Updated {affected_rows} orders from 'preparing' to 'processing'")
            
            result = db.session.execute("UPDATE orders SET status = 'processing' WHERE status = 'ready'")
            affected_rows2 = result.rowcount
            print(f"Updated {affected_rows2} orders from 'ready' to 'processing'")
            
            db.session.commit()
            print("Successfully committed changes")
            
            # Verify fix
            distinct_statuses = db.session.execute("SELECT DISTINCT status FROM orders").fetchall()
            print("Current distinct statuses:")
            for status in distinct_statuses:
                print(f"  - {status[0]}")
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    fix_preparing_status()
