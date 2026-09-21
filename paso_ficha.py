import tkinter as tk
import customtkinter as ctk
import colores
import idiomas
from componentes.vender.utils_vender import FICHA_TECNICA_CATEGORIAS


class PasoFicha:
    def __init__(self, parent, wizard):
        self.parent = parent
        self.wizard = wizard
        self.app = wizard.app
        self.filas_personalizadas = []
        self._crear_ui()

    def validar(self):
        self._recolectar()
        if not self.wizard.datos.get("ficha_tecnica"):
            return [idiomas.t("paso_ficha_falta_atributo")]
        return []

    def guardar(self):
        pass

    def _crear_ui(self):
        tk.Label(self.parent, text=idiomas.t("paso_ficha_titulo"), bg=colores._CARD, fg=colores._TEXTO,
                  font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 4))
        categoria = self.wizard.datos.get("categoria", "general")
        atributos = FICHA_TECNICA_CATEGORIAS.get(categoria, list(FICHA_TECNICA_CATEGORIAS.values())[-1])
        tk.Label(self.parent, text=idiomas.t("paso_ficha_desc", c=categoria),
                  bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 16))

        scroll = ctk.CTkScrollableFrame(self.parent, fg_color=colores._CARD, height=320)
        scroll.pack(fill="both", expand=True)

        self.entradas_sugeridas = {}
        ficha_existente = self.wizard.datos.get("ficha_tecnica", {})
        for atributo in atributos:
            fila = tk.Frame(scroll, bg=colores._CARD)
            fila.pack(fill="x", pady=6)
            tk.Label(fila, text=atributo, bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold"), width=22, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(fila, width=320, height=34, corner_radius=8, fg_color=colores.FONDO_PRINCIPAL, text_color=colores._TEXTO)
            entry.pack(side="left")
            entry.insert(0, ficha_existente.get(atributo, ""))
            self.entradas_sugeridas[atributo] = entry

        self.frame_personalizados = tk.Frame(scroll, bg=colores._CARD)
        self.frame_personalizados.pack(fill="x", pady=(10, 0))
        for clave, valor in ficha_existente.items():
            if clave not in atributos:
                self._agregar_fila_personalizada(clave, valor)

        ctk.CTkButton(self.parent, text=idiomas.t("paso_ficha_agregar_atributo"), height=34, corner_radius=8,
                      fg_color="transparent", hover_color=colores._VENDER_THUMB_BG, border_width=1,
                      border_color=colores.MARCA_TEAL, text_color=colores.MARCA_TEAL,
                      font=("Segoe UI", 11, "bold"), command=lambda: self._agregar_fila_personalizada("", "")).pack(anchor="w", pady=(12, 0))

    def _agregar_fila_personalizada(self, clave, valor):
        fila = tk.Frame(self.frame_personalizados, bg=colores._CARD)
        fila.pack(fill="x", pady=4)
        entry_clave = ctk.CTkEntry(fila, placeholder_text=idiomas.t("paso_ficha_placeholder_nombre"), width=200, height=34, corner_radius=8,
                                    fg_color=colores.FONDO_PRINCIPAL, text_color=colores._TEXTO)
        entry_clave.pack(side="left", padx=(0, 8))
        entry_clave.insert(0, clave)
        entry_valor = ctk.CTkEntry(fila, placeholder_text=idiomas.t("paso_ficha_placeholder_valor"), width=200, height=34, corner_radius=8,
                                    fg_color=colores.FONDO_PRINCIPAL, text_color=colores._TEXTO)
        entry_valor.pack(side="left", padx=(0, 8))
        entry_valor.insert(0, valor)
        btn_quitar = tk.Label(fila, text="🗑", bg=colores._CARD, fg=colores._CARRITO_ELIMINAR, cursor="hand2", font=("Segoe UI Symbol", 12))
        btn_quitar.pack(side="left")
        btn_quitar.bind("<Button-1>", lambda e, f=fila: (f.destroy(), self.filas_personalizadas.remove((entry_clave, entry_valor))))
        self.filas_personalizadas.append((entry_clave, entry_valor))

    def _recolectar(self):
        ficha = {}
        for atributo, entry in self.entradas_sugeridas.items():
            valor = entry.get().strip()
            if valor:
                ficha[atributo] = valor
        for entry_clave, entry_valor in self.filas_personalizadas:
            clave = entry_clave.get().strip()
            valor = entry_valor.get().strip()
            if clave and valor:
                ficha[clave] = valor
        self.wizard.datos["ficha_tecnica"] = ficha