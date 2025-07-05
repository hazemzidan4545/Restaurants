#!/usr/bin/env python3
"""
Test QR Code Generation Locally
Verifies that QR code generation works with the installed packages
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_qr_generation():
    """Test QR code generation locally"""
    
    print("🧪 Testing QR Code Generation Locally")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        import qrcode
        from PIL import Image
        import io
        import base64
        print("✅ All imports successful")
        
        # Test QR code generation
        print("\n2. Testing QR code generation...")
        test_url = "http://localhost:5000/table/1"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(test_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((300, 300), Image.Resampling.LANCZOS)

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        print(f"✅ QR code generated successfully")
        print(f"   URL: {test_url}")
        print(f"   Image size: {len(img_str)} characters (base64)")
        print(f"   Data URI preview: data:image/png;base64,{img_str[:50]}...")
        
        # Test with Flask app context
        print("\n3. Testing with Flask app context...")
        from app import create_app
        from app.models import Table
        
        app = create_app()
        with app.app_context():
            tables = Table.query.limit(3).all()
            print(f"✅ Found {len(tables)} tables in database")
            
            for table in tables:
                print(f"   Table {table.table_number} (ID: {table.table_id})")
        
        print(f"\n🎉 All tests passed! QR generation should work now.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Try running: pip install qrcode[pil] Pillow")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()

if __name__ == '__main__':
    test_qr_generation()
