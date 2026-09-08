import tkinter as tk
import customtkinter as ctk
import colores
import idiomas

class PantallaCarga(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=colores._CARGA_FONDO)
        self.app = app
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._dots_job = None
        self._dots_estado = 0
        self.crear_widgets()
        self.animar_puntos()

    def crear_widgets(self):
        contenedor = tk.Frame(self, bg=colores._CARGA_FONDO)
        contenedor.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(contenedor,text=idiomas.t("carga_titulo"),bg=colores._CARGA_FONDO,fg=colores.MARCA_TEAL,font=("Segoe UI", 42, "bold")).pack(pady=(0, 6))
        tk.Label(contenedor,text=idiomas.t("carga_subtitulo"),bg=colores._CARGA_FONDO,fg=colores._CARGA_TEXTO_SUB,font=("Segoe UI", 13)).pack(pady=(0, 30))
        self.barra = ctk.CTkProgressBar(contenedor,width=320,height=10,corner_radius=10,progress_color=colores.MARCA_TEAL,fg_color=colores._CARGA_BARRA_FONDO)
        self.barra.set(0)
        self.barra.pack(pady=(0, 12))
        self.lbl_estado = tk.Label(contenedor,text="",bg=colores._CARGA_FONDO,fg=colores.TEXTO_GRIS,font=("Segoe UI", 11))
        self.lbl_estado.pack()

    def animar_puntos(self):
        if not self.winfo_exists():
            return
        puntos = "." * (self._dots_estado % 4)
        self.lbl_estado.configure(text=idiomas.t("carga_estado", puntos=puntos))
        self._dots_estado += 1
        self._dots_job = self.after(400, self.animar_puntos)

    def actualizar_progreso(self, actual, total):
        if not self.winfo_exists():
            return
        fraccion = 1 if total <= 0 else min(actual / total, 1)
        self.barra.set(fraccion)

    def finalizar(self):
        if self._dots_job:
            self.after_cancel(self._dots_job)
            self._dots_job = None
        self.destroy()