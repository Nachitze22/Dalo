import tkinter as tk
from componentes.grid_productos import GridProductos
import colores
import idiomas

class VistaInicio:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.variables()
        self.widgets()

    def variables(self):
        productos = self.app.productos_db.obtener_todos()
        self.app.e_productos = [p["id"] for p in productos]
        self.productos_home_originales = list(self.app.e_productos)
        self.letra_seleccionada = None
        self.botones_letra = {}
        self.ancho_ventana = self.app.ventana_principal.winfo_width()
        self.texto_legal_str = idiomas.t("inicio_texto_legal")

    def widgets(self):
        self.frame_grid = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.frame_grid.pack(fill="both", expand=True)
        self._renderizar_grid(self.app.e_productos)
        self.texto_legal()
        self.buscar_por_inicial()
        for letra in self.alfabeto:
            self.crear_boton_letra(letra)

    def _renderizar_grid(self, ids_productos):
        for w in self.frame_grid.winfo_children():
            w.destroy()
        if not ids_productos:
            self.app.mensaje_temporal(idiomas.t("inicio_sin_productos"))
            return
        GridProductos(self.frame_grid, self.app, ids_productos)
        self.app.ventana_principal.update_idletasks()
        self.app.canvas.yview_moveto(0)

    def texto_legal(self):
        label_legal = tk.Label(self.parent,text=self.texto_legal_str,bg=colores.FONDO_PRINCIPAL,fg=colores.TEXTO_GRIS,font=("Arial", 8),wraplength=1000,justify="center")
        label_legal.pack(pady=(20,40))

    def buscar_por_inicial(self):
        self.buscar_por_inicial = tk.Frame(self.parent, bg = colores.BARRA_LETRAS, width = self.ancho_ventana, height = 100)
        self.buscar_por_inicial.pack(side = "bottom", fill = "x")
        self.buscar_por_inicial.pack_propagate(False)
        self.texto_buscar_inicial = tk.Label(self.buscar_por_inicial, text = idiomas.t("inicio_buscar_letra"), bg = colores.BARRA_LETRAS, fg = colores.TEXTO_NEGRO, font = ("Colibri", 22))
        self.texto_buscar_inicial.place(x = 10, y = 10)
        self.alfabeto = list("ABCDEFGHIJKLMNÑOPQRSTUVWXYZ")
        self.barra_letras = tk.Frame(self.buscar_por_inicial, bg=colores.BARRA_LETRAS)
        self.barra_letras.place(relx=0.439, rely=0.70, anchor="center")

    def buscar_por_letra(self, letra):
        if self.letra_seleccionada == letra:
            self.letra_seleccionada = None
            ids = list(self.productos_home_originales)
            self.app.mensaje_temporal(idiomas.t("inicio_mostrando_destacados"))
        else:
            ids = self.app.productos_db.obtener_por_letra_inicial(letra)
            self.letra_seleccionada = letra
            if ids:
                self.app.mensaje_temporal(idiomas.t("inicio_mostrando_letra", letra=letra))
            else:
                self.app.mensaje_temporal(idiomas.t("inicio_sin_resultados_letra", letra=letra))
                self._actualizar_estilos_letras()
                return
        self.app.e_productos = ids
        self._renderizar_grid(ids)

    def crear_boton_letra(self, letra):
        frame = tk.Frame(self.barra_letras,bg=colores.BOTON_LETRA,width=34,height=34)
        frame.pack(side="left", padx=3, pady = 5)
        frame.pack_propagate(False)
        label = tk.Label(frame,text=letra,bg=colores.BOTON_LETRA,fg="black", pady = 10, font=("Segoe UI", 12, "bold"),cursor="hand2")
        label.place(relx=0.5, rely=0.5, anchor="center")
        self.botones_letra[letra] = (frame, label)
        def entrar(e):
            if self.letra_seleccionada == letra:
                return
            frame.configure(bg=colores.MARCA_TEAL_HOVER)
            label.configure(bg=colores.MARCA_TEAL_HOVER, fg="white")
        def salir(e):
            self._restaurar_color_letra(letra)
            label.place_configure(rely=0.5)
        def presionar(e):
            label.place_configure(rely=0.56)
        def soltar(e):
            label.place_configure(rely=0.5)
            self.buscar_por_letra(letra)
        widgets = [frame, label]
        for w in widgets:
            w.bind("<Enter>", entrar)
            w.bind("<Leave>", salir)
            w.bind("<ButtonPress-1>", presionar)
            w.bind("<ButtonRelease-1>", soltar)

    def _restaurar_color_letra(self, letra):
        frame, label = self.botones_letra[letra]
        if not frame.winfo_exists():
            return
        if letra == self.letra_seleccionada:
            frame.configure(bg=colores.MARCA_TEAL)
            label.configure(bg=colores.MARCA_TEAL, fg="white")
        else:
            frame.configure(bg=colores.BOTON_LETRA)
            label.configure(bg=colores.BOTON_LETRA, fg="black")

    def _actualizar_estilos_letras(self):
        for letra in self.botones_letra:
            self._restaurar_color_letra(letra)