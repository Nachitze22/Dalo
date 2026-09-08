import tkinter as tk
import customtkinter as ctk
import colores
import idiomas


class PasoIA:
    def __init__(self, parent, wizard):
        self.parent = parent
        self.wizard = wizard
        self.app = wizard.app
        self._crear_ui()
        self.parent.after(200, self._analizar)

    def validar(self):
        return []

    def guardar(self):
        pass

    def _crear_ui(self):
        contenedor = tk.Frame(self.parent, bg=colores._CARD)
        contenedor.pack(expand=True, pady=60)
        tk.Label(contenedor, text="🤖", bg=colores._CARD, fg=colores._VENDER_IA_ANALIZANDO, font=("Segoe UI Symbol", 46)).pack()
        tk.Label(contenedor, text=idiomas.t("paso_ia_titulo"), bg=colores._CARD, fg=colores._TEXTO,
                  font=("Segoe UI", 16, "bold")).pack(pady=(14, 6))
        tk.Label(contenedor, text=idiomas.t("paso_ia_desc"),
                  bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(pady=(0, 20))
        self.barra = ctk.CTkProgressBar(contenedor, width=320, mode="indeterminate",
                                          progress_color=colores._VENDER_IA_ANALIZANDO, fg_color=colores._CARGA_BARRA_FONDO)
        self.barra.pack()
        self.barra.start()

    def _analizar(self):
        datos_para_moderar = dict(self.wizard.datos)
        datos_para_moderar["imagenes"] = list(range(len(self.wizard.imagenes)))

        def callback(es_valida, errores):
            self.barra.stop()
            if es_valida:
                self.app.mensaje_temporal(idiomas.t("paso_ia_todo_ok"))
                self.wizard.avanzar_automatico()
            else:
                for w in self.parent.winfo_children():
                    w.destroy()
                self._mostrar_errores(errores)
        self.app.ia.moderar_publicacion(datos_para_moderar, callback)

    def _mostrar_errores(self, errores):
        contenedor = tk.Frame(self.parent, bg=colores._CARD)
        contenedor.pack(expand=True, pady=40)
        tk.Label(contenedor, text="⚠️", bg=colores._CARD, fg=colores._ROJO_STOCK, font=("Segoe UI Symbol", 40)).pack()
        tk.Label(contenedor, text=idiomas.t("paso_ia_problemas"), bg=colores._CARD, fg=colores._TEXTO,
                  font=("Segoe UI", 15, "bold")).pack(pady=(12, 10))
        for err in errores:
            tk.Label(contenedor, text=f"•  {err}", bg=colores._CARD, fg=colores._ROJO_STOCK, font=("Segoe UI", 11)).pack(anchor="w")
        ctk.CTkButton(contenedor, text=idiomas.t("paso_ia_volver_revisar"), height=38, corner_radius=10, fg_color=colores.MARCA_TEAL,
                      hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 11, "bold"),
                      command=lambda: self.wizard.ir_a_paso(1)).pack(pady=(16, 0))