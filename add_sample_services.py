#!/usr/bin/env python3
"""
Add sample services for testing
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Service

def add_sample_services():
    """Add sample services to test with"""
    app = create_app('development')
    
    with app.app_context():
        # Check if services already exist
        existing_services = Service.query.count()
        if existing_services > 0:
            print(f"Found {existing_services} existing services. Skipping creation.")
            return
        
        # Sample services matching the screenshot design
        services = [
            {
                'name': 'Waiter',
                'icon': 'fas fa-concierge-bell',
                'description': 'Call waiter to your table for assistance',
                'is_active': True,
                'display_order': 1
            },
            {
                'name': 'Request the Bill',
                'icon': 'fas fa-receipt',
                'description': 'Request bill and payment processing',
                'is_active': True,
                'display_order': 2
            },
            {
                'name': 'Extra Napkins',
                'icon': 'fas fa-hands-wash',
                'description': 'Request additional napkins or tissues',
                'is_active': True,
                'display_order': 3
            },
            {
                'name': 'Refill Coats',
                'icon': 'fas fa-redo',
                'description': 'Refill coat check or storage assistance',
                'is_active': True,
                'display_order': 4
            },
            {
                'name': 'Order Ice',
                'icon': 'fas fa-cube',
                'description': 'Request extra ice for drinks',
                'is_active': True,
                'display_order': 5
            },
            {
                'name': 'Adjust AC',
                'icon': 'fas fa-thermometer-half',
                'description': 'Temperature adjustment assistance',
                'is_active': True,
                'display_order': 6
            },
            {
                'name': 'Clean My Table',
                'icon': 'fas fa-broom',
                'description': 'Table cleaning and sanitization',
                'is_active': True,
                'display_order': 7
            },
            {
                'name': 'Custom Request',
                'icon': 'fas fa-comment-alt',
                'description': 'Make a custom service request',
                'is_active': True,
                'display_order': 8
            }
        ]
        
        print("Adding sample services...")
        for service_data in services:
            service = Service(**service_data)
            db.session.add(service)
        
        try:
            db.session.commit()
            print(f"Successfully added {len(services)} sample services!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding services: {e}")

if __name__ == '__main__':
    add_sample_services()
