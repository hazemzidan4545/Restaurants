#!/usr/bin/env python3
"""
Quick status check for the restaurant system
"""

from app import create_app
from app.models import User, Order, OrderItem, MenuItem, Table, ServiceRequest
from app.extensions import db

def check_system_status():
    app = create_app()
    
    with app.app_context():
        print("=== RESTAURANT SYSTEM STATUS CHECK ===\n")
        
        # Check users
        users = User.query.all()
        print(f"Total Users: {len(users)}")
        for user in users:
            order_count = Order.query.filter_by(user_id=user.user_id).count()
            print(f"  - {user.username} ({user.role}): {order_count} orders")
        print()
        
        # Check orders
        orders = Order.query.all()
        print(f"Total Orders: {len(orders)}")
        if orders:
            print("Recent orders:")
            recent_orders = Order.query.order_by(Order.order_time.desc()).limit(5).all()
            for order in recent_orders:
                user = User.query.get(order.user_id)
                username = user.username if user else f"Unknown (ID: {order.user_id})"
                print(f"  - Order #{order.order_id}: {username}, Status: {order.status}, Amount: ${order.total_amount}")
        print()
        
        # Check order items
        order_items = OrderItem.query.all()
        print(f"Total Order Items: {len(order_items)}")
        print()
        
        # Check menu items
        menu_items = MenuItem.query.all()
        available_items = MenuItem.query.filter_by(status='available').count()
        print(f"Total Menu Items: {len(menu_items)} ({available_items} available)")
        print()
        
        # Check tables
        tables = Table.query.all()
        print(f"Total Tables: {len(tables)}")
        if tables:
            occupied_tables = Table.query.filter_by(status='occupied').count()
            available_tables = Table.query.filter_by(status='available').count()
            print(f"  - Available: {available_tables}")
            print(f"  - Occupied: {occupied_tables}")
        print()
        
        # Check service requests
        service_requests = ServiceRequest.query.all()
        pending_requests = ServiceRequest.query.filter_by(status='pending').count()
        print(f"Total Service Requests: {len(service_requests)} ({pending_requests} pending)")
        print()
        
        print("=== STATUS CHECK COMPLETE ===")

if __name__ == "__main__":
    check_system_status()
