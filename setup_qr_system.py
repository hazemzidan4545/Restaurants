#!/usr/bin/env python3
"""
Setup and Generate QR Codes
Installs dependencies and generates QR codes for all tables
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required packages for QR code generation"""
    required_packages = [
        'qrcode[pil]',
        'Pillow'
    ]
    
    print("Installing QR code dependencies...")
    
    for package in required_packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {package}: {e}")
            return False
    
    return True

def update_database_schema():
    """Update database to include QR image data column"""
    print("\nUpdating database schema...")
    
    try:
        # Run the table session creation script
        subprocess.run([sys.executable, 'create_table_session_db.py'], check=True)
        print("✅ Database schema updated")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error updating database: {e}")
        return False

def generate_qr_codes():
    """Generate QR codes for all tables"""
    print("\nGenerating QR codes for all tables...")
    
    try:
        subprocess.run([sys.executable, 'qr_generator.py'], check=True)
        print("✅ QR codes generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating QR codes: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 QR CODE SYSTEM SETUP")
    print("=" * 40)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies. Please install manually:")
        print("pip install qrcode[pil] Pillow")
        return False
    
    # Step 2: Update database schema
    if not update_database_schema():
        print("\n❌ Failed to update database schema")
        return False
    
    # Step 3: Generate QR codes
    if not generate_qr_codes():
        print("\n❌ Failed to generate QR codes")
        return False
    
    print("\n🎉 QR CODE SYSTEM SETUP COMPLETE!")
    print("=" * 40)
    print("✅ Dependencies installed")
    print("✅ Database schema updated")
    print("✅ QR codes generated for all tables")
    print("\nYour QR code system is now ready!")
    print("- Visit /admin/qr-codes to manage QR codes")
    print("- Download individual or all QR codes")
    print("- QR codes link to /table/{id} for customer access")
    
    return True

if __name__ == '__main__':
    main()
