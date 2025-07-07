#!/usr/bin/env python3
"""
Initialize default system settings
"""

from app import create_app
from app.extensions import db
from app.models import SystemSettings

def initialize_system_settings():
    """Initialize default system settings if they don't exist"""
    app = create_app()
    
    with app.app_context():
        try:
            default_settings = [
                ('system_currency', 'EGP', 'System currency for price display', 'string'),
                ('tax_rate', '0', 'Tax rate percentage', 'float'),
                ('service_charge', '0', 'Service charge percentage', 'float'),
                ('restaurant_name', 'Restaurant Management System', 'Restaurant name', 'string'),
                ('restaurant_phone', '', 'Restaurant phone number', 'string'),
                ('restaurant_address', '', 'Restaurant address', 'string'),
                ('auto_accept_orders', 'false', 'Automatically accept new orders', 'boolean'),
                ('default_prep_time', '30', 'Default preparation time in minutes', 'integer'),
                ('max_order_items', '50', 'Maximum items per order', 'integer'),
                ('enable_push_notifications', 'true', 'Enable push notifications', 'boolean'),
                ('enable_email_notifications', 'true', 'Enable email notifications', 'boolean'),
                ('enable_sound_alerts', 'true', 'Enable sound alerts', 'boolean'),
                ('loyalty_enabled', 'true', 'Enable loyalty program', 'boolean'),
                ('points_per_currency', '2', 'Points earned per currency unit spent', 'integer'),
                ('point_value', '0.5', 'Value of each loyalty point', 'float'),
                ('maintenance_mode', 'false', 'Enable maintenance mode', 'boolean'),
                ('backup_frequency', 'daily', 'Automatic backup frequency', 'string'),
            ]
            
            settings_created = 0
            
            for key, value, description, setting_type in default_settings:
                existing = SystemSettings.query.filter_by(key=key).first()
                if not existing:
                    # Use the set_setting method which handles the database properly
                    SystemSettings.set_setting(key, value, description, setting_type)
                    settings_created += 1
                    print(f"  ✓ Created setting: {key} = {value}")
            
            if settings_created > 0:
                print(f"✅ Created {settings_created} default system settings!")
            else:
                print("✅ All default system settings already exist")
            
        except Exception as e:
            print(f"❌ Initialization failed: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    initialize_system_settings()
