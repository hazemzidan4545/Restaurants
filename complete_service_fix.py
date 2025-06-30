#!/usr/bin/env python3
"""
Complete database setup and service request fix
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Complete database setup for service requests"""
    try:
        from app import create_app
        from app.extensions import db
        from app.models import User, Table, ServiceRequest
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("🔧 Setting up database for service requests...")
            
            # 1. Create all tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Tables created/verified")
            
            # 2. Check and add description column if missing
            try:
                result = db.session.execute(text("""
                    SELECT COUNT(*) 
                    FROM pragma_table_info('service_requests') 
                    WHERE name = 'description'
                """)).scalar()
                
                if result == 0:
                    print("➕ Adding description column...")
                    db.session.execute(text("""
                        ALTER TABLE service_requests 
                        ADD COLUMN description TEXT
                    """))
                    db.session.commit()
                    print("✅ Description column added")
                else:
                    print("✅ Description column already exists")
            except Exception as e:
                print(f"⚠️  Column check error (might be normal): {e}")
            
            # 3. Create system user if not exists
            system_user = User.query.filter_by(email='system@restaurant.com').first()
            if not system_user:
                print("👤 Creating system user...")
                system_user = User(
                    name='System User',
                    email='system@restaurant.com',
                    role='customer'
                )
                system_user.set_password('system123')
                db.session.add(system_user)
                db.session.commit()
                print("✅ System user created")
            else:
                print("✅ System user already exists")
            
            # 4. Create tables 1-10 if not exist
            for i in range(1, 11):
                table = Table.query.filter_by(table_id=i).first()
                if not table:
                    table = Table(
                        table_number=str(i),
                        capacity=4,
                        status='available'
                    )
                    db.session.add(table)
            
            db.session.commit()
            print("✅ Tables 1-10 created/verified")
            
            # 5. Test service request creation
            print("🧪 Testing service request creation...")
            
            test_request = ServiceRequest(
                user_id=system_user.user_id,
                table_id=1,
                request_type='test',
                description='Database setup test',
                status='pending'
            )
            
            db.session.add(test_request)
            db.session.commit()
            
            print(f"✅ Test request created with ID: {test_request.request_id}")
            
            # Clean up test request
            db.session.delete(test_request)
            db.session.commit()
            print("✅ Test request cleaned up")
            
            return True
            
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api():
    """Test the service request API"""
    try:
        from app import create_app
        from app.modules.service.api import create_service_request_api
        import json
        
        app = create_app()
        create_service_request_api(app)
        
        with app.test_client() as client:
            print("\n🧪 Testing service request API...")
            
            # Test service request
            test_data = {
                "table_id": 5,
                "request_type": "waiter",
                "description": "API test request"
            }
            
            response = client.post('/service/api/request',
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Service request successful!")
                print(f"   Request ID: {data.get('request_id')}")
                print(f"   Table: {data.get('table_id')}")
                print(f"   Type: {data.get('type')}")
                return True
            else:
                print(f"❌ Service request failed")
                print(f"   Response: {response.get_data(as_text=True)}")
                return False
                
    except Exception as e:
        print(f"❌ API test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Complete Service Request Setup")
    print("=" * 40)
    
    # Step 1: Setup database
    db_ok = setup_database()
    
    if db_ok:
        # Step 2: Test API
        api_ok = test_api()
        
        print("\n" + "=" * 40)
        if api_ok:
            print("🎉 Service requests are now working!")
            print("\n✅ What was fixed:")
            print("  - Database tables created/verified")
            print("  - Description column added to service_requests")
            print("  - System user created for anonymous requests")
            print("  - Tables 1-10 created/verified")
            print("  - API tested and working")
            print("\n🚀 Users can now request services successfully!")
        else:
            print("❌ API test failed - please check the error messages")
    else:
        print("❌ Database setup failed - please check the error messages")
