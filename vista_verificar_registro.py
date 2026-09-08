import tkinter as tk
import customtkinter as ctk
import time
import auth
import colores
import idiomas


class VistaVerificarRegistro(tk.Frame):
    DURACION_REENVIO = 60

    def __init__(self, parent, app, email):
        super().__init__(parent, bg=colores.FONDO_PRINCIPAL)
        self.app = app
        self.email = email
        self.pack(fill="both", expand=True)
        self._resend_disponible_en = time.time() + self.DURACION_REENVIO
        self.crear_widgets()
        self._actualizar_reenvio()

    def crear_widgets(self):
        contenedor_padre = tk.Frame(self, bg=colores.FONDO_PRINCIPAL)
        contenedor_padre.pack(fill="both", expand=True)
        self.app.ventana_principal.update_idletasks()
        alto = self.app.ventana_principal.winfo_height()
        contenedor_padre.config(height=alto)

        self.contenedor = ctk.CTkFrame(
            contenedor_padre, width=420, height=460, corner_radius=20,
            fg_color=colores.FONDO_TARJETA_LOGIN, border_width=2, border_color=colores.MARCA_TEAL,
        )
        self.contenedor.place(relx=0.5, rely=0.40, anchor="center")
        self.contenedor.pack_propagate(False)

        ctk.CTkLabel(self.contenedor, text="✉", font=("Segoe UI Symbol", 34), text_color=colores.MARCA_TEAL).pack(pady=(28, 6))
        ctk.CTkLabel(self.contenedor, text=idiomas.t("verificar_titulo"), font=("Segoe UI", 24, "bold"), text_color="white").pack()
        ctk.CTkLabel(
            self.contenedor, text=idiomas.t("verificar_subtitulo", email=self.email),
            font=("Segoe UI", 12), text_color=colores.TEXTO_GRIS, justify="center",
        ).pack(pady=(6, 20))

        self.entry_codigo = ctk.CTkEntry(
            self.contenedor, placeholder_text=idiomas.t("verificar_placeholder"), width=280, height=42,
            corner_radius=10, justify="center", font=("Segoe UI", 16, "bold"),
        )
        self.entry_codigo.pack(pady=6)
        self.entry_codigo.bind("<Return>", lambda e: self._verificar())
        self.entry_codigo.bind("<Key>", self._limpiar_estado)

        self.label_estado = ctk.CTkLabel(self.contenedor, text="", font=("Segoe UI", 11), text_color=colores._ROJO_STOCK, wraplength=350)
        self.label_estado.pack(pady=(4, 6))

        self.btn_verificar = ctk.CTkButton(
            self.contenedor, text=idiomas.t("verificar_btn"), width=280, height=42, corner_radius=10,
            fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 13, "bold"),
            command=self._verificar,
        )
        self.btn_verificar.pack(pady=(6, 10))

        self.btn_reenviar = tk.Label(
            self.contenedor, text=idiomas.t("verificar_reenviar"), bg=colores.FONDO_TARJETA_LOGIN,
            fg=colores._DIRECCION_FORM_BTN_UBICACION_TEXTO, font=("Segoe UI", 11, "bold"), cursor="hand2",
        )
        self.btn_reenviar.pack()
        self.btn_reenviar.bind("<Button-1>", lambda e: self._reenviar())

        ctk.CTkButton(
            self.contenedor, text=idiomas.t("verificar_cancelar"), width=280, height=36, corner_radius=10, fg_color="transparent",
            hover_color=colores.BTN_OSCURO_HOVER, border_width=1, border_color=colores.TEXTO_GRIS,
            font=("Segoe UI", 11), command=self._cancelar,
        ).pack(pady=(14, 0))

    def _limpiar_estado(self, event=None):
        self.label_estado.configure(text="")

    def _verificar(self):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            self.label_estado.configure(text=idiomas.t("verificar_ingresa_codigo"), text_color=colores._ROJO_STOCK)
            return
        ok, mensaje = auth.verificar_codigo_registro(self.email, codigo)
        if not ok:
            self.label_estado.configure(text=mensaje, text_color=colores._ROJO_STOCK)
            return
        if not auth.completar_registro(self.email):
            self.label_estado.configure(text=idiomas.t("verificar_email_registrado"), text_color=colores._ROJO_STOCK)
            return
        auth.guardar_sesion(self.email)
        self.app.usuario = self.email
        self.app.cargar_direcciones()
        nombre = auth.obtener_nombre_visible(self.email)
        self.app.mensaje_temporal(idiomas.t("verificar_cuenta_creada", nombre=nombre))
        self.app.historial.clear()
        self.app.cambiar_vista(self.app.mostrar_inicio)

    def _reenviar(self):
        if time.time() < self._resend_disponible_en:
            return
        if auth.reenviar_codigo_registro(self.email):
            self._resend_disponible_en = time.time() + self.DURACION_REENVIO
            self.label_estado.configure(text=idiomas.t("verificar_reenviado"), text_color=colores._VERDE_STOCK)
        else:
            self.label_estado.configure(text=idiomas.t("verificar_error_reenvio"), text_color=colores._ROJO_STOCK)

    def _actualizar_reenvio(self):
        if not self.btn_reenviar.winfo_exists():
            return
        restante = int(self._resend_disponible_en - time.time())
        if restante > 0:
            self.btn_reenviar.configure(text=idiomas.t("verificar_reenviar_espera", s=restante), cursor="arrow", fg=colores.TEXTO_GRIS)
        else:
            self.btn_reenviar.configure(text=idiomas.t("verificar_reenviar"), cursor="hand2", fg=colores._DIRECCION_FORM_BTN_UBICACION_TEXTO)
        self.app.ventana_principal.after(1000, self._actualizar_reenvio)

    def _cancelar(self):
        self.app.cambiar_vista(self.app.vista_login)