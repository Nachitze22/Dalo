import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import random
import colores
import idiomas
import variables_globales

class VistaComprar:
    RADIO_GRANDE = 20
    RADIO_MEDIO = 16
    RADIO_CHICO = 14
    SEDE_DIRECCION = variables_globales.SEDE_DIRECCION
    SEDE_HORARIO = variables_globales.SEDE_HORARIO
    COSTO_ENVIO_DOMICILIO = 4500

    def __init__(self, parent, app, producto_id, cantidad=1):
        self.parent = parent
        self.app = app
        self.producto_id = producto_id
        self.producto = self.app.productos_db.obtener_producto(producto_id)
        self.cantidad = cantidad
        self.oferta = self.app.productos_db.obtener_oferta_activa(producto_id)
        self.entrega_seleccionada = "retiro"
        self.metodo_pago_seleccionado = "mercado_pago"
        self._imagen_resumen = None
        self.direcciones_envio = [d for d in self.app.direcciones_guardadas if d.get("tipo") != "sede"]
        self.direccion_envio_elegida = self.direcciones_envio[0] if self.direcciones_envio else None
        self.cupon_aplicado = None
        self.cupon_mensaje = None
        self.cupon_mensaje_ok = False
        self.crear_widgets()

    @property
    def METODOS_PAGO(self):
        return [
            ("mercado_pago", idiomas.t("checkout_mercado_pago"), idiomas.t("checkout_acreditacion")),
            ("tarjeta", idiomas.t("checkout_tarjeta_credito"), idiomas.t("checkout_tarjeta_sub")),
            ("transferencia", idiomas.t("checkout_transferencia_cbu"), idiomas.t("checkout_transferencia_sub")),
        ]

    # ================= Construcción principal =================
    def crear_widgets(self):
        if not self.producto:
            self._mostrar_error_producto()
            return
        self.contenedor_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor_principal.pack(fill="both", expand=True, padx=50, pady=36)
        self.card = ctk.CTkFrame(self.contenedor_principal, corner_radius=self.RADIO_GRANDE, fg_color=colores._CARD, border_width=1, border_color=colores._CARD_BORDE)
        self.card.pack(fill="both", expand=True)
        self.pad = tk.Frame(self.card, bg=colores._CARD)
        self.pad.pack(fill="both", expand=True, padx=40, pady=40)
        self._crear_header()
        self._crear_cuerpo()

    def _mostrar_error_producto(self):
        contenedor = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        contenedor.pack(fill="both", expand=True, padx=50, pady=36)
        tk.Label(contenedor, text=idiomas.t("checkout_no_pudo_cargar"), bg=colores.FONDO_PRINCIPAL, fg=colores._TEXTO, font=("Segoe UI", 14)).pack(pady=40)

    # ================= Header =================
    def _crear_header(self):
        panel = ctk.CTkFrame(self.pad, corner_radius=self.RADIO_CHICO, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        panel.pack(fill="x", pady=(0, 12))
        fila = tk.Frame(panel, bg=colores._CHECKOUT_FONDO_OSCURO)
        fila.pack(fill="x", padx=22, pady=14)
        self.btn_volver_texto = tk.Label(fila, text=idiomas.t("checkout_volver_producto"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.MARCA_TEAL, font=("Segoe UI", 12, "bold"), cursor="hand2")
        self.btn_volver_texto.pack(side="left")
        self.btn_volver_texto.bind("<Enter>", lambda e: self.btn_volver_texto.configure(fg=colores.MARCA_TEAL_HOVER))
        self.btn_volver_texto.bind("<Leave>", lambda e: self.btn_volver_texto.configure(fg=colores.MARCA_TEAL))
        self.btn_volver_texto.bind("<Button-1>", lambda e: self.app.volver())
        tk.Label(fila, text=idiomas.t("checkout_simulacion_tag"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.MARCA_TEAL, font=("Segoe UI", 10, "bold")).pack(side="right")
        aviso = tk.Frame(self.pad, bg=colores._CARD)
        aviso.pack(fill="x", pady=(0, 22))
        tk.Label(aviso, text=idiomas.t("checkout_aviso_simulacion"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10, "italic"), wraplength=900, justify="left").pack(anchor="w")

    # ================= Cuerpo (dos columnas) =================
    def _crear_cuerpo(self):
        cuerpo = tk.Frame(self.pad, bg=colores._CARD)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(0, weight=65)
        cuerpo.grid_columnconfigure(1, weight=0)
        cuerpo.grid_columnconfigure(2, weight=35)
        cuerpo.grid_rowconfigure(0, weight=1)

        self.col_izquierda = tk.Frame(cuerpo, bg=colores._CARD)
        self.col_izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 30))

        tk.Frame(cuerpo, bg=colores._SEPARADOR, width=1).grid(row=0, column=1, sticky="ns", pady=4)

        self.panel_derecha = ctk.CTkFrame(cuerpo, corner_radius=self.RADIO_MEDIO + 2, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        self.panel_derecha.grid(row=0, column=2, sticky="nsew", padx=(30, 0))
        self.col_derecha = tk.Frame(self.panel_derecha, bg=colores._CHECKOUT_FONDO_OSCURO)
        self.col_derecha.pack(fill="both", expand=True, padx=26, pady=26)

        self._crear_columna_izquierda()
        self._crear_columna_derecha()

    def _crear_titulo_seccion(self, parent, numero, texto, bg=None, pady_top=0):
        bg = bg or colores._CARD
        fila = tk.Frame(parent, bg=bg)
        fila.pack(fill="x", pady=(pady_top, 16), anchor="w")
        tk.Label(fila, text=f"{numero}.", bg=bg, fg=colores.MARCA_TEAL, font=("Segoe UI", 16, "bold")).pack(side="left", padx=(0, 8))
        tk.Label(fila, text=texto, bg=bg, fg=colores._TEXTO, font=("Segoe UI", 16, "bold")).pack(side="left")

    # ================= Columna izquierda =================
    def _crear_columna_izquierda(self):
        self._crear_titulo_seccion(self.col_izquierda, "1", idiomas.t("checkout_paso1"))
        self._crear_card_entrega()
        self.frame_ubicacion = tk.Frame(self.col_izquierda, bg=colores._CARD)
        self.frame_ubicacion.pack(fill="x")
        self._actualizar_card_ubicacion()
        self._crear_titulo_seccion(self.col_izquierda, "2", idiomas.t("checkout_paso2"), pady_top=34)
        self._crear_card_pago()
        self._crear_panel_detalle_pago()

    # ----- Forma de entrega -----
    def _crear_card_entrega(self):
        self.frame_entrega = tk.Frame(self.col_izquierda, bg=colores._CARD)
        self.frame_entrega.pack(fill="x", pady=(0, 16))
        self._actualizar_entrega()

    def _actualizar_entrega(self):
        for w in self.frame_entrega.winfo_children():
            w.destroy()
        self.frame_entrega.grid_columnconfigure(0, weight=1, uniform="entrega")
        self.frame_entrega.grid_columnconfigure(1, weight=1, uniform="entrega")
        retiro = self._construir_tarjeta_entrega(
            self.frame_entrega, clave="retiro", icono="🏬", titulo=idiomas.t("checkout_retirar_sede"),
            subtitulo=idiomas.t("checkout_gratis_retiro"),
            descripcion=f"{self.SEDE_DIRECCION.split(',', 2)[0]}, {self.SEDE_DIRECCION.split(',', 2)[1].strip()}.",
            disponible=True,
        )
        retiro.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        envio = self._construir_tarjeta_entrega(
            self.frame_entrega, clave="envio", icono="🚚", titulo=idiomas.t("checkout_envio_domicilio"),
            subtitulo=self.app.formatear_precio(self.COSTO_ENVIO_DOMICILIO, self.producto["moneda"]),
            descripcion=idiomas.t("checkout_envio_desc"),
            disponible=True,
        )
        envio.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

    def _construir_tarjeta_entrega(self, parent, clave, icono, titulo, subtitulo, descripcion, disponible):
        seleccionada = (clave == self.entrega_seleccionada)
        if seleccionada:
            bg = colores._CHECKOUT_CARD_SELECCIONADA
            borde_normal = colores.MARCA_TEAL
        else:
            bg = colores._CARD
            borde_normal = colores._CARD_BORDE
        tarjeta = ctk.CTkFrame(parent, corner_radius=self.RADIO_MEDIO, fg_color=bg, border_width=2, border_color=borde_normal, cursor="hand2")
        contenido = tk.Frame(tarjeta, bg=bg)
        contenido.pack(fill="both", expand=True, padx=18, pady=16)
        encabezado = tk.Frame(contenido, bg=bg)
        encabezado.pack(fill="x", anchor="w")
        tk.Label(encabezado, text=icono, bg=bg, fg=colores._ICONO_COMPRAR   , font=("Segoe UI Symbol", 15)).pack(side="left", padx=(0, 8))
        tk.Label(encabezado, text=titulo, bg=bg, fg=colores._TEXTO, font=("Segoe UI", 13, "bold")).pack(side="left")
        color_subtitulo = colores.MARCA_TEAL
        tk.Label(contenido, text=subtitulo, bg=bg, fg=color_subtitulo, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8, 4))
        tk.Label(contenido, text=descripcion, bg=bg, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10), wraplength=260, justify="left").pack(anchor="w")
        widgets = [tarjeta, contenido, encabezado] + encabezado.winfo_children() + contenido.winfo_children()
        for w in widgets:
            w.bind("<Button-1>", lambda e, c=clave: self._seleccionar_card("entrega", c))
            w.bind("<Enter>", lambda e, f=tarjeta, bn=borde_normal: self._hover_card(f, True, bn))
            w.bind("<Leave>", lambda e, f=tarjeta, bn=borde_normal: self._hover_card(f, False, bn))
        return tarjeta

    # ----- Card de ubicación (dinámica: sede o dirección de envío) -----
    def _actualizar_card_ubicacion(self):
        for w in self.frame_ubicacion.winfo_children():
            w.destroy()
        if self.entrega_seleccionada == "retiro":
            self._card_ubicacion_sede()
        else:
            self._card_ubicacion_envio()

    def _card_ubicacion_sede(self):
        tarjeta = ctk.CTkFrame(self.frame_ubicacion, corner_radius=self.RADIO_CHICO, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        tarjeta.pack(fill="x")
        contenido = tk.Frame(tarjeta, bg=colores._CHECKOUT_FONDO_OSCURO)
        contenido.pack(fill="x", padx=22, pady=18)
        encabezado = tk.Frame(contenido, bg=colores._CHECKOUT_FONDO_OSCURO)
        encabezado.pack(fill="x", anchor="w")
        tk.Label(encabezado, text="📍", bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._CHECKOUT_ICONO_AZUL, font=("Segoe UI Symbol", 12)).pack(side="left", padx=(0, 8))
        tk.Label(encabezado, text=idiomas.t("checkout_retiro_habilitado"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(contenido, text=self.SEDE_DIRECCION, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.MARCA_TEAL, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8, 2))
        tk.Label(contenido, text=self.SEDE_HORARIO, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w")

    def _card_ubicacion_envio(self):
        tarjeta = ctk.CTkFrame(self.frame_ubicacion, corner_radius=self.RADIO_CHICO, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        tarjeta.pack(fill="x")
        contenido = tk.Frame(tarjeta, bg=colores._CHECKOUT_FONDO_OSCURO)
        contenido.pack(fill="x", padx=22, pady=18)
        encabezado = tk.Frame(contenido, bg=colores._CHECKOUT_FONDO_OSCURO)
        encabezado.pack(fill="x", anchor="w")
        tk.Label(encabezado, text="📍", bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._CHECKOUT_ICONO_AZUL, font=("Segoe UI Symbol", 12)).pack(side="left", padx=(0, 8))
        tk.Label(encabezado, text=idiomas.t("checkout_elegir_direccion"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(side="left")
        if not self.direcciones_envio:
            tk.Label(contenido, text=idiomas.t("checkout_sin_direcciones"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10), wraplength=460, justify="left").pack(anchor="w", pady=(10, 12))
            ctk.CTkButton(contenido, text=idiomas.t("checkout_agregar_direccion"), corner_radius=10, height=36, fg_color="transparent", hover_color=colores._DIRECCIONES_ITEM_BG, border_width=1, border_color=colores._DIRECCIONES_BTN_AGREGAR, text_color=colores._DIRECCIONES_BTN_AGREGAR, font=("Segoe UI", 11, "bold"), command=self._ir_a_nueva_direccion).pack(anchor="w")
            return
        lista = tk.Frame(contenido, bg=colores._CHECKOUT_FONDO_OSCURO)
        lista.pack(fill="x", pady=(10, 10))
        for direccion in self.direcciones_envio:
            self._fila_direccion_envio(lista, direccion)
        ctk.CTkButton(contenido, text=idiomas.t("checkout_agregar_otra"), corner_radius=10, height=32, fg_color="transparent", hover_color=colores._DIRECCIONES_ITEM_BG, border_width=1, border_color=colores._DIRECCIONES_BTN_AGREGAR, text_color=colores._DIRECCIONES_BTN_AGREGAR, font=("Segoe UI", 10, "bold"), command=self._ir_a_nueva_direccion).pack(anchor="w")

    def _fila_direccion_envio(self, parent, direccion):
        seleccionada = self.direccion_envio_elegida is not None and direccion["id"] == self.direccion_envio_elegida["id"]
        bg = colores._DIRECCIONES_ITEM_BG_SELECCIONADO if seleccionada else colores._DIRECCIONES_ITEM_BG
        borde = colores._DIRECCIONES_ITEM_BORDE_SELECCIONADO if seleccionada else colores._DIRECCIONES_ITEM_BORDE
        fila = ctk.CTkFrame(parent, corner_radius=10, fg_color=bg, border_width=2, border_color=borde, cursor="hand2")
        fila.pack(fill="x", pady=4)
        interior = tk.Frame(fila, bg=bg)
        interior.pack(fill="x", padx=14, pady=10)
        radio = tk.Canvas(interior, width=16, height=16, bg=bg, highlightthickness=0)
        radio.pack(side="left", padx=(0, 10))
        color_radio = colores.MARCA_TEAL if seleccionada else colores._CHECKOUT_RADIO_INACTIVO
        radio.create_oval(2, 2, 14, 14, outline=color_radio, width=2)
        if seleccionada:
            radio.create_oval(5, 5, 11, 11, fill=colores.MARCA_TEAL, outline="")
        textos = tk.Frame(interior, bg=bg)
        textos.pack(side="left", fill="x", expand=True)
        tk.Label(textos, text=direccion["etiqueta"], bg=bg, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 11, "bold"), anchor="w").pack(anchor="w")
        subt = direccion.get("localidad") or direccion.get("direccion_completa", "")
        tk.Label(textos, text=subt, bg=bg, fg=colores.TEXTO_GRIS, font=("Segoe UI", 9), anchor="w").pack(anchor="w")
        widgets = [fila, interior, radio, textos] + textos.winfo_children()
        for w in widgets:
            w.bind("<Button-1>", lambda e, d=direccion: self._seleccionar_direccion_envio(d))

    # ----- Método de pago -----
    def _crear_card_pago(self):
        self.frame_pago = tk.Frame(self.col_izquierda, bg=colores._CARD)
        self.frame_pago.pack(fill="x", pady=(0, 16))
        for i in range(3):
            self.frame_pago.grid_columnconfigure(i, weight=1, uniform="pago")

    def _crear_panel_detalle_pago(self):
        self.frame_detalle_pago = tk.Frame(self.col_izquierda, bg=colores._CARD)
        self.frame_detalle_pago.pack(fill="x")
        self._actualizar_metodo_pago()

    def _actualizar_metodo_pago(self):
        for w in self.frame_pago.winfo_children():
            w.destroy()
        for i, (clave, titulo, subtitulo) in enumerate(self.METODOS_PAGO):
            tarjeta = self._construir_tarjeta_pago(self.frame_pago, clave, titulo, subtitulo)
            tarjeta.grid(row=0, column=i, sticky="nsew", padx=(0, 8) if i < 2 else (0, 0))
        self._actualizar_panel_detalle_pago()

    def _construir_tarjeta_pago(self, parent, clave, titulo, subtitulo):
        seleccionada = (clave == self.metodo_pago_seleccionado)
        bg = colores._CHECKOUT_CARD_SELECCIONADA if seleccionada else colores._CARD
        borde_normal = colores.MARCA_TEAL if seleccionada else colores._CARD_BORDE
        tarjeta = ctk.CTkFrame(parent, corner_radius=self.RADIO_MEDIO, fg_color=bg, border_width=2, border_color=borde_normal, cursor="hand2")
        contenido = tk.Frame(tarjeta, bg=bg)
        contenido.pack(fill="both", expand=True, padx=16, pady=14)
        fila = tk.Frame(contenido, bg=bg)
        fila.pack(fill="x", anchor="w")
        radio = tk.Canvas(fila, width=18, height=18, bg=bg, highlightthickness=0)
        radio.pack(side="left", padx=(0, 10))
        color_radio = colores.MARCA_TEAL if seleccionada else colores._CHECKOUT_RADIO_INACTIVO
        radio.create_oval(2, 2, 16, 16, outline=color_radio, width=2)
        if seleccionada:
            radio.create_oval(6, 6, 12, 12, fill=colores.MARCA_TEAL, outline="")
        textos = tk.Frame(fila, bg=bg)
        textos.pack(side="left")
        tk.Label(textos, text=titulo, bg=bg, fg=colores._TEXTO, font=("Segoe UI", 11, "bold"), wraplength=140, justify="left").pack(anchor="w")
        tk.Label(textos, text=subtitulo, bg=bg, fg=colores.MARCA_TEAL if seleccionada else colores.TEXTO_GRIS, font=("Segoe UI", 9), wraplength=140, justify="left").pack(anchor="w")
        widgets = [tarjeta, contenido, fila, radio, textos] + textos.winfo_children()
        for w in widgets:
            w.bind("<Button-1>", lambda e, c=clave: self._seleccionar_card("pago", c))
            w.bind("<Enter>", lambda e, f=tarjeta, bn=borde_normal: self._hover_card(f, True, bn))
            w.bind("<Leave>", lambda e, f=tarjeta, bn=borde_normal: self._hover_card(f, False, bn))
        return tarjeta

    def _actualizar_panel_detalle_pago(self):
        for w in self.frame_detalle_pago.winfo_children():
            w.destroy()
        detalle = ctk.CTkFrame(self.frame_detalle_pago, corner_radius=self.RADIO_CHICO, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        detalle.pack(fill="x")
        contenido = tk.Frame(detalle, bg=colores._CHECKOUT_FONDO_OSCURO)
        contenido.pack(fill="x", padx=22, pady=18)
        titulo, lineas = self._contenido_detalle_pago()
        encabezado = tk.Frame(contenido, bg=colores._CHECKOUT_FONDO_OSCURO)
        encabezado.pack(fill="x", anchor="w", pady=(0, 10))
        tk.Label(encabezado, text="ℹ", bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._CHECKOUT_ICONO_AZUL, font=("Segoe UI Symbol", 13, "bold")).pack(side="left", padx=(0, 8))
        tk.Label(encabezado, text=titulo, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(side="left")
        for linea in lineas:
            tk.Label(contenido, text=f"•  {linea}", bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10), wraplength=560, justify="left").pack(anchor="w", pady=(0, 4))

    def _contenido_detalle_pago(self):
        if self.metodo_pago_seleccionado == "mercado_pago":
            return idiomas.t("checkout_mp_titulo"), [idiomas.t("checkout_mp_1"), idiomas.t("checkout_mp_2")]
        if self.metodo_pago_seleccionado == "tarjeta":
            return idiomas.t("checkout_tarjeta_titulo"), [idiomas.t("checkout_tarjeta_1"), idiomas.t("checkout_tarjeta_2")]
        return idiomas.t("checkout_transf_titulo"), [idiomas.t("checkout_transf_1"), idiomas.t("checkout_transf_2")]

    # ================= Columna derecha =================
    def _crear_columna_derecha(self):
        bg = colores._CHECKOUT_FONDO_OSCURO
        tk.Label(self.col_derecha, text=idiomas.t("checkout_resumen_pedido"), bg=bg, fg=colores._TEXTO, font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 20))
        self._crear_card_resumen()
        tk.Frame(self.col_derecha, bg=colores._CHECKOUT_BORDE_SUAVE, height=1).pack(fill="x", pady=18)
        self._crear_seccion_cupon()
        tk.Frame(self.col_derecha, bg=colores._CHECKOUT_BORDE_SUAVE, height=1).pack(fill="x", pady=18)
        self.frame_desglose = tk.Frame(self.col_derecha, bg=bg)
        self.frame_desglose.pack(fill="x")
        tk.Frame(self.col_derecha, bg=colores._CHECKOUT_BORDE_SUAVE, height=1).pack(fill="x", pady=18)
        self.frame_total = tk.Frame(self.col_derecha, bg=bg)
        self.frame_total.pack(fill="x", pady=(0, 24))
        self._actualizar_total()
        self._crear_boton_confirmar()

    def _crear_card_resumen(self):
        tarjeta = ctk.CTkFrame(self.col_derecha, corner_radius=self.RADIO_CHICO, fg_color=colores._CARD, border_width=1, border_color=colores._CARD_BORDE)
        tarjeta.pack(fill="x")
        contenido = tk.Frame(tarjeta, bg=colores._CARD)
        contenido.pack(fill="x", padx=16, pady=16)
        self.lbl_imagen_resumen = tk.Label(contenido, bg=colores._IMG_FONDO, width=64, height=64)
        self.lbl_imagen_resumen.pack(side="left", padx=(0, 14))
        self._cargar_imagen_resumen()
        textos = tk.Frame(contenido, bg=colores._CARD)
        textos.pack(side="left", fill="both", expand=True)
        tk.Label(textos, text=self.producto["nombre"], bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold"), wraplength=200, justify="left", anchor="w").pack(anchor="w")
        tk.Label(textos, text=(self.producto.get("categoria") or "").upper(), bg=colores._CARD, fg=colores.MARCA_TEAL, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 4))
        tk.Label(textos, text=f"{idiomas.t('cuenta_cantidad')}: {self.cantidad}", bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w")

    def _cargar_imagen_resumen(self):
        def terminar(img):
            if img is None or not self.lbl_imagen_resumen.winfo_exists():
                return
            img = self._ajustar_imagen(img, 64, 64, bg=self._hex_a_rgb(colores._IMG_FONDO))
            self._imagen_resumen = ImageTk.PhotoImage(img)
            self.lbl_imagen_resumen.configure(image=self._imagen_resumen, text="")
        imagen_url = self.producto.get("imagen")
        if imagen_url:
            self.app.obtener_imagen(imagen_url, callback=terminar)

    # ----- Cupón de descuento -----
    def _crear_seccion_cupon(self):
        self.frame_cupon = tk.Frame(self.col_derecha, bg=colores._CHECKOUT_FONDO_OSCURO)
        self.frame_cupon.pack(fill="x")
        self._actualizar_seccion_cupon()

    def _actualizar_seccion_cupon(self):
        for w in self.frame_cupon.winfo_children():
            w.destroy()
        bg = colores._CHECKOUT_FONDO_OSCURO
        tk.Label(self.frame_cupon, text=idiomas.t("checkout_cupon_titulo"), bg=bg, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        if self.cupon_aplicado:
            panel = ctk.CTkFrame(self.frame_cupon, corner_radius=10, fg_color=colores._CUPON_APLICADO_BG, border_width=1, border_color=colores._CUPON_APLICADO_BORDE)
            panel.pack(fill="x")
            interior = tk.Frame(panel, bg=colores._CUPON_APLICADO_BG)
            interior.pack(fill="x", padx=14, pady=10)
            tk.Label(interior, text=idiomas.t("checkout_cupon_aplicado", codigo=self.cupon_aplicado['codigo']), bg=colores._CUPON_APLICADO_BG, fg=colores._CUPON_APLICADO_TEXTO, font=("Segoe UI", 11, "bold")).pack(side="left")
            btn_quitar = tk.Label(interior, text=idiomas.t("checkout_cupon_quitar"), bg=colores._CUPON_APLICADO_BG, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10, "bold"), cursor="hand2")
            btn_quitar.pack(side="right")
            btn_quitar.bind("<Button-1>", lambda e: self._quitar_cupon())
            return
        fila = tk.Frame(self.frame_cupon, bg=bg)
        fila.pack(fill="x")
        self.entry_cupon = ctk.CTkEntry(fila, placeholder_text=idiomas.t("checkout_cupon_placeholder"), width=170, height=36, corner_radius=8, fg_color=colores._CUPON_INPUT_BG, border_color=colores._CUPON_INPUT_BORDE, text_color=colores._TEXTO)
        self.entry_cupon.pack(side="left", padx=(0, 8))
        ctk.CTkButton(fila, text=idiomas.t("checkout_cupon_aplicar"), width=90, height=36, corner_radius=8, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 11, "bold"), command=self._aplicar_cupon).pack(side="left")
        if self.cupon_mensaje:
            color = colores._CUPON_APLICADO_TEXTO if self.cupon_mensaje_ok else colores._CUPON_ERROR_TEXTO
            tk.Label(self.frame_cupon, text=self.cupon_mensaje, bg=bg, fg=color, font=("Segoe UI", 9)).pack(anchor="w", pady=(6, 0))

    def _aplicar_cupon(self):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("checkout_necesita_login_cupon"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        usuario_id = self.app.auth.obtener_id_por_email(sesion)
        codigo = self.entry_cupon.get().strip()
        if not codigo:
            self.cupon_mensaje, self.cupon_mensaje_ok = idiomas.t("checkout_cupon_ingresa"), False
            self._actualizar_seccion_cupon()
            return
        subtotal = self._calcular_precio_unitario() * self.cantidad
        ok, mensaje, cupon = self.app.cupones_db.validar_cupon(codigo, usuario_id, subtotal)
        self.cupon_mensaje, self.cupon_mensaje_ok = mensaje, ok
        if ok:
            self.cupon_aplicado = cupon
        self._actualizar_seccion_cupon()
        self._actualizar_total()

    def _quitar_cupon(self):
        self.cupon_aplicado = None
        self.cupon_mensaje = None
        self._actualizar_seccion_cupon()
        self._actualizar_total()

    def _actualizar_desglose(self):
        for w in self.frame_desglose.winfo_children():
            w.destroy()
        precio_unitario = self._calcular_precio_unitario()
        subtotal = precio_unitario * self.cantidad
        unidad = idiomas.t("checkout_cantidad_unidad") if self.cantidad == 1 else idiomas.t("checkout_cantidad_unidades")
        self._fila_precio(self.frame_desglose, idiomas.t("checkout_subtotal", n=self.cantidad, u=unidad), self.app.formatear_precio(subtotal, self.producto["moneda"]), colores._TEXTO)
        costo_envio, texto_envio = self._info_costo_envio()
        color_envio = colores._VERDE_STOCK if costo_envio == 0 and self.entrega_seleccionada == "retiro" else colores._TEXTO
        self._fila_precio(self.frame_desglose, idiomas.t("checkout_costo_entrega"), texto_envio, color_envio)
        descuento_unitario = self.producto["precio"] - precio_unitario
        if descuento_unitario > 0:
            descuento_total = descuento_unitario * self.cantidad
            self._fila_precio(self.frame_desglose, idiomas.t("checkout_descuento_aplicado"), f"-{self.app.formatear_precio(descuento_total, self.producto['moneda'])}", colores._OFERTA_BANNER_TEXTO)
        if self.cupon_aplicado:
            descuento_cupon = self.app.cupones_db.calcular_descuento(self.cupon_aplicado, subtotal)
            if descuento_cupon > 0:
                self._fila_precio(self.frame_desglose, f"{idiomas.t('checkout_cupon_titulo').split()[-1].capitalize()} {self.cupon_aplicado['codigo']}", f"-{self.app.formatear_precio(descuento_cupon, self.producto['moneda'])}", colores._CUPON_APLICADO_TEXTO)

    def _fila_precio(self, parent, etiqueta, valor, color_valor):
        fila = tk.Frame(parent, bg=colores._CHECKOUT_FONDO_OSCURO)
        fila.pack(fill="x", pady=4)
        tk.Label(fila, text=etiqueta, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(side="left")
        tk.Label(fila, text=valor, bg=colores._CHECKOUT_FONDO_OSCURO, fg=color_valor, font=("Segoe UI", 11, "bold")).pack(side="right")

    def _info_costo_envio(self):
        if self.entrega_seleccionada == "retiro":
            return 0, idiomas.t("checkout_gratis_en", d=self.SEDE_DIRECCION.split(',')[0])
        if not self.direccion_envio_elegida:
            return 0, idiomas.t("checkout_elegi_direccion_corta")
        return self.COSTO_ENVIO_DOMICILIO, self.app.formatear_precio(self.COSTO_ENVIO_DOMICILIO, self.producto["moneda"])

    def _calcular_precio_unitario(self):
        precio = self.producto["precio"]
        if self.oferta and self.oferta["tipo"] == "descuento" and self.oferta.get("valor"):
            return precio * (1 - self.oferta["valor"] / 100)
        return precio

    def _calcular_total(self):
        precio_unitario = self._calcular_precio_unitario()
        subtotal = precio_unitario * self.cantidad
        costo_envio, _ = self._info_costo_envio()
        descuento_cupon = self.app.cupones_db.calcular_descuento(self.cupon_aplicado, subtotal) if self.cupon_aplicado else 0
        return max(subtotal + costo_envio - descuento_cupon, 0)

    def _actualizar_total(self):
        self._actualizar_desglose()
        for w in self.frame_total.winfo_children():
            w.destroy()
        bg = colores._CHECKOUT_FONDO_OSCURO
        tk.Label(self.frame_total, text=idiomas.t("checkout_total_final"), bg=bg, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(anchor="w")
        fila_valor = tk.Frame(self.frame_total, bg=bg)
        fila_valor.pack(fill="x", anchor="w", pady=(4, 0))
        total = self._calcular_total()
        tk.Label(fila_valor, text=self.app.formatear_precio(total, self.producto["moneda"]), bg=bg, fg=colores.MARCA_TEAL, font=("Segoe UI", 30, "bold")).pack(side="left")
        tk.Label(fila_valor, text=f" {self.producto['moneda']}", bg=bg, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11, "bold")).pack(side="left", anchor="s", pady=(0, 6))

    def _crear_boton_confirmar(self):
        self.btn_confirmar = ctk.CTkButton(self.col_derecha, text=idiomas.t("checkout_confirmar"), height=48, corner_radius=self.RADIO_CHICO, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 13, "bold"), command=self._confirmar_compra)
        self.btn_confirmar.pack(fill="x")
        tk.Label(self.col_derecha, text=idiomas.t("checkout_confirmar_nota"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 9)).pack(pady=(10, 0))

    # ================= Interacción =================
    def _seleccionar_card(self, tipo, clave):
        if tipo == "entrega":
            if clave == self.entrega_seleccionada:
                return
            self.entrega_seleccionada = clave
            self._actualizar_entrega()
            self._actualizar_card_ubicacion()
        else:
            if clave == self.metodo_pago_seleccionado:
                return
            self.metodo_pago_seleccionado = clave
            self._actualizar_metodo_pago()
        self._actualizar_total()

    def _seleccionar_direccion_envio(self, direccion):
        if self.direccion_envio_elegida and direccion["id"] == self.direccion_envio_elegida["id"]:
            return
        self.direccion_envio_elegida = direccion
        self._actualizar_card_ubicacion()
        self._actualizar_total()

    def _hover_card(self, frame, entrando, borde_normal):
        if not frame.winfo_exists():
            return
        frame.configure(border_color=colores.MARCA_TEAL_HOVER if entrando else borde_normal)

    def _ir_a_nueva_direccion(self):
        self.app.cambiar_vista(self.app.mostrar_nueva_direccion)

    # ================= Confirmación de compra =================
    def _confirmar_compra(self):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("checkout_necesita_login"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        if self.entrega_seleccionada == "envio" and not self.direccion_envio_elegida:
            self.app.mensaje_temporal(idiomas.t("checkout_elegi_direccion_envio"))
            return
        producto_actual = self.app.productos_db.obtener_producto(self.producto_id)
        stock_actual = int(producto_actual["stock"]) if producto_actual and producto_actual["stock"] else 0
        if self.cantidad > stock_actual:
            self.app.mensaje_temporal(idiomas.t("checkout_sin_stock"))
            return
        if not self.app.productos_db.descontar_stock(self.producto_id, self.cantidad):
            self.app.mensaje_temporal(idiomas.t("checkout_error_stock"))
            return
        usuario_id = self.app.auth.obtener_id_por_email(sesion)
        if self.cupon_aplicado:
            self.app.cupones_db.registrar_uso(self.cupon_aplicado["id"], usuario_id)
        numero_orden = f"#DL-{random.randint(1000, 9999)}"
        direccion_envio_texto = self.direccion_envio_elegida["direccion_completa"] if (self.entrega_seleccionada == "envio" and self.direccion_envio_elegida) else None
        self.app.productos_db.registrar_pedido(
            self.producto_id, usuario_id, self.cantidad, self._calcular_precio_unitario(), numero_orden,
            entrega_tipo=self.entrega_seleccionada, direccion_envio=direccion_envio_texto,
        )
        self.app.carrito_de_compra_pedidos.pop(self.producto_id, None)
        self.app.actualizar_carrito_ui()   
        self._mostrar_pantalla_exito(numero_orden)

    def _mostrar_pantalla_exito(self, numero_orden):
        for w in self.contenedor_principal.winfo_children():
            w.destroy()
        tarjeta = ctk.CTkFrame(self.contenedor_principal, corner_radius=self.RADIO_GRANDE, fg_color=colores._CARD, border_width=1, border_color=colores._CARD_BORDE)
        tarjeta.pack(expand=True)
        contenido = tk.Frame(tarjeta, bg=colores._CARD)
        contenido.pack(padx=70, pady=50)
        canvas = tk.Canvas(contenido, width=90, height=90, bg=colores._CARD, highlightthickness=0)
        canvas.pack(pady=(0, 20))
        canvas.create_oval(5, 5, 85, 85, outline=colores.MARCA_TEAL, width=3)
        canvas.create_text(45, 45, text="✓", fill=colores.MARCA_TEAL, font=("Segoe UI", 32, "bold"))
        tk.Label(contenido, text=idiomas.t("checkout_exito_titulo"), bg=colores._CARD, fg=colores.MARCA_TEAL, font=("Segoe UI", 20, "bold")).pack(pady=(0, 6))
        fila_orden = tk.Frame(contenido, bg=colores._CARD)
        fila_orden.pack(pady=(0, 24))
        tk.Label(fila_orden, text=idiomas.t("checkout_numero_orden"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(side="left")
        tk.Label(fila_orden, text=numero_orden, bg=colores.FONDO_PRINCIPAL, fg=colores._TEXTO, font=("Segoe UI", 11, "bold"), padx=8, pady=2).pack(side="left")
        if self.entrega_seleccionada == "envio" and self.direccion_envio_elegida:
            self._panel_exito_envio(contenido)
        else:
            self._panel_exito_retiro(contenido)
        btn = ctk.CTkButton(contenido, text=idiomas.t("checkout_entendido"), corner_radius=self.RADIO_CHICO, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 12, "bold"), command=self._volver_a_inicio)
        btn.pack()

    def _panel_exito_retiro(self, contenido):
        info = ctk.CTkFrame(contenido, corner_radius=self.RADIO_CHICO, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        info.pack(fill="x", pady=(0, 14))
        info_contenido = tk.Frame(info, bg=colores._CHECKOUT_FONDO_OSCURO)
        info_contenido.pack(fill="x", padx=22, pady=18)
        encabezado = tk.Frame(info_contenido, bg=colores._CHECKOUT_FONDO_OSCURO)
        encabezado.pack(fill="x", anchor="w")
        tk.Label(encabezado, text="🏬", bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._CHECKOUT_ICONO_AZUL, font=("Segoe UI Symbol", 12)).pack(side="left", padx=(0, 8))
        tk.Label(encabezado, text=idiomas.t("checkout_retiro_info"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(info_contenido, text=idiomas.t("checkout_sucursal"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 2))
        tk.Label(info_contenido, text=idiomas.t("checkout_direccion", d=self.SEDE_DIRECCION), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.MARCA_TEAL, font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(info_contenido, text=idiomas.t("checkout_horario", h=self.SEDE_HORARIO.replace('Atención presencial: ', '')), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 10))
        tk.Label(info_contenido, text=idiomas.t("checkout_nota_retiro"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 9), wraplength=460, justify="left").pack(anchor="w")

    def _panel_exito_envio(self, contenido):
        dias = random.randint(3, 5)
        direccion = self.direccion_envio_elegida
        info = ctk.CTkFrame(contenido, corner_radius=self.RADIO_CHICO, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        info.pack(fill="x", pady=(0, 14))
        info_contenido = tk.Frame(info, bg=colores._CHECKOUT_FONDO_OSCURO)
        info_contenido.pack(fill="x", padx=22, pady=18)
        encabezado = tk.Frame(info_contenido, bg=colores._CHECKOUT_FONDO_OSCURO)
        encabezado.pack(fill="x", anchor="w")
        tk.Label(encabezado, text="🚚", bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._CHECKOUT_ICONO_AZUL, font=("Segoe UI Symbol", 12)).pack(side="left", padx=(0, 8))
        tk.Label(encabezado, text=idiomas.t("checkout_envio_info"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(info_contenido, text=direccion["etiqueta"], bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 2))
        tk.Label(info_contenido, text=direccion.get("direccion_completa", ""), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.MARCA_TEAL, font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(info_contenido, text=idiomas.t("checkout_llegada_estimada", a=dias, b=dias + 2), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 10))
        tk.Label(info_contenido, text=idiomas.t("checkout_nota_envio"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 9), wraplength=460, justify="left").pack(anchor="w")

    def _volver_a_inicio(self):
        self.app.cambiar_vista(self.app.mostrar_inicio)
        self.app.historial.clear()
        self.app.header.btn_volver.place_forget()

    # ================= Utilidades de imagen =================
    @staticmethod
    def _hex_a_rgb(hex_color):
        h = hex_color.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def _ajustar_imagen(img, w, h, bg=(255, 255, 255)):
        img = img.convert("RGBA")
        r = img.width / img.height
        if r > w / h:
            nw, nh = w, int(w / r)
        else:
            nh, nw = h, int(h * r)
        img = img.resize((nw, nh), Image.LANCZOS)
        fondo = Image.new("RGBA", (w, h), (*bg, 255))
        fondo.paste(img, ((w - nw) // 2, (h - nh) // 2), img)
        return fondo