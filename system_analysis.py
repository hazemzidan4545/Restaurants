#!/usr/bin/env python3
"""
Complete System Analysis for QR Code Table Management Implementation
"""

from app import create_app
from app.models import db, Table, Order, User, OrderItem, MenuItem, QRCode, Service, ServiceRequest, Payment
from sqlalchemy import text
import os

def analyze_system():
    app = create_app()
    with app.app_context():
        print('=== COMPLETE SYSTEM ANALYSIS ===')
        
        # 1. Database Tables Analysis
        print('\n1. DATABASE SCHEMA ANALYSIS:')
        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables_in_db = [row[0] for row in result.fetchall()]
        print(f'   Tables in database: {tables_in_db}')
        
        # 2. Current Tables Analysis
        print('\n2. RESTAURANT TABLES ANALYSIS:')
        tables = Table.query.all()
        print(f'   Total tables: {len(tables)}')
        if tables:
            for table in tables[:10]:
                orders_count = Order.query.filter_by(table_id=table.table_id).count()
                qr_count = QRCode.query.filter_by(table_id=table.table_id).count()
                print(f'   - Table {table.table_number}: {table.status}, capacity: {table.capacity}, orders: {orders_count}, QRs: {qr_count}')
        else:
            print('   No tables found in database')
        
        # 3. QR Codes Analysis
        print('\n3. QR CODES ANALYSIS:')
        qr_codes = QRCode.query.all()
        print(f'   Total QR codes: {len(qr_codes)}')
        if qr_codes:
            for qr in qr_codes[:5]:
                print(f'   - QR {qr.qr_id}: Table {qr.table_id}, Type: {qr.qr_type}, Active: {qr.is_active}')
                print(f'     URL: {qr.url}')
        else:
            print('   No QR codes found in database')
        
        # 4. Orders Analysis
        print('\n4. ORDERS ANALYSIS:')
        total_orders = Order.query.count()
        orders_with_tables = Order.query.filter(Order.table_id.isnot(None)).count()
        recent_orders = Order.query.order_by(Order.order_time.desc()).limit(5).all()
        print(f'   Total orders: {total_orders}')
        print(f'   Orders with tables: {orders_with_tables}')
        print(f'   Recent orders:')
        for order in recent_orders:
            table_info = f'Table {order.table.table_number}' if order.table else 'No table'
            customer_name = order.customer.name if order.customer else 'Unknown'
            print(f'   - Order #{order.order_id}: {order.status}, {table_info}, Customer: {customer_name}')
        
        # 5. Services Analysis
        print('\n5. SERVICES ANALYSIS:')
        services = Service.query.all()
        service_requests = ServiceRequest.query.count()
        print(f'   Total services: {len(services)}')
        print(f'   Total service requests: {service_requests}')
        
        # 6. Users Analysis
        print('\n6. USERS ANALYSIS:')
        customers = User.query.filter_by(role='customer').count()
        admins = User.query.filter_by(role='admin').count()
        waiters = User.query.filter_by(role='waiter').count()
        print(f'   Customers: {customers}, Admins: {admins}, Waiters: {waiters}')
        
        # 7. Check for missing components
        print('\n7. MISSING COMPONENTS ANALYSIS:')
        missing_components = []
        
        # Check if tables exist
        if len(tables) == 0:
            missing_components.append('No restaurant tables defined')
        
        # Check if QR codes exist for tables
        if len(tables) > 0 and len(qr_codes) == 0:
            missing_components.append('No QR codes generated for tables')
        
        # Check table-QR mapping
        tables_without_qr = []
        for table in tables:
            qr_count = QRCode.query.filter_by(table_id=table.table_id).count()
            if qr_count == 0:
                tables_without_qr.append(table.table_number)
        
        if tables_without_qr:
            missing_components.append(f'Tables without QR codes: {", ".join(tables_without_qr)}')
        
        if missing_components:
            for component in missing_components:
                print(f'   ❌ {component}')
        else:
            print('   ✅ All basic components present')
        
        # 8. Routes Analysis
        print('\n8. ROUTES ANALYSIS:')
        routes_to_check = [
            '/admin/api/tables',
            '/admin/api/tables/<int:table_id>',
            '/table/<int:table_id>',
            '/api/table-session'
        ]
        print('   Routes that need to be implemented:')
        for route in routes_to_check:
            print(f'   - {route}')
        
        # 9. Files Analysis
        print('\n9. FILES ANALYSIS:')
        files_to_check = [
            'app/modules/admin/routes.py',
            'app/main/routes.py',
            'app/api/routes.py',
            'app/templates/table_landing.html'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f'   ✅ {file_path} exists')
            else:
                print(f'   ❌ {file_path} missing')
        
        return {
            'tables_count': len(tables),
            'qr_codes_count': len(qr_codes),
            'orders_count': total_orders,
            'missing_components': missing_components
        }

if __name__ == '__main__':
    try:
        results = analyze_system()
        print('\n=== ANALYSIS COMPLETE ===')
        print(f'System has {results["tables_count"]} tables, {results["qr_codes_count"]} QR codes, {results["orders_count"]} orders')
        if results['missing_components']:
            print(f'Found {len(results["missing_components"])} missing components that need implementation')
        else:
            print('System appears to be complete')
    except Exception as e:
        print(f'Analysis failed: {e}')
        import traceback
        traceback.print_exc()
