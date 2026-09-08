import sqlite3

def eliminar_usuario_especifico(email):
    try:
        conn = sqlite3.connect("dalo.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE email = ?", (email,))
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Éxito: El usuario {email} ha sido eliminado.")
        else:
            print(f"Aviso: No se encontró ningún usuario con el email {email}.")
    except Exception as e:
        print(f"Error al intentar eliminar: {e}")
    finally:
        conn.close()
eliminar_usuario_especifico("nacho.ignacio.2208@gmail.com")
