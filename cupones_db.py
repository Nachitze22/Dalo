import sqlite3
from datetime import datetime
from database.db import obtener_conexion

TIPOS_CUPON_VALIDOS = {"porcentaje", "monto_fijo"}


class CuponesDB:
    # ================= Administración (panel admin) =================
    def crear_cupon(self, codigo, tipo, valor, monto_minimo=0, usos_maximos=None, fecha_fin=None):
        codigo = (codigo or "").strip().upper()
        if not codigo or tipo not in TIPOS_CUPON_VALIDOS or not valor or valor <= 0:
            return False, "Datos de cupón inválidos"
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO cupones (codigo, tipo, valor, monto_minimo, usos_maximos, fecha_fin, activo)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (codigo, tipo, valor, monto_minimo or 0, usos_maximos, fecha_fin))
            conn.commit()
            return True, "Cupón creado correctamente"
        except sqlite3.IntegrityError:
            return False, "Ya existe un cupón con ese código"

    def obtener_todos_cupones(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cupones ORDER BY fecha_creacion DESC")
        return [dict(f) for f in cursor.fetchall()]

    def cambiar_estado_cupon(self, cupon_id, activo):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE cupones SET activo = ? WHERE id = ?", (1 if activo else 0, cupon_id))
        ok = cursor.rowcount > 0
        conn.commit()
        return ok

    # ================= Uso en el checkout =================
    def obtener_cupon_por_codigo(self, codigo):
        codigo = (codigo or "").strip().upper()
        if not codigo:
            return None
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cupones WHERE codigo = ?", (codigo,))
        fila = cursor.fetchone()
        return dict(fila) if fila else None

    def usuario_ya_uso_cupon(self, cupon_id, usuario_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM cupones_usos WHERE cupon_id = ? AND usuario_id = ?", (cupon_id, usuario_id))
        return cursor.fetchone() is not None

    def validar_cupon(self, codigo, usuario_id, subtotal):
        """Devuelve (ok, mensaje, cupon_dict|None)."""
        cupon = self.obtener_cupon_por_codigo(codigo)
        if not cupon:
            return False, "Ese código de cupón no existe", None
        if not cupon.get("activo"):
            return False, "Ese cupón ya no está activo", None
        if cupon.get("fecha_fin"):
            try:
                if datetime.now().date() > datetime.strptime(cupon["fecha_fin"], "%Y-%m-%d").date():
                    return False, "Ese cupón ya venció", None
            except ValueError:
                pass
        if cupon.get("usos_maximos") is not None and cupon.get("usos_actuales", 0) >= cupon["usos_maximos"]:
            return False, "Ese cupón alcanzó su límite de usos", None
        if usuario_id and self.usuario_ya_uso_cupon(cupon["id"], usuario_id):
            return False, "Ya usaste este cupón anteriormente", None
        if cupon.get("monto_minimo") and subtotal < cupon["monto_minimo"]:
            return False, f"Este cupón requiere una compra mínima de ${cupon['monto_minimo']:,.0f}".replace(",", "."), None
        return True, "Cupón aplicado correctamente", cupon

    def calcular_descuento(self, cupon, subtotal):
        if not cupon:
            return 0
        if cupon["tipo"] == "porcentaje":
            descuento = subtotal * (cupon["valor"] / 100)
        else:
            descuento = cupon["valor"]
        return min(descuento, subtotal)

    def registrar_uso(self, cupon_id, usuario_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO cupones_usos (cupon_id, usuario_id) VALUES (?, ?)", (cupon_id, usuario_id))
            cursor.execute("UPDATE cupones SET usos_actuales = COALESCE(usos_actuales, 0) + 1 WHERE id = ?", (cupon_id,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False