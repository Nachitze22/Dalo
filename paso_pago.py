import tkinter as tk
import customtkinter as ctk
import colores
import idiomas
from componentes.vender.utils_vender import MEDIOS_PAGO_DISPONIBLES


class PasoPago:
    def __init__(self, parent, wizard):
        self.parent = parent
        self.wizard = wizard
        self.app = wizard.app
        self.switches = {}
        self._crear_ui()

    def validar(self):
        self._recolectar()
        if not self.wizard.datos.get("medios_pago"):
            return [idiomas.t("paso_pago_elegi_uno")]
        return []

    def guardar(self):
        pass

    def _crear_ui(self):
        tk.Label(self.parent, text=idiomas.t("paso_pago_titulo"), bg=colores._CARD, fg=colores._TEXTO,
                  font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(self.parent, text=idiomas.t("paso_pago_desc"), bg=colores._CARD,
                  fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 16))

        seleccionados = set(self.wizard.datos.get("medios_pago", []))
        grid = tk.Frame(self.parent, bg=colores._CARD)
        grid.pack(fill="x")
        for i, (clave, icono, titulo) in enumerate(MEDIOS_PAGO_DISPONIBLES):
            tarjeta = ctk.CTkFrame(grid, corner_radius=14, fg_color=colores._VENDER_THUMB_BG,
                                    border_width=2, border_color=colores.MARCA_TEAL if clave in seleccionados else colores._VENDER_THUMB_BORDE)
            tarjeta.grid(row=i // 2, column=i % 2, sticky="ew", padx=8, pady=8)
            grid.grid_columnconfigure(i % 2, weight=1)
            interior = tk.Frame(tarjeta, bg=colores._VENDER_THUMB_BG)
            interior.pack(fill="x", padx=16, pady=14)
            tk.Label(interior, text=icono, bg=colores._VENDER_THUMB_BG, font=("Segoe UI Symbol", 16), fg="White").pack(side="left", padx=(0, 10))
            var = tk.BooleanVar(value=clave in seleccionados)
            switch = ctk.CTkSwitch(interior, text=titulo, variable=var, fg_color=colores._VENDER_STEP_INACTIVO,
                                    progress_color=colores.MARCA_TEAL,
                                    command=lambda c=clave, t=tarjeta: self._toggle_visual(c, t))
            switch.pack(side="left")
            self.switches[clave] = (var, tarjeta)

    def _toggle_visual(self, clave, tarjeta):
        var, _ = self.switches[clave]
        tarjeta.configure(border_color=colores.MARCA_TEAL if var.get() else colores._VENDER_THUMB_BORDE)

    def _recolectar(self):
        self.wizard.datos["medios_pago"] = [clave for clave, (var, _) in self.switches.items() if var.get()]