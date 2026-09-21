import tkinter as tk
import customtkinter as ctk
import colores
from componentes.grid_productos import GridProductos


class VistaBusqueda:
    RADIO_CHICO = 14

    def __init__(self, parent, app, texto):
        self.parent = parent
        self.app = app
        self.texto = (texto or "").strip()
        # Igual que VistaInicio: el contenedor raíz ocupa todo el ancho,
        # sin padx/pady que le resten espacio a la grilla de productos.
        self.frame_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.frame_principal.pack(fill="both", expand=True)
        self.construir()

    # ================= Construcción =================
    def construir(self):
        for w in self.frame_principal.winfo_children():
            w.destroy()
        ids = self.app.productos_db.buscar_productos(self.texto)
        self.app.e_productos = ids
        self._crear_header(len(ids))
        # frame_grid se empaqueta a ancho completo, igual que en VistaInicio,
        # para que GridProductos calcule las 5 columnas con el mismo ancho
        # disponible en ambas vistas y las tarjetas no se vean distorsionadas.
        self.frame_grid = tk.Frame(self.frame_principal, bg=colores.FONDO_PRINCIPAL)
        self.frame_grid.pack(fill="both", expand=True)
        if not ids:
            self._crear_estado_vacio()
        else:
            GridProductos(self.frame_grid, self.app, ids)

    def _crear_header(self, cantidad):
        fila = tk.Frame(self.frame_principal, bg=colores.FONDO_PRINCIPAL)
        fila.pack(fill="x", padx=40, pady=(30, 20))
        tk.Label(fila, text=f'Resultados para "{self.texto}"', bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        if cantidad:
            subtitulo = f"{cantidad} producto{'s' if cantidad != 1 else ''} encontrado{'s' if cantidad != 1 else ''}"
        else:
            subtitulo = "No se encontraron productos con ese criterio"
        tk.Label(fila, text=subtitulo, bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(anchor="w", pady=(4, 0))

    def _crear_estado_vacio(self):
        contenedor = tk.Frame(self.frame_grid, bg=colores.FONDO_PRINCIPAL)
        contenedor.pack(expand=True, pady=80)
        tk.Label(contenedor, text="🔎", bg=colores.FONDO_PRINCIPAL, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 60)).pack()
        tk.Label(contenedor, text="No encontramos productos", bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 18, "bold")).pack(pady=(16, 6))
        tk.Label(contenedor, text="Probá con otras palabras o revisá la ortografía.", bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(pady=(0, 24))
        ctk.CTkButton(contenedor, text="Volver al inicio", corner_radius=self.RADIO_CHICO, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 13, "bold"), height=42, command=self._ir_a_inicio).pack()

    def _ir_a_inicio(self):
        self.app.cambiar_vista(self.app.mostrar_inicio)