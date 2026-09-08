import tkinter as tk
import customtkinter as ctk
import colores
import idiomas
from componentes.vender.utils_vender import PASOS_WIZARD
from componentes.vender.paso_fotos import PasoFotos
from componentes.vender.paso_info import PasoInfo
from componentes.vender.paso_ficha import PasoFicha
from componentes.vender.paso_precio import PasoPrecio
from componentes.vender.paso_pago import PasoPago
from componentes.vender.paso_ia import PasoIA
from componentes.vender.paso_preview import PasoPreview


class VistaVender:
    RADIO_GRANDE = 20
    RADIO_MEDIO = 16

    def __init__(self, parent, app, producto_id=None):
        self.parent = parent
        self.app = app
        self.paso_actual = 0
        self.producto_id_editar = producto_id
        self.imagenes = []
        self.datos = {}

        if producto_id:
            self._cargar_datos_edicion(producto_id)

        self.contenedor_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor_principal.pack(fill="both", expand=True, padx=50, pady=36)
        self.card = ctk.CTkFrame(self.contenedor_principal, corner_radius=self.RADIO_GRANDE,
                                  fg_color=colores._CARD, border_width=1, border_color=colores._CARD_BORDE)
        self.card.pack(fill="both", expand=True)
        self.pad = tk.Frame(self.card, bg=colores._CARD)
        self.pad.pack(fill="both", expand=True, padx=40, pady=34)

        self._crear_header()
        self._crear_progreso()
        self.frame_paso = tk.Frame(self.pad, bg=colores._CARD)
        self.frame_paso.pack(fill="both", expand=True, pady=(24, 0))
        self._crear_navegacion()
        self._render_paso()

    # ================= Carga de datos para edición =================
    def _cargar_datos_edicion(self, producto_id):
        publicacion = self.app.publicaciones_db.obtener_publicacion_completa(producto_id)
        if not publicacion:
            self.app.mensaje_temporal(idiomas.t("vend_no_pudo_cargar_edicion"))
            self.producto_id_editar = None
            return
        self.datos = {
            "titulo": publicacion.get("nombre") or "",
            "subtitulo": publicacion.get("subtitulo") or "",
            "descripcion": publicacion.get("descripcion") or "",
            "categoria": publicacion.get("categoria") or "general",
            "subcategoria": publicacion.get("subcategoria") or "",
            "estado_producto": publicacion.get("estado_producto") or "nuevo",
            "marca": publicacion.get("marca") or "",
            "modelo": publicacion.get("modelo") or "",
            "color": publicacion.get("color") or "",
            "material": publicacion.get("material") or "",
            "peso": publicacion.get("peso") or "",
            "dimensiones": publicacion.get("dimensiones") or "",
            "stock": publicacion.get("stock") or 0,
            "sku": publicacion.get("sku") or "",
            "etiquetas": publicacion.get("etiquetas") or "",
            "garantia": publicacion.get("garantia") or "",
            "tipo_envio": publicacion.get("tipo_envio") or "retiro",
            "ficha_tecnica": publicacion.get("ficha_tecnica") or {},
            "precio": publicacion.get("precio") or 0,
            "tiene_oferta": bool(publicacion.get("precio_oferta")),
            "precio_oferta": publicacion.get("precio_oferta"),
            "cuotas_cantidad": publicacion.get("cuotas_cantidad"),
            "cuotas_interes": publicacion.get("cuotas_interes") or 0,
            "moneda": publicacion.get("moneda") or "ARS",
            "medios_pago": publicacion.get("medios_pago") or [],
        }
        urls_imagenes = self.app.productos_db.obtener_imagenes(producto_id) or [publicacion.get("imagen")]
        for i, url in enumerate(urls_imagenes):
            if not url:
                continue
            try:
                img = self.app.obtener_imagen(url)
            except Exception as e:
                print(f"No se pudo cargar la imagen {url} para editar: {e}")
                img = None
            if img is not None:
                self.imagenes.append({"pil": img, "principal": i == 0})

    # ================= Header =================
    def _crear_header(self):
        fila = tk.Frame(self.pad, bg=colores._CARD)
        fila.pack(fill="x", pady=(0, 8))
        titulo = idiomas.t("vend_editar_titulo") if self.producto_id_editar else idiomas.t("vend_titulo")
        tk.Label(fila, text=titulo, bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(fila, text=idiomas.t("vend_subtitulo"),
                 bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 0))

    # ================= Barra de progreso por pasos =================
    def _crear_progreso(self):
        self.frame_progreso = tk.Frame(self.pad, bg=colores._CARD)
        self.frame_progreso.pack(fill="x", pady=(18, 0))
        self._widgets_pasos = []
        for i, nombre in enumerate(PASOS_WIZARD):
            if i > 0:
                linea = tk.Frame(self.frame_progreso, bg=colores._VENDER_LINEA_PROGRESO, height=2)
                linea.pack(side="left", fill="x", expand=True, pady=15)
            col = tk.Frame(self.frame_progreso, bg=colores._CARD)
            col.pack(side="left")
            circulo = tk.Canvas(col, width=32, height=32, bg=colores._CARD, highlightthickness=0)
            circulo.pack()
            etiqueta = tk.Label(col, text=nombre, bg=colores._CARD, fg=colores._VENDER_STEP_TEXTO, font=("Segoe UI", 9, "bold"), wraplength=75, justify="center")
            etiqueta.pack(pady=(4, 0))
            self._widgets_pasos.append((circulo, etiqueta))
        self._actualizar_progreso()

    def _actualizar_progreso(self):
        for i, (circulo, etiqueta) in enumerate(self._widgets_pasos):
            circulo.delete("all")
            if i < self.paso_actual:
                circulo.create_oval(2, 2, 30, 30, fill=colores._VENDER_STEP_ACTIVO, outline="")
                circulo.create_text(16, 16, text="✓", fill=colores.TEXTO_BLANCO, font=("Segoe UI", 12, "bold"))
                etiqueta.configure(fg=colores._VENDER_STEP_ACTIVO)
            elif i == self.paso_actual:
                circulo.create_oval(2, 2, 30, 30, fill=colores.MARCA_TEAL, outline="")
                circulo.create_text(16, 16, text=str(i + 1), fill=colores.TEXTO_BLANCO, font=("Segoe UI", 12, "bold"))
                etiqueta.configure(fg=colores.MARCA_TEAL)
            else:
                circulo.create_oval(2, 2, 30, 30, fill="", outline=colores._VENDER_STEP_INACTIVO, width=2)
                circulo.create_text(16, 16, text=str(i + 1), fill=colores._VENDER_STEP_INACTIVO, font=("Segoe UI", 12, "bold"))
                etiqueta.configure(fg=colores._VENDER_STEP_TEXTO)

    # ================= Navegación =================
    def _crear_navegacion(self):
        self.frame_nav = tk.Frame(self.pad, bg=colores._CARD)
        self.frame_nav.pack(fill="x", pady=(24, 0))
        self.btn_atras = ctk.CTkButton(self.frame_nav, text=idiomas.t("vend_atras"), width=120, height=40, corner_radius=12,
                                        fg_color=colores.BTN_OSCURO, hover_color=colores.BTN_OSCURO_HOVER,
                                        font=("Segoe UI", 12, "bold"), command=self._ir_atras)
        self.btn_atras.pack(side="left")
        self.btn_siguiente = ctk.CTkButton(self.frame_nav, text=idiomas.t("vend_continuar"), width=160, height=40, corner_radius=12,
                                            fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER,
                                            font=("Segoe UI", 12, "bold"), command=self._ir_adelante)
        self.btn_siguiente.pack(side="right")

    def _ir_atras(self):
        if self.paso_actual == 0:
            self.app.volver()
            return
        self.paso_actual -= 1
        self._actualizar_progreso()
        self._render_paso()

    def _ir_adelante(self):
        errores = self.paso_widget.validar()
        if errores:
            self.app.mensaje_temporal(errores[0])
            return
        self.paso_widget.guardar()
        if self.paso_actual < len(PASOS_WIZARD) - 1:
            self.paso_actual += 1
            self._actualizar_progreso()
            self._render_paso()

    def avanzar_automatico(self):
        if self.paso_actual < len(PASOS_WIZARD) - 1:
            self.paso_actual += 1
            self._actualizar_progreso()
            self._render_paso()

    def ir_a_paso(self, indice):
        self.paso_actual = indice
        self._actualizar_progreso()
        self._render_paso()

    # ================= Render del paso actual =================
    def _render_paso(self):
        if hasattr(self, "paso_widget") and hasattr(self.paso_widget, "cerrar"):
            try:
                self.paso_widget.cerrar()
            except Exception as e:
                print(f"Error cerrando paso anterior: {e}")
        for w in self.frame_paso.winfo_children():
            w.destroy()
        clases = [PasoFotos, PasoInfo, PasoFicha, PasoPrecio, PasoPago, PasoIA, PasoPreview]
        clase = clases[self.paso_actual]
        try:
            self.paso_widget = clase(self.frame_paso, self)
        except Exception as e:
            print(f"Error al construir el paso {self.paso_actual}: {e}")
            for w in self.frame_paso.winfo_children():
                w.destroy()
            tk.Label(self.frame_paso, text=idiomas.t("vend_error_paso"),
                      bg=colores._CARD, fg=colores._ROJO_STOCK, font=("Segoe UI", 12, "bold"), wraplength=500).pack(pady=40)
            raise
        ultimo = self.paso_actual == len(PASOS_WIZARD) - 1
        es_ia = self.paso_actual == 5
        self.btn_siguiente.pack_forget() if (ultimo or es_ia) else self.btn_siguiente.pack(side="right")
        self.btn_atras.configure(text=idiomas.t("vend_atras") if self.paso_actual > 0 else idiomas.t("vend_cancelar"))