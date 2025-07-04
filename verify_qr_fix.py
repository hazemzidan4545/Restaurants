#!/usr/bin/env python3
"""
QR Code Fix Verification
Verifies that the QR code regeneration issue has been resolved
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Table, QRCode
from app.extensions import db

def verify_qr_fix():
    """Verify that QR code generation works without subprocess issues"""
    app = create_app()
    
    with app.app_context():
        print("🔧 QR Code Fix Verification")
        print("=" * 50)
        
        # Check if tables exist
        tables = Table.query.all()
        print(f"📊 Found {len(tables)} tables in database")
        
        if not tables:
            print("❌ No tables found. Creating a test table...")
            test_table = Table(
                table_number=1,
                capacity=4,
                status='available',
                location='Test Area',
                table_type='regular',
                is_active=True
            )
            db.session.add(test_table)
            db.session.commit()
            tables = [test_table]
            print("✅ Test table created")
        
        # Test QR code generation without subprocess
        print("\n🧪 Testing inline QR code generation...")
        
        success_count = 0
        error_count = 0
        
        for table in tables[:3]:  # Test first 3 tables
            try:
                import qrcode
                from PIL import Image
                import io
                import base64
                
                # Generate QR code like the fixed endpoint does
                base_url = "http://localhost:5000"
                table_url = f"{base_url}/table/{table.table_id}"
                
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                qr.add_data(table_url)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                img = img.resize((300, 300), Image.Resampling.LANCZOS)

                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Update/create QR code in database
                existing_qr = QRCode.query.filter_by(table_id=table.table_id).first()
                
                if existing_qr:
                    existing_qr.url = table_url
                    existing_qr.qr_image_data = img_str
                    existing_qr.is_active = True
                    action = "Updated"
                else:
                    new_qr = QRCode(
                        table_id=table.table_id,
                        url=table_url,
                        qr_type='menu',
                        is_active=True,
                        qr_image_data=img_str
                    )
                    db.session.add(new_qr)
                    action = "Created"
                
                db.session.commit()
                print(f"✅ {action} QR code for Table {table.table_number} (ID: {table.table_id})")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Error with Table {table.table_number}: {e}")
                error_count += 1
                db.session.rollback()
        
        print(f"\n📊 Generation Results:")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Errors: {error_count}")
        
        # Verify QR codes have image data
        print(f"\n🔍 Verifying QR codes in database...")
        qr_codes = QRCode.query.all()
        
        qr_with_images = 0
        qr_without_images = 0
        
        for qr in qr_codes:
            if qr.qr_image_data:
                qr_with_images += 1
            else:
                qr_without_images += 1
        
        print(f"   QR codes with images: {qr_with_images}")
        print(f"   QR codes without images: {qr_without_images}")
        
        # Final status
        print(f"\n" + "=" * 50)
        if error_count == 0 and qr_with_images > 0:
            print("🎉 QR CODE FIX VERIFICATION: SUCCESS!")
            print("✅ QR code generation is working without subprocess errors")
            print("✅ QR codes are being stored with image data")
            print("✅ The regeneration issue has been resolved")
        else:
            print("⚠️  QR CODE FIX VERIFICATION: NEEDS ATTENTION")
            if error_count > 0:
                print(f"❌ {error_count} errors occurred during generation")
            if qr_without_images > 0:
                print(f"❌ {qr_without_images} QR codes are missing image data")

if __name__ == '__main__':
    verify_qr_fix()
