import sqlite3

conn = sqlite3.connect('instance/restaurant_dev.db')
cursor = conn.cursor()

# Fix the invalid 'preparing' status
cursor.execute('UPDATE orders SET status = "processing" WHERE status = "preparing"')
rows_affected = cursor.rowcount
conn.commit()

print(f'Fixed {rows_affected} orders with "preparing" status to "processing"')

# Check for any other invalid statuses
cursor.execute('SELECT DISTINCT status FROM orders')
statuses = cursor.fetchall()
print('All distinct statuses in database:')
for status in statuses:
    print(f'  {status[0]}')

valid_statuses = ['new', 'processing', 'completed', 'rejected', 'cancelled']
invalid_statuses = []
for status in statuses:
    if status[0] not in valid_statuses:
        invalid_statuses.append(status[0])

if invalid_statuses:
    print(f'Invalid statuses found: {invalid_statuses}')
    # Fix any other invalid statuses by converting them to 'processing'
    for invalid_status in invalid_statuses:
        cursor.execute('UPDATE orders SET status = "processing" WHERE status = ?', (invalid_status,))
        print(f'Fixed "{invalid_status}" to "processing"')
    conn.commit()
else:
    print('All statuses are valid!')

conn.close()
