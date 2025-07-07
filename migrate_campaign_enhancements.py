#!/usr/bin/env python3
"""
Migration script to add enhanced campaign fields
"""

from app import create_app
from app.extensions import db
from app.models import PromotionalCampaign
from sqlalchemy import text

def migrate_campaign_enhancements():
    """Add new fields to promotional campaigns table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('promotional_campaigns')]
            
            new_columns = [
                'minimum_order_amount',
                'maximum_uses_per_customer', 
                'total_usage_limit',
                'target_customer_tier',
                'applicable_days',
                'specific_menu_categories',
                'discount_type',
                'discount_value',
                'updated_at'
            ]
            
            columns_to_add = [col for col in new_columns if col not in existing_columns]
            
            if not columns_to_add:
                print("✅ All campaign enhancement columns already exist")
                return
            
            print(f"🔧 Adding {len(columns_to_add)} new columns to promotional_campaigns table...")
            
            # Add new columns
            with db.engine.connect() as conn:
                if 'minimum_order_amount' in columns_to_add:
                    conn.execute(text("ALTER TABLE promotional_campaigns ADD COLUMN minimum_order_amount FLOAT DEFAULT 0.0"))
                    print("  ✓ Added minimum_order_amount column")
                
                if 'maximum_uses_per_customer' in columns_to_add:
                    conn.execute(text("ALTER TABLE promotional_campaigns ADD COLUMN maximum_uses_per_customer INTEGER"))
                    print("  ✓ Added maximum_uses_per_customer column")
                
                if 'total_usage_limit' in columns_to_add:
                    conn.execute(text("ALTER TABLE promotional_campaigns ADD COLUMN total_usage_limit INTEGER"))
                    print("  ✓ Added total_usage_limit column")
                
                if 'target_customer_tier' in columns_to_add:
                    conn.execute(text("ALTER TABLE promotional_campaigns ADD COLUMN target_customer_tier VARCHAR(20)"))
                    print("  ✓ Added target_customer_tier column")
                
                if 'applicable_days' in columns_to_add:
                    conn.execute(text("ALTER TABLE promotional_campaigns ADD COLUMN applicable_days VARCHAR(20) DEFAULT 'all'"))
                    print("  ✓ Added applicable_days column")
                
                if 'specific_menu_categories' in columns_to_add:
                    conn.execute(text("ALTER TABLE promotional_campaigns ADD COLUMN specific_menu_categories TEXT"))
                    print("  ✓ Added specific_menu_categories column")
                
                if 'discount_type' in columns_to_add:
                    conn.execute(text("ALTER TABLE promotional_campaigns ADD COLUMN discount_type VARCHAR(20) DEFAULT 'points_multiplier'"))
                    print("  ✓ Added discount_type column")
                
                if 'discount_value' in columns_to_add:
                    conn.execute(text("ALTER TABLE promotional_campaigns ADD COLUMN discount_value FLOAT"))
                    print("  ✓ Added discount_value column")
                
                if 'updated_at' in columns_to_add:
                    conn.execute(text("ALTER TABLE promotional_campaigns ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                    print("  ✓ Added updated_at column")
                
                conn.commit()
            
            print("✅ Campaign enhancement migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_campaign_enhancements()
