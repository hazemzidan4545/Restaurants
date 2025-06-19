## Functional Requirements

### 1. **User Management**

* User registration and login/logout
* Profile management (username, email, phone, profile photo)

### 2. **Menu and Services Display**

* Display of categories: Hookah, Drinks, Brunch, etc.
* Menu items with:

  * Names
  * Prices (e.g., 500 EP)
  * Stock status (e.g., "out of stock")
  * Images
  * Descriptions

### 3. **Ordering System**

* Add items to order
* Place an order
* View order confirmation and status updates (e.g., "Order Confirmed", "Your order will arrive in 10 minutes")
* Special requests for waiter (e.g., “Clean my table”, “Refill coals”, “Adjust AC”)

### 4. **Order Management Dashboard (Admin/Waiter Panel)**

* Dashboard with:

  * Number of orders
  * Meals prepared
  * Status filters: New, In Transit, Completed, Rejected, etc.
* View detailed order info: table number, items, modifications (e.g., “Burger (No Onions)”)

### 5. **QR Code Functionality**

* Likely used for accessing menus or customer login at a table

### 6. **Statistics and Analytics**

* Track orders, meals completed, and statuses
* Possibly filter by date or status

---

##  Non-Functional Requirements

### 1. **Web-Based Architecture**

* Responsive UI for different devices (inferred from web layout)

### 2. **Usability**

* Clean, intuitive UI
* Quick access to key functions (place order, call waiter, etc.)

### 3. **Performance**

* Fast response for order placing and updates
* Real-time status updates

### 4. **Scalability**

* Supports multiple orders and users concurrently (suggested by dashboard and multiple order statuses)

### 5. **Localization**

* Pricing in EGP (Egyptian Pound), indicating support for specific currencies and possible regional formats

### 6. **Security**

* User authentication and session management
* Order and customer information privacy

---

## Modules

| Module              | Description                        |
| ------------------- | ---------------------------------- |
| User Module         | Profile creation, login/logout     |
| Menu Management     | Add/edit/delete items, track stock |
| Order Management    | Create, update, and track orders   |
| Service Requests    | Send real-time waiter requests     |
| Admin Dashboard     | View analytics, control system     |
| Notification System | Inform users about order status    |
| QR Code System      | Table-based quick access/login     |

---
## Database Schema 
**1. `users`**

Stores all user accounts.

| Field         | Type     | Description                   |
| ------------- | -------- | ----------------------------- |
| `user_id`     | INT (PK) | Unique user ID                |
| `name`        | VARCHAR  | Full name                     |
| `email`       | VARCHAR  | Unique email                  |
| `phone`       | VARCHAR  | Phone number                  |
| `password`    | VARCHAR  | Hashed password               |
| `role`        | ENUM     | 'customer', 'admin', 'waiter' |
| `profile_img` | TEXT     | Image URL                     |

---

**2. `tables`**

Physical tables in the restaurant.

| Field      | Type     | Description                         |
| ---------- | -------- | ----------------------------------- |
| `table_id` | INT (PK) | Unique ID                           |
| `status`   | ENUM     | 'available', 'occupied', 'reserved' |

---

**3. `categories`**

Menu categories like Drinks, Meals, etc.

| Field         | Type     | Description   |
| ------------- | -------- | ------------- |
| `category_id` | INT (PK) | Unique ID     |
| `name`        | VARCHAR  | Category name |

---

**4. `menu_items`**

Food or services offered.

| Field         | Type     | Description                   |
| ------------- | -------- | ----------------------------- |
| `item_id`     | INT (PK) | Unique ID                     |
| `name`        | VARCHAR  | Name                          |
| `description` | TEXT     | Item details                  |
| `price`       | DECIMAL  | Price in EGP                  |
| `category_id` | INT (FK) | Linked to `categories`        |
| `image_url`   | TEXT     | Item image                    |
| `stock`       | INT      | Inventory count               |
| `status`      | ENUM     | 'available', 'out\_of\_stock' |

---

**5. `orders`**

All orders made.

| Field        | Type      | Description                         |
| ------------ | --------- | ----------------------------------- |
| `order_id`   | INT (PK)  | Unique ID                           |
| `user_id`    | INT (FK)  | Who placed the order                |
| `table_id`   | INT (FK)  | Table number                        |
| `order_time` | TIMESTAMP | Time placed                         |
| `status`     | ENUM      | 'new', 'processing', 'completed'... |

---

**6. `order_items`**

Individual items in each order.

| Field           | Type     | Description            |
| --------------- | -------- | ---------------------- |
| `order_item_id` | INT (PK) | Unique ID              |
| `order_id`      | INT (FK) | Linked to `orders`     |
| `item_id`       | INT (FK) | Linked to `menu_items` |
| `quantity`      | INT      | Number ordered         |
| `note`          | TEXT     | Customization          |

---

**7. `service_requests`**

Requests made by customers (e.g., Adjust AC).

| Field          | Type      | Description                       |
| -------------- | --------- | --------------------------------- |
| `request_id`   | INT (PK)  | Unique request                    |
| `user_id`      | INT (FK)  | Who made the request              |
| `table_id`     | INT (FK)  | Table associated                  |
| `request_type` | VARCHAR   | Type of request                   |
| `status`       | ENUM      | 'pending', 'acknowledged', 'done' |
| `timestamp`    | TIMESTAMP | Time made                         |

---

**8. `feedback`**

Customer feedback and ratings.

| Field         | Type      | Description              |
| ------------- | --------- | ------------------------ |
| `feedback_id` | INT (PK)  | Unique ID                |
| `user_id`     | INT (FK)  | Who gave feedback        |
| `item_id`     | INT (FK)  | Optional - reviewed item |
| `order_id`    | INT (FK)  | Optional - order context |
| `rating`      | INT       | 1–5 stars                |
| `comment`     | TEXT      | Feedback content         |
| `timestamp`   | TIMESTAMP | Time submitted           |

---

**9. `payments`**

Tracks payment for each order.

| Field          | Type      | Description                 |
| -------------- | --------- | --------------------------- |
| `payment_id`   | INT (PK)  | Unique ID                   |
| `order_id`     | INT (FK)  | Order paid                  |
| `amount`       | DECIMAL   | Payment amount              |
| `payment_type` | ENUM      | 'cash', 'card', 'wallet'    |
| `status`       | ENUM      | 'pending', 'paid', 'failed' |
| `timestamp`    | TIMESTAMP | Payment time                |

---

**10. `audit_logs`**

Tracks admin/waiter actions.

| Field         | Type      | Description                        |
| ------------- | --------- | ---------------------------------- |
| `log_id`      | INT (PK)  | Unique log ID                      |
| `user_id`     | INT (FK)  | Who did it                         |
| `action_type` | VARCHAR   | Type of action (e.g. delete\_item) |
| `description` | TEXT      | Action details                     |
| `timestamp`   | TIMESTAMP | When it occurred                   |

---

**11. `notifications`**

System or admin messages to users.

| Field             | Type      | Description |
| ----------------- | --------- | ----------- |
| `notification_id` | INT (PK)  | Unique ID   |
| `user_id`         | INT (FK)  | Recipient   |
| `message`         | TEXT      | Content     |
| `seen`            | BOOLEAN   | Read/unread |
| `timestamp`       | TIMESTAMP | Sent time   |

---
**12. `qr_codes`**

QR links associated with tables or orders.

| Field      | Type     | Description                      |
| ---------- | -------- | -------------------------------- |
| `qr_id`    | INT (PK) | Unique ID                        |
| `table_id` | INT (FK) | Table linked to this QR          |
| `url`      | TEXT     | URL the QR code resolves to      |
| `type`     | VARCHAR  | e.g., 'menu', 'login', 'payment' |

---

## ERD Diagram 

```
users
 ├── orders
 │    ├── order_items
 │    └── payments
 ├── service_requests
 ├── feedback
 ├── audit_logs
 └── notifications

tables
 ├── orders
 └── service_requests
 └── qr_codes

menu_items
 ├── order_items
 └── feedback
 └── categories

qr_codes
 └── tables
```
