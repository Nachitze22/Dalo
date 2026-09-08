"""
HACER QUE EN CUALQUIER COMPUTADORA EL PROGRAMA SE VEA IGUAL (creo que para este punto 
no hay que usar place, o al menos no de la manera que lo estoy haciendo con parametros x, y)

Acelerar App

MEJORAR ARQUITECTURA

HACER QUE LA APLICACIÓN SEA UN ARCHIVO CLICKEABLE CON ICONO COMO UNA APP REAL
"""

# Imports de Librerias
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
ctk.set_appearance_mode("dark")
from datetime import datetime
from PIL import Image, ImageTk
import threading
import pywinstyles
import requests
from io import BytesIO

# Imports de Archivos
import auth
import variables_globales
from componentes.header import Header
from componentes.vista_login import Vista_login
from componentes.vista_recuperar_password import Vista_recuperar_password
from componentes.grid_productos import GridProductos
from database.db import crear_db
from componentes.vista_inicio import VistaInicio
from helpers import Helpers
from ia import IA
from componentes.vista_producto import VistaProducto
from componentes.pantalla_carga import PantallaCarga
from database.productos_db import ProductosDB
from database.direcciones_db import DireccionesDB
import colores
from componentes.vista_comprar import VistaComprar
from componentes.vista_carrito import VistaCarrito
from componentes.vista_direcciones import VistaSeleccionarDireccion, VistaNuevaDireccion
from componentes.vista_verificar_registro import VistaVerificarRegistro
from componentes.vista_deseos import VistaDeseos
from componentes.vista_busqueda import VistaBusqueda
from componentes.vista_cuenta import VistaCuenta
from database.publicaciones_db import PublicacionesDB
from componentes.vender.vista_vender import VistaVender
from componentes.vender.vista_panel_vendedor import VistaPanelVendedor
from componentes.vista_perfil_vendedor import VistaPerfilVendedor
from componentes.vista_listado import VistaListadoProductos
from componentes.vista_ayuda import VistaAyuda
from database.cupones_db import CuponesDB
from componentes.vista_admin_cupones import VistaAdminCupones
from componentes.vista_configuracion import VistaConfiguracion
import idiomas

class Dalo(Helpers):
    def __init__(self, ventana_principal, usuario):
        self.ventana_principal = ventana_principal
        self.ventana_principal.title("Dalo")
        self.ventana_principal.state("zoomed")
        self.ventana_principal.configure(bg=colores.FONDO_PRINCIPAL)
        pywinstyles.apply_style(self.ventana_principal,"mica")
        self.cache_imagenes = {}
        self.descargas_en_curso = {}
        self.productos_db = ProductosDB()
        self.publicaciones_db = PublicacionesDB()
        self.cupones_db = CuponesDB()
        self.ia = IA(self)
        self.lista_de_deseos_lista = []
        self.carrito_de_compra_pedidos = {}
        self.historial_busquedas = []
        self.direcciones_db = DireccionesDB()
        self.direcciones_guardadas = []
        self.direccion_envio_seleccionada = None
        self.preferencias_notificaciones = {
            "ofertas": True, "pedidos": True, "newsletter": False, "preguntas": True,
        }
        self.cargar_direcciones()
        self.cargar_lista_deseos()
        self.usuario = usuario
        self.variables_globales = variables_globales
        self.auth = auth
        self.historial = []
        self.texto_fecha = tk.StringVar()
        self.texto_hora = tk.StringVar()
        self.nombre = 0
        self.precio = 0
        self.stock = 0
        self.e_productos = []
        # ===== Pantalla de carga =====
        self._carga_activa = True
        self._carga_total = 0
        self._carga_pendientes = 0
        self.pantalla_carga = PantallaCarga(self.ventana_principal, self)
        self.ventana_principal.after(10000, self._finalizar_carga) 
        self.ventana_principal.after(50, self._construir_interfaz) 

    def _construir_interfaz(self):
        self.header = Header(self.ventana_principal,self)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        self.canvas = tk.Canvas(self.ventana_principal, bg=colores.FONDO_PRINCIPAL, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self.ventana_principal, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.main_frame = tk.Frame(self.canvas, bg=colores.FONDO_PRINCIPAL)
        self.canvas_window = self.canvas.create_window((0, 0),window=self.main_frame,anchor="nw")
        self.main_frame.bind("<Configure>", self.actualizar_scroll)
        self.canvas.bind("<Configure>", self.ajustar_ancho)
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self.scroll_mouse))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        self.ventana_principal.update_idletasks()
        self.vista_actual = self.mostrar_inicio
        self.mostrar_inicio()
        self.actualizar_reloj()
        self.pantalla_carga.lift()
        if self._carga_total == 0:
            self._finalizar_carga()

    # ================= Carga inicial =================
    def carga_task_iniciada(self):
        if not self._carga_activa:
            return
        self._carga_total += 1
    def carga_task_finalizada(self):
        if not self._carga_activa:
            return
        self._carga_pendientes += 1
        self.pantalla_carga.actualizar_progreso(self._carga_pendientes, self._carga_total)
        if self._carga_pendientes >= self._carga_total:
            self._finalizar_carga()
    def _finalizar_carga(self):
        if not self._carga_activa:
            return
        self._carga_activa = False
        self.pantalla_carga.finalizar()

    # ================= Métodos =================
    def obtener_imagen(self, url, callback=None):
        if url in self.cache_imagenes:
            if callback:
                callback(self.cache_imagenes[url].copy())
            return self.cache_imagenes[url].copy()
        if callback is None:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            self.cache_imagenes[url] = img
            return img.copy()
        def descargar():
            try:
                response = requests.get(url, timeout=8)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content)).convert("RGBA")
                self.cache_imagenes[url] = img
                self.ventana_principal.after(0,lambda: callback(img.copy()))
            except Exception as e:
                print(e)
                self.ventana_principal.after(0,lambda: callback(None))
        threading.Thread(target=descargar, daemon=True).start()
        return None
    def _icono_imagen(self, parent, url, size, size2, bg=None):
        bg = bg or colores._CARD
        lbl = tk.Label(parent, bg=bg)
        self.carga_task_iniciada()
        def terminar(img):
            try:
                if img is None or not lbl.winfo_exists():
                    return
                img = img.convert("RGBA").resize((size, size2), Image.LANCZOS)
                foto = ImageTk.PhotoImage(img)
                lbl.configure(image=foto)
                lbl.image = foto
            finally:
                self.carga_task_finalizada()
        self.obtener_imagen(url, callback=terminar)
        return lbl
    def vista_login(self):
        self.limpiar_contenido()
        self.login_view = Vista_login(self.main_frame,self)
    def vista_recuperar_password(self, email):
        self.limpiar_contenido()
        self.recuperar_view = Vista_recuperar_password(self.main_frame,self,email)
    def mostrar_verificar_registro(self, email):
        self.limpiar_contenido()
        VistaVerificarRegistro(self.main_frame, self, email)
    def cambiar_vista(self, funcion):
        if hasattr(self, "vista_actual"):
            self.historial.append(self.vista_actual)
        self.vista_actual = funcion
        funcion()
        self.ventana_principal.update_idletasks()
        self.canvas.yview_moveto(0)
        if self.historial:
            self.header.btn_volver.place(x=0, y=0)
        else:
            self.header.btn_volver.place_forget()
    def volver(self):
        if self.historial:
            self.vista_actual = self.historial.pop()
            self.vista_actual()
        if not self.historial:
            self.header.btn_volver.place_forget()
    def limpiar_contenido(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    def mostrar_categoria_ia(self, categoria):
        self.limpiar_contenido()
        productos_a = self.ia.filtrar_hibrido(categoria)
        self.e_productos = productos_a
        contenedor = tk.Frame(self.main_frame, bg=colores.FONDO_PRINCIPAL)
        contenedor.pack(fill="both", expand=True, anchor="nw")
        contenedor.grid_anchor("nw")
        imagenes = []
        GridProductos(self.main_frame,self,self.e_productos)
        self.imagenes_categoria = imagenes
    def actualizar_scroll(self, event=None):
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(self.canvas_window)
        if bbox:
            self.canvas.configure(scrollregion=bbox)
    def scroll_mouse(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    def actualizar_reloj(self):
        if not self.ventana_principal.winfo_exists():
            return
        ahora = datetime.now()
        self.texto_fecha.set(ahora.strftime("%d/%m/%Y"))
        self.texto_hora.set(ahora.strftime("%H:%M:%S"))
        self.ventana_principal.after(1000, self.actualizar_reloj)
    # ================= Contenido En Scroll =================
    def limitar_texto(self, texto, max_chars=32):
        if len(texto) <= max_chars:
            return texto
        return texto[:max_chars-3] + "..."
    def ajustar_ancho(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    def mensaje_temporal(self, texto):
        label = tk.Label(self.ventana_principal,text=texto,bg=colores.FONDO_PRINCIPAL,fg="white",font=("Arial",12))
        label.place(relx=0.5, rely=0.96, anchor="center")
        self.ventana_principal.after(2000, label.destroy)
    def mostrar_inicio(self):
        self.limpiar_contenido()
        VistaInicio(self.main_frame, self)
    def mostrar_producto(self, producto_id):
        self.limpiar_contenido()
        VistaProducto(self.main_frame, self, producto_id)
    def mostrar_comprar(self, producto_id, cantidad=1):
        self.limpiar_contenido()
        VistaComprar(self.main_frame, self, producto_id, cantidad)
    def mostrar_carrito(self):
        self.limpiar_contenido()
        VistaCarrito(self.main_frame, self)
    def actualizar_carrito_ui(self):
        if hasattr(self, "header"):
            self.header.actualizar_badge_carrito()
    def mostrar_deseos(self):
        self.limpiar_contenido()
        VistaDeseos(self.main_frame, self)
    def actualizar_deseos_ui(self):
        if hasattr(self, "header"):
            self.header.actualizar_badge_deseos()
    def mostrar_cuenta(self, seccion="resumen"):
        self.limpiar_contenido()
        VistaCuenta(self.main_frame, self, seccion)
    def mostrar_nueva_direccion(self, direccion_editar=None):
        self.limpiar_contenido()
        VistaNuevaDireccion(self.main_frame, self, direccion_editar)
    def mostrar_seleccionar_direccion(self):
        self.limpiar_contenido()
        VistaSeleccionarDireccion(self.main_frame, self)
    def cargar_direcciones(self):
        usuario_id = None
        sesion = auth.cargar_sesion()
        if sesion:
            usuario_id = auth.obtener_id_por_email(sesion)
        self.direcciones_guardadas = self.direcciones_db.obtener_direcciones_disponibles(usuario_id)
        id_actual = self.direccion_envio_seleccionada.get("id") if self.direccion_envio_seleccionada else None
        if not any(d["id"] == id_actual for d in self.direcciones_guardadas):
            self.direccion_envio_seleccionada = self.direcciones_guardadas[0] if self.direcciones_guardadas else None
        if hasattr(self, "header"):
            self.header.actualizar_texto_envio_a()
    def cargar_lista_deseos(self):
        usuario_id = None
        sesion = auth.cargar_sesion()
        if sesion:
            usuario_id = auth.obtener_id_por_email(sesion)
        self.lista_de_deseos_lista = self.productos_db.obtener_ids_deseos(usuario_id) if usuario_id else []
        if hasattr(self, "header"):
            self.header.actualizar_badge_deseos()
    def agregar_a_historial_busqueda(self, texto):
        texto = (texto or "").strip()
        if not texto:
            return
        texto_lower = texto.lower()
        self.historial_busquedas = [t for t in self.historial_busquedas if t.lower() != texto_lower]
        self.historial_busquedas.insert(0, texto)
        self.historial_busquedas = self.historial_busquedas[:8]
    def borrar_historial_busqueda(self):
        self.historial_busquedas.clear()
    def mostrar_busqueda(self, texto):
        self.limpiar_contenido()
        VistaBusqueda(self.main_frame, self, texto)
    def mostrar_vender(self, producto_id=None):
        self.limpiar_contenido()
        VistaVender(self.main_frame, self, producto_id)
    def mostrar_mas_vendidos(self):
        self.limpiar_contenido()
        ids = self.productos_db.obtener_mas_vendidos()
        VistaListadoProductos(
            self.main_frame, self,
            idiomas.t("mas_vendido_titulo"), idiomas.t("mas_vendido_sub"),
            ids, icono_vacio="🔥", texto_vacio=idiomas.t("mas_vendido_vacio"),
        )
    def mostrar_ofertas(self):
        self.limpiar_contenido()
        ids = self.productos_db.obtener_ids_en_oferta()
        VistaListadoProductos(
            self.main_frame, self,
            idiomas.t("ofertas_titulo"), idiomas.t("ofertas_sub"),
            ids, texto_vacio=idiomas.t("ofertas_vacio"),
        )
    def mostrar_ayuda(self):
        self.limpiar_contenido()
        VistaAyuda(self.main_frame, self)
    def mostrar_panel_vendedor(self):
        self.limpiar_contenido()
        VistaPanelVendedor(self.main_frame, self)
    def mostrar_perfil_vendedor(self, vendedor_id):
        self.limpiar_contenido()
        VistaPerfilVendedor(self.main_frame, self, vendedor_id)
    def es_admin(self):
        sesion = self.auth.cargar_sesion()
        return bool(sesion) and sesion in variables_globales.ADMIN_EMAILS
    def mostrar_admin_cupones(self):
        self.limpiar_contenido()
        VistaAdminCupones(self.main_frame, self)
    def mostrar_configuracion(self):
        self.limpiar_contenido()
        VistaConfiguracion(self.main_frame, self)

    # ================= Idioma =================
    def cambiar_idioma(self, codigo):
        if codigo not in ("es", "en", "fr"):
            return
        variables_globales.guardar_idioma(codigo)
        sesion = self.auth.cargar_sesion()
        if sesion:
            usuario_id = self.auth.obtener_id_por_email(sesion)
            if usuario_id:
                self.auth.actualizar_idioma(usuario_id, codigo)
        # Reconstruye el header completo (sus textos dependen del idioma)
        if hasattr(self, "header"):
            for w in self.header.winfo_children():
                w.destroy()
            self.header.crear_widgets()
        # Vuelve a renderizar la vista actual para que tome las nuevas
        # traducciones, sin apilarla en el historial de navegación.
        if hasattr(self, "vista_actual"):
            self.vista_actual()

# ============== Main ============== 
if __name__ == "__main__":
    crear_db()
    try:
        from tkinterdnd2 import TkinterDnD
        ventana_principal = TkinterDnD.Tk()
    except ImportError:
        ventana_principal = tk.Tk()
    ventana_principal.configure(bg=colores.FONDO_PRINCIPAL)
    ventana_principal.deiconify()
    ventana_principal.state("zoomed")
    Dalo(ventana_principal, "Invitado")
    ventana_principal.mainloop()