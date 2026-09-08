
import sqlite3

conexion = sqlite3.connect("dalo.db")
cursor = conexion.cursor()

cursor.execute("""
    UPDATE productos
    SET
    activo = 1
    WHERE id = 12;
""")
conexion.commit()
conexion.close()