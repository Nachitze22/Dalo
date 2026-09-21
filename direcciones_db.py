import sqlite3
from database.db import obtener_conexion

class DireccionesDB:
    def obtener_sedes(self, solo_activas=True):
        conn = obtener_conexion()
        cursor = conn.cursor()
        if solo_activas:
            cursor.execute("SELECT * FROM sedes WHERE activa = 1 ORDER BY etiqueta")
        else:
            cursor.execute("SELECT * FROM sedes ORDER BY etiqueta")
        return [dict(fila) for fila in cursor.fetchall()]

    def agregar_sede(self, id_sede, etiqueta, direccion_completa, cp, localidad, tipo="sede"):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO sedes (id, etiqueta, direccion_completa, cp, localidad, tipo, activa)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (id_sede, etiqueta, direccion_completa, cp, localidad, tipo))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def editar_sede(self, id_sede, **campos):
        columnas_validas = {"etiqueta", "direccion_completa", "cp", "localidad", "tipo", "activa"}
        sets, valores = [], []
        for campo, valor in campos.items():
            if campo in columnas_validas:
                sets.append(f"{campo} = ?")
                valores.append(valor)
        if not sets:
            return False
        valores.append(id_sede)
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE sedes SET {', '.join(sets)} WHERE id = ?", valores)
        editado = cursor.rowcount > 0
        conn.commit()
        return editado

    def eliminar_sede(self, id_sede):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE sedes SET activa = 0 WHERE id = ?", (id_sede,))
        eliminada = cursor.rowcount > 0
        conn.commit()
        return eliminada

    def obtener_direcciones_usuario(self, usuario_id):
        if not usuario_id:
            return []
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM direcciones
            WHERE usuario_id = ? AND activa = 1
            ORDER BY fecha_creacion DESC
        """, (usuario_id,))
        return [dict(fila) for fila in cursor.fetchall()]

    def obtener_direccion_por_id(self, direccion_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM direcciones WHERE id = ? AND activa = 1", (direccion_id,))
        fila = cursor.fetchone()
        return dict(fila) if fila else None

    def agregar_direccion(self, usuario_id, etiqueta, direccion_completa, cp="", localidad="", provincia="", departamento="", indicaciones="", nombre_receptor="", telefono_receptor="", tipo="guardada"):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO direcciones
            (usuario_id, etiqueta, direccion_completa, cp, localidad, provincia,
             departamento, indicaciones, nombre_receptor, telefono_receptor, tipo, activa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (usuario_id, etiqueta, direccion_completa, cp, localidad, provincia,
              departamento, indicaciones, nombre_receptor, telefono_receptor, tipo))
        conn.commit()
        return cursor.lastrowid

    def editar_direccion(self, direccion_id, usuario_id, **campos):
        columnas_validas = {"etiqueta", "direccion_completa", "cp", "localidad", "provincia",
                             "departamento", "indicaciones", "nombre_receptor", "telefono_receptor"}
        sets, valores = [], []
        for campo, valor in campos.items():
            if campo in columnas_validas:
                sets.append(f"{campo} = ?")
                valores.append(valor)
        if not sets:
            return False
        valores.extend([direccion_id, usuario_id])
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE direcciones SET {', '.join(sets)} WHERE id = ? AND usuario_id = ?", valores)
        editado = cursor.rowcount > 0
        conn.commit()
        return editado

    def eliminar_direccion(self, direccion_id, usuario_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE direcciones SET activa = 0 WHERE id = ? AND usuario_id = ?", (direccion_id, usuario_id))
        eliminada = cursor.rowcount > 0
        conn.commit()
        return eliminada

    def eliminar_direccion_por_id_combinado(self, id_combinado, usuario_id):
        if not usuario_id or not str(id_combinado).startswith("dir_"):
            return False
        try:
            direccion_id = int(str(id_combinado).replace("dir_", "", 1))
        except ValueError:
            return False
        return self.eliminar_direccion(direccion_id, usuario_id)

    # ================= Combinado: lo que ve la UI de "Enviar a" =================
    def obtener_direcciones_disponibles(self, usuario_id):
        disponibles = []
        for sede in self.obtener_sedes():
            disponibles.append({
                "id": sede["id"], "etiqueta": sede["etiqueta"],
                "direccion_completa": sede["direccion_completa"], "cp": sede["cp"],
                "localidad": sede["localidad"], "tipo": sede["tipo"],
            })
        for direccion in self.obtener_direcciones_usuario(usuario_id):
            disponibles.append({
                "id": f"dir_{direccion['id']}", "etiqueta": direccion["etiqueta"],
                "direccion_completa": direccion["direccion_completa"], "cp": direccion["cp"],
                "localidad": direccion["localidad"], "provincia": direccion.get("provincia"),
                "departamento": direccion.get("departamento"), "indicaciones": direccion.get("indicaciones"),
                "nombre_receptor": direccion.get("nombre_receptor"),
                "telefono_receptor": direccion.get("telefono_receptor"), "tipo": direccion["tipo"],
            })
        return disponibles