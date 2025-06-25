from app import create_app
from app.extensions import db
from sqlalchemy import text
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'development')

with app.app_context():
    try:
        print("Fixing order status values...")
        
        # Check current status values
        result = db.session.execute(text("SELECT DISTINCT status FROM orders"))
        current_statuses = [row[0] for row in result.fetchall()]
        print(f"Current status values: {current_statuses}")
        
        # Update uppercase to lowercase
        updates = [
            ("UPDATE orders SET status = 'new' WHERE status = 'NEW'", 'NEW -> new'),
            ("UPDATE orders SET status = 'processing' WHERE status = 'PROCESSING'", 'PROCESSING -> processing'),
            ("UPDATE orders SET status = 'preparing' WHERE status = 'PREPARING'", 'PREPARING -> preparing'),
            ("UPDATE orders SET status = 'ready' WHERE status = 'READY'", 'READY -> ready'),
            ("UPDATE orders SET status = 'completed' WHERE status = 'COMPLETED'", 'COMPLETED -> completed'),
            ("UPDATE orders SET status = 'cancelled' WHERE status = 'CANCELLED'", 'CANCELLED -> cancelled')
        ]
        
        for sql, description in updates:
            result = db.session.execute(text(sql))
            if result.rowcount > 0:
                print(f"Updated {result.rowcount} orders: {description}")
        
        db.session.commit()
        print("Database fix completed!")
        
        # Verify the fix
        result = db.session.execute(text("SELECT DISTINCT status FROM orders"))
        new_statuses = [row[0] for row in result.fetchall()]
        print(f"Updated status values: {new_statuses}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
