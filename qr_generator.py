#!/usr/bin/env python3
"""
QR Code Generator for Restaurant Tables
Creates actual QR codes and stores them in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import qrcode
from PIL import Image
import io
import base64
from app import create_app
from app.models import Table, QRCode
from app.extensions import db

def generate_qr_code_image(data, size=(300, 300)):
    """Generate QR code image and return as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize if needed
    if img.size != size:
        img = img.resize(size, Image.Resampling.LANCZOS)

    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

def create_table_qr_codes():
    """Create QR codes for all tables"""
    app = create_app()
    
    with app.app_context():
        # Get current domain - you can change this to your production domain
        # For development, use localhost. For production, change to your actual domain.
        base_url = "http://localhost:5000"  # Change this to your production domain: https://yourrestaurant.com
        
        tables = Table.query.all()
        created_count = 0
        updated_count = 0
        
        print(f"Processing {len(tables)} tables...")
        
        for table in tables:
            try:
                # Create table URL
                table_url = f"{base_url}/table/{table.table_id}"
                
                # Check if QR code already exists for this table
                existing_qr = QRCode.query.filter_by(table_id=table.table_id).first()
                
                # Generate QR code image
                qr_image_data = generate_qr_code_image(table_url)
                
                if existing_qr:
                    # Update existing QR code
                    existing_qr.url = table_url
                    existing_qr.qr_image_data = qr_image_data
                    existing_qr.is_active = True
                    updated_count += 1
                    print(f"Updated QR code for Table {table.table_number}")
                else:
                    # Create new QR code
                    new_qr = QRCode(
                        table_id=table.table_id,
                        url=table_url,
                        qr_type='menu',
                        is_active=True,
                        qr_image_data=qr_image_data
                    )
                    db.session.add(new_qr)
                    created_count += 1
                    print(f"Created QR code for Table {table.table_number}")
                
            except Exception as e:
                print(f"Error processing Table {table.table_number}: {e}")
                continue
        
        try:
            db.session.commit()
            print(f"\n✅ Successfully processed QR codes:")
            print(f"   Created: {created_count}")
            print(f"   Updated: {updated_count}")
            print(f"   Total: {created_count + updated_count}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error saving to database: {e}")

def generate_single_qr(table_id):
    """Generate QR code for a single table"""
    app = create_app()
    
    with app.app_context():
        table = Table.query.get(table_id)
        if not table:
            return None, "Table not found"
        
        try:
            base_url = "http://localhost:5000"  # Change this to your production domain
            table_url = f"{base_url}/table/{table.table_id}"
            
            # Generate QR code image
            qr_image_data = generate_qr_code_image(table_url)
            
            # Check if QR code exists
            existing_qr = QRCode.query.filter_by(table_id=table.table_id).first()
            
            if existing_qr:
                existing_qr.url = table_url
                existing_qr.qr_image_data = qr_image_data
                existing_qr.is_active = True
            else:
                new_qr = QRCode(
                    table_id=table.table_id,
                    url=table_url,
                    qr_type='menu',
                    is_active=True,
                    qr_image_data=qr_image_data
                )
                db.session.add(new_qr)
            
            db.session.commit()
            return qr_image_data, "Success"
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)

if __name__ == '__main__':
    create_table_qr_codes()
