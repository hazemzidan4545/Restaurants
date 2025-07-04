#!/usr/bin/env python3
"""
Complete System Analysis for Table Management Features
Run this before implementing table management enhancements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import *
from app.extensions import db
from sqlalchemy import text
import json

def analyze_database_schema():
    """Analyze current database schema for table management"""
    print("=== DATABASE SCHEMA ANALYSIS ===")
    
    # Check table columns
    tables_columns = db.session.execute(text("PRAGMA table_info(tables)")).fetchall()
    print(f"Tables table columns: {len(tables_columns)}")
    for col in tables_columns:
        print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
    
    # Check QR codes columns  
    qr_columns = db.session.execute(text("PRAGMA table_info(qr_codes)")).fetchall()
    print(f"\nQR Codes table columns: {len(qr_columns)}")
    for col in qr_columns:
        print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
    
    # Check Orders table for table_id
    orders_columns = db.session.execute(text("PRAGMA table_info(orders)")).fetchall()
    table_id_in_orders = any(col[1] == 'table_id' for col in orders_columns)
    print(f"\nOrders table has table_id column: {table_id_in_orders}")
    
    # Check ServiceRequests table for table_id
    service_columns = db.session.execute(text("PRAGMA table_info(service_requests)")).fetchall()
    table_id_in_service = any(col[1] == 'table_id' for col in service_columns)
    print(f"Service Requests table has table_id column: {table_id_in_service}")
    
    # Check if TableSession table exists
    try:
        session_columns = db.session.execute(text("PRAGMA table_info(table_sessions)")).fetchall()
        print(f"\nTable Sessions table exists: True")
        print(f"Table Sessions columns: {len(session_columns)}")
        for col in session_columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
    except Exception:
        print(f"\nTable Sessions table exists: False")

def analyze_current_data():
    """Analyze current data state"""
    print("\n=== CURRENT DATA ANALYSIS ===")
    
    # Tables analysis
    tables = Table.query.all()
    print(f"Total tables: {len(tables)}")
    
    tables_with_qr = []
    tables_without_qr = []
    
    for table in tables:
        qr_count = QRCode.query.filter_by(table_id=table.table_id).count()
        if qr_count > 0:
            tables_with_qr.append(table.table_number)
        else:
            tables_without_qr.append(table.table_number)
    
    print(f"Tables with QR codes: {len(tables_with_qr)} - {tables_with_qr}")
    print(f"Tables without QR codes: {len(tables_without_qr)} - {tables_without_qr}")
    
    # Orders with/without table assignment
    orders_with_table = Order.query.filter(Order.table_id.isnot(None)).count()
    orders_without_table = Order.query.filter(Order.table_id.is_(None)).count()
    print(f"\nOrders with table assignment: {orders_with_table}")
    print(f"Orders without table assignment: {orders_without_table}")
    
    # Service requests with table
    service_with_table = ServiceRequest.query.filter(ServiceRequest.table_id.isnot(None)).count()
    total_service_requests = ServiceRequest.query.count()
    print(f"\nService requests with table: {service_with_table}/{total_service_requests}")

def analyze_routes():
    """Analyze existing routes"""
    print("\n=== ROUTES ANALYSIS ===")
    
    # Check route files
    routes_to_check = [
        ('/admin/api/tables', 'app/modules/admin/routes.py'),
        ('/admin/api/tables/<int:table_id>', 'app/modules/admin/routes.py'),
        ('/table/<int:table_id>', 'app/main/routes.py'),
        ('/api/table-session', 'app/api/routes.py'),
    ]
    
    for route, file_path in routes_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if route.replace('<int:table_id>', '') in content:
                    print(f"✅ {route} - Found in {file_path}")
                else:
                    print(f"❌ {route} - Missing from {file_path}")
        except FileNotFoundError:
            print(f"❌ {route} - File {file_path} not found")

def analyze_templates():
    """Analyze template files"""
    print("\n=== TEMPLATES ANALYSIS ===")
    
    templates_to_check = [
        'app/templates/table_landing.html',
        'app/modules/admin/templates/qr_codes.html',
    ]
    
    for template in templates_to_check:
        if os.path.exists(template):
            print(f"✅ {template} - Exists")
            # Check for key functionality
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'table_landing.html' in template:
                    if 'table_id' in content:
                        print(f"   - Contains table_id reference")
                    if 'qr' in content.lower():
                        print(f"   - Contains QR code references")
                elif 'qr_codes.html' in template:
                    if 'generateQR' in content:
                        print(f"   - Contains QR generation functionality")
                    if 'modal' in content.lower():
                        print(f"   - Contains modal functionality")
        else:
            print(f"❌ {template} - Missing")

def analyze_missing_features():
    """Analyze what features need to be implemented"""
    print("\n=== MISSING FEATURES ANALYSIS ===")
    
    missing_features = []
    
    # Check for table session tracking
    if not hasattr(db.Model, 'TableSession'):
        missing_features.append("TableSession model for session tracking")
    
    # Check for customer table route
    try:
        with open('app/main/routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if '/table/' not in content:
                missing_features.append("Customer table landing route (/table/<int:table_id>)")
    except FileNotFoundError:
        missing_features.append("Main routes file missing")
    
    # Check for table session API
    try:
        with open('app/api/routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'table-session' not in content:
                missing_features.append("Table session API endpoint (/api/table-session)")
    except FileNotFoundError:
        missing_features.append("API routes file missing")
    
    # Check if QR codes exist for tables
    tables_without_qr = Table.query.outerjoin(QRCode).filter(QRCode.qr_id.is_(None)).count()
    if tables_without_qr > 0:
        missing_features.append(f"QR codes for {tables_without_qr} tables")
    
    if missing_features:
        print("Missing features that need implementation:")
        for i, feature in enumerate(missing_features, 1):
            print(f"{i}. {feature}")
    else:
        print("✅ All core features appear to be implemented")

def generate_implementation_plan():
    """Generate implementation plan based on analysis"""
    print("\n=== IMPLEMENTATION PLAN ===")
    
    plan_steps = [
        "1. Create TableSession model for session tracking",
        "2. Implement /table/<int:table_id> customer route in main/routes.py",
        "3. Implement /api/table-session endpoint in api/routes.py", 
        "4. Generate QR codes for all tables without them",
        "5. Update order creation to include table context",
        "6. Update service request creation to include table context",
        "7. Add table session management to admin panel",
        "8. Test end-to-end QR code scanning workflow"
    ]
    
    for step in plan_steps:
        print(step)

def main():
    """Run complete system analysis"""
    app = create_app()
    
    with app.app_context():
        print("COMPLETE SYSTEM ANALYSIS FOR TABLE MANAGEMENT")
        print("=" * 60)
        
        try:
            analyze_database_schema()
            analyze_current_data()
            analyze_routes()
            analyze_templates()
            analyze_missing_features()
            generate_implementation_plan()
            
            print("\n" + "=" * 60)
            print("ANALYSIS COMPLETE")
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
