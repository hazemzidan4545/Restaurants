#!/usr/bin/env python3
"""
Generate QR codes for all tables that don't have them
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Table, QRCode
from app.extensions import db
from flask import url_for

def generate_qr_codes_for_tables():
    """Generate QR codes for tables that don't have them"""
    app = create_app()
    
    with app.app_context():
        # Get all tables without QR codes
        tables_without_qr = Table.query.outerjoin(QRCode).filter(QRCode.qr_id.is_(None)).all()
        
        print(f"Found {len(tables_without_qr)} tables without QR codes")
        
        created_count = 0
        
        for table in tables_without_qr:
            try:
                # Generate URL for table landing page
                table_url = f"/table/{table.table_id}"
                
                # Create QR code record
                qr_code = QRCode(
                    table_id=table.table_id,
                    url=table_url,
                    qr_type='menu',
                    is_active=True
                )
                
                db.session.add(qr_code)
                created_count += 1
                
                print(f"Created QR code for Table {table.table_number} -> {table_url}")
                
            except Exception as e:
                print(f"Error creating QR code for Table {table.table_number}: {e}")
                db.session.rollback()
                continue
        
        if created_count > 0:
            db.session.commit()
            print(f"\nSuccessfully created {created_count} QR codes")
        else:
            print("No QR codes were created")
        
        # Verify results
        total_tables = Table.query.count()
        total_qr_codes = QRCode.query.count()
        tables_with_qr = Table.query.join(QRCode).count()
        
        print(f"\nFinal status:")
        print(f"Total tables: {total_tables}")
        print(f"Total QR codes: {total_qr_codes}")
        print(f"Tables with QR codes: {tables_with_qr}")

if __name__ == '__main__':
    generate_qr_codes_for_tables()
