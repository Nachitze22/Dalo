import tkinter as tk
import colores
import idiomas
import customtkinter as ctk
from PIL import Image, ImageTk

BANDERAS_EMOJI = {"AR": "🇦🇷", "US": "🇺🇸", "FR": "🇫🇷"}
URL_ICONO_CANDADO = "https://res.cloudinary.com/czevmfkz/image/upload/v1784985748/8dc58c67-8eb5-40a6-aa8c-ba816b1fb913_rvhklv.png"
URL_ICONO_FUERZA  = "https://res.cloudinary.com/czevmfkz/image/upload/v1784986250/da3df1d1-28b6-4125-8001-bbed2ff964ee_rr6jym.png"
URL_ICONO_TICK    = "https://res.cloudinary.com/czevmfkz/image/upload/v1784986119/7f2fb267-5694-4816-b455-3c08d97b0d25_t36ecr.png"
class OpinionesProducto:
    def __init__(self, parent, vista_producto):
        self.parent = parent
        self.vista = vista_producto
        self.app = vista_producto.app
        self.producto = vista_producto.producto
        self.editando_id = None
        self.calificacion_editando = 0
        self.estrellas_editando_widgets = []
        self.crear()
    def crear(self):
        sesion = self.app.auth.cargar_sesion()
        self.usuario_id_actual = self.app.auth.obtener_id_por_email(sesion) if sesion else None
        self.contenedor = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor.pack(fill="x", pady=(24, 0))
        self.col_izq = tk.Frame(self.contenedor,bg=colores._CARD,width=480,highlightbackground=colores._CARD_BORDE,highlightthickness=1)
        self.col_izq.pack(side="left", fill="y")
        self.col_izq.pack_propagate(False)
        self.col_der = tk.Frame(self.contenedor,bg=colores._CARD,highlightbackground=colores._CARD_BORDE,highlightthickness=1)
        self.col_der.pack(side="left", fill="both", expand=True, padx=(24, 0))
        self._resumen_calificacion()
        self._formulario_opinion()
        self._lista_opiniones()
    def _resumen_calificacion(self):
        datos = self.app.productos_db.obtener_resumen_calificacion(self.producto["id"])
        pad = tk.Frame(self.col_izq, bg=colores._CARD)
        pad.pack(fill="both", expand=True, padx=30, pady=24)
        tk.Label(pad,text=idiomas.t("op_titulo"),bg=colores._CARD,fg=colores._TEXTO,font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 14))
        total = datos["total"]
        promedio = datos["promedio"]
        texto_prom = idiomas.t("op_estrellas", p=f"{promedio:.1f}") if total > 0 else idiomas.t("op_sin_calificaciones")
        tk.Label(pad,text=texto_prom,bg=colores._CARD,fg=colores.MARCA_TEAL,font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 18))
        for estrella in (5, 4, 3, 2, 1):
            cantidad = datos["por_estrella"].get(estrella, 0)
            proporcion = cantidad / total if total else 0
            fila = tk.Frame(pad, bg=colores._CARD)
            fila.pack(fill="x", pady=3)
            riel = tk.Frame(fila, bg=colores._BARRA_CALIF_FONDO, height=10, width=220)
            riel.pack(side="left")
            riel.pack_propagate(False)
            ancho_lleno = int(220 * proporcion)
            if ancho_lleno > 0:
                tk.Frame(riel, bg=colores.MARCA_TEAL, height=10, width=ancho_lleno).place(x=0, y=0)
            tk.Label(fila,text=f"  {estrella}★  ({cantidad})",bg=colores._CARD,fg=colores.TEXTO_GRIS,font=("Segoe UI", 11)).pack(side="left", padx=(10, 0))
    def _lista_opiniones(self):
        self.lista_container = tk.Frame(self.col_der, bg=colores._CARD)
        self.lista_container.pack(fill="both", expand=True, padx=30, pady=24)
        self._recargar_opiniones()
    def _recargar_opiniones(self):
        self.opiniones_cache = self.app.productos_db.obtener_opiniones(self.producto["id"])
        self._renderizar_lista()

    def _renderizar_lista(self):
        for w in self.lista_container.winfo_children():
            w.destroy()
        pad = self.lista_container
        tk.Label(pad,text=idiomas.t("op_opiniones_titulo"),bg=colores._CARD,fg=colores._TEXTO,font=("Segoe UI", 16, "bold")).pack(anchor="w")
        cantidad = len(self.opiniones_cache)
        tk.Label(pad,text=idiomas.t("op_n_comentarios", n=cantidad, s="s" if cantidad != 1 else ""),bg=colores._CARD,fg=colores.TEXTO_GRIS,font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 14))
        if not self.opiniones_cache:
            tk.Label(pad,text=idiomas.t("op_sin_opiniones"),bg=colores._CARD,fg=colores.TEXTO_GRIS,font=("Segoe UI", 12)).pack(anchor="w")
            return
        for op in self.opiniones_cache:
            if self.editando_id == op["id"]:
                self._fila_edicion(pad, op)
            else:
                self._fila_normal(pad, op)
    def _fila_normal(self, pad, op):
        fila = tk.Frame(pad, bg=colores._CARD)
        fila.pack(fill="x", pady=8)
        encabezado = tk.Frame(fila, bg=colores._CARD)
        encabezado.pack(fill="x", anchor="w")
        estrellas = "⭐" * op["calificacion"]
        autor = op["nombre_visible"] or idiomas.t("op_usuario_anonimo")
        tk.Label(encabezado,text=f"{estrellas}   —   {autor}",bg=colores._CARD,fg=colores.MARCA_TEAL,font=("Segoe UI", 12, "bold")).pack(side="left", anchor="w")
        bandera = BANDERAS_EMOJI.get(op["pais"], "🌐")
        fecha = str(op["fecha_creacion"]).split(" ")[0] if op["fecha_creacion"] else ""
        tk.Label(encabezado,text=f"{bandera}  {fecha}",bg=colores._CARD,fg=colores.TEXTO_GRIS,font=("Segoe UI", 10)).pack(side="right", anchor="e")
        tk.Label(fila,text=op["comentario"] or "",bg=colores._CARD,fg=colores._TEXTO,font=("Segoe UI", 12),wraplength=460,justify="left").pack(anchor="w", pady=(4, 6))
        pie = tk.Frame(fila, bg=colores._CARD)
        pie.pack(fill="x", anchor="w")
        acciones = tk.Frame(pie, bg=colores._CARD)
        acciones.pack(side="right")
        es_propio = self.usuario_id_actual is not None and op["usuario_id"] == self.usuario_id_actual
        if es_propio:
            self._boton_editar(acciones, op)
            self._boton_borrar(acciones, op["id"])
        else:
            self._boton_util(acciones, op)
            self._boton_denunciar(acciones, op)
        self._div(pad)
    def _boton_editar(self, parent, op):
        btn = tk.Label(parent,text="✎",font=("Segoe UI Symbol", 12),bg=colores._CARD,fg=colores.TEXTO_GRIS,cursor="hand2")
        btn.pack(side="left", padx=(10, 0))
        btn.bind("<Enter>", lambda e: btn.configure(fg=colores.MARCA_TEAL))
        btn.bind("<Leave>", lambda e: btn.configure(fg=colores.TEXTO_GRIS))
        btn.bind("<Button-1>", lambda e, o=op: self._iniciar_edicion(o))
    def _boton_borrar(self, parent, opinion_id):
        btn = tk.Label(parent,text="🗑",font=("Segoe UI Symbol", 12),bg=colores._CARD,fg=colores.TEXTO_GRIS,cursor="hand2")
        btn.pack(side="left", padx=(10, 0))
        btn.bind("<Enter>", lambda e: btn.configure(fg=colores._ROJO_STOCK))
        btn.bind("<Leave>", lambda e: btn.configure(fg=colores.TEXTO_GRIS))
        btn.bind("<Button-1>", lambda e, oid=opinion_id: self._borrar_opinion(oid))
    def _borrar_opinion(self, opinion_id):
        if self.usuario_id_actual is None:
            return
        if self.app.productos_db.eliminar_opinion(opinion_id, self.usuario_id_actual):
            self.app.mensaje_temporal(idiomas.t("op_comentario_eliminado"))
            self.app.mostrar_producto(self.producto["id"])
        else:
            self.app.mensaje_temporal(idiomas.t("op_no_se_pudo_eliminar"))
    def _boton_util(self, parent, op):
        ya_marcado = (self.usuario_id_actual is not None and self.app.productos_db.usuario_marco_util(op["id"], self.usuario_id_actual))
        color = colores.MARCA_TEAL if ya_marcado else colores.TEXTO_GRIS
        btn = tk.Label(parent,text=idiomas.t("op_util", n=op['utiles']),font=("Segoe UI", 11, "bold"),bg=colores._CARD,fg=color,cursor="hand2")
        btn.pack(side="left", padx=(14, 0))
        btn.bind("<Enter>", lambda e: btn.configure(fg=colores.MARCA_TEAL_HOVER))
        btn.bind("<Leave>", lambda e, c=color: btn.configure(fg=c))
        btn.bind("<Button-1>", lambda e, o=op: self._toggle_util(o))
    def _toggle_util(self, op):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("op_necesita_login_util"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        self.app.productos_db.marcar_util(op["id"], self.usuario_id_actual)
        self._recargar_opiniones()
    def _boton_denunciar(self, parent, op):
        btn = tk.Label(parent,text="🚩",font=("Segoe UI Symbol", 12),bg=colores._CARD,fg=colores.TEXTO_GRIS,cursor="hand2")
        btn.pack(side="left", padx=(10, 0))
        btn.bind("<Enter>", lambda e: btn.configure(fg=colores._ROJO_STOCK))
        btn.bind("<Leave>", lambda e: btn.configure(fg=colores.TEXTO_GRIS))
        btn.bind("<Button-1>", lambda e, o=op, b=btn: self._denunciar_opinion(o, b))
    def _denunciar_opinion(self, op, btn):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("op_necesita_login_denunciar"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        if not btn.winfo_exists():
            return
        btn.unbind("<Button-1>")
        btn.configure(text="⏳", cursor="arrow")
        self.app.mensaje_temporal(idiomas.t("op_analizando"))
        def resultado_ia(es_ofensivo):
            if not btn.winfo_exists():
                return
            if es_ofensivo:
                self.app.productos_db.eliminar_opinion_moderacion(op["id"])
                self.app.mensaje_temporal(idiomas.t("op_eliminado_moderacion"))
                self.app.mostrar_producto(self.producto["id"])
            else:
                self.app.mensaje_temporal(idiomas.t("op_sin_ofensivo"))
                btn.configure(text="🚩", cursor="hand2")
                btn.bind("<Button-1>", lambda e, o=op, b=btn: self._denunciar_opinion(o, b))
        self.app.ia.comentario_ofensivo_ia(op["comentario"] or "", resultado_ia)
    def _iniciar_edicion(self, op):
        self.editando_id = op["id"]
        self.calificacion_editando = op["calificacion"]
        self._renderizar_lista()
    def _cancelar_edicion(self):
        self.editando_id = None
        self._renderizar_lista()
    def _fila_edicion(self, pad, op):
        fila = tk.Frame(pad, bg=colores._CARD)
        fila.pack(fill="x", pady=8)
        tk.Label(fila,text=idiomas.t("op_editando"),bg=colores._CARD,fg=colores._TEXTO,font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        self.estrellas_editando_widgets = []
        fila_estrellas = tk.Frame(fila, bg=colores._CARD)
        fila_estrellas.pack(anchor="w", pady=(0, 8))
        for i in range(1, 6):
            lbl = tk.Label(fila_estrellas,text="★" if i <= self.calificacion_editando else "☆",font=("Segoe UI Symbol", 20),bg=colores._CARD,fg=colores.MARCA_TEAL if i <= self.calificacion_editando else colores.TEXTO_GRIS,cursor="hand2")
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda e, n=i: self._seleccionar_estrella_edicion(n))
            lbl.bind("<Enter>", lambda e, n=i: self._hover_estrellas_edicion(n))
            lbl.bind("<Leave>", lambda e: self._hover_estrellas_edicion(self.calificacion_editando))
            self.estrellas_editando_widgets.append(lbl)
        entry_comentario = ctk.CTkTextbox(fila,width=400,height=80,corner_radius=10,fg_color=colores.FONDO_PRINCIPAL,text_color=colores._TEXTO,font=("Segoe UI", 12))
        entry_comentario.insert("1.0", op["comentario"] or "")
        entry_comentario.pack(anchor="w", pady=(0, 8))
        botones = tk.Frame(fila, bg=colores._CARD)
        botones.pack(anchor="w")
        btn_guardar = tk.Label(botones,text=idiomas.t("op_guardar_cambios"),bg=colores.MARCA_TEAL,fg=colores._TEXTO,font=("Segoe UI", 12, "bold"),padx=18,pady=9,cursor="hand2")
        btn_guardar.pack(side="left", padx=(0, 10))
        btn_cancelar = tk.Label(botones,text=idiomas.t("op_cancelar"),bg=colores.BTN_OSCURO,fg=colores._TEXTO,font=("Segoe UI", 12, "bold"),padx=18,pady=9,cursor="hand2")
        btn_cancelar.pack(side="left")
        btn_guardar.bind("<Enter>", lambda e: btn_guardar.configure(bg=colores.MARCA_TEAL_HOVER))
        btn_guardar.bind("<Leave>", lambda e: btn_guardar.configure(bg=colores.MARCA_TEAL))
        btn_guardar.bind("<ButtonPress-1>", lambda e: btn_guardar.configure(bg=colores.MARCA_TEAL_PRESS))
        btn_guardar.bind("<ButtonRelease-1>", lambda e: self._guardar_edicion(op, entry_comentario, btn_guardar))
        btn_cancelar.bind("<Enter>", lambda e: btn_cancelar.configure(bg=colores.BTN_OSCURO_HOVER))
        btn_cancelar.bind("<Leave>", lambda e: btn_cancelar.configure(bg=colores.BTN_OSCURO))
        btn_cancelar.bind("<ButtonRelease-1>", lambda e: self._cancelar_edicion())
        self._div(pad)
    def _hover_estrellas_edicion(self, n):
        for i, w in enumerate(self.estrellas_editando_widgets, start=1):
            w.configure(text="★" if i <= n else "☆",fg=colores.MARCA_TEAL if i <= n else colores.TEXTO_GRIS)
    def _seleccionar_estrella_edicion(self, n):
        self.calificacion_editando = n
        self._hover_estrellas_edicion(n)
    def _guardar_edicion(self, op, entry_comentario, btn_guardar):
        if self.calificacion_editando == 0:
            self.app.mensaje_temporal(idiomas.t("op_elegi_calificacion"))
            return
        comentario = entry_comentario.get("1.0", "end").strip()
        if not comentario:
            self.app.mensaje_temporal(idiomas.t("op_escribi_comentario"))
            return
        if self.app.ia.nombre_ofensivo(comentario):
            entry_comentario.delete("1.0", "end")
            self.app.mensaje_temporal(idiomas.t("op_eliminado_ofensivo"))
            return
        btn_guardar.unbind("<ButtonRelease-1>")
        btn_guardar.configure(text=idiomas.t("op_analizando"), cursor="arrow", bg=colores.BTN_OSCURO)
        calificacion = self.calificacion_editando
        def resultado_ia(es_ofensivo):
            if not btn_guardar.winfo_exists():
                return
            if es_ofensivo:
                entry_comentario.delete("1.0", "end")
                self.app.mensaje_temporal(idiomas.t("op_eliminado_ofensivo"))
                btn_guardar.configure(text=idiomas.t("op_guardar_cambios"), cursor="hand2", bg=colores.MARCA_TEAL_HOVER)
                btn_guardar.bind("<ButtonRelease-1>", lambda e: self._guardar_edicion(op, entry_comentario, btn_guardar))
                return
            self.app.productos_db.editar_opinion(op["id"], self.usuario_id_actual, calificacion, comentario)
            self.editando_id = None
            self.app.mensaje_temporal(idiomas.t("op_actualizada"))
            self.app.mostrar_producto(self.producto["id"])
        self.app.ia.comentario_ofensivo_ia(comentario, resultado_ia)
    def _div(self, parent):
        tk.Frame(parent, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=8)
    def _formulario_opinion(self):
        self.calificacion_nueva = 0
        self.estrellas_widgets = []
        pad = tk.Frame(self.col_der, bg=colores._CARD)
        pad.pack(fill="x", padx=30, pady=(24, 4))
        fila_titulo = tk.Frame(pad, bg=colores._CARD)
        fila_titulo.pack(anchor="w", pady=(0, 12))
        self.app._icono_imagen(fila_titulo, URL_ICONO_FUERZA, 18, 18, bg=colores._CARD).pack(side="left", padx=(0, 6))
        tk.Label(fila_titulo,text=idiomas.t("op_dejar_opinion"),bg=colores._CARD,fg=colores._TEXTO,font=("Segoe UI", 14, "bold")).pack(side="left")
        ya_opino = self.usuario_id_actual is not None and self.app.productos_db.usuario_ya_opino(self.producto["id"], self.usuario_id_actual)
        compro = self.usuario_id_actual is not None and self.app.productos_db.usuario_compro_producto(self.producto["id"], self.usuario_id_actual)
        if ya_opino:
            self._panel_ya_opino(pad)
            self._div(pad)
            return
        if not compro:
            self._panel_formulario_bloqueado(pad)
            self._div(pad)
            return
        fila_estrellas = tk.Frame(pad, bg=colores._CARD)
        fila_estrellas.pack(anchor="w", pady=(0, 10))
        for i in range(1, 6):
            lbl = tk.Label(fila_estrellas,text="☆",font=("Segoe UI Symbol", 20),bg=colores._CARD,fg=colores.TEXTO_GRIS,cursor="hand2")
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda e, n=i: self._seleccionar_estrella(n))
            lbl.bind("<Enter>", lambda e, n=i: self._hover_estrellas(n))
            lbl.bind("<Leave>", lambda e: self._hover_estrellas(self.calificacion_nueva))
            self.estrellas_widgets.append(lbl)
        self.entry_comentario = ctk.CTkTextbox(pad,width=400,height=80,corner_radius=10,fg_color=colores.FONDO_PRINCIPAL,text_color=colores._TEXTO,font=("Segoe UI", 12))
        self.entry_comentario.pack(anchor="w", pady=(0, 10))
        self.btn_publicar = tk.Label(pad,text=idiomas.t("op_publicar"),bg=colores.MARCA_TEAL,fg=colores._TEXTO,font=("Segoe UI", 12, "bold"),padx=20,pady=10,cursor="hand2")
        self.btn_publicar.pack(anchor="w")
        self.btn_publicar.bind("<Enter>", lambda e: self.btn_publicar.configure(bg=colores.MARCA_TEAL_HOVER))
        self.btn_publicar.bind("<Leave>", lambda e: self.btn_publicar.configure(bg=colores.MARCA_TEAL))
        self.btn_publicar.bind("<ButtonPress-1>", lambda e: self.btn_publicar.configure(bg=colores.MARCA_TEAL_PRESS))
        self.btn_publicar.bind("<ButtonRelease-1>", lambda e: (self.btn_publicar.configure(bg=colores.MARCA_TEAL_HOVER), self._publicar_opinion()))
        self._div(pad)

    def _panel_formulario_bloqueado(self, parent):
        box = ctk.CTkFrame(parent,fg_color=colores._CHECKOUT_FONDO_OSCURO,border_width=1,border_color=colores._CHECKOUT_BORDE_SUAVE,corner_radius=14)
        box.pack(fill="x", pady=(0, 4))
        contenido = tk.Frame(box, bg=colores._CHECKOUT_FONDO_OSCURO)
        contenido.pack(fill="x", padx=30, pady=26)
        self.app._icono_imagen(contenido, URL_ICONO_CANDADO, 34, 34, bg=colores._CHECKOUT_FONDO_OSCURO).pack(anchor="center", pady=(0, 10))
        tk.Label(contenido,text=idiomas.t("op_bloqueado_titulo"),bg=colores._CHECKOUT_FONDO_OSCURO,fg=colores._TEXTO,font=("Segoe UI", 13, "bold")).pack(anchor="center", pady=(0, 8))
        tk.Label(contenido,text=idiomas.t("op_bloqueado_desc"),bg=colores._CHECKOUT_FONDO_OSCURO,fg=colores.TEXTO_GRIS,font=("Segoe UI", 11),justify="center").pack(anchor="center")
        fila = tk.Frame(contenido, bg=colores._CHECKOUT_FONDO_OSCURO)
        fila.pack(anchor="center", pady=(2, 0))
        tk.Label(fila,text=idiomas.t("op_bloqueado_usando"),bg=colores._CHECKOUT_FONDO_OSCURO,fg=colores.TEXTO_GRIS,font=("Segoe UI", 11)).pack(side="left")
        tk.Label(fila,text=idiomas.t("op_bloqueado_comprar"),bg=colores._CHECKOUT_FONDO_OSCURO,fg=colores.MARCA_TEAL,font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(fila,text=idiomas.t("op_bloqueado_para"),bg=colores._CHECKOUT_FONDO_OSCURO,fg=colores.TEXTO_GRIS,font=("Segoe UI", 11)).pack(side="left")

    def _panel_ya_opino(self, parent):
        box = ctk.CTkFrame(parent,fg_color=colores._CHECKOUT_FONDO_OSCURO,border_width=1,border_color=colores.MARCA_TEAL,corner_radius=14)
        box.pack(fill="x", pady=(0, 4))
        contenido = tk.Frame(box, bg=colores._CHECKOUT_FONDO_OSCURO)
        contenido.pack(fill="x", padx=30, pady=22)
        self.app._icono_imagen(contenido, URL_ICONO_TICK, 30, 30, bg=colores._CHECKOUT_FONDO_OSCURO).pack(anchor="center", pady=(0, 8))
        tk.Label(contenido,text=idiomas.t("op_ya_opinaste_titulo"),bg=colores._CHECKOUT_FONDO_OSCURO,fg=colores.MARCA_TEAL,font=("Segoe UI", 13, "bold")).pack(anchor="center")
        tk.Label(contenido,text=idiomas.t("op_ya_opinaste_desc"),bg=colores._CHECKOUT_FONDO_OSCURO,fg=colores.TEXTO_GRIS,font=("Segoe UI", 11)).pack(anchor="center", pady=(4, 0))
    def _hover_estrellas(self, n):
        for i, w in enumerate(self.estrellas_widgets, start=1):
            w.configure(text="★" if i <= n else "☆",fg=colores.MARCA_TEAL if i <= n else colores.TEXTO_GRIS)
    def _seleccionar_estrella(self, n):
        self.calificacion_nueva = n
        self._hover_estrellas(n)
    def _publicar_opinion(self):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("op_necesita_login_opinar"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        usuario_id = self.app.auth.obtener_id_por_email(sesion)
        if self.app.productos_db.usuario_ya_opino(self.producto["id"], usuario_id):
            self.app.mensaje_temporal(idiomas.t("op_ya_opinaste_msg"))
            return
        if self.calificacion_nueva == 0:
            self.app.mensaje_temporal(idiomas.t("op_elegi_calificacion"))
            return
        comentario = self.entry_comentario.get("1.0", "end").strip()
        if not comentario:
            self.app.mensaje_temporal(idiomas.t("op_escribi_comentario"))
            return
        if self.app.ia.nombre_ofensivo(comentario):
            self.entry_comentario.delete("1.0", "end")
            self.app.mensaje_temporal(idiomas.t("op_eliminado_ofensivo"))
            return
        pais = getattr(self.app.header, "region_actual", "AR")
        self._deshabilitar_boton()
        def resultado_ia(es_ofensivo):
            if not self.btn_publicar.winfo_exists():
                return
            if es_ofensivo:
                self.entry_comentario.delete("1.0", "end")
                self.app.mensaje_temporal(idiomas.t("op_eliminado_ofensivo"))
                self._rehabilitar_boton()
                return
            if self.app.productos_db.usuario_ya_opino(self.producto["id"], usuario_id):
                self.app.mensaje_temporal(idiomas.t("op_ya_opinaste_msg"))
                self._rehabilitar_boton()
                return
            self.app.productos_db.agregar_opinion(self.producto["id"], usuario_id, self.calificacion_nueva, comentario, pais)
            self.app.mensaje_temporal(idiomas.t("op_gracias"))
            self.app.mostrar_producto(self.producto["id"])
        self.app.ia.comentario_ofensivo_ia(comentario, resultado_ia)
    def _deshabilitar_boton(self):
        self.btn_publicar.unbind("<ButtonRelease-1>")
        self.btn_publicar.configure(text=idiomas.t("op_analizando"), cursor="arrow", bg=colores.BTN_OSCURO)
    def _rehabilitar_boton(self):
        self.btn_publicar.configure(text=idiomas.t("op_publicar"), cursor="hand2", bg=colores.MARCA_TEAL_HOVER)
        self.btn_publicar.bind("<ButtonRelease-1>", lambda e: (self.btn_publicar.configure(bg=colores.MARCA_TEAL_HOVER), self._publicar_opinion()))