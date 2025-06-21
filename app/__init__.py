from flask import Flask
from config import config
from app.extensions import init_extensions

def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app import models
    
    # Register blueprints
    from app.modules.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.modules.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.modules.waiter import bp as waiter_bp
    app.register_blueprint(waiter_bp, url_prefix='/waiter')
    
    from app.modules.customer import bp as customer_bp
    app.register_blueprint(customer_bp, url_prefix='/customer')
    
    from app.modules.menu import bp as menu_bp
    app.register_blueprint(menu_bp, url_prefix='/menu')
    
    from app.modules.order import bp as order_bp
    app.register_blueprint(order_bp, url_prefix='/order')
    
    from app.modules.service import bp as service_bp
    app.register_blueprint(service_bp, url_prefix='/service')
    
    from app.modules.loyalty import bp as loyalty_bp
    app.register_blueprint(loyalty_bp, url_prefix='/loyalty')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register main routes
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
