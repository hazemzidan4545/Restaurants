#!/usr/bin/env python3

from app import create_app
from app.extensions import db
from app.models import Order
import os

def check_and_fix_order_status():
    app = create_app(os.getenv('FLASK_CONFIG') or 'development')
    
    with app.app_context():
        print("Checking order status values...")
        
        # Get all orders and check their raw status values
        try:
            result = db.session.execute('SELECT id, status FROM orders')
            orders_data = result.fetchall()
            
            uppercase_orders = []
            for order_id, status in orders_data:
                if status and status.isupper():
                    uppercase_orders.append((order_id, status))
            
            print(f"Found {len(uppercase_orders)} orders with uppercase status values:")
            for order_id, status in uppercase_orders:
                print(f"  Order {order_id}: '{status}'")
            
            if uppercase_orders:
                print("\nFixing uppercase status values...")
                
                # Update all uppercase status values to lowercase
                for order_id, status in uppercase_orders:
                    lowercase_status = status.lower()
                    print(f"  Updating order {order_id}: '{status}' -> '{lowercase_status}'")
                    db.session.execute(
                        'UPDATE orders SET status = ? WHERE id = ?', 
                        (lowercase_status, order_id)
                    )
                
                db.session.commit()
                print(f"\nSuccessfully updated {len(uppercase_orders)} orders!")
            else:
                print("No uppercase status values found. All orders are properly formatted.")
                
        except Exception as e:
            print(f"Error checking/fixing status values: {e}")
            db.session.rollback()

if __name__ == '__main__':
    check_and_fix_order_status()
