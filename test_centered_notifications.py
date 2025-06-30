#!/usr/bin/env python3
"""
Test script to verify centered notifications work properly
"""

from app import create_app
from app.models import Service
from app.extensions import db

def test_delete_notification():
    """Test that delete notifications appear correctly"""
    app = create_app()
    
    with app.app_context():
        # Create a test service to delete
        test_service = Service(
            name="Test Notification Service",
            icon="fas fa-test",
            description="This service will be deleted to test notifications",
            is_active=True,
            display_order=999
        )
        
        try:
            db.session.add(test_service)
            db.session.commit()
            print(f"✓ Created test service: {test_service.name} (ID: {test_service.service_id})")
            
            print("\n🎯 To test the centered delete notification:")
            print(f"1. Go to http://localhost:5000/admin/services")
            print(f"2. Find the service '{test_service.name}'")
            print(f"3. Click the Delete button")
            print(f"4. Confirm deletion in the modal")
            print(f"5. The delete notification should appear in the CENTER of the page")
            print(f"6. The notification should auto-disappear after 5 seconds")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating test service: {e}")

if __name__ == "__main__":
    test_delete_notification()
