import tkinter as tk
import customtkinter as ctk
import colores
import variables_globales
import idiomas
from PIL import Image, ImageTk

class PanelInfoProducto:
    def __init__(self, parent, vista_producto):
        self.parent = parent
        self.vista = vista_producto
        self.app = vista_producto.app
        self.producto = vista_producto.producto
        self._detalle = None
        self.crear()

    def crear(self):
        self.col = ctk.CTkFrame(self.parent, fg_color=colores._CARD, corner_radius=22)
        self.col.pack(side="left", fill="both", expand=True)
        self.pad = ctk.CTkFrame(self.col, fg_color=colores._CARD, corner_radius=0)
        self.pad.pack(fill="both", expand=True, padx=36, pady=30)
        p = self.producto
        stock = int(p["stock"]) if p["stock"] else 0
        self.oferta = self.app.productos_db.obtener_oferta_activa(p["id"])
        self._enc(p)
        self._rating_vendedor(p)
        self._precio(p, stock)
        self._oferta_compacta()
        self._entrega_info()
        self._cantidad(stock)
        self._botones(stock)
        
    def _enc(self, p):
        fila_meta = ctk.CTkFrame(self.pad, fg_color="transparent")
        fila_meta.pack(anchor="w", pady=(0, 10))
        badge = ctk.CTkFrame(fila_meta, fg_color=colores._BADGE_BG, corner_radius=14)
        badge.pack(side="left")
        ctk.CTkLabel(badge, text=f"  {(p['categoria'] or 'GENERAL').upper()}  ", fg_color="transparent", text_color=colores.MARCA_TEAL, font=("Segoe UI", 13, "bold"), corner_radius=20).pack(ipadx=4, ipady=3)
        meta_texto = idiomas.t("prod_publicado_recientemente")
        vendidos = p.get("vendidos") or 0
        ctk.CTkLabel(fila_meta, text=meta_texto, fg_color="transparent", text_color=colores.TEXTO_GRIS, font=("Segoe UI", 13)).pack(side="left", padx=(12, 0))
        if vendidos > 0:
            vendidos_texto = idiomas.t("prod_vendidos", n=vendidos)
            ctk.CTkLabel(fila_meta, text=vendidos_texto, fg_color="transparent", text_color=colores.MARCA_TEAL, font=("Segoe UI", 13)).pack(side="left", padx=(12, 0))
        ctk.CTkLabel(self.pad, text=p["nombre"], fg_color="transparent", text_color=colores._TEXTO, font=("Segoe UI", 30, "bold"), wraplength=480, justify="left").pack(anchor="w", pady=10)
    def _rating_vendedor(self, p):
        resumen = self.app.productos_db.obtener_resumen_calificacion(p["id"])
        total = resumen["total"]
        calificacion_redondeada = round(p["calificacion"]) if p["calificacion"] else 0
        fila = ctk.CTkFrame(self.pad, fg_color="transparent")
        fila.pack(anchor="w", pady=(2, 12))
        estrellas = "★" * calificacion_redondeada + "☆" * (5 - calificacion_redondeada)
        ctk.CTkLabel(fila, text=estrellas, fg_color="transparent", text_color="yellow", font=("Segoe UI Symbol", 18)).pack(side="left")
        texto_opiniones = idiomas.t("prod_opinion_1", n=total) if total == 1 else idiomas.t("prod_opinion_n", n=total)
        ctk.CTkLabel(fila, text=f"  {texto_opiniones}", fg_color="transparent", text_color=colores.TEXTO_GRIS, font=("Segoe UI", 14)).pack(side="left")
        ctk.CTkLabel(fila, text="   |   ", fg_color="transparent", text_color=colores.TEXTO_GRIS, font=("Segoe UI", 14)).pack(side="left")
        vendedor = self.app.productos_db.obtener_vendedor_producto(p["id"])
        nombre_vendedor = vendedor["nombre_visible"] if vendedor else "Dalo Oficial S.R.L."
        vendedor_id = p.get("vendedor_id")
        lbl_vendedor = ctk.CTkLabel(
            fila, text=idiomas.t("prod_vendedor", n=nombre_vendedor), fg_color="transparent",
            text_color=colores._RATING_TEXTO, font=("Segoe UI", 14, "bold"),
            cursor="hand2" if vendedor_id else "arrow",
        )
        lbl_vendedor.pack(side="left")
        if vendedor_id:
            lbl_vendedor.bind("<Button-1>", lambda e, vid=vendedor_id: self.app.cambiar_vista(lambda vid=vid: self.app.mostrar_perfil_vendedor(vid)))
            lbl_vendedor.bind("<Enter>", lambda e: lbl_vendedor.configure(text_color=colores.MARCA_TEAL))
            lbl_vendedor.bind("<Leave>", lambda e: lbl_vendedor.configure(text_color=colores._RATING_TEXTO))
        self._div(self.pad)
    def _precio(self, p, stock_val):
        self._detalle = self.app.detalle_oferta(p, self.oferta) if self.oferta else None
        if self._detalle and self._detalle.get("pct"):
            pct = self._detalle["pct"]
            precio_oferta_valor = p["precio"] * (1 - pct / 100)
            precio_original_fmt = self.app.formatear_precio(p["precio"], p["moneda"])
            precio_oferta_fmt = self.app.formatear_precio(precio_oferta_valor, p["moneda"])
            fila_original = ctk.CTkFrame(self.pad, fg_color="transparent")
            fila_original.pack(anchor="w", pady=(0, 2))
            ctk.CTkLabel(fila_original, text=precio_original_fmt, fg_color="transparent", text_color=colores._OFERTA_PRECIO_TACHADO, font=("Segoe UI", 16, "overstrike")).pack(side="left")
            ctk.CTkLabel(fila_original, text=f" {pct}% OFF  ", fg_color=colores._OFERTA_BADGE_BG, text_color=colores.TEXTO_BLANCO, corner_radius=10, font=("Segoe UI", 15, "bold")).pack(side="left", padx=(10, 0))
            fila_precio = ctk.CTkFrame(self.pad, fg_color="transparent")
            fila_precio.pack(anchor="w", pady=(0, 4))
            ctk.CTkLabel(fila_precio, text=precio_oferta_fmt, fg_color="transparent", text_color=colores.MARCA_TEAL, font=("Segoe UI", 35, "bold")).pack(side="left")
            ctk.CTkLabel(fila_precio, text=f" {p['moneda']}", fg_color="transparent", text_color=colores.TEXTO_GRIS, font=("Segoe UI", 15, "bold")).pack(side="left", anchor="s", pady=(0, 8))
            self._precio_final_calculado = precio_oferta_valor
        else:
            precio_fmt = self.app.formatear_precio(p["precio"], p["moneda"])
            fila_precio = ctk.CTkFrame(self.pad, fg_color="transparent")
            fila_precio.pack(anchor="w", pady=(4, 4))
            ctk.CTkLabel(fila_precio, text=precio_fmt, fg_color="transparent", text_color=colores.MARCA_TEAL, font=("Segoe UI", 37, "bold")).pack(side="left")
            ctk.CTkLabel(fila_precio, text=f" {p['moneda']}", fg_color="transparent", text_color=colores.TEXTO_GRIS, font=("Segoe UI", 15, "bold")).pack(side="left", anchor="s", pady=(0, 8))
            self._precio_final_calculado = p["precio"]
        self._div(self.pad)
    def _oferta_compacta(self):
        detalle = self._detalle
        if not detalle:
            return
        lineas = []
        if detalle.get("es_2x1"):
            lineas.append(idiomas.t("prod_2x1"))
        if detalle.get("medio_pago_texto"):
            lineas.append(f"💳  {detalle['medio_pago_texto']}")
        if detalle.get("cuotas_texto"):
            lineas.append(idiomas.t("prod_cuotas", c=detalle["cuotas_texto"]))
        if detalle.get("extra"):
            lineas.append(detalle["extra"])
        for linea in lineas:
            ctk.CTkLabel(self.pad, text=linea, fg_color="transparent", text_color=colores.MARCA_TEAL, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 4))
        if detalle.get("valido_hasta"):
            fecha_txt = detalle["valido_hasta"].replace("Válido hasta el ", "")
            ctk.CTkLabel(self.pad, text=idiomas.t("prod_valido_hasta", f=fecha_txt), fg_color="transparent", text_color=colores.TEXTO_GRIS, font=("Segoe UI", 13, "italic")).pack(anchor="w", pady=(2, 0))
        if lineas or detalle.get("valido_hasta"):
            self._div(self.pad)
    def _entrega_info(self):
        if variables_globales.ENVIO_GRATIS_HABILITADO:
            banner = ctk.CTkFrame(self.pad, fg_color=colores._ENVIO_GRATIS_BG, border_width=1, border_color=colores._ENVIO_GRATIS_BORDE, corner_radius=12)
            banner.pack(anchor="w", fill="x", pady=(0, 16))
            ctk.CTkLabel(banner, text=idiomas.t("prod_envio_gratis"), fg_color="transparent", text_color=colores._ENVIO_GRATIS_TEXTO, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=10)
            return
        box = ctk.CTkFrame(self.pad, fg_color=colores._ENTREGA_BOX_BG, border_width=1, border_color=colores._ENTREGA_BOX_BORDE, corner_radius=12)
        box.pack(fill="x", pady=(0, 16))
        inner = ctk.CTkFrame(box, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)
        encabezado = ctk.CTkFrame(inner, fg_color="transparent")
        encabezado.pack(anchor="w")
        ctk.CTkLabel(encabezado, text="📍", fg_color="transparent", text_color=colores._ENTREGA_ICONO_TITULO, font=("Segoe UI Symbol", 14)).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(encabezado, text=idiomas.t("prod_metodo_entrega"), fg_color="transparent", text_color=colores.MARCA_TEAL, font=("Segoe UI", 13, "bold")).pack(side="left")
        fila_direccion = ctk.CTkFrame(inner, fg_color="transparent")
        fila_direccion.pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(fila_direccion, text=idiomas.t("prod_retiro_gratis"), fg_color="transparent", text_color=colores._TEXTO, font=("Segoe UI", 14)).pack(side="left")
        ctk.CTkLabel(fila_direccion, text=variables_globales.SEDE_DIRECCION, fg_color="transparent", text_color=colores._TEXTO, font=("Segoe UI", 14, "bold"), wraplength=380, justify="left").pack(side="left")
        ctk.CTkLabel(inner, text=idiomas.t("prod_envio_proximamente"), fg_color="transparent", text_color=colores._ENTREGA_SUBTEXTO, font=("Segoe UI", 9, "italic"), wraplength=440, justify="left").pack(anchor="w")
    def _cantidad(self, stock_max):
        fila = ctk.CTkFrame(self.pad, fg_color="transparent")
        fila.pack(anchor="w", pady=20)
        ctk.CTkLabel(fila, text=idiomas.t("prod_cantidad"), fg_color="transparent", text_color=colores.TEXTO_GRIS, font=("Segoe UI", 13)).pack(side="left", padx=(0, 14))
        ctrl = ctk.CTkFrame(fila, fg_color=colores.FONDO_PRINCIPAL, border_width=1, border_color=colores._CARD_BORDE, corner_radius=12)
        ctrl.pack(side="left")
        self.btn_menos = self._btn_c(ctrl, "−", lambda: self._delta(-1, stock_max))
        self.btn_menos.pack(side="left")
        ctk.CTkFrame(ctrl, fg_color=colores._CARD_BORDE, width=1, height=34, corner_radius=0).pack(side="left")
        self.lbl_cant = ctk.CTkLabel(ctrl, text="1", fg_color="transparent", text_color=colores._TEXTO, font=("Segoe UI", 15, "bold"), width=36)
        self.lbl_cant.pack(side="left", padx=10, pady=5)
        ctk.CTkFrame(ctrl, fg_color=colores._CARD_BORDE, width=1, height=34, corner_radius=0).pack(side="left")
        self.btn_mas = self._btn_c(ctrl, "+", lambda: self._delta(1, stock_max))
        self.btn_mas.pack(side="left")
        if stock_max == 0:
            stock_txt = idiomas.t("prod_sin_stock")
            stock_color = colores._ROJO_STOCK
        elif stock_max == 1:
            stock_txt = idiomas.t("prod_ultima_unidad")
            stock_color = colores._ROJO_STOCK
        elif stock_max <= 3:
            stock_txt = idiomas.t("prod_quedan_n", n=stock_max)
            stock_color = colores._ROJO_STOCK
        elif stock_max <= 10:
            stock_txt = idiomas.t("prod_stock_limitado", n=stock_max)
            stock_color = colores._NARANJA_STOCK
        elif stock_max <= 30:
            stock_txt = idiomas.t("prod_en_stock", n=stock_max)
            stock_color = colores._VERDE_STOCK
        else:
            stock_txt = idiomas.t("prod_disponible")
            stock_color = colores._VERDE_STOCK
        self.lbl_stock_cantidad = ctk.CTkLabel(fila, text=stock_txt, fg_color="transparent", text_color=stock_color, font=("Segoe UI", 12))
        self.lbl_stock_cantidad.pack(side="left", padx=(16, 0))
    def _btn_c(self, parent, txt, cmd):
        return ctk.CTkButton(parent, text=txt, width=42, height=38, corner_radius=0, fg_color=colores.FONDO_PRINCIPAL, hover_color=colores.MARCA_TEAL_HOVER, text_color=colores._TEXTO, font=("Segoe UI", 18, "bold"), border_width=0, command=cmd)
    def _delta(self, d, stock_max):
        nueva = self.vista.cantidad + d
        if nueva < 1:
            return
        if nueva > stock_max:
            self.app.mensaje_temporal(idiomas.t("prod_no_stock_suficiente"))
            return
        self.vista.cantidad = nueva
        self.lbl_cant.configure(text=str(nueva))
    def _botones(self, stock_val):
        fila = ctk.CTkFrame(self.pad, fg_color="transparent")
        fila.pack(anchor="w", pady=20)
        self.btn_comprar = self._btn_accion(fila, texto=idiomas.t("prod_comprar_ahora"), fg=colores._BTN_COMPRAR, hover=colores._BTN_COMPRAR_H, press="#1F618D", cmd=self._comprar_ahora, activo=stock_val > 0)
        self.btn_comprar.pack(side="left", padx=(0, 10))
        self.btn_carrito = self._btn_accion(fila, texto=self._txt_carrito(), fg=colores.MARCA_TEAL if stock_val > 0 else "#4a4a4a", hover=colores.MARCA_TEAL_HOVER, press=colores.MARCA_TEAL_PRESS, cmd=self._toggle_carrito, activo=stock_val > 0)
        self.btn_carrito.pack(side="left", padx=(0, 10))
        self.btn_deseos = self._btn_accion(fila, texto=self._txt_deseos(), fg=colores.BTN_OSCURO, hover=colores.BTN_OSCURO_HOVER, press="#1a1a1a", cmd=self._toggle_deseos)
        self.btn_deseos.pack(side="left")
    def _btn_accion(self, parent, texto, fg, hover, press, cmd, activo=True):
        b = ctk.CTkButton(parent, text=texto, fg_color=fg, hover_color=hover if activo else fg, text_color=colores._TEXTO, font=("Segoe UI", 17, "bold"), corner_radius=10, height=44, border_width=0, cursor="hand2" if activo else "arrow", state="normal" if activo else "disabled", command=cmd if activo else None)
        if activo:
            b.bind("<ButtonPress-1>", lambda e: b.configure(fg_color=press))
            b.bind("<ButtonRelease-1>", lambda e: b.configure(fg_color=hover))
        return b
    def _comprar_ahora(self):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("prod_necesita_login_comprar"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        stock_actual = int(self.producto["stock"]) if self.producto["stock"] else 0
        if stock_actual <= 0:
            self.app.mensaje_temporal(idiomas.t("prod_sin_stock_disponible"))
            return
        if self.vista.cantidad > stock_actual:
            self.app.mensaje_temporal(idiomas.t("prod_no_stock_suficiente"))
            return
        producto_id = self.producto["id"]
        cantidad = self.vista.cantidad
        self.app.cambiar_vista(lambda: self.app.mostrar_comprar(producto_id, cantidad))
    def _toggle_carrito(self):
        if not self.app.auth.cargar_sesion():
            self.app.mensaje_temporal(idiomas.t("prod_necesita_login_carrito"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        producto_id = self.producto["id"]
        if producto_id not in self.vista.app.carrito_de_compra_pedidos:
            self.app.carrito_de_compra_pedidos[producto_id] = self.vista.cantidad
            self.vista.en_carrito = True
            self.vista.app.mensaje_temporal(idiomas.t("prod_agregado_carrito"))
        else:
            self.app.carrito_de_compra_pedidos.pop(producto_id, None)
            self.vista.en_carrito = False
            self.vista.app.mensaje_temporal(idiomas.t("prod_eliminado_carrito"))
        self.app.actualizar_carrito_ui()
        self.btn_carrito.configure(text=self._txt_carrito())
    def _toggle_deseos(self):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("prod_necesita_login_deseos"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        usuario_id = self.app.auth.obtener_id_por_email(sesion)
        producto_id = self.producto["id"]
        ahora_en_deseos = self.app.productos_db.toggle_deseo(usuario_id, producto_id)
        if ahora_en_deseos:
            if producto_id not in self.app.lista_de_deseos_lista:
                self.app.lista_de_deseos_lista.append(producto_id)
            self.vista.en_deseos = True
            self.vista.app.mensaje_temporal(idiomas.t("prod_agregado_deseos"))
        else:
            if producto_id in self.app.lista_de_deseos_lista:
                self.app.lista_de_deseos_lista.remove(producto_id)
            self.vista.en_deseos = False
            self.app.mensaje_temporal(idiomas.t("prod_eliminado_deseos"))
        self.app.actualizar_deseos_ui()
        self.btn_deseos.configure(text=self._txt_deseos())
    def _txt_carrito(self):
        return idiomas.t("prod_en_carrito") if self.vista.en_carrito else idiomas.t("prod_agregar_carrito")
    def _txt_deseos(self):
        return idiomas.t("prod_en_deseos") if self.vista.en_deseos else idiomas.t("prod_lista_deseos")
    def _div(self, parent):
        ctk.CTkFrame(parent, fg_color=colores._SEPARADOR, height=1, corner_radius=0).pack(fill="x", pady=8)