import sqlite3
from database.db import obtener_conexion

TIPOS_OFERTA_VALIDOS = {"descuento", "2x1", "medio_pago", "cuotas"}

class ProductosDB:
    def agregar_producto(self, nombre, descripcion, precio, moneda, stock, imagen, categoria):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos
            (nombre, descripcion, precio, stock, imagen, categoria)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre, descripcion, precio, moneda, stock, imagen, categoria))
        conn.commit()

    def actualizar_categoria(self, producto_id, categoria):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET categoria = ? WHERE id = ?", (categoria, producto_id))
        conn.commit()

    def obtener_producto(self, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        fila = cursor.fetchone()
        return dict(fila) if fila else None

    def obtener_todos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE COALESCE(activo, 1) = 1")
        return [dict(fila) for fila in cursor.fetchall()]

    def obtener_ids(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM productos")
        return [fila[0] for fila in cursor.fetchall()]

    def obtener_por_categoria(self, categoria):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE categoria = ? AND COALESCE(activo, 1) = 1", (categoria,))
        return [dict(fila) for fila in cursor.fetchall()]

    def obtener_por_letra_inicial(self, letra):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM productos
            WHERE nombre LIKE ? COLLATE NOCASE AND COALESCE(activo, 1) = 1
            ORDER BY nombre
        """, (f"{letra}%",))
        return [fila[0] for fila in cursor.fetchall()]

    def buscar_productos(self, texto):
        texto = (texto or "").strip()
        if not texto:
            return []
        palabras = [p for p in texto.split() if p]
        if not palabras:
            return []
        conn = obtener_conexion()
        cursor = conn.cursor()
        condiciones = []
        valores = []
        for palabra in palabras:
            patron = f"%{palabra}%"
            condiciones.append("""(
                nombre LIKE ? COLLATE NOCASE OR
                descripcion LIKE ? COLLATE NOCASE OR
                categoria LIKE ? COLLATE NOCASE OR
                marca LIKE ? COLLATE NOCASE
            )""")
            valores.extend([patron, patron, patron, patron])
        query = f"SELECT * FROM productos WHERE {' AND '.join(condiciones)} AND COALESCE(activo, 1) = 1"
        cursor.execute(query, valores)
        filas = [dict(fila) for fila in cursor.fetchall()]

        texto_lower = texto.lower()
        def puntuar(producto):
            nombre = (producto["nombre"] or "").lower()
            categoria = (producto["categoria"] or "").lower()
            marca = (producto["marca"] or "").lower()
            puntaje = 0
            if nombre == texto_lower:
                puntaje += 100
            elif nombre.startswith(texto_lower):
                puntaje += 60
            elif texto_lower in nombre:
                puntaje += 40
            puntaje += sum(10 for p in palabras if p.lower() in nombre)
            if texto_lower in categoria or texto_lower in marca:
                puntaje += 5
            return puntaje

        filas.sort(key=puntuar, reverse=True)
        return [f["id"] for f in filas]

    def sugerir_productos(self, texto, limite=6):
        texto = (texto or "").strip()
        if not texto:
            return []
        conn = obtener_conexion()
        cursor = conn.cursor()
        patron_prefijo = f"{texto}%"
        patron_contiene = f"%{texto}%"
        cursor.execute("""
            SELECT DISTINCT nombre,
                CASE WHEN nombre LIKE ? COLLATE NOCASE THEN 2 ELSE 1 END AS prioridad
            FROM productos
            WHERE nombre LIKE ? COLLATE NOCASE AND COALESCE(activo, 1) = 1
            ORDER BY prioridad DESC, LENGTH(nombre) ASC, nombre ASC
            LIMIT ?
        """, (patron_prefijo, patron_contiene, limite))
        return [fila[0] for fila in cursor.fetchall()]

    def agregar_oferta(self, producto_id, tipo, valor=None, medio_pago=None,
                        cuotas_cantidad=None, cuotas_interes=0, etiqueta_personalizada=None, fecha_fin=None):
        if tipo not in TIPOS_OFERTA_VALIDOS:
            return False
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE ofertas SET activa = 0 WHERE producto_id = ? AND activa = 1", (producto_id,))
        cursor.execute("""
            INSERT INTO ofertas
            (producto_id, tipo, valor, medio_pago, cuotas_cantidad, cuotas_interes, etiqueta_personalizada, fecha_fin, activa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (producto_id, tipo, valor, medio_pago, cuotas_cantidad, int(cuotas_interes), etiqueta_personalizada, fecha_fin))
        conn.commit()
        return True

    def obtener_oferta_activa(self, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM ofertas
            WHERE producto_id = ? AND activa = 1
            ORDER BY fecha_creacion DESC LIMIT 1
        """, (producto_id,))
        fila = cursor.fetchone()
        return dict(fila) if fila else None

    def desactivar_oferta(self, oferta_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE ofertas SET activa = 0 WHERE id = ?", (oferta_id,))
        desactivada = cursor.rowcount > 0
        conn.commit()
        return desactivada

    def obtener_ofertas(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, o.id AS oferta_id, o.tipo AS oferta_tipo, o.valor AS oferta_valor,
                   o.medio_pago AS oferta_medio_pago, o.cuotas_cantidad AS oferta_cuotas_cantidad,
                   o.cuotas_interes AS oferta_cuotas_interes, o.etiqueta_personalizada AS oferta_etiqueta
            FROM productos p
            JOIN ofertas o ON o.producto_id = p.id
            WHERE o.activa = 1
        """)
        return [dict(fila) for fila in cursor.fetchall()]

    def obtener_mas_vendidos(self, limite=None):
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            SELECT id FROM productos
            WHERE COALESCE(activo, 1) = 1
            ORDER BY COALESCE(vendidos, 0) DESC, id DESC
        """
        if limite:
            query += " LIMIT ?"
            cursor.execute(query, (limite,))
        else:
            cursor.execute(query)
        return [fila[0] for fila in cursor.fetchall()]

    def obtener_ids_en_oferta(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT p.id
            FROM productos p
            JOIN ofertas o ON o.producto_id = p.id
            WHERE o.activa = 1 AND COALESCE(p.activo, 1) = 1
            ORDER BY p.id DESC
        """)
        return [fila[0] for fila in cursor.fetchall()]

    def actualizar_oferta(self, producto_id, precio_oferta):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET precio_oferta = ? WHERE id = ?", (precio_oferta, producto_id))
        conn.commit()

    def agregar_imagen(self, producto_id, imagen, orden):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO producto_imagenes (producto_id, imagen, orden)
            VALUES (?, ?, ?)
        """, (producto_id, imagen, orden))
        conn.commit()

    def obtener_imagenes(self, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT imagen FROM producto_imagenes WHERE producto_id = ? ORDER BY orden", (producto_id,))
        return [fila[0] for fila in cursor.fetchall()]

    def obtener_vendedor_producto(self, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.nombre_visible
            FROM productos p
            JOIN usuarios u ON p.vendedor_id = u.id
            WHERE p.id = ?
        """, (producto_id,))
        fila = cursor.fetchone()
        if fila:
            return {"nombre_visible": fila[0]}
        return None

    def obtener_resumen_calificacion_vendedor(self, vendedor_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT AVG(o.calificacion), COUNT(*)
            FROM opiniones o
            JOIN productos p ON p.id = o.producto_id
            WHERE p.vendedor_id = ?
        """, (vendedor_id,))
        promedio, total = cursor.fetchone()
        return {"promedio": promedio or 0, "total": total or 0}

    def _recalcular_calificacion(self, cursor, producto_id):
        cursor.execute("SELECT AVG(calificacion) FROM opiniones WHERE producto_id = ?", (producto_id,))
        promedio = cursor.fetchone()[0] or 0
        cursor.execute("UPDATE productos SET calificacion = ? WHERE id = ?", (promedio, producto_id))

    def agregar_opinion(self, producto_id, usuario_id, calificacion, comentario, pais="AR"):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO opiniones (producto_id, usuario_id, calificacion, comentario, pais)
            VALUES (?, ?, ?, ?, ?)
        """, (producto_id, usuario_id, calificacion, comentario, pais))
        self._recalcular_calificacion(cursor, producto_id)
        conn.commit()

    def obtener_opiniones(self, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.usuario_id, o.calificacion, o.comentario, o.fecha_creacion, o.pais, u.nombre_visible,
                   (SELECT COUNT(*) FROM opinion_utiles ou WHERE ou.opinion_id = o.id) AS utiles
            FROM opiniones o
            LEFT JOIN usuarios u ON o.usuario_id = u.id
            WHERE o.producto_id = ?
            ORDER BY o.fecha_creacion DESC
        """, (producto_id,))
        return [dict(fila) for fila in cursor.fetchall()]

    def usuario_ya_opino(self, producto_id, usuario_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM opiniones WHERE producto_id = ? AND usuario_id = ?", (producto_id, usuario_id))
        return cursor.fetchone() is not None

    def eliminar_opinion(self, opinion_id, usuario_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT producto_id FROM opiniones WHERE id = ? AND usuario_id = ?", (opinion_id, usuario_id))
        fila = cursor.fetchone()
        if not fila:
            return False
        producto_id = fila[0]
        cursor.execute("DELETE FROM opiniones WHERE id = ? AND usuario_id = ?", (opinion_id, usuario_id))
        eliminado = cursor.rowcount > 0
        if eliminado:
            self._recalcular_calificacion(cursor, producto_id)
        conn.commit()
        return eliminado

    def editar_opinion(self, opinion_id, usuario_id, calificacion, comentario):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE opiniones SET calificacion = ?, comentario = ?
            WHERE id = ? AND usuario_id = ?
        """, (calificacion, comentario, opinion_id, usuario_id))
        editado = cursor.rowcount > 0
        if editado:
            cursor.execute("SELECT producto_id FROM opiniones WHERE id = ?", (opinion_id,))
            producto_id = cursor.fetchone()[0]
            self._recalcular_calificacion(cursor, producto_id)
        conn.commit()
        return editado

    def obtener_resumen_calificacion(self, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT calificacion, COUNT(*) FROM opiniones
            WHERE producto_id = ? GROUP BY calificacion
        """, (producto_id,))
        filas = cursor.fetchall()
        por_estrella = {estrella: cantidad for estrella, cantidad in filas}
        total = sum(por_estrella.values())
        promedio = sum(e * c for e, c in por_estrella.items()) / total if total else 0
        return {"por_estrella": por_estrella, "total": total, "promedio": promedio}

    def usuario_marco_util(self, opinion_id, usuario_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM opinion_utiles WHERE opinion_id = ? AND usuario_id = ?", (opinion_id, usuario_id))
        return cursor.fetchone() is not None

    def marcar_util(self, opinion_id, usuario_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM opinion_utiles WHERE opinion_id = ? AND usuario_id = ?", (opinion_id, usuario_id))
        ya_marcado = cursor.fetchone() is not None
        if ya_marcado:
            cursor.execute("DELETE FROM opinion_utiles WHERE opinion_id = ? AND usuario_id = ?", (opinion_id, usuario_id))
        else:
            cursor.execute("INSERT INTO opinion_utiles (opinion_id, usuario_id) VALUES (?, ?)", (opinion_id, usuario_id))
        conn.commit()
        return not ya_marcado

    def eliminar_opinion_moderacion(self, opinion_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT producto_id FROM opiniones WHERE id = ?", (opinion_id,))
        fila = cursor.fetchone()
        if not fila:
            return False
        producto_id = fila[0]
        cursor.execute("DELETE FROM opiniones WHERE id = ?", (opinion_id,))
        eliminado = cursor.rowcount > 0
        if eliminado:
            self._recalcular_calificacion(cursor, producto_id)
        conn.commit()
        return eliminado

    def descontar_stock(self, producto_id, cantidad):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM productos WHERE id = ?", (producto_id,))
        fila = cursor.fetchone()
        if not fila:
            return False
        stock_actual = fila[0] or 0
        if cantidad > stock_actual:
            return False
        nuevo_stock = stock_actual - cantidad
        if nuevo_stock <= 0:
            cursor.execute("""
                UPDATE productos SET stock = 0, vendidos = COALESCE(vendidos, 0) + ?, activo = 0
                WHERE id = ?
            """, (cantidad, producto_id))
        else:
            cursor.execute("""
                UPDATE productos SET stock = ?, vendidos = COALESCE(vendidos, 0) + ?
                WHERE id = ?
            """, (nuevo_stock, cantidad, producto_id))
        conn.commit()
        return True

    def registrar_pedido(self, producto_id, usuario_id, cantidad, precio_unitario, numero_orden, entrega_tipo="retiro", direccion_envio=None):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pedidos (producto_id, usuario_id, cantidad, precio_unitario, numero_orden, entrega_tipo, direccion_envio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (producto_id, usuario_id, cantidad, precio_unitario, numero_orden, entrega_tipo, direccion_envio))
        conn.commit()

    def usuario_compro_producto(self, producto_id, usuario_id):
        if not usuario_id:
            return False
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pedidos WHERE producto_id = ? AND usuario_id = ? LIMIT 1", (producto_id, usuario_id))
        return cursor.fetchone() is not None

    def obtener_pedidos_usuario(self, usuario_id):
        if not usuario_id:
            return []
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pe.id, pe.producto_id, pe.cantidad, pe.precio_unitario, pe.numero_orden, pe.fecha_creacion,
                   pe.entrega_tipo, pe.direccion_envio, p.nombre, p.imagen, p.moneda
            FROM pedidos pe
            JOIN productos p ON p.id = pe.producto_id
            WHERE pe.usuario_id = ?
            ORDER BY pe.fecha_creacion DESC
        """, (usuario_id,))
        return [dict(fila) for fila in cursor.fetchall()]

    # ================= Lista de deseos =================
    def usuario_tiene_en_deseos(self, usuario_id, producto_id):
        if not usuario_id:
            return False
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM lista_deseos WHERE usuario_id = ? AND producto_id = ?", (usuario_id, producto_id))
        return cursor.fetchone() is not None

    def agregar_a_deseos(self, usuario_id, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO lista_deseos (usuario_id, producto_id) VALUES (?, ?)", (usuario_id, producto_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def quitar_de_deseos(self, usuario_id, producto_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lista_deseos WHERE usuario_id = ? AND producto_id = ?", (usuario_id, producto_id))
        eliminado = cursor.rowcount > 0
        conn.commit()
        return eliminado

    def toggle_deseo(self, usuario_id, producto_id):
        if self.usuario_tiene_en_deseos(usuario_id, producto_id):
            self.quitar_de_deseos(usuario_id, producto_id)
            return False
        self.agregar_a_deseos(usuario_id, producto_id)
        return True

    def obtener_ids_deseos(self, usuario_id):
        if not usuario_id:
            return []
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT producto_id FROM lista_deseos WHERE usuario_id = ? ORDER BY fecha_creacion DESC", (usuario_id,))
        return [fila[0] for fila in cursor.fetchall()]