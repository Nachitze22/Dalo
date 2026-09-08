import tkinter as tk
import customtkinter as ctk
import json
import os
import bcrypt
import smtplib
from email.mime.text import MIMEText
import random
import sqlite3
from datetime import datetime

SESSION_FILE = "session.json"
DURACION_CODIGO_REGISTRO = 600  # 10 minutos

def obtener_usuario(email):
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email, password, nombre_visible FROM usuarios WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def obtener_id_por_email(email):
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    fila = cursor.fetchone()
    conn.close()
    return fila[0] if fila else None

def obtener_usuario_por_id(id_usuario):
    conn = sqlite3.connect("dalo.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, nombre_visible, fecha_creacion, foto_perfil, foto_perfil_public_id, idioma FROM usuarios WHERE id = ?", (id_usuario,))
    fila = cursor.fetchone()
    conn.close()
    return dict(fila) if fila else None

def obtener_nombre_visible(email):
    usuario = obtener_usuario(email)
    if usuario:
        return usuario[2]
    return email

def guardar_usuario(email, password, nombre_visible=None):
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (email, password, nombre_visible) VALUES (?, ?, ?)", (email, password, nombre_visible))
        conn.commit()
    except Exception as e:
        conn.close()
        print(e)
        return False
    conn.close()
    return True

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verificar_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def guardar_sesion(email):
    with open(SESSION_FILE, "w") as f:
        json.dump({"email": email}, f)

def cargar_sesion():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r") as f:
        return json.load(f).get("email")

def cerrar_sesion():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def enviar_codigo(email):
    codigo = str(random.randint(100000, 999999))
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not remitente or not password:
        print("Faltan variables de entorno")
        return None
    nombre = email.split("@")[0].capitalize()
    html = f"""
    <html>
    <body style="font-family: Arial; background:#f4f4f4; padding:20px;">
        <div style="max-width:500px;margin:auto;background:white;padding:25px;border-radius:10px;">
            <h2 style="color:#2563eb;">Dalo</h2>
            <p>Hola <b>{nombre}</b>,</p>
            <p>Gracias por registrarte.</p>
            <p>Tu código de verificación es:</p>
            <h1 style="text-align:center;letter-spacing:5px;">{codigo}</h1>
            <p style="text-align:center;color:#666;">Válido por 10 minutos</p>
            <hr>
            <p style="font-size:12px;color:#888;">Si tu no haz solicitado este mensaje, ignóralo.</p>
            <p style="font-size:12px;color:#888;">— Equipo de Dalo</p>
        </div>
    </body>
    </html>
    """
    mensaje = MIMEText(html, "html")
    mensaje["Subject"] = "Código de verificación – Dalo"
    mensaje["From"] = f"Dalo <{remitente}>"
    mensaje["To"] = email
    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.send_message(mensaje)
        servidor.quit()
        return codigo
    except Exception as e:
        print(e)
        return None

def actualizar_password(email, nueva_password):
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET password = ? WHERE email = ?",
        (hash_password(nueva_password), email)
    )
    conn.commit()
    conn.close()

# ================= Registro con verificación por email =================
def _enviar_codigo_registro(email, nombre_visible, codigo):
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    if not remitente or not password:
        print("Faltan variables de entorno")
        return False
    html = f"""
    <html>
    <body style="font-family: Arial; background:#f4f4f4; padding:20px;">
        <div style="max-width:500px;margin:auto;background:white;padding:25px;border-radius:10px;">
            <h2 style="color:#2563eb;">Dalo</h2>
            <p>Hola <b>{nombre_visible}</b>,</p>
            <p>Para terminar de crear tu cuenta, ingresá este código de verificación:</p>
            <h1 style="text-align:center;letter-spacing:5px;">{codigo}</h1>
            <p style="text-align:center;color:#666;">Válido por 10 minutos</p>
            <hr>
            <p style="font-size:12px;color:#888;">Si vos no solicitaste esto, ignorá este mensaje.</p>
            <p style="font-size:12px;color:#888;">— Equipo de Dalo</p>
        </div>
    </body>
    </html>
    """
    mensaje = MIMEText(html, "html")
    mensaje["Subject"] = "Confirmá tu cuenta – Dalo"
    mensaje["From"] = f"Dalo <{remitente}>"
    mensaje["To"] = email
    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.send_message(mensaje)
        servidor.quit()
        return True
    except Exception as e:
        print(e)
        return False

def iniciar_registro(email, password_hash, nombre_visible):
    """Guarda un registro pendiente de verificación y envía el código por email.
    Devuelve el código si se envió correctamente, o None si falló."""
    codigo = str(random.randint(100000, 999999))
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO registros_pendientes (email, password, nombre_visible, codigo, fecha_creacion)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(email) DO UPDATE SET
                password = excluded.password,
                nombre_visible = excluded.nombre_visible,
                codigo = excluded.codigo,
                fecha_creacion = CURRENT_TIMESTAMP
        """, (email, password_hash, nombre_visible, codigo))
        conn.commit()
    except Exception as e:
        conn.close()
        print(e)
        return None
    conn.close()
    if not _enviar_codigo_registro(email, nombre_visible, codigo):
        return None
    return codigo

def reenviar_codigo_registro(email):
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_visible FROM registros_pendientes WHERE email = ?", (email,))
    fila = cursor.fetchone()
    if not fila:
        conn.close()
        return False
    nombre_visible = fila[0]
    codigo = str(random.randint(100000, 999999))
    cursor.execute("""
        UPDATE registros_pendientes SET codigo = ?, fecha_creacion = CURRENT_TIMESTAMP
        WHERE email = ?
    """, (codigo, email))
    conn.commit()
    conn.close()
    return _enviar_codigo_registro(email, nombre_visible, codigo)

def verificar_codigo_registro(email, codigo):
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, fecha_creacion FROM registros_pendientes WHERE email = ?", (email,))
    fila = cursor.fetchone()
    conn.close()
    if not fila:
        return False, "No hay un registro pendiente para este correo"
    codigo_guardado, fecha_creacion = fila
    try:
        creado = datetime.strptime(fecha_creacion, "%Y-%m-%d %H:%M:%S")
        if (datetime.utcnow() - creado).total_seconds() > DURACION_CODIGO_REGISTRO:
            return False, "El código expiró, pedí uno nuevo"
    except (TypeError, ValueError):
        pass
    if codigo != codigo_guardado:
        return False, "Código incorrecto"
    return True, "Código verificado correctamente"

def completar_registro(email):
    """Mueve el registro pendiente a la tabla usuarios. Devuelve False si el email ya existe."""
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password, nombre_visible FROM registros_pendientes WHERE email = ?", (email,))
    fila = cursor.fetchone()
    if not fila:
        conn.close()
        return False
    password_hash, nombre_visible = fila
    try:
        cursor.execute("INSERT INTO usuarios (email, password, nombre_visible) VALUES (?, ?, ?)", (email, password_hash, nombre_visible))
        cursor.execute("DELETE FROM registros_pendientes WHERE email = ?", (email,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.close()
    return True

def actualizar_foto_perfil(usuario_id, url, public_id=None):
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET foto_perfil = ?, foto_perfil_public_id = ? WHERE id = ?",
        (url, public_id, usuario_id),
    )
    actualizado = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return actualizado

# ================= Idioma =================
def obtener_idioma(usuario_id):
    if not usuario_id:
        return "es"
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT idioma FROM usuarios WHERE id = ?", (usuario_id,))
    fila = cursor.fetchone()
    conn.close()
    return fila[0] if fila and fila[0] else "es"

def actualizar_idioma(usuario_id, idioma):
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET idioma = ? WHERE id = ?", (idioma, usuario_id))
    actualizado = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return actualizado

# ================= Eliminar cuenta =================
def eliminar_cuenta(usuario_id, email):
    conn = sqlite3.connect("dalo.db")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        conn.commit()
        eliminado = cursor.rowcount > 0
    except Exception as e:
        print(f"Error eliminando cuenta: {e}")
        eliminado = False
    conn.close()
    if eliminado:
        cerrar_sesion()
    return eliminado