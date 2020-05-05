import sqlite3

conn = sqlite3.connect('H:/12DTP/Pizza/Pizzadb.db')
cur = conn.cursor()
cur.execute('SELECT * FROM Pizza WHERE id=1;')
results = cur.fetchone()
print(results)