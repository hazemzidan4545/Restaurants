# Restaurant Management System

## Project Overview

This is a comprehensive web-based Restaurant Management System designed to streamline restaurant operations, enhance customer experience, and provide powerful management tools for restaurant owners and staff.

## Quick Start

### Prerequisites
- Python 3.8+
- Flask
- SQLAlchemy

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/restaurant-system.git
cd restaurant-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Run the application
python run.py
```

### Default Login Credentials
- **Admin**: admin@restaurant.com / admin123
- **Waiter**: waiter@restaurant.com / waiter123
- **Customer**: Register via the signup page, login maybe through QRcode

---

## System Specification

Create a comprehensive web-based Restaurant Management System with the following specifications:

## Technology Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite for development (easily upgradeable to PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5 + HTML/CSS/JavaScript with Jinja2 templates
- **Authentication**: Flask-Login with role-based access control
- **Security**: CSRF protection, password hashing
- **File Management**: File upload system for menu item images and resources
- **Real-time Features**: WebSocket integration for order status updates
- **QR Code Integration**: QR code generation and scanning functionality

## System Architecture

- **Modular Blueprint Structure**: Separate modules for admin, waiter, customer, menu, order, and auth
- **Role-Based Authentication**: Three user types (Admin, Waiter, Customer) with distinct permissions
- **RESTful API**: JSON API endpoints for mobile/external integration
- **Responsive Design**: Mobile-first Bootstrap interface with custom CSS
- **Real-time Updates**: Live order status notifications and dashboard updates

## Database Models & Relationships

### User Models

1. **User**: Unified user model with role-based permissions
   - Fields: user_id, name, email, phone, password, role (customer/admin/waiter), profile_img
   - Roles: Admin (full system access), Waiter (order management, service requests), Customer (ordering, profile management)

2. **Tables**: Physical restaurant tables
   - Fields: table_id, status (available/occupied/reserved)
   - QR code integration for table-based ordering

### Menu Management

1. **Categories**: Menu organization (Hookah, Drinks, Brunch, etc.)
   - Fields: category_id, name, description, display_order

2. **MenuItem**: Food and service items
   - Fields: item_id, name, description, price (EGP), category_id, image_url, stock, status (available/out_of_stock)
   - Stock management and availability tracking

3. **MenuItemImages**: Multiple images per menu item
   - Support for multiple product photos

### Order Management

1. **Order**: Customer orders with status tracking
   - Fields: order_id, user_id, table_id, order_time, status (new/processing/completed/rejected), total_amount
   - Real-time status updates and notifications

2. **OrderItem**: Individual items within orders
   - Fields: order_item_id, order_id, item_id, quantity, note (customizations like "No Onions")
   - Support for item modifications and special requests

3. **Payment**: Payment tracking and processing
   - Fields: payment_id, order_id, amount, payment_type (cash/card/wallet), status, timestamp

### Service & Communication

1. **ServiceRequest**: Waiter service requests
   - Real-time notification system for staff

2. **Notification**: System-wide messaging
   - Fields: notification_id, user_id, message, seen, timestamp
   - Order updates and system alerts

3. **Feedback**: Customer reviews and ratings
   - Fields: feedback_id, user_id, item_id, order_id, rating (1-5), comment, timestamp

### Loyalty & Rewards System

1. **LoyaltyProgram**: Point-based customer rewards
   - Fields: program_id, name, description, points_per_50EGP, status, created_date
   - Configurable earning rates and program settings

2. **CustomerLoyalty**: Individual customer loyalty accounts
   - Fields: loyalty_id, user_id, total_points, lifetime_points, tier_level, join_date
   - Track customer points balance and loyalty status

3. **PointTransaction**: Point earning and redemption history
   - Fields: transaction_id, user_id, order_id, points_earned, points_redeemed, transaction_type, description, timestamp
   - Complete audit trail of all point activities

4. **RewardItem**: Available rewards for point redemption
   - Fields: reward_id, name, description, points_required, item_id, category, status, expiry_date
   - Link menu items to point values for redemption

5. **RewardRedemption**: Track reward usage
   - Fields: redemption_id, user_id, reward_id, order_id, points_used, redemption_date, status
   - Monitor reward redemption patterns and usage

6. **PromotionalCampaign**: Bonus point campaigns
   - Fields: campaign_id, name, description, bonus_multiplier, start_date, end_date, conditions
   - Special promotions and bonus point events

### System Management

1. **QRCode**: Table-based QR codes
   - Fields: qr_id, table_id, url, type (menu/login/payment)
   - Dynamic QR generation for table access

2. **AuditLog**: System activity tracking
   - Fields: log_id, user_id, action_type, description, timestamp
   - Administrative oversight and security

## Core Features

### Customer Interface

**Menu Browsing & Ordering**
- Browse menu by categories (Hookah, Drinks, Brunch, etc.)
- View item details: names, prices (EGP), descriptions, images
- Stock status display ("out of stock" indicators)
- Add items to cart with quantity selection
- Apply item modifications (e.g., "Burger - No Onions")
- Place orders with table number selection

**Order Tracking**
- Real-time order status updates ("Order Confirmed", "Your order will arrive in 10 minutes")
- Order history and receipt viewing
- Estimated delivery time display

**Service Requests**
- Quick service buttons: "Clean my table", "Refill coals", "Adjust AC"
- Custom waiter request messaging
- Request status tracking

**Loyalty Program Management**
- Points earning system (configurable points per 50 EGP spent)
- Point balance tracking and transaction history
- Reward catalog with point-based redemption
- Tier-based loyalty levels with progressive benefits
- Promotional campaigns and bonus point events

**Profile Management**
- User registration and login/logout
- Profile updates: username, email, phone, profile photo
- Order history and preferences
- Loyalty points balance and redemption history
- Reward notifications and expiry alerts

### Waiter Dashboard

**Order Management**
- Real-time order queue with status filters (New, In Transit, Completed, Rejected)
- Detailed order view: table number, items, modifications
- Order status updates and customer notifications
- Print order tickets and receipts

**Service Request Handling**
- Live service request notifications
- Request acknowledgment and completion tracking
- Table status management

**Table Management**
- Table availability and occupancy status
- Table assignment and reservation system
- QR code management for tables

### Admin Dashboard

**System Overview**
- Statistics dashboard: number of orders, meals prepared, revenue tracking
- Real-time system metrics and KPIs
- Date-based filtering and reporting

**Menu Management**
- Create/edit/delete menu categories and items
- Inventory management and stock tracking
- Price management and promotional pricing
- Image upload and management

**User Management**
- Create/edit/deactivate customers, waiters, and admins
- Role assignment and permission management
- User activity monitoring

**Order Analytics**
- Comprehensive order reporting and analytics
- Revenue tracking and financial reports
- Popular item analysis and trends
- Customer behavior insights

**Loyalty Program Management**
- Create and configure loyalty programs with earning rates
- Manage reward catalog and point requirements
- Set up promotional campaigns and bonus point events
- Track customer loyalty metrics and engagement
- Generate loyalty program reports and analytics
- Point expiration management and notifications

**System Administration**
- Audit log monitoring
- System configuration and settings
- Backup and maintenance tools

## Advanced Features

### QR Code System
- **Table-Based Access**: Unique QR codes for each table
- **Quick Menu Access**: Direct menu browsing without app installation
- **Contactless Ordering**: Complete ordering process via QR scan
- **Dynamic QR Generation**: Administrative QR code management

### Real-Time Features
- **Live Order Updates**: WebSocket-based status notifications
- **Instant Service Requests**: Real-time waiter notifications
- **Dashboard Synchronization**: Live data updates across all interfaces
- **Push Notifications**: Order confirmations and delivery alerts

### Inventory Management
- **Stock Tracking**: Real-time inventory monitoring
- **Low Stock Alerts**: Automatic notifications for restocking
- **Item Availability**: Dynamic menu updates based on stock
- **Waste Tracking**: Inventory loss and expiration management

### Loyalty & Rewards System
- **Point Earning**: Configurable points per dollar spent (default: 100 points per dollar)
- **Automatic Point Allocation**: Points awarded on successful order completion
- **Reward Catalog**: Menu items available for point redemption
- **Point Redemption**: Direct integration with ordering system
- **Bonus Campaigns**: Promotional multipliers and special offers
- **Point Expiration**: Automatic point expiry after 6 months
- **Tier System**: Progressive loyalty levels with enhanced benefits
- **Transaction History**: Complete audit trail of point activities

### Payment Integration
- **Multiple Payment Methods**: Cash, card, digital wallet support
- **Payment Tracking**: Comprehensive transaction logging
- **Receipt Generation**: Digital and printable receipts
- **Split Bill Feature**: Multi-customer payment options
- **Loyalty Integration**: Automatic point earning with payments

## User Interface Requirements

### Design System
- **Color Scheme**: Professional restaurant branding with warm, inviting colors
- **Typography**: Clean, readable fonts optimized for menu display
- **Icons**: Font Awesome integration for intuitive navigation
- **Animations**: Smooth transitions and engaging micro-interactions

### Dashboard Layouts
- **Role-Specific Navigation**: Customized interfaces for each user type
- **Statistics Cards**: Visual KPI displays with real-time updates
- **Data Tables**: Sortable, searchable order and menu management
- **Modal Forms**: Clean popup forms for order and menu management

### Mobile Optimization
- **Touch-Friendly Design**: Large buttons and swipe gestures
- **Offline Capability**: Basic functionality without internet
- **Fast Loading**: Optimized images and minimal data usage
- **QR Scanner Integration**: Built-in camera functionality

## Security & Authentication

### User Authentication
- **Secure Login**: Password hashing with Werkzeug
- **Session Management**: Flask-Login with secure session handling
- **Role-Based Access Control**: Decorator-based route protection
- **Multi-Factor Authentication**: Optional SMS/email verification

### Data Security
- **CSRF Protection**: Form security against attacks
- **Input Validation**: Comprehensive client and server-side validation
- **Data Encryption**: Sensitive information protection
- **Audit Trails**: Complete activity logging

### Payment Security
- **PCI Compliance**: Secure payment data handling
- **Transaction Encryption**: End-to-end payment security
- **Fraud Detection**: Suspicious activity monitoring

## Database Setup & Seeding

- **Migration System**: Flask-Migrate for database versioning
- **Seed Data**: Sample menu items, users, and orders for testing
- **Multi-Language Support**: Arabic and English content support
- **Development Tools**: Database reset and initialization scripts

## API Integration

### RESTful Endpoints
- **Menu API**: GET /api/menu, /api/categories
- **Order API**: POST /api/orders, GET /api/orders/{id}
- **User API**: GET /api/profile, PUT /api/profile
- **Service API**: POST /api/service-requests
- **Loyalty API**: GET /api/loyalty/points, POST /api/loyalty/redeem, GET /api/rewards
- **Campaign API**: GET /api/campaigns/active, POST /api/campaigns/enroll

### External Integrations
- **Payment Gateways**: Stripe, PayPal, local payment providers
- **SMS Notifications**: Order and service request alerts
- **Email Services**: Receipts and promotional messaging

## File Structure

```
restaurant-system/
├── app/
│   ├── modules/
│   │   ├── admin/
│   │   ├── waiter/
│   │   ├── customer/
│   │   ├── menu/
│   │   ├── order/
│   │   ├── service/
│   │   ├── loyalty/
│   │   └── auth/
│   ├── templates/
│   │   ├── admin/
│   │   ├── waiter/
│   │   ├── customer/
│   │   ├── loyalty/
│   │   └── shared/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   └── uploads/
│   ├── api/
│   └── extensions.py
├── instance/
├── uploads/
│   ├── menu_images/
│   ├── profile_images/
│   └── receipts/
├── config.py
├── requirements.txt
└── run.py
```

## Loyalty Program Features

### Point Earning System
- **Standard Rate**: 100 points per dollar spent on eligible purchases
- **Automatic Allocation**: Points awarded upon successful order completion
- **Eligible Purchases**: All menu items except promotional or discounted items
- **Multiple Channels**: Earn points through app orders, in-store purchases, and drive-thru
- **Bonus Points**: Special promotional multipliers during campaigns
- **New User Bonus**: Welcome points for app downloads and account creation

### Point Redemption
- **Reward Catalog**: Free menu items available for point redemption
- **Flexible Redemption**: Redeem through app or at point of sale
- **Variable Point Values**: Different rewards require different point amounts
- **One-Time Redemption**: Rewards can be redeemed one at a time
- **Order Integration**: Add rewards directly to mobile orders
- **Restaurant Code**: Use redemption codes at physical locations

### Program Management
- **Point Tracking**: Real-time point balance and transaction history
- **Expiration Policy**: Points expire 6 months after earning date
- **No Cash Value**: Points cannot be converted to cash or transferred
- **Digital Platform**: App-based program with seamless integration
- **Tier System**: Progressive loyalty levels with enhanced benefits
- **Promotional Campaigns**: Seasonal bonus point events and special offers

### Customer Experience
- **Dashboard**: View points balance, transaction history, and available rewards
- **Notifications**: Point earning confirmations and expiry reminders
- **Reward Browser**: Browse and filter available rewards by category
- **Redemption History**: Track previously redeemed rewards
- **Progress Tracking**: Visual indicators for reaching reward thresholds
- **Personalized Offers**: Targeted rewards based on ordering history

---

1. **Phase 1**: User authentication and basic menu display
2. **Phase 2**: Order placement and basic order management
3. **Phase 3**: Loyalty program integration and point system
4. **Phase 4**: Real-time updates and service requests
5. **Phase 5**: Admin dashboard and analytics
6. **Phase 6**: QR code integration and mobile optimization
7. **Phase 7**: Payment integration and advanced features

## Testing Requirements

- **Unit Tests**: Model validation and business logic testing
- **Integration Tests**: End-to-end ordering workflow testing
- **User Acceptance Testing**: Role-based feature validation
- **Performance Testing**: Load testing for concurrent orders
- **Security Testing**: Authentication and data protection validation

## Performance Requirements

- **Response Time**: Page loads under 2 seconds
- **Concurrent Users**: Support for 100+ simultaneous users
- **Database Optimization**: Indexed queries and efficient relationships
- **Caching Strategy**: Redis integration for frequently accessed data
- **Image Optimization**: Compressed images with CDN delivery

## Deployment Considerations

- **Containerization**: Docker support for easy deployment
- **Environment Configuration**: Development, staging, production configs
- **Monitoring**: Application performance and error tracking
- **Backup Strategy**: Regular database and file backups
- **Scaling**: Horizontal scaling capability for high traffic
