#!/usr/bin/env python3
"""
Script to verify all admin endpoints referenced in base template exist
"""

import sys
import re
from app import create_app
from flask import url_for

def verify_admin_endpoints():
    """Verify all admin endpoints exist"""
    app = create_app()
    
    # List of endpoints referenced in base template
    endpoints = [
        'admin.dashboard',
        'admin.orders',
        'admin.menu_management',
        'admin.category_management',
        'admin.popular_items_analytics',
        'admin.services',
        'admin.qr_codes',
        'admin.rewards_management',
        'admin.loyalty_management',
        'admin.campaigns_management',
        'admin.profile',
        'admin.add_menu_item',
        'admin.add_category',
        'admin.add_service',
        'auth.logout'
    ]
    
    with app.app_context():
        print("Verifying admin endpoints...")
        
        for endpoint in endpoints:
            try:
                # Try to generate URL for the endpoint
                url = url_for(endpoint)
                print(f"✓ {endpoint} -> {url}")
            except Exception as e:
                print(f"✗ {endpoint} -> ERROR: {e}")
        
        # List all available admin endpoints
        print("\n" + "="*50)
        print("All available admin endpoints:")
        
        for rule in app.url_map.iter_rules():
            if rule.endpoint and rule.endpoint.startswith('admin.'):
                print(f"  {rule.endpoint} -> {rule.rule}")

if __name__ == '__main__':
    verify_admin_endpoints()
