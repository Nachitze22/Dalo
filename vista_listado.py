import tkinter as tk
import customtkinter as ctk
import colores
import idiomas
from componentes.grid_productos import GridProductos


class VistaListadoProductos:
    """Vista genérica para listados de productos con título/subtítulo
    personalizados (se usa para 'Lo más vendido' y 'Ofertas')."""
    RADIO_CHICO = 14

    def __init__(self, parent, app, titulo, subtitulo, ids, icono_vacio="🔎", texto_vacio="No se encontraron productos."):
        self.parent = parent
        self.app = app
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.ids = ids or []
        self.icono_vacio = icono_vacio
        self.texto_vacio = texto_vacio
        self.frame_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.frame_principal.pack(fill="both", expand=True)
        self.construir()

    def construir(self):
        for w in self.frame_principal.winfo_children():
            w.destroy()
        self._crear_header()
        self.frame_grid = tk.Frame(self.frame_principal, bg=colores.FONDO_PRINCIPAL)
        self.frame_grid.pack(fill="both", expand=True)
        if not self.ids:
            self._crear_estado_vacio()
        else:
            GridProductos(self.frame_grid, self.app, self.ids)

    def _crear_header(self, cantidad=None):
        fila = tk.Frame(self.frame_principal, bg=colores.FONDO_PRINCIPAL)
        fila.pack(fill="x", padx=40, pady=(30, 20))
        tk.Label(fila, text=self.titulo, bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        cantidad = len(self.ids)
        if cantidad:
            contador = idiomas.t("listado_contador_productos", n=cantidad, s="s" if cantidad != 1 else "")
            sub = f"{self.subtitulo}  •  {contador}"
        else:
            sub = self.subtitulo
        tk.Label(fila, text=sub, bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(anchor="w", pady=(4, 0))

    def _crear_estado_vacio(self):
        contenedor = tk.Frame(self.frame_grid, bg=colores.FONDO_PRINCIPAL)
        contenedor.pack(expand=True, pady=80)
        tk.Label(contenedor, text=self.icono_vacio, bg=colores.FONDO_PRINCIPAL, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 60)).pack()
        tk.Label(contenedor, text=self.texto_vacio, bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_GRIS, font=("Segoe UI", 13), wraplength=420, justify="center").pack(pady=(16, 24))
        ctk.CTkButton(contenedor, text=idiomas.t("volver_inicio"), corner_radius=self.RADIO_CHICO, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 13, "bold"), height=42, command=self._ir_a_inicio).pack()

    def _ir_a_inicio(self):
        self.app.cambiar_vista(self.app.mostrar_inicio)