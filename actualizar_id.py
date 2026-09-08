import sqlite3

conn = sqlite3.connect("dalo.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE productos
SET stock = 10
WHERE id = 4
""")
conn.commit()
conn.close()
print("Actualizado")