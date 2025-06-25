import sqlite3

conn = sqlite3.connect('instance/restaurant_dev.db')
cursor = conn.cursor()

# Get all orders
cursor.execute('SELECT order_id, status FROM orders ORDER BY order_id')
orders = cursor.fetchall()

print('Current order statuses:')
uppercase_found = False
for order_id, status in orders:
    print(f'Order {order_id}: {status}')
    if status and status.isupper():
        uppercase_found = True

print(f'\nTotal orders: {len(orders)}')

if uppercase_found:
    print('\nFound uppercase statuses. Fixing...')
    # Fix uppercase statuses
    cursor.execute('UPDATE orders SET status = "new" WHERE status = "NEW"')
    cursor.execute('UPDATE orders SET status = "processing" WHERE status = "PROCESSING"')
    cursor.execute('UPDATE orders SET status = "completed" WHERE status = "COMPLETED"')
    cursor.execute('UPDATE orders SET status = "rejected" WHERE status = "REJECTED"')
    cursor.execute('UPDATE orders SET status = "cancelled" WHERE status = "CANCELLED"')
    
    conn.commit()
    print('Fixed uppercase statuses!')
else:
    print('No uppercase statuses found.')

conn.close()
