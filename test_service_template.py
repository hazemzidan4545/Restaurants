#!/usr/bin/env python
from app import create_app
from app.models import Service

app = create_app()

# Test the service route
with app.test_client() as client:
    with app.app_context():
        # Check if services are being fetched
        services = Service.query.filter_by(is_active=True).order_by(Service.display_order, Service.name).all()
        print(f'Active services in database: {len(services)}')
        
        for service in services:
            print(f'- {service.name} (Icon: {service.icon})')
        
        # Test the service route
        response = client.get('/service/')
        print(f'\nService route status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ Service route is working')
            # Check if services are rendered in the template
            if b'service-item' in response.data:
                print('✅ Service items found in template')
                
                # Count how many services are rendered
                service_count = response.data.count(b'service-item')
                print(f'✅ Number of services rendered: {service_count}')
            else:
                print('❌ Service items not found in template')
        else:
            print(f'❌ Service route failed: {response.status_code}')
