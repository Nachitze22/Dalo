import hashlib
import os
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import requests
from PIL import Image, ImageTk, ImageDraw
import colores
import idiomas
import cloudinary_utils


class VistaCuenta:
    RADIO_GRANDE = 22
    RADIO_MEDIO = 18
    RADIO_CHICO = 14

    def __init__(self, parent, app, seccion="resumen"):
        self.parent = parent
        self.app = app
        self._imagenes = {}
        self._avatar_foto = None
        self._avatar_modo = "inicial"
        self._avatar_inicial_letra = "?"
        self.contenedor_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor_principal.pack(fill="both", expand=True, padx=54, pady=40)

        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self._mostrar_requiere_login()
            return

        self.email = sesion
        self.usuario_id = self.app.auth.obtener_id_por_email(sesion)
        self.usuario_info = self.app.auth.obtener_usuario_por_id(self.usuario_id) or {}

        self.SECCIONES = [
            ("resumen", "🏠", "cuenta_seccion_resumen"),
            ("compras", "📦", "cuenta_seccion_compras"),
            ("ventas", "💰", "cuenta_seccion_ventas"),
            ("datos", "🧾", "cuenta_seccion_datos"),
        ]

        claves_validas = {s[0] for s in self.SECCIONES}
        self.seccion_actual = seccion if seccion in claves_validas else "resumen"

        self.card = ctk.CTkFrame(self.contenedor_principal, corner_radius=self.RADIO_GRANDE, fg_color=colores._CARD, border_width=1, border_color=colores._CARD_BORDE)
        self.card.pack(fill="both", expand=True)
        self.pad = tk.Frame(self.card, bg=colores._CARD)
        self.pad.pack(fill="both", expand=True, padx=46, pady=42)
        self.construir()

    # ================= Sin sesión =================
    def _mostrar_requiere_login(self):
        card = ctk.CTkFrame(self.contenedor_principal, corner_radius=self.RADIO_GRANDE, fg_color=colores._CARD, border_width=1, border_color=colores._CARD_BORDE)
        card.pack(fill="both", expand=True)
        contenedor = tk.Frame(card, bg=colores._CARD)
        contenedor.pack(expand=True, pady=90)
        tk.Label(contenedor, text="👤", bg=colores._CARD, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 52)).pack()
        tk.Label(contenedor, text=idiomas.t("cuenta_requiere_login_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 17, "bold")).pack(pady=(16, 6))
        tk.Label(contenedor, text=idiomas.t("cuenta_requiere_login_desc"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(pady=(0, 22))
        ctk.CTkButton(contenedor, text=idiomas.t("config_requiere_login_btn"), corner_radius=self.RADIO_CHICO, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 12, "bold"), height=42, width=180, command=lambda: self.app.cambiar_vista(self.app.vista_login)).pack()

    # ================= Construcción =================
    def construir(self):
        for w in self.pad.winfo_children():
            w.destroy()
        self._crear_header()
        cuerpo = tk.Frame(self.pad, bg=colores._CARD)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(0, weight=29)
        cuerpo.grid_columnconfigure(1, weight=0)
        cuerpo.grid_columnconfigure(2, weight=71)
        cuerpo.grid_rowconfigure(0, weight=1)
        self.col_izq = tk.Frame(cuerpo, bg=colores._CARD)
        self.col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 30))
        tk.Frame(cuerpo, bg=colores._SEPARADOR, width=1).grid(row=0, column=1, sticky="ns", pady=6)
        self.col_der = tk.Frame(cuerpo, bg=colores._CARD)
        self.col_der.grid(row=0, column=2, sticky="nsew", padx=(30, 0))
        self._crear_sidebar()
        self._crear_contenido()

    # ================= Encabezado con avatar editable =================
    def _crear_header(self):
        fila = tk.Frame(self.pad, bg=colores._CARD)
        fila.pack(fill="x", pady=(0, 32))
        nombre = self.usuario_info.get("nombre_visible") or self.email.split("@")[0].capitalize()
        self._avatar_inicial_letra = nombre[0].upper() if nombre else "?"
        self._avatar_modo = "inicial"

        self.avatar_canvas = tk.Canvas(fila, width=66, height=66, bg=colores._CARD, highlightthickness=0, cursor="hand2")
        self.avatar_canvas.pack(side="left", padx=(0, 20))
        self._redibujar_avatar_base()
        self._cargar_avatar_inicial_o_gravatar()
        self._registrar_eventos_avatar()

        textos = tk.Frame(fila, bg=colores._CARD)
        textos.pack(side="left", anchor="w")
        tk.Label(textos, text=idiomas.t("cuenta_mi_cuenta"), bg=colores._CARD, fg=colores.MARCA_TEAL, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(textos, text=idiomas.t("cuenta_hola", nombre=nombre), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 27, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Label(textos, text=self.email, bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(anchor="w", pady=(3, 0))
        tk.Frame(self.pad, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(0, 32))

    # ----- Dibujo base del avatar -----
    def _redibujar_avatar_base(self):
        if not self.avatar_canvas.winfo_exists():
            return
        self.avatar_canvas.delete("all")
        if self._avatar_modo == "foto" and self._avatar_foto is not None:
            self.avatar_canvas.create_image(33, 33, image=self._avatar_foto)
            self.avatar_canvas.create_oval(2, 2, 64, 64, outline=colores.MARCA_TEAL, width=2)
        else:
            self.avatar_canvas.create_oval(2, 2, 64, 64, fill=colores._CUENTA_AVATAR_BG, outline="")
            self.avatar_canvas.create_text(33, 34, text=self._avatar_inicial_letra, fill=colores._TEXTO, font=("Segoe UI", 23, "bold"))

    def _mostrar_imagen_en_avatar(self, img):
        if not self.avatar_canvas.winfo_exists():
            return
        img = img.convert("RGBA").resize((66, 66), Image.LANCZOS)
        mascara = Image.new("L", (66, 66), 0)
        ImageDraw.Draw(mascara).ellipse((0, 0, 66, 66), fill=255)
        img.putalpha(mascara)
        self._avatar_foto = ImageTk.PhotoImage(img)
        self._avatar_modo = "foto"
        self._redibujar_avatar_base()

    def _cargar_avatar_inicial_o_gravatar(self):
        url_foto = self.usuario_info.get("foto_perfil")
        if url_foto and str(url_foto).startswith("http"):
            def terminar(img):
                if img is None or not self.avatar_canvas.winfo_exists():
                    return
                self._mostrar_imagen_en_avatar(img)
            self.app.obtener_imagen(url_foto, callback=terminar)
            return
        self._cargar_avatar_gravatar(self.email)

    def _cargar_avatar_gravatar(self, email):
        email_hash = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
        url = f"https://www.gravatar.com/avatar/{email_hash}?s=132&d=404"

        def terminar(img):
            if img is None or not self.avatar_canvas.winfo_exists():
                return
            self._mostrar_imagen_en_avatar(img)

        self.app.obtener_imagen(url, callback=terminar)

    # ----- Interacción avatar -----
    def _registrar_eventos_avatar(self):
        self.avatar_canvas.bind("<Enter>", self._mostrar_overlay_editar)
        self.avatar_canvas.bind("<Leave>", lambda e: self._redibujar_avatar_base())
        self.avatar_canvas.bind("<Button-1>", lambda e: self._iniciar_cambio_foto())
        self._registrar_drag_and_drop()

    def _mostrar_overlay_editar(self, event=None):
        if not self.avatar_canvas.winfo_exists():
            return
        self.avatar_canvas.create_oval(2, 2, 64, 64, fill=colores.MARCA_DARK, stipple="gray50", outline="")
        self.avatar_canvas.create_text(33, 33, text="✎", fill=colores.TEXTO_BLANCO, font=("Segoe UI Symbol", 20, "bold"))

    def _registrar_drag_and_drop(self):
        try:
            from tkinterdnd2 import DND_FILES, DND_TEXT
        except ImportError:
            return
        try:
            self.avatar_canvas.drop_target_register(DND_FILES, DND_TEXT)
            self.avatar_canvas.dnd_bind("<<Drop>>", self._manejar_drop)
        except Exception as e:
            print(f"Drag and drop no disponible: {e}")

    def _manejar_drop(self, event):
        datos = (getattr(event, "data", "") or "").strip()
        if not datos:
            return
        partes = self.avatar_canvas.tk.splitlist(datos)
        if not partes:
            return
        origen = partes[0].strip("{}")
        if origen.startswith("http://") or origen.startswith("https://"):
            self._procesar_imagen_desde_url(origen)
        else:
            self._procesar_imagen_perfil(origen)

    def _iniciar_cambio_foto(self):
        ruta = filedialog.askopenfilename(
            title="",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")],
        )
        if not ruta:
            return
        self._procesar_imagen_perfil(ruta)

    def _procesar_imagen_desde_url(self, url):
        self.app.mensaje_temporal("...")
        def descargar():
            try:
                respuesta = requests.get(url, timeout=8)
                respuesta.raise_for_status()
                extension = os.path.splitext(url.split("?")[0])[1] or ".jpg"
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
                temp.write(respuesta.content)
                temp.close()
                self.app.ventana_principal.after(0, lambda: self._procesar_imagen_perfil(temp.name, es_temporal=True))
            except Exception as e:
                print(f"Error descargando imagen arrastrada: {e}")
        threading.Thread(target=descargar, daemon=True).start()

    def _procesar_imagen_perfil(self, ruta, es_temporal=False):
        def resultado(es_valida, mensaje):
            if es_valida:
                if not self._guardar_foto_perfil(ruta):
                    mensaje = "..."
            if es_temporal:
                try:
                    os.remove(ruta)
                except OSError:
                    pass
            if self.avatar_canvas.winfo_exists():
                self.app.mensaje_temporal(mensaje)

        self.app.ia.verificar_imagen_perfil(ruta, resultado)

    def _guardar_foto_perfil(self, ruta_origen):
        ruta_temp = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                ruta_temp = tmp.name
            with Image.open(ruta_origen) as img:
                img = img.convert("RGB")
                img.save(ruta_temp, format="JPEG", quality=90)

            url, public_id = cloudinary_utils.subir_foto_perfil(ruta_temp, self.usuario_id)
            if not url:
                return False
            if not self.app.auth.actualizar_foto_perfil(self.usuario_id, url, public_id):
                return False

            self.usuario_info["foto_perfil"] = url
            self.usuario_info["foto_perfil_public_id"] = public_id

            def terminar(img_descargada):
                if img_descargada is None or not self.avatar_canvas.winfo_exists():
                    return
                self._mostrar_imagen_en_avatar(img_descargada)

            self.app.obtener_imagen(url, callback=terminar)
            return True
        except Exception as e:
            print(f"Error guardando foto de perfil: {e}")
            return False
        finally:
            if ruta_temp:
                try:
                    os.remove(ruta_temp)
                except OSError:
                    pass

    # ================= Sidebar =================
    def _crear_sidebar(self):
        tk.Label(self.col_izq, text=idiomas.t("cuenta_seccion_resumen_sidebar"), bg=colores._CARD, fg=colores._CUENTA_SECCION_TITULO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 10))
        for clave, icono, titulo_key in self.SECCIONES:
            if clave == "ventas":
                comando = lambda: self.app.cambiar_vista(self.app.mostrar_panel_vendedor)
            else:
                comando = lambda c=clave: self._cambiar_seccion(c)
            self._fila_menu(self.col_izq, icono, idiomas.t(titulo_key), activo=(clave == self.seccion_actual), comando=comando)
        tk.Frame(self.col_izq, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=18)
        tk.Label(self.col_izq, text=idiomas.t("cuenta_accesos_rapidos"), bg=colores._CARD, fg=colores._CUENTA_SECCION_TITULO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 10))
        self._fila_menu(self.col_izq, "📍", idiomas.t("cuenta_direcciones"), activo=False, comando=lambda: self.app.cambiar_vista(self.app.mostrar_seleccionar_direccion))
        self._fila_menu(self.col_izq, "✨", idiomas.t("cuenta_lista_deseos"), activo=False, comando=lambda: self.app.cambiar_vista(self.app.mostrar_deseos))
        self._fila_menu(self.col_izq, "🛒", idiomas.t("cuenta_carrito"), activo=False, comando=lambda: self.app.cambiar_vista(self.app.mostrar_carrito))
        tk.Frame(self.col_izq, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=18)
        self._fila_menu(self.col_izq, "🚪", idiomas.t("cuenta_cerrar_sesion"), activo=False, comando=self._cerrar_sesion, color_texto=colores._CARRITO_ELIMINAR)

    def _fila_menu(self, parent, icono, titulo, activo, comando, color_texto=None):
        bg = colores._CHECKOUT_CARD_SELECCIONADA if activo else colores._CUENTA_BTN_FONDO
        bg_hover = colores._CUENTA_BTN_FONDO_HOVER
        fg = color_texto or (colores.MARCA_TEAL if activo else colores._TEXTO)
        fila = ctk.CTkFrame(parent, corner_radius=self.RADIO_CHICO, fg_color=bg, cursor="hand2")
        fila.pack(fill="x", pady=3)
        interior = tk.Frame(fila, bg=bg)
        interior.pack(fill="x", padx=8, pady=8)
        circulo = tk.Canvas(interior, width=28, height=28, bg=bg, highlightthickness=0)
        circulo.pack(side="left", padx=(4, 10))
        circulo.create_oval(1, 1, 27, 27, fill=colores.MARCA_TEAL, outline="")
        circulo.create_text(14, 14, text=icono, font=("Segoe UI Symbol", 11))
        lbl = tk.Label(interior, text=titulo, bg=bg, fg=fg, font=("Segoe UI", 12, "bold" if activo else "normal"), anchor="w", wraplength=170, justify="left")
        lbl.pack(side="left", fill="x", expand=True)

        widgets = [fila, interior, circulo, lbl]

        def entrar(e=None):
            if activo:
                return
            fila.configure(fg_color=bg_hover)
            interior.configure(bg=bg_hover)
            circulo.configure(bg=bg_hover)
            lbl.configure(bg=bg_hover)

        def salir(e=None):
            if activo:
                return
            fila.configure(fg_color=bg)
            interior.configure(bg=bg)
            circulo.configure(bg=bg)
            lbl.configure(bg=bg)

        for w in widgets:
            w.bind("<Button-1>", lambda e: comando())
            w.bind("<Enter>", entrar)
            w.bind("<Leave>", salir)
        return fila

    def _cambiar_seccion(self, clave):
        if clave == self.seccion_actual:
            return
        self.seccion_actual = clave
        self.construir()

    def _cerrar_sesion(self):
        if hasattr(self.app, "header"):
            self.app.header.cerrar_sesion_ui()

    # ================= Contenido por sección =================
    def _crear_contenido(self):
        if self.seccion_actual == "compras":
            self._seccion_compras()
        elif self.seccion_actual == "ventas":
            self._seccion_ventas()
        elif self.seccion_actual == "datos":
            self._seccion_datos()
        else:
            self._seccion_resumen()

    def _titulo_seccion(self, texto):
        tk.Label(self.col_der, text=texto, bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 19, "bold")).pack(anchor="w", pady=(0, 22))

    # ----- Resumen (tarjetas) -----
    def _seccion_resumen(self):
        self._titulo_seccion(idiomas.t("cuenta_seccion_resumen"))
        opciones = [
            ("📦", idiomas.t("cuenta_seccion_compras"), idiomas.t("cuenta_compras_desc"), lambda: self._cambiar_seccion("compras")),
            ("💰", idiomas.t("cuenta_seccion_ventas"), idiomas.t("cuenta_ventas_desc"), lambda: self.app.cambiar_vista(self.app.mostrar_panel_vendedor)),
            ("📍", idiomas.t("cuenta_direcciones"), idiomas.t("cuenta_direcciones_desc"), lambda: self.app.cambiar_vista(self.app.mostrar_seleccionar_direccion)),
            ("✨", idiomas.t("cuenta_lista_deseos"), idiomas.t("cuenta_deseos_desc"), lambda: self.app.cambiar_vista(self.app.mostrar_deseos)),
            ("🛒", idiomas.t("cuenta_carrito"), idiomas.t("cuenta_carrito_desc"), lambda: self.app.cambiar_vista(self.app.mostrar_carrito)),
        ]
        grid = tk.Frame(self.col_der, bg=colores._CARD)
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=1, uniform="cuenta")
        grid.grid_columnconfigure(1, weight=1, uniform="cuenta")
        for i, (icono, titulo, desc, comando) in enumerate(opciones):
            fila, columna = divmod(i, 2)
            self._tarjeta_elevada(grid, icono, titulo, desc, comando).grid(row=fila, column=columna, sticky="nsew", padx=10, pady=10)

    def _tarjeta_elevada(self, parent, icono, titulo, desc, comando):
        tarjeta = ctk.CTkFrame(parent, corner_radius=self.RADIO_MEDIO, fg_color=colores._CUENTA_BTN_FONDO, border_width=1, border_color=colores._CUENTA_CARD_BORDE, cursor="hand2")
        contenido = tk.Frame(tarjeta, bg=colores._CUENTA_BTN_FONDO)
        contenido.pack(fill="both", expand=True, padx=24, pady=22)
        circulo = tk.Canvas(contenido, width=48, height=48, bg=colores._CUENTA_BTN_FONDO, highlightthickness=0)
        circulo.pack(anchor="w", pady=(0, 14))
        circulo.create_oval(2, 2, 46, 46, fill=colores.MARCA_TEAL, outline="")
        circulo.create_text(24, 24, text=icono, font=("Segoe UI Symbol", 18))
        tk.Label(contenido, text=titulo, bg=colores._CUENTA_BTN_FONDO, fg=colores._TEXTO, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(contenido, text=desc, bg=colores._CUENTA_BTN_FONDO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10), wraplength=270, justify="left").pack(anchor="w", pady=(5, 0))
        widgets = [tarjeta, contenido, circulo] + contenido.winfo_children()
        for w in widgets:
            w.bind("<Button-1>", lambda e: comando())
            w.bind("<Enter>", lambda e, f=tarjeta: f.configure(border_color=colores.MARCA_TEAL, border_width=2, fg_color=colores._CUENTA_BTN_FONDO_HOVER))
            w.bind("<Leave>", lambda e, f=tarjeta: f.configure(border_color=colores._CUENTA_CARD_BORDE, border_width=1, fg_color=colores._CUENTA_BTN_FONDO))
        return tarjeta

    # ----- Datos personales -----
    def _seccion_datos(self):
        self._titulo_seccion(idiomas.t("cuenta_seccion_datos"))
        panel = ctk.CTkFrame(self.col_der, corner_radius=self.RADIO_MEDIO, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        panel.pack(fill="x")
        contenido = tk.Frame(panel, bg=colores._CHECKOUT_FONDO_OSCURO)
        contenido.pack(fill="x", padx=28, pady=24)
        nombre = self.usuario_info.get("nombre_visible") or "—"
        fecha = self.usuario_info.get("fecha_creacion")
        fecha_txt = str(fecha).split(" ")[0] if fecha else "—"
        filas = [
            (idiomas.t("cuenta_nombre_visible"), nombre),
            (idiomas.t("cuenta_correo"), self.email),
            (idiomas.t("cuenta_miembro_desde"), fecha_txt),
        ]
        for i, (etiqueta, valor) in enumerate(filas):
            fila = tk.Frame(contenido, bg=colores._CHECKOUT_FONDO_OSCURO)
            fila.pack(fill="x", pady=10, anchor="w")
            tk.Label(fila, text=etiqueta, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._DIRECCION_CONFIRM_ETIQUETA, font=("Segoe UI", 10, "bold"), width=20, anchor="w").pack(side="left")
            tk.Label(fila, text=valor, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 12), anchor="w").pack(side="left")
            if i < len(filas) - 1:
                tk.Frame(contenido, bg=colores._CHECKOUT_BORDE_SUAVE, height=1).pack(fill="x", pady=(4, 0))
        tk.Label(self.col_der, text=idiomas.t("cuenta_edicion_proximamente"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=(16, 0))

    # ----- Mis ventas -----
    def _seccion_ventas(self):
        self._titulo_seccion(idiomas.t("cuenta_seccion_ventas"))
        publicaciones = self.app.publicaciones_db.obtener_publicaciones_vendedor(self.usuario_id)
        publicaciones_reales = [p for p in publicaciones if p.get("activo", 1)]
        if not publicaciones_reales:
            self._panel_sin_ventas()
            return
        self._panel_estadisticas_ventas(publicaciones_reales)

    def _panel_sin_ventas(self):
        panel = ctk.CTkFrame(self.col_der, corner_radius=self.RADIO_MEDIO, fg_color=colores._CUENTA_BTN_FONDO, border_width=1, border_color=colores._CUENTA_CARD_BORDE)
        panel.pack(fill="both", expand=True)
        contenedor = tk.Frame(panel, bg=colores._CUENTA_BTN_FONDO)
        contenedor.pack(expand=True, pady=54)
        tk.Label(contenedor, text="💰", bg=colores._CUENTA_BTN_FONDO, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 52)).pack()
        tk.Label(contenedor, text=idiomas.t("cuenta_sin_ventas_titulo"), bg=colores._CUENTA_BTN_FONDO, fg=colores._TEXTO, font=("Segoe UI", 15, "bold")).pack(pady=(16, 4))
        tk.Label(
            contenedor,
            text=idiomas.t("cuenta_sin_ventas_desc"),
            bg=colores._CUENTA_BTN_FONDO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11), justify="center",
        ).pack(pady=(0, 20))
        ctk.CTkButton(contenedor, text=idiomas.t("cuenta_publicar_primero"), corner_radius=self.RADIO_CHICO, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 12, "bold"), height=42, command=lambda: self.app.cambiar_vista(self.app.mostrar_vender)).pack()

    def _panel_estadisticas_ventas(self, publicaciones):
        total_ventas = sum(p.get("vendidos") or 0 for p in publicaciones)
        total_visitas = sum(p.get("visitas") or 0 for p in publicaciones)
        total_ingresos = sum((p.get("vendidos") or 0) * (p.get("precio_oferta") or p.get("precio") or 0) for p in publicaciones)
        activas = [p for p in publicaciones if (p.get("estado_publicacion") or "activo") == "activo"]
        pausadas = [p for p in publicaciones if (p.get("estado_publicacion") or "activo") == "pausado"]
        nivel = self.app.publicaciones_db.nivel_vendedor(self.usuario_id)

        tarjetas = [
            ("💵", self.app.formatear_precio(total_ingresos, "ARS"), idiomas.t("cuenta_ingresos")),
            ("🛒", str(total_ventas), idiomas.t("cuenta_unidades_vendidas")),
            ("👁", str(total_visitas), idiomas.t("cuenta_visitas_totales")),
            ("📦", idiomas.t("cuenta_activas_pausadas", a=len(activas), p=len(pausadas)), idiomas.t("cuenta_publicaciones")),
        ]
        grid = tk.Frame(self.col_der, bg=colores._CARD)
        grid.pack(fill="x", pady=(0, 20))
        for i in range(2):
            grid.grid_columnconfigure(i, weight=1, uniform="ventas_stats")
        for i, (icono, valor, etiqueta) in enumerate(tarjetas):
            fila, columna = divmod(i, 2)
            box = ctk.CTkFrame(grid, corner_radius=self.RADIO_CHICO, fg_color=colores._CUENTA_BTN_FONDO, border_width=1, border_color=colores._CUENTA_CARD_BORDE)
            box.grid(row=fila, column=columna, sticky="nsew", padx=6, pady=6)
            contenido = tk.Frame(box, bg=colores._CUENTA_BTN_FONDO)
            contenido.pack(fill="x", padx=18, pady=16)
            tk.Label(contenido, text=icono, bg=colores._CUENTA_BTN_FONDO, fg=colores.MARCA_TEAL, font=("Segoe UI Symbol", 18)).pack(anchor="w")
            tk.Label(contenido, text=valor, bg=colores._CUENTA_BTN_FONDO, fg=colores._TEXTO, font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(4, 0))
            tk.Label(contenido, text=etiqueta, bg=colores._CUENTA_BTN_FONDO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 9)).pack(anchor="w")

        fila_nivel = ctk.CTkFrame(self.col_der, corner_radius=self.RADIO_CHICO, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        fila_nivel.pack(fill="x", pady=(0, 20))
        contenido_nivel = tk.Frame(fila_nivel, bg=colores._CHECKOUT_FONDO_OSCURO)
        contenido_nivel.pack(fill="x", padx=20, pady=16)
        tk.Label(contenido_nivel, text=f"🏅  {nivel['nivel']}", bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._VENDER_NIVEL_ORO, font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(contenido_nivel, text=idiomas.t("cuenta_reputacion", r=nivel['reputacion']), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        top = max(publicaciones, key=lambda p: p.get("vendidos") or 0)
        if (top.get("vendidos") or 0) > 0:
            tk.Label(self.col_der, text=idiomas.t("cuenta_producto_top"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
            self._fila_top_producto(top)

        ctk.CTkButton(self.col_der, text=idiomas.t("cuenta_ir_panel_vendedor"), corner_radius=self.RADIO_CHICO, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 12, "bold"), height=42, command=lambda: self.app.cambiar_vista(self.app.mostrar_panel_vendedor)).pack(pady=(10, 0))

    def _fila_top_producto(self, producto):
        tarjeta = ctk.CTkFrame(self.col_der, corner_radius=self.RADIO_MEDIO, fg_color=colores._CUENTA_PEDIDO_ITEM_BG, border_width=1, border_color=colores._CUENTA_PEDIDO_BORDE, cursor="hand2")
        tarjeta.pack(fill="x", pady=(0, 16))
        contenido = tk.Frame(tarjeta, bg=colores._CUENTA_PEDIDO_ITEM_BG)
        contenido.pack(fill="x", padx=18, pady=14)
        lbl_img = tk.Label(contenido, bg=colores._IMG_FONDO, width=56, height=56)
        lbl_img.pack(side="left", padx=(0, 16))
        self._cargar_imagen_item(lbl_img, producto.get("imagen"))
        info = tk.Frame(contenido, bg=colores._CUENTA_PEDIDO_ITEM_BG)
        info.pack(side="left", fill="both", expand=True)
        tk.Label(info, text=producto["nombre"], bg=colores._CUENTA_PEDIDO_ITEM_BG, fg=colores._TEXTO, font=("Segoe UI", 12, "bold"), anchor="w").pack(anchor="w")
        tk.Label(info, text=idiomas.t("cuenta_unidades_vendidas_n", n=producto.get('vendidos') or 0), bg=colores._CUENTA_PEDIDO_ITEM_BG, fg=colores.MARCA_TEAL, font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))
        widgets = [tarjeta, contenido, lbl_img, info] + info.winfo_children()
        for w in widgets:
            w.bind("<Button-1>", lambda e, pid=producto["id"]: self.app.cambiar_vista(lambda pid=pid: self.app.mostrar_producto(pid)))

    # ----- Mis compras -----
    def _seccion_compras(self):
        self._titulo_seccion(idiomas.t("cuenta_seccion_compras"))
        pedidos = self.app.productos_db.obtener_pedidos_usuario(self.usuario_id)
        if not pedidos:
            self._estado_vacio_compras()
            return
        contenedor = tk.Frame(self.col_der, bg=colores._CARD)
        contenedor.pack(fill="both", expand=True)
        for pedido in pedidos:
            self._fila_pedido(contenedor, pedido)

    def _estado_vacio_compras(self):
        contenedor = tk.Frame(self.col_der, bg=colores._CARD)
        contenedor.pack(expand=True, pady=54)
        tk.Label(contenedor, text="📦", bg=colores._CARD, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 52)).pack()
        tk.Label(contenedor, text=idiomas.t("cuenta_sin_compras_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 15, "bold")).pack(pady=(16, 4))
        tk.Label(contenedor, text=idiomas.t("cuenta_sin_compras_desc"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack()

    def _fila_pedido(self, parent, pedido):
        tarjeta = ctk.CTkFrame(parent, corner_radius=self.RADIO_MEDIO, fg_color=colores._CUENTA_PEDIDO_ITEM_BG, border_width=1, border_color=colores._CUENTA_PEDIDO_BORDE)
        tarjeta.pack(fill="x", pady=8)
        contenido = tk.Frame(tarjeta, bg=colores._CUENTA_PEDIDO_ITEM_BG)
        contenido.pack(fill="x", padx=20, pady=16)
        lbl_img = tk.Label(contenido, bg=colores._IMG_FONDO, width=64, height=64, cursor="hand2")
        lbl_img.pack(side="left", padx=(0, 18))
        self._cargar_imagen_item(lbl_img, pedido.get("imagen"))
        info = tk.Frame(contenido, bg=colores._CUENTA_PEDIDO_ITEM_BG)
        info.pack(side="left", fill="both", expand=True)
        tk.Label(info, text=pedido["nombre"], bg=colores._CUENTA_PEDIDO_ITEM_BG, fg=colores._TEXTO, font=("Segoe UI", 13, "bold"), anchor="w").pack(anchor="w")
        fecha = str(pedido["fecha_creacion"]).split(" ")[0] if pedido.get("fecha_creacion") else "—"
        tk.Label(info, text=f"{idiomas.t('cuenta_orden', n=pedido['numero_orden'])}  •  {fecha}  •  {idiomas.t('cuenta_cantidad')}: {pedido['cantidad']}", bg=colores._CUENTA_PEDIDO_ITEM_BG, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))
        entrega_tipo = pedido.get("entrega_tipo") or "retiro"
        if entrega_tipo == "envio" and pedido.get("direccion_envio"):
            texto_entrega = idiomas.t("cuenta_envio_a", d=pedido['direccion_envio'])
        else:
            texto_entrega = idiomas.t("cuenta_retiro_sede")
        tk.Label(info, text=texto_entrega, bg=colores._CUENTA_PEDIDO_ITEM_BG, fg=colores._RATING_TEXTO, font=("Segoe UI", 10), wraplength=320, justify="left").pack(anchor="w", pady=(4, 0))
        tk.Label(info, text=idiomas.t("cuenta_entregado"), bg=colores._CUENTA_PEDIDO_ITEM_BG, fg=colores._CUENTA_ESTADO_ENTREGADO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 0))
        moneda = pedido.get("moneda") or "ARS"
        subtotal = (pedido["precio_unitario"] or 0) * pedido["cantidad"]
        tk.Label(contenido, text=self.app.formatear_precio(subtotal, moneda), bg=colores._CUENTA_PEDIDO_ITEM_BG, fg=colores.MARCA_TEAL, font=("Segoe UI", 14, "bold")).pack(side="right")
        lbl_img.bind("<Button-1>", lambda e, pid=pedido["producto_id"]: self.app.cambiar_vista(lambda pid=pid: self.app.mostrar_producto(pid)))

    # ================= Imagen =================
    def _cargar_imagen_item(self, label, url):
        if not url:
            return
        def terminar(img):
            if img is None or not label.winfo_exists():
                return
            img = self._ajustar_imagen(img, 64, 64, bg=self._hex_a_rgb(colores._IMG_FONDO))
            foto = ImageTk.PhotoImage(img)
            self._imagenes[id(label)] = foto
            label.configure(image=foto, text="")
        self.app.obtener_imagen(url, callback=terminar)

    @staticmethod
    def _hex_a_rgb(hex_color):
        h = hex_color.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def _ajustar_imagen(img, w, h, bg=(255, 255, 255)):
        img = img.convert("RGBA")
        r = img.width / img.height
        if r > w / h:
            nw, nh = w, int(w / r)
        else:
            nh, nw = h, int(h * r)
        img = img.resize((nw, nh), Image.LANCZOS)
        fondo = Image.new("RGBA", (w, h), (*bg, 255))
        fondo.paste(img, ((w - nw) // 2, (h - nh) // 2), img)
        return fondo