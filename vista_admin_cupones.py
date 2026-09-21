import tkinter as tk
import customtkinter as ctk
import colores
import idiomas


class VistaAdminCupones:
    RADIO_GRANDE = 20
    RADIO_CHICO = 14

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.contenedor_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor_principal.pack(fill="both", expand=True, padx=50, pady=36)

        if not self.app.es_admin():
            self._mostrar_sin_permiso()
            return

        self.card = ctk.CTkFrame(self.contenedor_principal, corner_radius=self.RADIO_GRANDE, fg_color=colores._CARD, border_width=1, border_color=colores._CARD_BORDE)
        self.card.pack(fill="both", expand=True)
        self.pad = tk.Frame(self.card, bg=colores._CARD)
        self.pad.pack(fill="both", expand=True, padx=40, pady=36)
        self.construir()

    def _mostrar_sin_permiso(self):
        contenedor = tk.Frame(self.contenedor_principal, bg=colores.FONDO_PRINCIPAL)
        contenedor.pack(expand=True, pady=90)
        tk.Label(contenedor, text="🚫", bg=colores.FONDO_PRINCIPAL, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 46)).pack()
        tk.Label(contenedor, text=idiomas.t("admin_sin_permiso"), bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 15, "bold")).pack(pady=(14, 0))

    def construir(self):
        for w in self.pad.winfo_children():
            w.destroy()
        tk.Label(self.pad, text=idiomas.t("admin_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(self.pad, text=idiomas.t("admin_subtitulo"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 20))

        cuerpo = tk.Frame(self.pad, bg=colores._CARD)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(0, weight=38)
        cuerpo.grid_columnconfigure(1, weight=0)
        cuerpo.grid_columnconfigure(2, weight=62)
        cuerpo.grid_rowconfigure(0, weight=1)

        col_form = tk.Frame(cuerpo, bg=colores._CARD)
        col_form.grid(row=0, column=0, sticky="nsew", padx=(0, 30))
        tk.Frame(cuerpo, bg=colores._SEPARADOR, width=1).grid(row=0, column=1, sticky="ns", pady=4)
        self.col_lista = tk.Frame(cuerpo, bg=colores._CARD)
        self.col_lista.grid(row=0, column=2, sticky="nsew", padx=(30, 0))

        self._crear_formulario(col_form)
        self._renderizar_lista()

    def _crear_formulario(self, parent):
        tk.Label(parent, text=idiomas.t("admin_nuevo_cupon"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 14))

        tk.Label(parent, text=idiomas.t("admin_codigo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_codigo = ctk.CTkEntry(parent, placeholder_text=idiomas.t("admin_placeholder_codigo"), width=280, height=38, corner_radius=8, fg_color=colores._CUPON_INPUT_BG, border_color=colores._CUPON_INPUT_BORDE, text_color=colores._TEXTO)
        self.entry_codigo.pack(anchor="w", pady=(0, 14))

        tk.Label(parent, text=idiomas.t("admin_tipo_descuento"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.segmento_tipo = ctk.CTkSegmentedButton(parent, values=["porcentaje", "monto_fijo"], fg_color=colores.FONDO_PRINCIPAL, selected_color=colores.MARCA_TEAL, selected_hover_color=colores.MARCA_TEAL_HOVER)
        self.segmento_tipo.set("porcentaje")
        self.segmento_tipo.pack(anchor="w", pady=(0, 14))

        tk.Label(parent, text=idiomas.t("admin_valor"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_valor = ctk.CTkEntry(parent, placeholder_text=idiomas.t("admin_placeholder_valor"), width=280, height=38, corner_radius=8, fg_color=colores._CUPON_INPUT_BG, border_color=colores._CUPON_INPUT_BORDE, text_color=colores._TEXTO)
        self.entry_valor.pack(anchor="w", pady=(0, 14))

        tk.Label(parent, text=idiomas.t("admin_compra_minima"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_minimo = ctk.CTkEntry(parent, placeholder_text=idiomas.t("admin_placeholder_minima"), width=280, height=38, corner_radius=8, fg_color=colores._CUPON_INPUT_BG, border_color=colores._CUPON_INPUT_BORDE, text_color=colores._TEXTO)
        self.entry_minimo.pack(anchor="w", pady=(0, 14))

        tk.Label(parent, text=idiomas.t("admin_usos_maximos"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_usos = ctk.CTkEntry(parent, placeholder_text=idiomas.t("admin_placeholder_usos"), width=280, height=38, corner_radius=8, fg_color=colores._CUPON_INPUT_BG, border_color=colores._CUPON_INPUT_BORDE, text_color=colores._TEXTO)
        self.entry_usos.pack(anchor="w", pady=(0, 14))

        tk.Label(parent, text=idiomas.t("admin_vencimiento"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_vencimiento = ctk.CTkEntry(parent, placeholder_text=idiomas.t("admin_placeholder_vencimiento"), width=280, height=38, corner_radius=8, fg_color=colores._CUPON_INPUT_BG, border_color=colores._CUPON_INPUT_BORDE, text_color=colores._TEXTO)
        self.entry_vencimiento.pack(anchor="w", pady=(0, 18))

        self.lbl_estado_form = tk.Label(parent, text="", bg=colores._CARD, font=("Segoe UI", 10, "bold"))
        self.lbl_estado_form.pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(parent, text=idiomas.t("admin_crear_cupon"), height=42, corner_radius=10, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 12, "bold"), command=self._crear_cupon).pack(anchor="w")

    def _crear_cupon(self):
        codigo = self.entry_codigo.get().strip()
        tipo = self.segmento_tipo.get()
        try:
            valor = float(self.entry_valor.get().replace(",", "."))
        except ValueError:
            self.lbl_estado_form.configure(text=idiomas.t("admin_valor_invalido"), fg=colores._CUPON_ERROR_TEXTO)
            return
        try:
            monto_minimo = float(self.entry_minimo.get().replace(",", ".")) if self.entry_minimo.get().strip() else 0
        except ValueError:
            monto_minimo = 0
        try:
            usos_maximos = int(self.entry_usos.get().strip()) if self.entry_usos.get().strip() else None
        except ValueError:
            usos_maximos = None
        fecha_fin = self.entry_vencimiento.get().strip() or None

        ok, mensaje = self.app.cupones_db.crear_cupon(codigo, tipo, valor, monto_minimo, usos_maximos, fecha_fin)
        self.lbl_estado_form.configure(text=mensaje, fg=colores._CUPON_APLICADO_TEXTO if ok else colores._CUPON_ERROR_TEXTO)
        if ok:
            for entry in (self.entry_codigo, self.entry_valor, self.entry_minimo, self.entry_usos, self.entry_vencimiento):
                entry.delete(0, "end")
            self._renderizar_lista()

    def _renderizar_lista(self):
        for w in self.col_lista.winfo_children():
            w.destroy()
        tk.Label(self.col_lista, text=idiomas.t("admin_cupones_existentes"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 14))
        cupones = self.app.cupones_db.obtener_todos_cupones()
        if not cupones:
            tk.Label(self.col_lista, text=idiomas.t("admin_sin_cupones"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(anchor="w")
            return
        for cupon in cupones:
            self._fila_cupon(cupon)

    def _fila_cupon(self, cupon):
        tarjeta = ctk.CTkFrame(self.col_lista, corner_radius=self.RADIO_CHICO, fg_color=colores._ADMIN_CARD_BG, border_width=1, border_color=colores._ADMIN_CARD_BORDE)
        tarjeta.pack(fill="x", pady=6)
        contenido = tk.Frame(tarjeta, bg=colores._ADMIN_CARD_BG)
        contenido.pack(fill="x", padx=18, pady=14)

        fila_sup = tk.Frame(contenido, bg=colores._ADMIN_CARD_BG)
        fila_sup.pack(fill="x", anchor="w")
        tk.Label(fila_sup, text=cupon["codigo"], bg=colores._ADMIN_CARD_BG, fg=colores._TEXTO, font=("Segoe UI", 13, "bold")).pack(side="left")
        activo = bool(cupon.get("activo"))
        bg_badge = colores._ADMIN_BADGE_ACTIVO_BG if activo else colores._ADMIN_BADGE_INACTIVO_BG
        fg_badge = colores._ADMIN_BADGE_ACTIVO_TXT if activo else colores._ADMIN_BADGE_INACTIVO_TXT
        etiqueta_activo = idiomas.t("admin_activo") if activo else idiomas.t("admin_inactivo")
        tk.Label(fila_sup, text=f"  {etiqueta_activo}  ", bg=bg_badge, fg=fg_badge, font=("Segoe UI", 9, "bold")).pack(side="left", padx=(10, 0))

        if cupon["tipo"] == "porcentaje":
            desc_valor = idiomas.t("admin_pct_descuento", v=int(cupon['valor']))
        else:
            desc_valor = idiomas.t("admin_monto_descuento", v=f"{cupon['valor']:,.0f}".replace(",", "."))
        tk.Label(contenido, text=desc_valor, bg=colores._ADMIN_CARD_BG, fg=colores.MARCA_TEAL, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(6, 0))

        detalles = []
        if cupon.get("monto_minimo"):
            detalles.append(idiomas.t("admin_compra_minima_txt", v=f"{cupon['monto_minimo']:,.0f}".replace(",", ".")))
        if cupon.get("usos_maximos") is not None:
            detalles.append(idiomas.t("admin_usos_txt", a=cupon.get('usos_actuales', 0), m=cupon['usos_maximos']))
        else:
            detalles.append(idiomas.t("admin_usos_ilimitado", a=cupon.get('usos_actuales', 0)))
        if cupon.get("fecha_fin"):
            detalles.append(idiomas.t("admin_vence_txt", f=cupon['fecha_fin']))
        tk.Label(contenido, text="  •  ".join(detalles), bg=colores._ADMIN_CARD_BG, fg=colores.TEXTO_GRIS, font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 10))

        btn_toggle = tk.Label(contenido, text=(idiomas.t("admin_desactivar") if activo else idiomas.t("admin_activar")), bg=colores._ADMIN_CARD_BG, fg=(colores._CARRITO_ELIMINAR if activo else colores.MARCA_TEAL), font=("Segoe UI", 10, "bold"), cursor="hand2")
        btn_toggle.pack(anchor="w")
        btn_toggle.bind("<Button-1>", lambda e, cid=cupon["id"], est=activo: self._toggle_cupon(cid, est))

    def _toggle_cupon(self, cupon_id, estaba_activo):
        self.app.cupones_db.cambiar_estado_cupon(cupon_id, not estaba_activo)
        self._renderizar_lista()