#!/usr/bin/env python3
"""
Database migration script for Service model
"""

from app import create_app
from app.models import Service, ServiceRequest
from app.extensions import db

def check_and_update_database():
    """Check database schema and update if needed"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if we can access services
            services = Service.query.all()
            print(f"✓ Services table exists with {len(services)} records")
            
            # Try to check the service_requests relationship
            first_service = services[0] if services else None
            if first_service:
                # Test the relationship safely
                try:
                    request_count = first_service.service_requests.count()
                    print(f"✓ Service requests relationship works ({request_count} requests for '{first_service.name}')")
                except Exception as e:
                    print(f"✗ Service requests relationship error: {e}")
                    print("This suggests the foreign key relationship needs to be fixed.")
            
            # Check ServiceRequest table structure
            try:
                service_requests = ServiceRequest.query.all()
                print(f"✓ ServiceRequest table exists with {len(service_requests)} records")
                
                # Check if service_id column exists
                if service_requests:
                    first_request = service_requests[0]
                    print(f"✓ First service request: ID={first_request.request_id}, Service ID={getattr(first_request, 'service_id', 'NOT FOUND')}")
            except Exception as e:
                print(f"✗ ServiceRequest table error: {e}")
            
        except Exception as e:
            print(f"✗ Database error: {e}")
            print("Creating tables...")
            
            # Create all tables
            db.create_all()
            print("✓ Database tables created/updated")

if __name__ == "__main__":
    check_and_update_database()
