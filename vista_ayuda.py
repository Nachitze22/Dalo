import tkinter as tk
import customtkinter as ctk
import colores
import idiomas


def _construir_faq():
    return [(idiomas.t(f"faq_{i}_q"), idiomas.t(f"faq_{i}_a")) for i in range(1, 9)]


class VistaAyuda:
    RADIO_GRANDE = 20
    RADIO_MEDIO = 14

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self._abierta = None
        self._filas = {}
        self.contenedor_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor_principal.pack(fill="both", expand=True, padx=50, pady=36)
        self.card = ctk.CTkFrame(self.contenedor_principal, corner_radius=self.RADIO_GRANDE, fg_color=colores._CARD, border_width=1, border_color=colores._CARD_BORDE)
        self.card.pack(fill="both", expand=True)
        self.pad = tk.Frame(self.card, bg=colores._CARD)
        self.pad.pack(fill="both", expand=True, padx=44, pady=40)
        self.construir()

    def construir(self):
        for w in self.pad.winfo_children():
            w.destroy()
        self._abierta = None
        self._filas = {}
        self._crear_header()
        self._crear_preguntas()
        self._crear_contacto()

    def _crear_header(self):
        tk.Label(self.pad, text=idiomas.t("ayuda_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(self.pad, text=idiomas.t("ayuda_subtitulo"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(anchor="w", pady=(4, 0))
        tk.Frame(self.pad, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(20, 24))

    def _crear_preguntas(self):
        self.frame_preguntas = tk.Frame(self.pad, bg=colores._CARD)
        self.frame_preguntas.pack(fill="both", expand=True)
        for i, (pregunta, respuesta) in enumerate(_construir_faq()):
            self._fila_pregunta(i, pregunta, respuesta)

    def _fila_pregunta(self, indice, pregunta, respuesta):
        tarjeta = ctk.CTkFrame(self.frame_preguntas, corner_radius=self.RADIO_MEDIO, fg_color=colores._CUENTA_BTN_FONDO, border_width=1, border_color=colores._CUENTA_CARD_BORDE, cursor="hand2")
        tarjeta.pack(fill="x", pady=6)
        interior = tk.Frame(tarjeta, bg=colores._CUENTA_BTN_FONDO)
        interior.pack(fill="x", padx=18, pady=14)
        fila_sup = tk.Frame(interior, bg=colores._CUENTA_BTN_FONDO)
        fila_sup.pack(fill="x")
        lbl_pregunta = tk.Label(fila_sup, text=pregunta, bg=colores._CUENTA_BTN_FONDO, fg=colores._TEXTO, font=("Segoe UI", 12, "bold"), anchor="w", justify="left", wraplength=760)
        lbl_pregunta.pack(side="left", fill="x", expand=True)
        lbl_flecha = tk.Label(fila_sup, text="▾", bg=colores._CUENTA_BTN_FONDO, fg=colores.MARCA_TEAL, font=("Segoe UI", 12, "bold"))
        lbl_flecha.pack(side="right")
        lbl_respuesta = tk.Label(interior, text=respuesta, bg=colores._CUENTA_BTN_FONDO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11), justify="left", wraplength=760)

        self._filas[indice] = {"tarjeta": tarjeta, "interior": interior, "lbl_respuesta": lbl_respuesta, "lbl_flecha": lbl_flecha}

        widgets = [tarjeta, interior, fila_sup, lbl_pregunta, lbl_flecha]
        for w in widgets:
            w.bind("<Button-1>", lambda e, i=indice: self._toggle(i))

    def _toggle(self, indice):
        fila = self._filas[indice]
        if self._abierta == indice:
            fila["lbl_respuesta"].pack_forget()
            fila["lbl_flecha"].configure(text="▾")
            self._abierta = None
            return
        if self._abierta is not None:
            anterior = self._filas[self._abierta]
            anterior["lbl_respuesta"].pack_forget()
            anterior["lbl_flecha"].configure(text="▾")
        fila["lbl_respuesta"].pack(anchor="w", pady=(10, 0))
        fila["lbl_flecha"].configure(text="▴")
        self._abierta = indice

    def _crear_contacto(self):
        tk.Frame(self.pad, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(24, 20))
        panel = ctk.CTkFrame(self.pad, corner_radius=self.RADIO_MEDIO, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        panel.pack(fill="x")
        contenido = tk.Frame(panel, bg=colores._CHECKOUT_FONDO_OSCURO)
        contenido.pack(fill="x", padx=22, pady=18)
        tk.Label(contenido, text=idiomas.t("ayuda_no_encontraste"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO, font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ctk.CTkTextbox(contenido, width=400, height=80, corner_radius=10, bg_color=colores._CHECKOUT_FONDO_OSCURO, fg_color=colores._CHECKOUT_FONDO_OSCURO, text_color=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(anchor="w", pady=(2, 0))
        ctk.CTkButton(contenido, text=idiomas.t("ayuda_enviar"), corner_radius=10, height=38, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 11, "bold"), command=self._enviar_simulado).pack(anchor="w", pady=(14, 0))

    def _enviar_simulado(self):
        self.app.mensaje_temporal(idiomas.t("ayuda_enviado"))