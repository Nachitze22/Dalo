import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import colores
import idiomas

class VistaCarrito:
    RADIO_GRANDE = 20
    RADIO_MEDIO = 16
    RADIO_CHICO = 14

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self._imagenes = {}
        self.contenedor_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor_principal.pack(fill="both", expand=True, padx=50, pady=36)
        self.card = ctk.CTkFrame(self.contenedor_principal, corner_radius=self.RADIO_GRANDE, fg_color=colores._CARD, border_width=1, border_color=colores._CARD_BORDE)
        self.card.pack(fill="both", expand=True)
        self.pad = tk.Frame(self.card, bg=colores._CARD)
        self.pad.pack(fill="both", expand=True, padx=40, pady=40)
        self.construir()

    # ================= Construcción =================
    def construir(self):
        for w in self.pad.winfo_children():
            w.destroy()
        self._crear_header()
        items = self._obtener_items()
        if not items:
            self._crear_estado_vacio()
        else:
            self._crear_cuerpo(items)

    def _crear_header(self):
        fila = tk.Frame(self.pad, bg=colores._CARD)
        fila.pack(fill="x", pady=(0, 26))
        col_titulo = tk.Frame(fila, bg=colores._CARD)
        col_titulo.pack(side="left")
        tk.Label(col_titulo, text=idiomas.t("carrito_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        cantidad_items = len(self.app.carrito_de_compra_pedidos)
        subtitulo = idiomas.t("carrito_subtitulo_items", n=cantidad_items, s="s" if cantidad_items != 1 else "") if cantidad_items else idiomas.t("carrito_subtitulo_vacio")
        tk.Label(col_titulo, text=subtitulo, bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(anchor="w", pady=(4, 0))
        if cantidad_items:
            btn_vaciar = tk.Label(fila, text=idiomas.t("carrito_vaciar"), bg=colores._CARD, fg=colores._CARRITO_ELIMINAR, font=("Segoe UI", 11, "bold"), cursor="hand2")
            btn_vaciar.pack(side="right", anchor="e", pady=(10, 0))
            btn_vaciar.bind("<Button-1>", lambda e: self._vaciar_carrito())
            btn_vaciar.bind("<Enter>", lambda e: btn_vaciar.configure(fg=colores._CARRITO_ELIMINAR_HOVER))
            btn_vaciar.bind("<Leave>", lambda e: btn_vaciar.configure(fg=colores._CARRITO_ELIMINAR))
        tk.Frame(self.pad, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(0, 26))

    def _crear_estado_vacio(self):
        contenedor = tk.Frame(self.pad, bg=colores._CARD)
        contenedor.pack(expand=True, pady=60)
        tk.Label(contenedor, text="🛒", bg=colores._CARD, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 60)).pack()
        tk.Label(contenedor, text=idiomas.t("carrito_vacio_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 18, "bold")).pack(pady=(16, 6))
        tk.Label(contenedor, text=idiomas.t("carrito_vacio_desc"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(pady=(0, 24))
        ctk.CTkButton(contenedor, text=idiomas.t("carrito_explorar"), corner_radius=self.RADIO_CHICO, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 13, "bold"), height=42, command=self._ir_a_inicio).pack()

    # ================= Datos =================
    def _obtener_items(self):
        items = []
        for producto_id, cantidad in list(self.app.carrito_de_compra_pedidos.items()):
            producto = self.app.productos_db.obtener_producto(producto_id)
            if not producto:
                self.app.carrito_de_compra_pedidos.pop(producto_id, None)
                continue
            stock = int(producto["stock"]) if producto["stock"] else 0
            if stock <= 0:
                self.app.carrito_de_compra_pedidos.pop(producto_id, None)
                self.app.actualizar_carrito_ui()
                continue
            if cantidad > stock:
                cantidad = stock
                self.app.carrito_de_compra_pedidos[producto_id] = cantidad
            oferta = self.app.productos_db.obtener_oferta_activa(producto_id)
            precio_unitario = self._precio_unitario(producto, oferta)
            items.append({
                "producto": producto,
                "cantidad": cantidad,
                "oferta": oferta,
                "precio_unitario": precio_unitario,
                "subtotal": precio_unitario * cantidad,
            })
        return items

    def _precio_unitario(self, producto, oferta):
        precio = producto["precio"]
        if oferta and oferta["tipo"] == "descuento" and oferta.get("valor"):
            return precio * (1 - oferta["valor"] / 100)
        return precio

    # ================= Cuerpo (dos columnas) =================
    def _crear_cuerpo(self, items):
        cuerpo = tk.Frame(self.pad, bg=colores._CARD)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(0, weight=65)
        cuerpo.grid_columnconfigure(1, weight=0)
        cuerpo.grid_columnconfigure(2, weight=35)
        cuerpo.grid_rowconfigure(0, weight=1)
        col_izq = tk.Frame(cuerpo, bg=colores._CARD)
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 30))
        tk.Frame(cuerpo, bg=colores._SEPARADOR, width=1).grid(row=0, column=1, sticky="ns", pady=4)
        panel_derecha = ctk.CTkFrame(cuerpo, corner_radius=self.RADIO_MEDIO + 2, fg_color=colores._CHECKOUT_FONDO_OSCURO, border_width=1, border_color=colores._CHECKOUT_BORDE_SUAVE)
        panel_derecha.grid(row=0, column=2, sticky="nsew", padx=(30, 0))
        col_der = tk.Frame(panel_derecha, bg=colores._CHECKOUT_FONDO_OSCURO)
        col_der.pack(fill="both", expand=True, padx=26, pady=26)
        for item in items:
            self._crear_item_carrito(col_izq, item)
        self._crear_resumen(col_der, items)

    # ----- Tarjeta de producto -----
    def _crear_item_carrito(self, parent, item):
        producto = item["producto"]
        producto_id = producto["id"]
        tarjeta = ctk.CTkFrame(parent, corner_radius=self.RADIO_MEDIO, fg_color=colores._CARRITO_ITEM_BG, border_width=1, border_color=colores._CARRITO_ITEM_BORDE)
        tarjeta.pack(fill="x", pady=(0, 16))
        contenido = tk.Frame(tarjeta, bg=colores._CARRITO_ITEM_BG)
        contenido.pack(fill="x", padx=20, pady=18)

        lbl_img = tk.Label(contenido, bg=colores._IMG_FONDO, width=90, height=90)
        lbl_img.pack(side="left", padx=(0, 18))
        self._cargar_imagen_item(lbl_img, producto.get("imagen"))

        lateral = tk.Frame(contenido, bg=colores._CARRITO_ITEM_BG)
        lateral.pack(side="right", fill="y")
        btn_eliminar = tk.Label(lateral, text="🗑", bg=colores._CARRITO_ITEM_BG, fg=colores._CARRITO_ELIMINAR, font=("Segoe UI Symbol", 16), cursor="hand2")
        btn_eliminar.pack(anchor="ne")
        btn_eliminar.bind("<Button-1>", lambda e, pid=producto_id: self._eliminar_item(pid))
        btn_eliminar.bind("<Enter>", lambda e: btn_eliminar.configure(fg=colores._CARRITO_ELIMINAR_HOVER))
        btn_eliminar.bind("<Leave>", lambda e: btn_eliminar.configure(fg=colores._CARRITO_ELIMINAR))
        tk.Label(lateral, text=self.app.formatear_precio(item["subtotal"], producto["moneda"]), bg=colores._CARRITO_ITEM_BG, fg=colores.MARCA_TEAL, font=("Segoe UI", 14, "bold")).pack(anchor="se", pady=(30, 0))

        info = tk.Frame(contenido, bg=colores._CARRITO_ITEM_BG)
        info.pack(side="left", fill="both", expand=True)
        tk.Label(info, text=producto["nombre"], bg=colores._CARRITO_ITEM_BG, fg=colores._TEXTO, font=("Segoe UI", 14, "bold"), wraplength=320, justify="left", anchor="w").pack(anchor="w")
        tk.Label(info, text=(producto.get("categoria") or "GENERAL").upper(), bg=colores._CARRITO_ITEM_BG, fg=colores.MARCA_TEAL, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4, 8))
        self._precio_item(info, producto, item)

        fila_controles = tk.Frame(info, bg=colores._CARRITO_ITEM_BG)
        fila_controles.pack(fill="x", anchor="w", pady=(12, 0))
        self._stepper_cantidad(fila_controles, producto, item)
        ctk.CTkButton(fila_controles, text=idiomas.t("carrito_comprar_item"), corner_radius=10, height=32, fg_color=colores._BTN_COMPRAR, hover_color=colores._BTN_COMPRAR_H, font=("Segoe UI", 11, "bold"), command=lambda pid=producto_id, cant=item["cantidad"]: self._comprar_item(pid, cant)).pack(side="left", padx=(16, 0))

    def _precio_item(self, parent, producto, item):
        oferta = item["oferta"]
        if oferta and oferta["tipo"] == "descuento" and oferta.get("valor"):
            fila = tk.Frame(parent, bg=colores._CARRITO_ITEM_BG)
            fila.pack(anchor="w")
            precio_original = self.app.formatear_precio(producto["precio"], producto["moneda"])
            tk.Label(fila, text=precio_original, bg=colores._CARRITO_ITEM_BG, fg=colores._OFERTA_PRECIO_TACHADO, font=("Segoe UI", 10, "overstrike")).pack(side="left")
            tk.Label(fila, text=f"  -{int(oferta['valor'])}%", bg=colores._CARRITO_ITEM_BG, fg=colores._OFERTA_BADGE_BG, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(6, 0))
        precio_unitario_fmt = self.app.formatear_precio(item["precio_unitario"], producto["moneda"])
        tk.Label(parent, text=f"{precio_unitario_fmt} {idiomas.t('carrito_cu')}", bg=colores._CARRITO_ITEM_BG, fg=colores._TEXTO, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(2, 0))

    def _stepper_cantidad(self, parent, producto, item):
        producto_id = producto["id"]
        stock = int(producto["stock"]) if producto["stock"] else 0
        ctrl = tk.Frame(parent, bg=colores.FONDO_PRINCIPAL, highlightbackground=colores._CARD_BORDE, highlightthickness=1)
        ctrl.pack(side="left")
        btn_menos = tk.Label(ctrl, text="−", bg=colores.FONDO_PRINCIPAL, fg=colores._TEXTO, font=("Segoe UI", 13, "bold"), width=3, cursor="hand2")
        btn_menos.pack(side="left")
        tk.Label(ctrl, text=str(item["cantidad"]), bg=colores.FONDO_PRINCIPAL, fg=colores._TEXTO, font=("Segoe UI", 12, "bold"), width=3).pack(side="left")
        btn_mas = tk.Label(ctrl, text="+", bg=colores.FONDO_PRINCIPAL, fg=colores._TEXTO, font=("Segoe UI", 13, "bold"), width=3, cursor="hand2")
        btn_mas.pack(side="left")
        btn_menos.bind("<Button-1>", lambda e: self._cambiar_cantidad(producto_id, -1, stock))
        btn_mas.bind("<Button-1>", lambda e: self._cambiar_cantidad(producto_id, 1, stock))
        for w in (btn_menos, btn_mas):
            w.bind("<Enter>", lambda e, ww=w: ww.configure(fg=colores.MARCA_TEAL))
            w.bind("<Leave>", lambda e, ww=w: ww.configure(fg=colores._TEXTO))

    # ----- Resumen -----
    def _crear_resumen(self, parent, items):
        tk.Label(parent, text=idiomas.t("carrito_resumen"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores._TEXTO, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 20))
        subtotal_bruto = sum(i["producto"]["precio"] * i["cantidad"] for i in items)
        subtotal_final = sum(i["subtotal"] for i in items)
        descuento_total = subtotal_bruto - subtotal_final
        moneda = items[0]["producto"]["moneda"]
        self._fila_resumen(parent, idiomas.t("carrito_productos_n", n=len(items)), self.app.formatear_precio(subtotal_bruto, moneda), colores._TEXTO)
        if descuento_total > 0:
            self._fila_resumen(parent, idiomas.t("carrito_descuentos"), f"-{self.app.formatear_precio(descuento_total, moneda)}", colores._OFERTA_BANNER_TEXTO)
        tk.Frame(parent, bg=colores._CHECKOUT_BORDE_SUAVE, height=1).pack(fill="x", pady=14)
        tk.Label(parent, text=idiomas.t("carrito_total_estimado"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(anchor="w")
        fila_total = tk.Frame(parent, bg=colores._CHECKOUT_FONDO_OSCURO)
        fila_total.pack(fill="x", anchor="w", pady=(4, 18))
        tk.Label(fila_total, text=self.app.formatear_precio(subtotal_final, moneda), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.MARCA_TEAL, font=("Segoe UI", 26, "bold")).pack(side="left")
        tk.Label(fila_total, text=f" {moneda}", bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11, "bold")).pack(side="left", anchor="s", pady=(0, 4))
        tk.Label(parent, text=idiomas.t("carrito_info_envio"), bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 9), wraplength=260, justify="left").pack(anchor="w", pady=(0, 18))
        ctk.CTkButton(parent, text=idiomas.t("carrito_seguir_comprando"), corner_radius=self.RADIO_CHICO, fg_color=colores.BTN_OSCURO, hover_color=colores.BTN_OSCURO_HOVER, font=("Segoe UI", 12, "bold"), height=42, command=self._ir_a_inicio).pack(fill="x")

    def _fila_resumen(self, parent, etiqueta, valor, color_valor):
        fila = tk.Frame(parent, bg=colores._CHECKOUT_FONDO_OSCURO)
        fila.pack(fill="x", pady=4)
        tk.Label(fila, text=etiqueta, bg=colores._CHECKOUT_FONDO_OSCURO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(side="left")
        tk.Label(fila, text=valor, bg=colores._CHECKOUT_FONDO_OSCURO, fg=color_valor, font=("Segoe UI", 11, "bold")).pack(side="right")

    # ================= Interacción =================
    def _cambiar_cantidad(self, producto_id, delta, stock_max):
        actual = self.app.carrito_de_compra_pedidos.get(producto_id, 1)
        nueva = actual + delta
        if nueva < 1:
            return
        if stock_max and nueva > stock_max:
            self.app.mensaje_temporal(idiomas.t("carrito_sin_stock_suficiente"))
            return
        self.app.carrito_de_compra_pedidos[producto_id] = nueva
        self.app.actualizar_carrito_ui()
        self.construir()

    def _eliminar_item(self, producto_id):
        self.app.carrito_de_compra_pedidos.pop(producto_id, None)
        self.app.mensaje_temporal(idiomas.t("carrito_eliminado"))
        self.app.actualizar_carrito_ui()
        self.construir()

    def _vaciar_carrito(self):
        self.app.carrito_de_compra_pedidos.clear()
        self.app.mensaje_temporal(idiomas.t("carrito_vaciado"))
        self.app.actualizar_carrito_ui()
        self.construir()

    def _comprar_item(self, producto_id, cantidad):
        self.app.cambiar_vista(lambda: self.app.mostrar_comprar(producto_id, cantidad))

    def _ir_a_inicio(self):
        self.app.cambiar_vista(self.app.mostrar_inicio)

    # ================= Imagen =================
    def _cargar_imagen_item(self, label, url):
        if not url:
            return
        def terminar(img):
            if img is None or not label.winfo_exists():
                return
            img = self._ajustar_imagen(img, 90, 90, bg=self._hex_a_rgb(colores._IMG_FONDO))
            foto = ImageTk.PhotoImage(img)
            self._imagenes[id(label)] = foto
            label.configure(image=foto, text="")
        self.app.obtener_imagen(url, callback=terminar)

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