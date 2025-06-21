from datetime import datetime, timedelta
from decimal import Decimal
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Numeric
from app.extensions import db

class User(UserMixin, db.Model):
    """Unified user model with role-based permissions"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('customer', 'admin', 'waiter', name='user_roles'), nullable=False, default='customer')
    profile_img = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    feedback = db.relationship('Feedback', backref='user', lazy='dynamic')
    loyalty_account = db.relationship('CustomerLoyalty', backref='user', uselist=False)
    point_transactions = db.relationship('PointTransaction', backref='user', lazy='dynamic')
    reward_redemptions = db.relationship('RewardRedemption', backref='user', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_waiter(self):
        return self.role == 'waiter'
    
    def is_customer(self):
        return self.role == 'customer'
    
    def __repr__(self):
        return f'<User {self.email}>'

class Table(db.Model):
    """Physical restaurant tables"""
    __tablename__ = 'tables'
    
    table_id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.String(10), unique=True, nullable=False)
    status = db.Column(db.Enum('available', 'occupied', 'reserved', name='table_status'), 
                      nullable=False, default='available')
    capacity = db.Column(db.Integer, nullable=False, default=4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='table', lazy='dynamic')
    service_requests = db.relationship('ServiceRequest', backref='table', lazy='dynamic')
    qr_codes = db.relationship('QRCode', backref='table', lazy='dynamic')
    
    def __repr__(self):
        return f'<Table {self.table_number}>'

class Category(db.Model):
    """Menu organization categories"""
    __tablename__ = 'categories'
    
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    menu_items = db.relationship('MenuItem', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class MenuItem(db.Model):
    """Food and service items"""
    __tablename__ = 'menu_items'
    
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(Numeric(10, 2), nullable=False)  # EGP
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Enum('available', 'out_of_stock', 'discontinued', name='item_status'), 
                      nullable=False, default='available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='menu_item', lazy='dynamic')
    images = db.relationship('MenuItemImage', backref='menu_item', lazy='dynamic')
    feedback = db.relationship('Feedback', backref='menu_item', lazy='dynamic')
    reward_items = db.relationship('RewardItem', backref='menu_item', lazy='dynamic')
    
    def __repr__(self):
        return f'<MenuItem {self.name}>'

class MenuItemImage(db.Model):
    """Multiple images per menu item"""
    __tablename__ = 'menu_item_images'
    
    image_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_items.item_id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MenuItemImage {self.image_url}>'

class Order(db.Model):
    """Customer orders with status tracking"""
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.table_id'), nullable=True)
    order_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('new', 'processing', 'completed', 'rejected', 'cancelled', name='order_status'),
                      nullable=False, default='new')
    total_amount = db.Column(Numeric(10, 2), nullable=False, default=0.00)
    notes = db.Column(db.Text, nullable=True)
    estimated_time = db.Column(db.Integer, nullable=True)  # minutes
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='order', lazy='dynamic')
    point_transactions = db.relationship('PointTransaction', backref='order', lazy='dynamic')
    reward_redemptions = db.relationship('RewardRedemption', backref='order', lazy='dynamic')

    def calculate_total(self):
        """Calculate total amount from order items"""
        total = sum(item.quantity * item.menu_item.price for item in self.order_items)
        self.total_amount = total
        return total

    def __repr__(self):
        return f'<Order {self.order_id}>'

class OrderItem(db.Model):
    """Individual items within orders"""
    __tablename__ = 'order_items'

    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_items.item_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    note = db.Column(db.String(255), nullable=True)  # customizations like "No Onions"
    unit_price = db.Column(Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f'<OrderItem {self.order_item_id}>'

class Payment(db.Model):
    """Payment tracking and processing"""
    __tablename__ = 'payments'

    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False)
    payment_type = db.Column(db.Enum('cash', 'card', 'wallet', name='payment_types'),
                           nullable=False, default='cash')
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded', name='payment_status'),
                      nullable=False, default='pending')
    transaction_id = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.payment_id}>'

class ServiceRequest(db.Model):
    """Waiter service requests"""
    __tablename__ = 'service_requests'

    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.table_id'), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)  # 'clean_table', 'refill_coals', 'adjust_ac', etc.
    status = db.Column(db.Enum('pending', 'acknowledged', 'done', name='request_status'),
                      nullable=False, default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ServiceRequest {self.request_id}>'

class Notification(db.Model):
    """System-wide messaging"""
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.Enum('order_update', 'service_request', 'loyalty_points', 'system', name='notification_types'),
                                nullable=False, default='system')
    seen = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.notification_id}>'

class Feedback(db.Model):
    """Customer reviews and ratings"""
    __tablename__ = 'feedback'

    feedback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_items.item_id'), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
    comment = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Feedback {self.feedback_id}>'

class LoyaltyProgram(db.Model):
    """Point-based customer rewards program"""
    __tablename__ = 'loyalty_programs'

    program_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    points_per_50EGP = db.Column(db.Integer, nullable=False, default=100)
    status = db.Column(db.Enum('active', 'inactive', name='program_status'),
                      nullable=False, default='active')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<LoyaltyProgram {self.name}>'

class CustomerLoyalty(db.Model):
    """Individual customer loyalty accounts"""
    __tablename__ = 'customer_loyalty'

    loyalty_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, unique=True)
    total_points = db.Column(db.Integer, nullable=False, default=0)
    lifetime_points = db.Column(db.Integer, nullable=False, default=0)
    tier_level = db.Column(db.Enum('bronze', 'silver', 'gold', 'platinum', name='loyalty_tiers'),
                          nullable=False, default='bronze')
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

    def update_tier(self):
        """Update tier based on lifetime points"""
        if self.lifetime_points >= 10000:
            self.tier_level = 'platinum'
        elif self.lifetime_points >= 5000:
            self.tier_level = 'gold'
        elif self.lifetime_points >= 2000:
            self.tier_level = 'silver'
        else:
            self.tier_level = 'bronze'

    def __repr__(self):
        return f'<CustomerLoyalty {self.user_id}>'

class PointTransaction(db.Model):
    """Point earning and redemption history"""
    __tablename__ = 'point_transactions'

    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=True)
    points_earned = db.Column(db.Integer, nullable=False, default=0)
    points_redeemed = db.Column(db.Integer, nullable=False, default=0)
    transaction_type = db.Column(db.Enum('earned', 'redeemed', 'expired', 'bonus', name='transaction_types'),
                               nullable=False)
    description = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<PointTransaction {self.transaction_id}>'

class RewardItem(db.Model):
    """Available rewards for point redemption"""
    __tablename__ = 'reward_items'

    reward_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    points_required = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_items.item_id'), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    status = db.Column(db.Enum('active', 'inactive', 'expired', name='reward_status'),
                      nullable=False, default='active')
    expiry_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    redemptions = db.relationship('RewardRedemption', backref='reward', lazy='dynamic')

    def __repr__(self):
        return f'<RewardItem {self.name}>'

class RewardRedemption(db.Model):
    """Track reward usage"""
    __tablename__ = 'reward_redemptions'

    redemption_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('reward_items.reward_id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=True)
    points_used = db.Column(db.Integer, nullable=False)
    redemption_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('pending', 'completed', 'cancelled', name='redemption_status'),
                      nullable=False, default='pending')
    redemption_code = db.Column(db.String(20), nullable=True, unique=True)

    def __repr__(self):
        return f'<RewardRedemption {self.redemption_id}>'

class PromotionalCampaign(db.Model):
    """Bonus point campaigns"""
    __tablename__ = 'promotional_campaigns'

    campaign_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    bonus_multiplier = db.Column(db.Float, nullable=False, default=1.0)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    conditions = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('active', 'inactive', 'expired', name='campaign_status'),
                      nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_active(self):
        """Check if campaign is currently active"""
        now = datetime.utcnow()
        return (self.status == 'active' and
                self.start_date <= now <= self.end_date)

    def __repr__(self):
        return f'<PromotionalCampaign {self.name}>'

class QRCode(db.Model):
    """Table-based QR codes"""
    __tablename__ = 'qr_codes'

    qr_id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.table_id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    qr_type = db.Column(db.Enum('menu', 'login', 'payment', name='qr_types'),
                       nullable=False, default='menu')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_scanned = db.Column(db.DateTime, nullable=True)
    scan_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<QRCode {self.qr_id}>'

class AuditLog(db.Model):
    """System activity tracking"""
    __tablename__ = 'audit_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    action_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.log_id}>'
