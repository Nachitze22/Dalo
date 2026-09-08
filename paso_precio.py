import tkinter as tk
import customtkinter as ctk
import colores
import idiomas
from componentes.vender.utils_vender import validar_precio


class PasoPrecio:
    def __init__(self, parent, wizard):
        self.parent = parent
        self.wizard = wizard
        self.app = wizard.app
        self._crear_ui()

    def validar(self):
        self._recolectar_base()
        return validar_precio(self.wizard.datos)

    def guardar(self):
        self._recolectar_base()

    def _crear_ui(self):
        tk.Label(self.parent, text=idiomas.t("paso_precio_titulo"), bg=colores._CARD, fg=colores._TEXTO,
                  font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(self.parent, text=idiomas.t("paso_precio_desc"),
                  bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 16))

        cuerpo = tk.Frame(self.parent, bg=colores._CARD)
        cuerpo.pack(fill="both", expand=True)
        col_izq = tk.Frame(cuerpo, bg=colores._CARD)
        col_izq.pack(side="left", fill="both", expand=True, padx=(0, 30))

        self.frame_resumen = ctk.CTkFrame(cuerpo, corner_radius=16, fg_color=colores._CHECKOUT_FONDO_OSCURO,
                                           border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE, width=280)

        d = self.wizard.datos

        tk.Label(col_izq, text=idiomas.t("paso_precio_original"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_precio = ctk.CTkEntry(col_izq, width=280, height=38, corner_radius=8, fg_color=colores.FONDO_PRINCIPAL, text_color=colores._TEXTO)
        self.entry_precio.pack(anchor="w")
        self.entry_precio.insert(0, str(d.get("precio", "")) if d.get("precio") else "")
        self.entry_precio.bind("<KeyRelease>", lambda e: self._actualizar_resumen())

        self.var_oferta = tk.BooleanVar(value=d.get("tiene_oferta", False))
        switch_oferta = ctk.CTkSwitch(col_izq, text=idiomas.t("paso_precio_tiene_oferta"), variable=self.var_oferta,
                                       fg_color="White", progress_color=colores.MARCA_TEAL, command=self._toggle_oferta)
        switch_oferta.pack(anchor="w", pady=(16, 6))
        self.entry_oferta = ctk.CTkEntry(col_izq, width=280, height=38, corner_radius=8, fg_color=colores.FONDO_PRINCIPAL,
                                          text_color=colores._TEXTO, placeholder_text=idiomas.t("paso_precio_placeholder_oferta"))
        self.entry_oferta.pack(anchor="w")
        self.entry_oferta.insert(0, str(d.get("precio_oferta", "")) if d.get("precio_oferta") else "")
        self.entry_oferta.bind("<KeyRelease>", lambda e: self._actualizar_resumen())

        self.var_cuotas = tk.BooleanVar(value=bool(d.get("cuotas_cantidad")))
        switch_cuotas = ctk.CTkSwitch(col_izq, text=idiomas.t("paso_precio_ofrecer_cuotas"), variable=self.var_cuotas,
                                       fg_color=colores._VENDER_STEP_INACTIVO, progress_color=colores.MARCA_TEAL,
                                       command=self._toggle_cuotas)
        switch_cuotas.pack(anchor="w", pady=(20, 6))
        self.combo_cuotas = ctk.CTkOptionMenu(col_izq, values=["3", "6", "12"], width=140, fg_color=colores.FONDO_PRINCIPAL,
                                               button_color=colores.MARCA_TEAL, button_hover_color=colores.MARCA_TEAL_HOVER,
                                               command=lambda v: self._actualizar_resumen())
        self.combo_cuotas.set(str(d.get("cuotas_cantidad") or 3))
        self.combo_cuotas.pack(anchor="w")
        self.var_interes = tk.BooleanVar(value=bool(d.get("cuotas_interes", 0)))
        self._toggle_oferta()
        self._toggle_cuotas()

        self.frame_resumen.pack(side="left", fill="y")
        self._actualizar_resumen()

    def _toggle_oferta(self):
        self.entry_oferta.configure(state="normal" if self.var_oferta.get() else "disabled")
        self._actualizar_resumen()

    def _toggle_cuotas(self):
        estado = "normal" if self.var_cuotas.get() else "disabled"
        self.combo_cuotas.configure(state=estado)
        self._actualizar_resumen()

    def _actualizar_resumen(self):
        for w in self.frame_resumen.winfo_children():
            w.destroy()
        pad = tk.Frame(self.frame_resumen, bg=colores._CHECKOUT_FONDO_OSCURO)
        pad.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(pad, text=idiomas.t("paso_precio_resumen_titulo"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO,
                  font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 12))
        try:
            precio = float(self.entry_precio.get().replace(",", "."))
        except ValueError:
            precio = 0
        precio_final = precio
        if self.var_oferta.get():
            try:
                oferta = float(self.entry_oferta.get().replace(",", "."))
                if 0 < oferta < precio:
                    precio_final = oferta
                    pct = round((1 - oferta / precio) * 100) if precio else 0
                    tk.Label(pad, text=idiomas.t("paso_precio_original_txt", p=f"{precio:,.0f}".replace(",", ".")), bg=colores._CHECKOUT_FONDO_OSCURO,
                              fg=colores._OFERTA_PRECIO_TACHADO, font=("Segoe UI", 11, "overstrike")).pack(anchor="w")
                    tk.Label(pad, text=f"-{pct}% OFF", bg=colores._OFERTA_BADGE_BG, fg=colores.TEXTO_BLANCO,
                              font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(4, 0))
            except ValueError:
                pass
        tk.Label(pad, text=f"${precio_final:,.0f}".replace(",", "."), bg=colores._CHECKOUT_FONDO_OSCURO,
                  fg=colores.MARCA_TEAL, font=("Segoe UI", 26, "bold")).pack(anchor="w", pady=(8, 0))
        if self.var_cuotas.get():
            cant = int(self.combo_cuotas.get())
            interes_txt = idiomas.t("paso_precio_con_interes") if self.var_interes.get() else idiomas.t("paso_precio_sin_interes")
            valor_cuota = precio_final / cant
            tk.Label(pad, text=idiomas.t("paso_precio_cuotas_txt", c=cant, i=interes_txt, v=f"{valor_cuota:,.0f}".replace(",", ".")),
                      bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 0))

    def _recolectar_base(self):
        try:
            precio = float(self.entry_precio.get().replace(",", "."))
        except ValueError:
            precio = 0
        precio_oferta = None
        if self.var_oferta.get():
            try:
                precio_oferta = float(self.entry_oferta.get().replace(",", "."))
            except ValueError:
                precio_oferta = None
        self.wizard.datos.update({
            "precio": precio,
            "tiene_oferta": self.var_oferta.get(),
            "precio_oferta": precio_oferta,
            "cuotas_cantidad": int(self.combo_cuotas.get()) if self.var_cuotas.get() else None,
            "cuotas_interes": 1 if self.var_interes.get() else 0,
            "moneda": "ARS",
        })