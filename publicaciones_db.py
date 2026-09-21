import sqlite3
import json
import random
from database.db import obtener_conexion


class PublicacionesDB:
    def __init__(self):
        self._crear_tablas()

    # ================= Setup =================
    def _crear_tablas(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preguntas_producto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                usuario_id INTEGER,
                pregunta TEXT NOT NULL,
                respuesta TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_respuesta TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notificaciones_vendedor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendedor_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                leida INTEGER DEFAULT 0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_publicacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                accion TEXT NOT NULL,
                detalle TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        migraciones = [
            ("productos", "subtitulo", "TEXT"),
            ("productos", "subcategoria", "TEXT"),
            ("productos", "modelo", "TEXT"),
            ("productos", "sku", "TEXT"),
            ("productos", "etiquetas", "TEXT"),
            ("productos", "tipo_envio", "TEXT DEFAULT 'retiro'"),
            ("productos", "estado_producto", "TEXT DEFAULT 'nuevo'"),
            ("productos", "color", "TEXT"),
            ("productos", "material", "TEXT"),
            ("productos", "peso", "TEXT"),
            ("productos", "dimensiones", "TEXT"),
            ("productos", "ficha_tecnica_json", "TEXT"),
            ("productos", "medios_pago_json", "TEXT"),
            ("productos", "cuotas_cantidad", "INTEGER"),
            ("productos", "cuotas_interes", "INTEGER DEFAULT 0"),
            ("productos", "fecha_publicacion", "TIMESTAMP"),
            ("productos", "estado_publicacion", "TEXT DEFAULT 'activo'"),
            ("productos", "visitas", "INTEGER DEFAULT 0"),
            ("productos", "favoritos_simulados", "INTEGER DEFAULT 0"),
        ]
        for tabla, columna, tipo in migraciones:
            try:
                cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
            except sqlite3.OperationalError:
                pass
        conn.commit()

    def generar_sku(self):
        return f"DL-{random.randint(100000, 999999)}"

    # ================= Crear / editar =================
    def crear_publicacion(self, vendedor_id, datos):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos
            (nombre, subtitulo, descripcion, precio, precio_oferta, stock, imagen, categoria,
             subcategoria, marca, modelo, color, material, peso, dimensiones, garantia,
             estado_producto, tipo_envio, sku, etiquetas, ficha_tecnica_json, medios_pago_json,
             cuotas_cantidad, cuotas_interes, vendedor_id, moneda, fecha_publicacion,
             estado_publicacion, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    CURRENT_TIMESTAMP, 'activo', 1)
        """, (
            datos["titulo"], datos.get("subtitulo"), datos["descripcion"], datos["precio"],
            datos.get("precio_oferta"), datos["stock"], datos["imagen_principal"], datos["categoria"],
            datos.get("subcategoria"), datos.get("marca"), datos.get("modelo"), datos.get("color"),
            datos.get("material"), datos.get("peso"), datos.get("dimensiones"), datos.get("garantia"),
            datos.get("estado_producto", "nuevo"), datos.get("tipo_envio", "retiro"), datos.get("sku"),
            datos.get("etiquetas"), json.dumps(datos.get("ficha_tecnica", {}), ensure_ascii=False),
            json.dumps(datos.get("medios_pago", []), ensure_ascii=False),
            datos.get("cuotas_cantidad"), int(datos.get("cuotas_interes", 0)), vendedor_id,
            datos.get("moneda", "ARS"),
        ))
        producto_id = cursor.lastrowid
        for i, url in enumerate(datos.get("imagenes", []), start=1):
            cursor.execute(
                "INSERT INTO producto_imagenes (producto_id, imagen, orden) VALUES (?, ?, ?)",
                (producto_id, url, i),
            )
        # NOTA: antes este bloque estaba duplicado (se insertaba 2 veces el
        # historial y la notificación por cada publicación nueva). Corregido.
        cursor.execute(
            "INSERT INTO historial_publicacion (producto_id, accion, detalle) VALUES (?, 'creada', 'Publicación creada')",
            (producto_id,),
        )
        cursor.execute(
            "INSERT INTO notificaciones_vendedor (vendedor_id, tipo, mensaje) VALUES (?, 'publicacion', ?)",
            (vendedor_id, f'Tu publicación "{datos["titulo"]}" ya está activa en Dalo.'),
        )
        self._registrar_oferta_si_corresponde(cursor, producto_id, datos)
        conn.commit()
        return producto_id

    def obtener_publicacion_completa(self, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        fila = cursor.fetchone()
        if not fila:
            return None
        datos = dict(fila)
        try:
            datos["ficha_tecnica"] = json.loads(datos.get("ficha_tecnica_json") or "{}")
        except (TypeError, ValueError):
            datos["ficha_tecnica"] = {}
        try:
            datos["medios_pago"] = json.loads(datos.get("medios_pago_json") or "[]")
        except (TypeError, ValueError):
            datos["medios_pago"] = []
        return datos

    # ================= Panel del vendedor =================
    def obtener_publicaciones_vendedor(self, vendedor_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM productos
            WHERE vendedor_id = ?
            ORDER BY fecha_publicacion DESC
        """, (vendedor_id,))
        return [dict(f) for f in cursor.fetchall()]

    def obtener_publicaciones_vendedor_publicas(self, vendedor_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM productos
            WHERE vendedor_id = ? AND COALESCE(activo, 1) = 1 AND estado_publicacion = 'activo'
            ORDER BY fecha_publicacion DESC
        """, (vendedor_id,))
        return [fila[0] for fila in cursor.fetchall()]

    def pausar_publicacion(self, producto_id, vendedor_id):
        return self._cambiar_estado(producto_id, vendedor_id, "pausado")

    def activar_publicacion(self, producto_id, vendedor_id):
        return self._cambiar_estado(producto_id, vendedor_id, "activo")

    def _cambiar_estado(self, producto_id, vendedor_id, nuevo_estado):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE productos SET estado_publicacion = ? WHERE id = ? AND vendedor_id = ?",
            (nuevo_estado, producto_id, vendedor_id),
        )
        ok = cursor.rowcount > 0
        if ok:
            cursor.execute(
                "INSERT INTO historial_publicacion (producto_id, accion, detalle) VALUES (?, ?, ?)",
                (producto_id, "cambio_estado", f"Publicación pasó a '{nuevo_estado}'"),
            )
        conn.commit()
        return ok

    def eliminar_publicacion(self, producto_id, vendedor_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE productos SET activo = 0, estado_publicacion = 'eliminado' WHERE id = ? AND vendedor_id = ?",
            (producto_id, vendedor_id),
        )
        ok = cursor.rowcount > 0
        conn.commit()
        return ok

    def actualizar_publicacion(self, producto_id, vendedor_id, datos):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT vendedor_id FROM productos WHERE id = ?", (producto_id,))
        fila = cursor.fetchone()
        if not fila or fila[0] != vendedor_id:
            return False
        cursor.execute("""
            UPDATE productos SET
                nombre = ?, subtitulo = ?, descripcion = ?, precio = ?, precio_oferta = ?,
                stock = ?, imagen = ?, categoria = ?, subcategoria = ?, marca = ?, modelo = ?,
                color = ?, material = ?, peso = ?, dimensiones = ?, garantia = ?,
                estado_producto = ?, tipo_envio = ?, etiquetas = ?,
                ficha_tecnica_json = ?, medios_pago_json = ?, cuotas_cantidad = ?, cuotas_interes = ?,
                moneda = ?
            WHERE id = ? AND vendedor_id = ?
        """, (
            datos["titulo"], datos.get("subtitulo"), datos["descripcion"], datos["precio"],
            datos.get("precio_oferta"), datos["stock"], datos["imagen_principal"], datos["categoria"],
            datos.get("subcategoria"), datos.get("marca"), datos.get("modelo"), datos.get("color"),
            datos.get("material"), datos.get("peso"), datos.get("dimensiones"), datos.get("garantia"),
            datos.get("estado_producto", "nuevo"), datos.get("tipo_envio", "retiro"),
            datos.get("etiquetas"), json.dumps(datos.get("ficha_tecnica", {}), ensure_ascii=False),
            json.dumps(datos.get("medios_pago", []), ensure_ascii=False),
            datos.get("cuotas_cantidad"), int(datos.get("cuotas_interes", 0)),
            datos.get("moneda", "ARS"),
            producto_id, vendedor_id,
        ))
        cursor.execute("DELETE FROM producto_imagenes WHERE producto_id = ?", (producto_id,))
        for i, url in enumerate(datos.get("imagenes", []), start=1):
            cursor.execute(
                "INSERT INTO producto_imagenes (producto_id, imagen, orden) VALUES (?, ?, ?)",
                (producto_id, url, i),
            )
        self._registrar_oferta_si_corresponde(cursor, producto_id, datos)
        cursor.execute(
            "INSERT INTO historial_publicacion (producto_id, accion, detalle) VALUES (?, 'editada', 'Publicación editada')",
            (producto_id,),
        )
        conn.commit()
        return True

    def duplicar_publicacion(self, producto_id, vendedor_id):
        original = self.obtener_publicacion_completa(producto_id)
        if not original or original.get("vendedor_id") != vendedor_id:
            return None
        conn = obtener_conexion()
        cursor = conn.cursor()
        campos = ["nombre", "subtitulo", "descripcion", "precio", "precio_oferta", "stock", "imagen",
                  "categoria", "subcategoria", "marca", "modelo", "color", "material", "peso",
                  "dimensiones", "garantia", "estado_producto", "tipo_envio", "etiquetas",
                  "ficha_tecnica_json", "medios_pago_json", "cuotas_cantidad", "cuotas_interes", "moneda"]
        valores = [original.get(c) for c in campos]
        placeholders = ", ".join(["?"] * len(campos))
        nuevo_sku = self.generar_sku()
        cursor.execute(f"""
            INSERT INTO productos ({", ".join(campos)}, sku, vendedor_id, fecha_publicacion, estado_publicacion, activo)
            VALUES ({placeholders}, ?, ?, CURRENT_TIMESTAMP, 'pausado', 1)
        """, (*valores, nuevo_sku, vendedor_id))
        nuevo_id = cursor.lastrowid
        cursor.execute("SELECT imagen, orden FROM producto_imagenes WHERE producto_id = ? ORDER BY orden", (producto_id,))
        for imagen, orden in cursor.fetchall():
            cursor.execute("INSERT INTO producto_imagenes (producto_id, imagen, orden) VALUES (?, ?, ?)", (nuevo_id, imagen, orden))
        cursor.execute(
            "INSERT INTO historial_publicacion (producto_id, accion, detalle) VALUES (?, 'duplicada', ?)",
            (nuevo_id, f"Duplicada desde publicación #{producto_id}"),
        )
        conn.commit()
        return nuevo_id

    # ================= Estadísticas simuladas =================
    def registrar_visita(self, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET visitas = COALESCE(visitas, 0) + 1 WHERE id = ?", (producto_id,))
        conn.commit()

    def obtener_estadisticas(self, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT visitas, favoritos_simulados, vendidos FROM productos WHERE id = ?", (producto_id,))
        fila = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM lista_deseos WHERE producto_id = ?", (producto_id,))
        favoritos_reales = cursor.fetchone()[0] or 0
        if not fila:
            return {"visitas": 0, "favoritos": 0, "ventas": 0}
        visitas, fav_sim, vendidos = fila
        return {
            "visitas": visitas or 0,
            "favoritos": (fav_sim or 0) + favoritos_reales,
            "ventas": vendidos or 0,
        }

    def _registrar_oferta_si_corresponde(self, cursor, producto_id, datos):
        precio = datos.get("precio") or 0
        precio_oferta = datos.get("precio_oferta")
        cursor.execute("UPDATE ofertas SET activa = 0 WHERE producto_id = ? AND activa = 1", (producto_id,))
        if not datos.get("tiene_oferta") or not precio_oferta or not precio or precio_oferta <= 0 or precio_oferta >= precio:
            return
        pct = round((1 - precio_oferta / precio) * 100)
        cursor.execute("""
            INSERT INTO ofertas (producto_id, tipo, valor, activa)
            VALUES (?, 'descuento', ?, 1)
        """, (producto_id, pct))

    # ================= Preguntas =================
    def agregar_pregunta(self, producto_id, usuario_id, pregunta):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO preguntas_producto (producto_id, usuario_id, pregunta) VALUES (?, ?, ?)",
            (producto_id, usuario_id, pregunta),
        )
        conn.commit()

    def responder_pregunta(self, pregunta_id, respuesta):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE preguntas_producto SET respuesta = ?, fecha_respuesta = CURRENT_TIMESTAMP WHERE id = ?",
            (respuesta, pregunta_id),
        )
        conn.commit()

    def obtener_preguntas_vendedor(self, vendedor_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pp.*, p.nombre AS producto_nombre
            FROM preguntas_producto pp
            JOIN productos p ON p.id = pp.producto_id
            WHERE p.vendedor_id = ?
            ORDER BY pp.fecha_creacion DESC
        """, (vendedor_id,))
        return [dict(f) for f in cursor.fetchall()]

    # ================= Notificaciones =================
    def obtener_notificaciones(self, vendedor_id, limite=10):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM notificaciones_vendedor
            WHERE vendedor_id = ?
            ORDER BY fecha_creacion DESC LIMIT ?
        """, (vendedor_id, limite))
        return [dict(f) for f in cursor.fetchall()]

    def marcar_notificaciones_leidas(self, vendedor_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE notificaciones_vendedor SET leida = 1 WHERE vendedor_id = ?", (vendedor_id,))
        conn.commit()

    # ================= Nivel / reputación simulados =================
    def nivel_vendedor(self, vendedor_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(vendidos), 0) FROM productos WHERE vendedor_id = ?", (vendedor_id,))
        ventas_totales = cursor.fetchone()[0] or 0
        if ventas_totales >= 50:
            return {"nivel": "Vendedor Platino", "reputacion": 98}
        if ventas_totales >= 15:
            return {"nivel": "Vendedor Oro", "reputacion": 92}
        if ventas_totales >= 5:
            return {"nivel": "Vendedor Plata", "reputacion": 85}
        return {"nivel": "Vendedor Nuevo", "reputacion": 70}