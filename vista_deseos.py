import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import colores
import idiomas


class VistaDeseos:
    RADIO_GRANDE = 20
    RADIO_MEDIO = 16
    RADIO_CHICO = 14
    COLUMNAS = 3
    ALTO_TARJETA = 430

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
            self._crear_grid(items)

    def _crear_header(self):
        fila = tk.Frame(self.pad, bg=colores._CARD_IMG)
        fila.pack(fill="x", pady=(0, 26))
        col_titulo = tk.Frame(fila, bg=colores._CARD_IMG)
        col_titulo.pack(side="left")
        tk.Label(col_titulo, text=idiomas.t("deseos_titulo"), bg=colores._CARD_IMG, fg=colores._TEXTO, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        cantidad_items = len(self.app.lista_de_deseos_lista)
        if cantidad_items:
            subtitulo = idiomas.t("deseos_subtitulo_items", n=cantidad_items, s="s" if cantidad_items != 1 else "", s2="s" if cantidad_items != 1 else "")
        else:
            subtitulo = idiomas.t("deseos_subtitulo_vacio")
        tk.Label(col_titulo, text=subtitulo, bg=colores._CARD_IMG, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(anchor="w")
        if cantidad_items:
            btn_vaciar = tk.Label(fila, text=idiomas.t("deseos_vaciar"), bg=colores._CARD, fg=colores._CARRITO_ELIMINAR, font=("Segoe UI", 11, "bold"), cursor="hand2")
            btn_vaciar.pack(side="right", anchor="e", pady=(10, 0))
            btn_vaciar.bind("<Button-1>", lambda e: self._vaciar_lista())
            btn_vaciar.bind("<Enter>", lambda e: btn_vaciar.configure(fg=colores._CARRITO_ELIMINAR_HOVER))
            btn_vaciar.bind("<Leave>", lambda e: btn_vaciar.configure(fg=colores._CARRITO_ELIMINAR))
        tk.Frame(self.pad, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(0, 26))

    def _crear_estado_vacio(self):
        contenedor = tk.Frame(self.pad, bg=colores._CARD)
        contenedor.pack(expand=True, pady=60)
        tk.Label(contenedor, text="🤍", bg=colores._CARD, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 60)).pack()
        tk.Label(contenedor, text=idiomas.t("deseos_vacio_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 18, "bold")).pack(pady=(16, 6))
        tk.Label(contenedor, text=idiomas.t("deseos_vacio_desc"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(pady=(0, 24))
        ctk.CTkButton(contenedor, text=idiomas.t("carrito_explorar"), corner_radius=self.RADIO_CHICO, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 13, "bold"), height=42, command=self._ir_a_inicio).pack()

    # ================= Datos =================
    def _obtener_items(self):
        items = []
        for producto_id in list(self.app.lista_de_deseos_lista):
            producto = self.app.productos_db.obtener_producto(producto_id)
            if not producto:
                self._remover_id_local(producto_id)
                continue
            oferta = self.app.productos_db.obtener_oferta_activa(producto_id)
            items.append({"producto": producto, "oferta": oferta})
        return items

    # ================= Grid =================
    def _crear_grid(self, items):
        grid = tk.Frame(self.pad, bg=colores._CARD)
        grid.pack(fill="both", expand=True)
        for col in range(self.COLUMNAS):
            grid.grid_columnconfigure(col, weight=1, uniform="deseos")
        for i, item in enumerate(items):
            fila, columna = divmod(i, self.COLUMNAS)
            tarjeta = self._crear_tarjeta(grid, item)
            tarjeta.grid(row=fila, column=columna, padx=12, pady=12, sticky="nsew")

    def _crear_tarjeta(self, parent, item):
        producto = item["producto"]
        producto_id = producto["id"]
        bg = colores._DESEOS_ITEM_BG

        tarjeta = ctk.CTkFrame(parent, corner_radius=self.RADIO_MEDIO, fg_color=bg, border_width=1, border_color=colores._DESEOS_ITEM_BORDE, height=self.ALTO_TARJETA)
        tarjeta.grid_propagate(False)

        contenido = tk.Frame(tarjeta, bg=bg)
        contenido.pack(fill="both", expand=True, padx=18, pady=18)

        fila_sup = tk.Frame(contenido, bg=bg)
        fila_sup.pack(fill="x")
        btn_eliminar = tk.Label(fila_sup, text="🗑", bg=bg, fg=colores._CARRITO_ELIMINAR, font=("Segoe UI Symbol", 14), cursor="hand2")
        btn_eliminar.pack(side="right")
        btn_eliminar.bind("<Button-1>", lambda e, pid=producto_id: self._eliminar_item(pid))
        btn_eliminar.bind("<Enter>", lambda e: btn_eliminar.configure(fg=colores._CARRITO_ELIMINAR_HOVER))
        btn_eliminar.bind("<Leave>", lambda e: btn_eliminar.configure(fg=colores._CARRITO_ELIMINAR))

        lbl_img = tk.Label(contenido, bg=colores._IMG_FONDO, width=140, height=140, cursor="hand2", highlightbackground=colores.BORDE_TARJETA, highlightthickness=2)
        lbl_img.pack(pady=(0, 12))
        lbl_img.bind("<Button-1>", lambda e, pid=producto_id: self._abrir_producto(pid))
        self._cargar_imagen_item(lbl_img, producto.get("imagen"))

        tk.Label(contenido, text=(producto.get("categoria") or "GENERAL").upper(), bg=bg, fg=colores.MARCA_TEAL, font=("Segoe UI", 9, "bold")).pack(anchor="w")

        nombre_lbl = tk.Label(contenido, text=producto["nombre"], bg=bg, fg=colores._TEXTO, font=("Segoe UI", 13, "bold"), wraplength=190, justify="left", anchor="nw", height=2, cursor="hand2")
        nombre_lbl.pack(anchor="w", fill="x", pady=(4, 8))
        nombre_lbl.bind("<Button-1>", lambda e, pid=producto_id: self._abrir_producto(pid))
        contenido.bind("<Configure>", lambda e, lbl=nombre_lbl: lbl.configure(wraplength=max(e.width - 4, 60)))

        frame_precio = tk.Frame(contenido, bg=bg, height=54)
        frame_precio.pack_propagate(False)
        frame_precio.pack(fill="x", anchor="w")
        self._precio_item(frame_precio, producto, item["oferta"])

        stock = int(producto["stock"]) if producto["stock"] else 0
        frame_stock = tk.Frame(contenido, bg=bg, height=22)
        frame_stock.pack_propagate(False)
        frame_stock.pack(fill="x", anchor="w", pady=(6, 12))
        if stock <= 0:
            tk.Label(frame_stock, text=idiomas.t("deseos_sin_stock"), bg=bg, fg=colores._ROJO_STOCK, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        elif stock <= 5:
            tk.Label(frame_stock, text=idiomas.t("deseos_ultimas_unidades", n=stock), bg=bg, fg=colores._NARANJA_STOCK, font=("Segoe UI", 10, "bold")).pack(anchor="w")

        ctk.CTkButton(
            contenido,
            text=idiomas.t("deseos_agregar_carrito") if stock > 0 else idiomas.t("deseos_sin_stock"),
            corner_radius=10, height=36,
            fg_color=colores.MARCA_TEAL if stock > 0 else "#4a4a4a",
            hover_color=colores.MARCA_TEAL_HOVER if stock > 0 else "#4a4a4a",
            text_color=colores._TEXTO, font=("Segoe UI", 11, "bold"),
            state="normal" if stock > 0 else "disabled",
            command=(lambda pid=producto_id: self._agregar_carrito(pid)) if stock > 0 else None,
        ).pack(fill="x", side="bottom")

        return tarjeta

    def _precio_item(self, parent, producto, oferta):
        if oferta and oferta["tipo"] == "descuento" and oferta.get("valor"):
            descuento = int(oferta["valor"])
            precio_oferta = producto["precio"] * (1 - descuento / 100)
            fila = tk.Frame(parent, bg=colores._DESEOS_ITEM_BG)
            fila.pack(anchor="w")
            tk.Label(fila, text=self.app.formatear_precio(producto["precio"], producto["moneda"]), bg=colores._DESEOS_ITEM_BG, fg=colores._OFERTA_PRECIO_TACHADO, font=("Segoe UI", 10, "overstrike")).pack(side="left")
            tk.Label(fila, text=f"  -{descuento}%", bg=colores._DESEOS_ITEM_BG, fg=colores._OFERTA_BADGE_BG, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(6, 0))
            tk.Label(parent, text=self.app.formatear_precio(precio_oferta, producto["moneda"]), bg=colores._DESEOS_ITEM_BG, fg=colores.MARCA_TEAL, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(2, 0))
        else:
            tk.Label(parent, text=self.app.formatear_precio(producto["precio"], producto["moneda"]), bg=colores._DESEOS_ITEM_BG, fg=colores.MARCA_TEAL, font=("Segoe UI", 15, "bold")).pack(anchor="w")

    # ================= Interacción =================
    def _eliminar_item(self, producto_id):
        sesion = self.app.auth.cargar_sesion()
        usuario_id = self.app.auth.obtener_id_por_email(sesion) if sesion else None
        if usuario_id:
            self.app.productos_db.quitar_de_deseos(usuario_id, producto_id)
        self._remover_id_local(producto_id)
        self.app.mensaje_temporal(idiomas.t("deseos_eliminado"))
        self.app.actualizar_deseos_ui()
        self.construir()

    def _remover_id_local(self, producto_id):
        if producto_id in self.app.lista_de_deseos_lista:
            self.app.lista_de_deseos_lista.remove(producto_id)

    def _vaciar_lista(self):
        sesion = self.app.auth.cargar_sesion()
        usuario_id = self.app.auth.obtener_id_por_email(sesion) if sesion else None
        if usuario_id:
            for producto_id in list(self.app.lista_de_deseos_lista):
                self.app.productos_db.quitar_de_deseos(usuario_id, producto_id)
        self.app.lista_de_deseos_lista.clear()
        self.app.mensaje_temporal(idiomas.t("deseos_vaciada"))
        self.app.actualizar_deseos_ui()
        self.construir()

    def _agregar_carrito(self, producto_id):
        if producto_id not in self.app.carrito_de_compra_pedidos:
            self.app.carrito_de_compra_pedidos[producto_id] = 1
            self.app.mensaje_temporal(idiomas.t("deseos_agregado_carrito"))
        else:
            self.app.mensaje_temporal(idiomas.t("deseos_ya_en_carrito"))
        self.app.actualizar_carrito_ui()

    def _abrir_producto(self, producto_id):
        self.app.cambiar_vista(lambda: self.app.mostrar_producto(producto_id))

    def _ir_a_inicio(self):
        self.app.cambiar_vista(self.app.mostrar_inicio)

    # ================= Imagen =================
    def _cargar_imagen_item(self, label, url):
        if not url:
            return
        def terminar(img):
            if img is None or not label.winfo_exists():
                return
            img = self._ajustar_imagen(img, 140, 140, bg=self._hex_a_rgb(colores._IMG_FONDO))
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