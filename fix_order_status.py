#!/usr/bin/env python3
"""
Fix order status values in database
Convert uppercase status values to lowercase to match enum definition
"""

import os
import sys
from app import create_app
from app.extensions import db
from app.models import Order

def fix_order_status():
    """Convert all uppercase order status values to lowercase"""
    
    app = create_app(os.getenv('FLASK_CONFIG') or 'development')
    
    with app.app_context():
        print("Starting order status fix...")
        
        # Define the mapping from uppercase to lowercase
        status_mapping = {
            'NEW': 'new',
            'PROCESSING': 'processing', 
            'PREPARING': 'preparing',
            'READY': 'ready',
            'COMPLETED': 'completed',
            'CANCELLED': 'cancelled'
        }
        
        try:
            # Get all orders with uppercase status values
            orders_to_fix = []
            
            # Use raw SQL to avoid the enum validation issue
            result = db.session.execute(
                "SELECT order_id, status FROM orders WHERE status IN ('NEW', 'PROCESSING', 'PREPARING', 'READY', 'COMPLETED', 'CANCELLED')"
            )
            
            orders_to_fix = result.fetchall()
            
            if not orders_to_fix:
                print("No orders found with uppercase status values.")
                return
            
            print(f"Found {len(orders_to_fix)} orders with uppercase status values.")
            
            # Update each order using raw SQL to avoid enum validation
            for order_id, current_status in orders_to_fix:
                new_status = status_mapping.get(current_status)
                if new_status:
                    print(f"Updating order {order_id}: {current_status} -> {new_status}")
                    db.session.execute(
                        "UPDATE orders SET status = :new_status WHERE order_id = :order_id",
                        {"new_status": new_status, "order_id": order_id}
                    )
            
            # Commit all changes
            db.session.commit()
            print(f"Successfully updated {len(orders_to_fix)} orders.")
            
        except Exception as e:
            print(f"Error fixing order status: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    fix_order_status()
    print("Order status fix completed successfully!")
