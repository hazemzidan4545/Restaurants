import sqlite3
conn = sqlite3.connect('instance/restaurant_dev.db')
cursor = conn.cursor()
cursor.execute("UPDATE orders SET status = 'processing' WHERE status = 'preparing'")
result1 = cursor.rowcount
cursor.execute("UPDATE orders SET status = 'processing' WHERE status = 'ready'")  
result2 = cursor.rowcount
conn.commit()
conn.close()
print(f'Fixed {result1 + result2} orders')
