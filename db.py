import sqlite3
import os
import threading
import variables_globales

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dalo.db")

_conn = None
_lock = threading.Lock()


def obtener_conexion():
    global _conn
    if _conn is None:
        with _lock:
            if _conn is None:
                _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                _conn.row_factory = sqlite3.Row
                _conn.execute("PRAGMA journal_mode=WAL")
                _conn.execute("PRAGMA foreign_keys=ON")
    return _conn


def crear_db():
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros_pendientes (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            nombre_visible TEXT NOT NULL,
            codigo TEXT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            imagen TEXT,
            categoria TEXT,
            vendedor_id INTEGER,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS producto_imagenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            imagen TEXT NOT NULL,
            orden INTEGER DEFAULT 1,
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sedes (
            id TEXT PRIMARY KEY,
            etiqueta TEXT NOT NULL,
            direccion_completa TEXT NOT NULL,
            cp TEXT NOT NULL,
            localidad TEXT NOT NULL,
            tipo TEXT NOT NULL,
            activa INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS direcciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            etiqueta TEXT NOT NULL,
            direccion_completa TEXT NOT NULL,
            cp TEXT,
            localidad TEXT,
            provincia TEXT,
            departamento TEXT,
            indicaciones TEXT,
            nombre_receptor TEXT,
            telefono_receptor TEXT,
            tipo TEXT DEFAULT 'guardada',
            activa INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opiniones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            usuario_id INTEGER,
            calificacion INTEGER NOT NULL,
            comentario TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(producto_id) REFERENCES productos(id),
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opinion_utiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opinion_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            UNIQUE(opinion_id, usuario_id),
            FOREIGN KEY(opinion_id) REFERENCES opiniones(id),
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL,
            numero_orden TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(producto_id) REFERENCES productos(id),
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lista_deseos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(usuario_id, producto_id),
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ofertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL,
            medio_pago TEXT,
            cuotas_cantidad INTEGER,
            cuotas_interes INTEGER DEFAULT 0,
            etiqueta_personalizada TEXT,
            activa INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cupones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            monto_minimo REAL DEFAULT 0,
            usos_maximos INTEGER,
            usos_actuales INTEGER DEFAULT 0,
            fecha_fin TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cupones_usos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cupon_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            fecha_uso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(cupon_id, usuario_id),
            FOREIGN KEY(cupon_id) REFERENCES cupones(id),
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    _migrar_columnas(cursor)
    _sembrar_sedes(cursor)
    conn.commit()


def _migrar_columnas(cursor):
    migraciones = [
        ("opiniones", "pais", "TEXT DEFAULT 'AR'"),
        ("productos", "precio_oferta", "REAL"),
        ("ofertas", "fecha_fin", "TEXT"),
        ("productos", "vendidos", "INTEGER DEFAULT 0"),
        ("productos", "marca", "TEXT DEFAULT 'No especificado'"),
        ("productos", "garantia", "TEXT DEFAULT 'No especificado'"),
        ("productos", "moneda", "TEXT DEFAULT 'ARS'"),
        ("productos", "activo", "INTEGER DEFAULT 1"),
        ("productos", "calificacion", "REAL DEFAULT 0"),
        ("usuarios", "nombre_visible", "TEXT"),
        ("usuarios", "fecha_creacion", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("usuarios", "foto_perfil", "TEXT"),
        ("usuarios", "foto_perfil_public_id", "TEXT"),
        ("usuarios", "idioma", "TEXT DEFAULT 'es'"),
        ("pedidos", "entrega_tipo", "TEXT DEFAULT 'retiro'"),
        ("pedidos", "direccion_envio", "TEXT"),
    ]
    for tabla, columna, tipo in migraciones:
        try:
            cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
        except sqlite3.OperationalError:
            pass


def _sembrar_sedes(cursor):
    cursor.execute("""
        INSERT OR IGNORE INTO sedes (id, etiqueta, direccion_completa, cp, localidad, tipo, activa)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (
        "sede_culpina",
        "Culpina 3308",
        variables_globales.SEDE_DIRECCION,
        "1437",
        "Villa Soldati, CABA",
        "sede",
    ))