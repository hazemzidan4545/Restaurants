import sqlite3

# Connect to database
conn = sqlite3.connect('instance/restaurant_dev.db')
cursor = conn.cursor()

print("Checking for invalid order status values...")

# Get all distinct status values
cursor.execute('SELECT DISTINCT status FROM orders')
all_statuses = [row[0] for row in cursor.fetchall()]

print(f"Found status values: {all_statuses}")

# Define valid statuses according to the enum
valid_statuses = ['new', 'processing', 'completed', 'rejected', 'cancelled']

# Find invalid statuses
invalid_statuses = [status for status in all_statuses if status not in valid_statuses]

if invalid_statuses:
    print(f"Invalid statuses found: {invalid_statuses}")
    
    # Fix each invalid status
    for invalid_status in invalid_statuses:
        # Count orders with this status
        cursor.execute('SELECT COUNT(*) FROM orders WHERE status = ?', (invalid_status,))
        count = cursor.fetchone()[0]
        
        print(f"Found {count} orders with status '{invalid_status}'")
        
        # Map invalid statuses to valid ones
        if invalid_status in ['preparing', 'ready']:
            new_status = 'processing'
        elif invalid_status.upper() in ['NEW', 'PROCESSING', 'COMPLETED', 'REJECTED', 'CANCELLED']:
            new_status = invalid_status.lower()
        else:
            new_status = 'processing'  # Default fallback
        
        print(f"Converting '{invalid_status}' to '{new_status}'")
        
        # Update the invalid status
        cursor.execute('UPDATE orders SET status = ? WHERE status = ?', (new_status, invalid_status))
        
    # Commit all changes
    conn.commit()
    print(f"Successfully fixed {len(invalid_statuses)} invalid status types!")
    
else:
    print("All status values are valid!")

# Verify the fix
print("\nVerification - Current status distribution:")
cursor.execute('SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status')
for status, count in cursor.fetchall():
    print(f"  {status}: {count} orders")

conn.close()
print("Database check and fix completed!")
