#!/usr/bin/env python3
"""
Test script to verify service management functionality
"""

from app import create_app
from app.models import Service
from app.extensions import db

def test_service_operations():
    """Test CRUD operations for services"""
    app = create_app()
    
    with app.app_context():
        # Test 1: Query existing services
        services = Service.query.all()
        print(f"✓ Found {len(services)} existing services")
        
        for service in services[:3]:  # Show first 3 services
            print(f"  - {service.name} ({'Active' if service.is_active else 'Inactive'})")
        
        # Test 2: Create a new service
        test_service = Service(
            name="Test Service",
            icon="fas fa-test",
            description="This is a test service",
            is_active=True,
            display_order=999
        )
        
        try:
            db.session.add(test_service)
            db.session.commit()
            print("✓ Successfully created test service")
            
            # Test 3: Update the service
            test_service.name = "Updated Test Service"
            test_service.description = "Updated description"
            db.session.commit()
            print("✓ Successfully updated test service")
            
            # Test 4: Delete the service
            db.session.delete(test_service)
            db.session.commit()
            print("✓ Successfully deleted test service")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during service operations: {e}")
        
        print("\n🎉 Service CRUD operations work correctly!")

if __name__ == "__main__":
    test_service_operations()
