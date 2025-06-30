from app import create_app
from flask import url_for

app = create_app()

with app.test_request_context():
    print("Testing routes:")
    print("loyalty_management:", url_for('admin.loyalty_management'))
    print("campaigns_management:", url_for('admin.campaigns_management'))
    print("rewards_management:", url_for('admin.rewards_management'))
    print("All routes working!")
