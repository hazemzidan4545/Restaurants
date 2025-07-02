#!/usr/bin/env python3
"""Create basic test users"""

from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    try:
        # Check if customer already exists
        customer = User.query.filter_by(email='customer@test.com').first()
        if not customer:
            customer = User(
                name='Test Customer',
                email='customer@test.com',
                password_hash=generate_password_hash('test123'),
                role='customer',
                phone='555-0123'
            )
            db.session.add(customer)
            db.session.commit()
            print(f"✅ Created customer: {customer.email}")
        else:
            print(f"✅ Customer exists: {customer.email}")
        
        print("\nLogin with: customer@test.com / test123")
        print("Then you can test the orders page at /customer/orders")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
