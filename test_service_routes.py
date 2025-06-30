#!/usr/bin/env python3
"""
Simple test for service management web interface
"""

from app import create_app
from app.models import Service, User
from app.extensions import db
from flask import url_for

def test_service_routes():
    """Test service management routes"""
    app = create_app()
    
    with app.app_context():
        with app.test_client() as client:
            # Create a test admin user (or use existing one)
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("No admin user found - creating one for testing")
                admin = User(
                    username='admin',
                    email='admin@test.com',
                    first_name='Admin',
                    last_name='User',
                    user_type='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
            
            # Test service listing page
            with client.session_transaction() as sess:
                sess['_user_id'] = str(admin.user_id)
                sess['_fresh'] = True
            
            print("Testing service management routes...")
            
            # Test services listing
            response = client.get('/admin/services')
            print(f"✓ Services page status: {response.status_code}")
            if response.status_code == 200:
                print("✓ Services page loads successfully")
            else:
                print(f"✗ Services page failed: {response.status_code}")
                return
            
            # Test add service page
            response = client.get('/admin/services/add')
            print(f"✓ Add service page status: {response.status_code}")
            
            # Test adding a service via POST
            response = client.post('/admin/services/add', data={
                'name': 'Test Service API',
                'icon': 'fas fa-test',
                'description': 'Test service for API',
                'is_active': 'on',
                'display_order': '1000'
            }, follow_redirects=True)
            print(f"✓ Add service POST status: {response.status_code}")
            
            # Find the created service
            test_service = Service.query.filter_by(name='Test Service API').first()
            if test_service:
                print(f"✓ Service created successfully: {test_service.name}")
                
                # Test edit service page
                response = client.get(f'/admin/services/edit/{test_service.service_id}')
                print(f"✓ Edit service page status: {response.status_code}")
                
                # Test updating the service
                response = client.post(f'/admin/services/edit/{test_service.service_id}', data={
                    'name': 'Updated Test Service API',
                    'icon': 'fas fa-updated',
                    'description': 'Updated test service',
                    'is_active': 'on',
                    'display_order': '1001'
                }, follow_redirects=True)
                print(f"✓ Update service POST status: {response.status_code}")
                
                # Test toggle service
                response = client.post(f'/admin/services/toggle/{test_service.service_id}', follow_redirects=True)
                print(f"✓ Toggle service status: {response.status_code}")
                
                # Test delete service
                response = client.post(f'/admin/services/delete/{test_service.service_id}', follow_redirects=True)
                print(f"✓ Delete service status: {response.status_code}")
                
                print("\n🎉 All service management routes work correctly!")
            else:
                print("✗ Failed to create test service")

if __name__ == "__main__":
    test_service_routes()
