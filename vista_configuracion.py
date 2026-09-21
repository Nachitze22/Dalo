import tkinter as tk
import customtkinter as ctk
import colores
import idiomas
import variables_globales


class VistaConfiguracion:
    RADIO_GRANDE = 22
    RADIO_MEDIO = 18
    RADIO_CHICO = 14

    def __init__(self, parent, app, seccion="general"):
        self.parent = parent
        self.app = app
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
            ("general", "🏠", "config_sec_general"),
            ("idioma", "🌐", "config_sec_idioma"),
            ("notificaciones", "🔔", "config_sec_notificaciones"),
            ("privacidad", "🔒", "config_sec_privacidad"),
            ("apariencia", "🎨", "config_sec_apariencia"),
            ("datos", "📄", "config_sec_datos"),
            ("acerca", "💡", "config_sec_acerca"),
        ]
        claves_validas = {s[0] for s in self.SECCIONES}
        self.seccion_actual = seccion if seccion in claves_validas else "general"

        if not hasattr(self.app, "preferencias_notificaciones"):
            self.app.preferencias_notificaciones = {
                "ofertas": True, "pedidos": True, "newsletter": False, "preguntas": True,
            }

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
        tk.Label(contenedor, text="⚙️", bg=colores._CARD, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 52)).pack()
        tk.Label(contenedor, text=idiomas.t("config_requiere_login_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 17, "bold")).pack(pady=(16, 6))
        tk.Label(contenedor, text=idiomas.t("config_requiere_login_desc"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(pady=(0, 22))
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

    def _crear_header(self):
        tk.Label(self.pad, text=idiomas.t("config_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(self.pad, text=idiomas.t("config_subtitulo"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(anchor="w", pady=(4, 0))
        tk.Frame(self.pad, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(20, 24))

    # ================= Sidebar =================
    def _crear_sidebar(self):
        for clave, icono, etiqueta_key in self.SECCIONES:
            self._fila_menu(self.col_izq, icono, idiomas.t(etiqueta_key), activo=(clave == self.seccion_actual), comando=lambda c=clave: self._cambiar_seccion(c))
        tk.Frame(self.col_izq, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=18)
        self._fila_menu(self.col_izq, "🚪", idiomas.t("config_cerrar_sesion"), activo=False, comando=self._cerrar_sesion, color_texto=colores._CARRITO_ELIMINAR)

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
            fila.configure(fg_color=bg_hover); interior.configure(bg=bg_hover); circulo.configure(bg=bg_hover); lbl.configure(bg=bg_hover)

        def salir(e=None):
            if activo:
                return
            fila.configure(fg_color=bg); interior.configure(bg=bg); circulo.configure(bg=bg); lbl.configure(bg=bg)

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
    def _titulo_seccion(self, texto):
        tk.Label(self.col_der, text=texto, bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 19, "bold")).pack(anchor="w", pady=(0, 22))

    def _panel(self, titulo=None, desc=None):
        panel = ctk.CTkFrame(self.col_der, corner_radius=self.RADIO_MEDIO, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        panel.pack(fill="x", pady=(0, 16))
        contenido = tk.Frame(panel, bg=colores._CHECKOUT_FONDO_OSCURO)
        contenido.pack(fill="x", padx=26, pady=22)
        if titulo:
            tk.Label(contenido, text=titulo, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO, font=("Segoe UI", 13, "bold"), wraplength=560, justify="left").pack(anchor="w")
        if desc:
            tk.Label(contenido, text=desc, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10), wraplength=560, justify="left").pack(anchor="w", pady=(6, 0))
        return contenido

    def _crear_contenido(self):
        if self.seccion_actual == "idioma":
            self._seccion_idioma()
        elif self.seccion_actual == "notificaciones":
            self._seccion_notificaciones()
        elif self.seccion_actual == "privacidad":
            self._seccion_privacidad()
        elif self.seccion_actual == "apariencia":
            self._seccion_apariencia()
        elif self.seccion_actual == "datos":
            self._seccion_datos()
        elif self.seccion_actual == "acerca":
            self._seccion_acerca()
        else:
            self._seccion_general()

    # ----- General -----
    def _seccion_general(self):
        self._titulo_seccion(idiomas.t("config_sec_general"))
        contenido = self._panel(idiomas.t("config_general_titulo"))
        nombre = self.usuario_info.get("nombre_visible") or self.email.split("@")[0].capitalize()
        fecha = self.usuario_info.get("fecha_creacion")
        fecha_txt = str(fecha).split(" ")[0] if fecha else "—"
        filas = [
            (idiomas.t("config_general_nombre"), nombre),
            (idiomas.t("config_general_email"), self.email),
            (idiomas.t("config_general_miembro"), fecha_txt),
        ]
        for etiqueta, valor in filas:
            fila = tk.Frame(contenido, bg=colores._CHECKOUT_FONDO_OSCURO)
            fila.pack(fill="x", pady=8, anchor="w")
            tk.Label(fila, text=etiqueta, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._DIRECCION_CONFIRM_ETIQUETA, font=("Segoe UI", 10, "bold"), width=20, anchor="w").pack(side="left")
            tk.Label(fila, text=valor, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 12), anchor="w").pack(side="left")
        botones = tk.Frame(self.col_der, bg=colores._CARD)
        botones.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(botones, text=idiomas.t("config_general_ir_cuenta"), corner_radius=10, height=40, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 11, "bold"), command=lambda: self.app.cambiar_vista(self.app.mostrar_cuenta)).pack(side="left", padx=(0, 10))
        ctk.CTkButton(botones, text=idiomas.t("config_general_ir_direcciones"), corner_radius=10, height=40, fg_color=colores.BTN_OSCURO, hover_color=colores.BTN_OSCURO_HOVER, font=("Segoe UI", 11, "bold"), command=lambda: self.app.cambiar_vista(self.app.mostrar_seleccionar_direccion)).pack(side="left")

    # ----- Idioma -----
    def _seccion_idioma(self):
        self._titulo_seccion(idiomas.t("config_sec_idioma"))
        self._panel(idiomas.t("config_idioma_titulo"), idiomas.t("config_idioma_desc"))
        actual = getattr(variables_globales, "IDIOMA_ACTUAL", "es")
        grid = tk.Frame(self.col_der, bg=colores._CARD)
        grid.pack(fill="x")
        for i in range(3):
            grid.grid_columnconfigure(i, weight=1, uniform="idiomas")
        for i, (codigo, bandera, nombre) in enumerate(idiomas.IDIOMAS_DISPONIBLES):
            self._tarjeta_idioma(grid, codigo, bandera, nombre, seleccionado=(codigo == actual)).grid(row=0, column=i, sticky="nsew", padx=6)

    def _tarjeta_idioma(self, parent, codigo, bandera, nombre, seleccionado):
        bg = colores._CHECKOUT_CARD_SELECCIONADA if seleccionado else colores._CUENTA_BTN_FONDO
        borde = colores.MARCA_TEAL if seleccionado else colores._CUENTA_CARD_BORDE
        tarjeta = ctk.CTkFrame(parent, corner_radius=self.RADIO_MEDIO, fg_color=bg, border_width=2, border_color=borde, cursor="hand2")
        contenido = tk.Frame(tarjeta, bg=bg)
        contenido.pack(fill="both", expand=True, padx=18, pady=20)
        tk.Label(contenido, text=bandera, bg=bg, font=("Segoe UI Symbol", 30)).pack()
        tk.Label(contenido, text=nombre, bg=bg, fg=colores.MARCA_TEAL if seleccionado else colores._TEXTO, font=("Segoe UI", 12, "bold")).pack(pady=(8, 0))
        if seleccionado:
            tk.Label(contenido, text=f"✓ {idiomas.t('config_idioma_actual')}", bg=bg, fg=colores.MARCA_TEAL, font=("Segoe UI", 9)).pack(pady=(4, 0))
        widgets = [tarjeta, contenido] + contenido.winfo_children()
        for w in widgets:
            w.bind("<Button-1>", lambda e, c=codigo: self._elegir_idioma(c))
        return tarjeta

    def _elegir_idioma(self, codigo):
        if codigo == getattr(variables_globales, "IDIOMA_ACTUAL", "es"):
            return
        self.app.cambiar_idioma(codigo)
        self.app.mensaje_temporal(idiomas.t("config_idioma_cambiado"))

    # ----- Notificaciones -----
    def _seccion_notificaciones(self):
        self._titulo_seccion(idiomas.t("config_sec_notificaciones"))
        contenido = self._panel(idiomas.t("config_notif_titulo"), idiomas.t("config_notif_desc"))
        prefs = self.app.preferencias_notificaciones
        opciones = [
            ("ofertas", idiomas.t("config_notif_ofertas")),
            ("pedidos", idiomas.t("config_notif_pedidos")),
            ("newsletter", idiomas.t("config_notif_newsletter")),
            ("preguntas", idiomas.t("config_notif_preguntas")),
        ]
        for clave, etiqueta in opciones:
            var = tk.BooleanVar(value=prefs.get(clave, True))
            ctk.CTkSwitch(contenido, text=etiqueta, variable=var, fg_color=colores._VENDER_STEP_INACTIVO, progress_color=colores.MARCA_TEAL, font=("Segoe UI", 11), command=lambda c=clave, v=var: self._guardar_notificacion(c, v)).pack(anchor="w", pady=8)

    def _guardar_notificacion(self, clave, var):
        self.app.preferencias_notificaciones[clave] = var.get()
        self.app.mensaje_temporal(idiomas.t("config_notif_guardado"))

    # ----- Privacidad y seguridad -----
    def _seccion_privacidad(self):
        self._titulo_seccion(idiomas.t("config_sec_privacidad"))

        c1 = self._panel(idiomas.t("config_priv_password_titulo"), idiomas.t("config_priv_password_desc"))
        ctk.CTkButton(c1, text=idiomas.t("config_priv_password_btn"), corner_radius=10, height=38, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 11, "bold"), command=self._ir_a_cambiar_password).pack(anchor="w", pady=(12, 0))

        c2 = self._panel(idiomas.t("config_priv_sesiones_titulo"))
        fila = tk.Frame(c2, bg=colores._CHECKOUT_FONDO_OSCURO)
        fila.pack(fill="x", pady=(6, 0), anchor="w")
        tk.Label(fila, text="💻", bg=colores._CHECKOUT_FONDO_OSCURO, font=("Segoe UI Symbol", 14)).pack(side="left", padx=(0, 8))
        tk.Label(fila, text=idiomas.t("config_priv_sesiones_desc"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 11)).pack(side="left")
        tk.Label(fila, text=f"  •  {self.email}", bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(side="left")

        c3 = self._panel(idiomas.t("config_priv_datos_titulo"), idiomas.t("config_priv_datos_desc"))
        ctk.CTkButton(c3, text=idiomas.t("config_priv_datos_btn"), corner_radius=10, height=38, fg_color=colores.BTN_OSCURO, hover_color=colores.BTN_OSCURO_HOVER, font=("Segoe UI", 11, "bold"), command=self._solicitar_datos).pack(anchor="w", pady=(12, 0))

        c4 = self._panel(idiomas.t("config_priv_eliminar_titulo"), idiomas.t("config_priv_eliminar_desc"))
        self.var_confirmar_eliminar = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(c4, text=idiomas.t("config_priv_eliminar_check"), variable=self.var_confirmar_eliminar, fg_color=colores._CARRITO_ELIMINAR, hover_color=colores._CARRITO_ELIMINAR_HOVER, text_color=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w", pady=(14, 8))
        ctk.CTkButton(c4, text=idiomas.t("config_priv_eliminar_btn"), corner_radius=10, height=38, fg_color=colores._CARRITO_ELIMINAR, hover_color=colores._CARRITO_ELIMINAR_HOVER, font=("Segoe UI", 11, "bold"), command=self._eliminar_cuenta).pack(anchor="w")

    def _ir_a_cambiar_password(self):
        self.app.cambiar_vista(lambda: self.app.vista_recuperar_password(self.email))

    def _solicitar_datos(self):
        self.app.mensaje_temporal(idiomas.t("config_priv_datos_simulado"))

    def _eliminar_cuenta(self):
        if not self.var_confirmar_eliminar.get():
            self.app.mensaje_temporal(idiomas.t("config_priv_eliminar_check"))
            return
        ok = self.app.auth.eliminar_cuenta(self.usuario_id, self.email)
        if not ok:
            self.app.mensaje_temporal(idiomas.t("config_priv_eliminar_error"))
            return
        self.app.usuario = "Invitado"
        self.app.lista_de_deseos_lista.clear()
        self.app.carrito_de_compra_pedidos.clear()
        self.app.cargar_direcciones()
        if hasattr(self.app, "header"):
            self.app.header.actualizar_badge_deseos()
            self.app.header.actualizar_badge_carrito()
        self.app.historial.clear()
        self.app.cambiar_vista(self.app.mostrar_inicio)
        self.app.mensaje_temporal(idiomas.t("config_priv_eliminar_hecho"))

    # ----- Apariencia -----
    def _seccion_apariencia(self):
        self._titulo_seccion(idiomas.t("config_sec_apariencia"))
        contenido = self._panel(idiomas.t("config_apariencia_titulo"), idiomas.t("config_apariencia_desc"))
        var = tk.BooleanVar(value=True)
        ctk.CTkSwitch(contenido, text=idiomas.t("config_apariencia_toggle"), variable=var, state="disabled", fg_color=colores._VENDER_STEP_INACTIVO, progress_color=colores.MARCA_TEAL, font=("Segoe UI", 11)).pack(anchor="w", pady=(12, 0))

    # ----- Datos y privacidad -----
    def _seccion_datos(self):
        self._titulo_seccion(idiomas.t("config_sec_datos"))
        contenido = self._panel(idiomas.t("config_datos_titulo"), idiomas.t("config_datos_desc"))
        fila = tk.Frame(contenido, bg=colores._CHECKOUT_FONDO_OSCURO)
        fila.pack(fill="x", pady=(14, 0), anchor="w")
        for texto in (idiomas.t("config_datos_politica"), idiomas.t("config_datos_terminos")):
            lbl = tk.Label(fila, text=f"📄  {texto}", bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.MARCA_TEAL, font=("Segoe UI", 11, "bold"), cursor="hand2")
            lbl.pack(anchor="w", pady=4)
            lbl.bind("<Button-1>", lambda e: self.app.mensaje_temporal(idiomas.t("config_datos_pendiente")))
            lbl.bind("<Enter>", lambda e, l=lbl: l.configure(fg=colores.MARCA_TEAL_HOVER))
            lbl.bind("<Leave>", lambda e, l=lbl: l.configure(fg=colores.MARCA_TEAL))

    # ----- Acerca de -----
    def _seccion_acerca(self):
        self._titulo_seccion(idiomas.t("config_sec_acerca"))
        contenido = self._panel(f"Dalo — {idiomas.t('config_acerca_version')} 1.0.0", idiomas.t("config_acerca_desc"))
        ctk.CTkButton(contenido, text=idiomas.t("config_acerca_ayuda"), corner_radius=10, height=38, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 11, "bold"), command=lambda: self.app.cambiar_vista(self.app.mostrar_ayuda)).pack(anchor="w", pady=(12, 0))