#!/usr/bin/env python
from app import create_app
from app.models import Service

app = create_app()

# Test the delete modal functionality
with app.test_client() as client:
    with app.app_context():
        # Check if we have services to test with
        services = Service.query.all()
        print(f'Total services in database: {len(services)}')
        
        if services:
            test_service = services[0]
            print(f'Testing with service: {test_service.name} (ID: {test_service.service_id})')
            
            # Test the services management page loads
            response = client.get('/admin/services')
            print(f'Services page status: {response.status_code}')
            
            if response.status_code == 200:
                print('✅ Services management page loads')
                
                # Check if delete modal exists
                if b'deleteModal' in response.data:
                    print('✅ Delete modal found in template')
                else:
                    print('❌ Delete modal not found in template')
                
                # Check if confirmDelete function exists
                if b'confirmDelete' in response.data:
                    print('✅ confirmDelete function found')
                else:
                    print('❌ confirmDelete function not found')
                
                # Check if delete buttons exist
                if b'delete-btn' in response.data:
                    print('✅ Delete buttons found')
                else:
                    print('❌ Delete buttons not found')
                    
                # Test the delete route (but don't actually delete)
                print(f'✅ Delete route would be: /admin/services/delete/{test_service.service_id}')
            else:
                print(f'❌ Services page failed: {response.status_code}')
        else:
            print('❌ No services found to test with')
