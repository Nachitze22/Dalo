import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import colores
import idiomas
from componentes.panel_info_producto import PanelInfoProducto   
from componentes.opiniones_producto import OpinionesProducto   

class VistaProducto:
    def __init__(self, parent, app, producto_id):
        self.parent   = parent
        self.app      = app
        self.producto_id = producto_id
        self.producto = self.app.productos_db.obtener_producto(producto_id)
        self.cantidad = 1
        self.en_carrito = producto_id in self.app.carrito_de_compra_pedidos
        self.en_deseos  = producto_id in self.app.lista_de_deseos_lista
        self._img_principal = None
        self._imgs_thumb    = []
        self.indice_inicio = 0
        self.labels_thumb = []
        self.marcos_thumb = []
        self.indice_actual = 0
        self.obtener_datos()
        self.crear_widgets()

    def obtener_datos(self):
        self.imagenes = self.app.productos_db.obtener_imagenes(self.producto["id"])
        if not self.imagenes:
            self.imagenes = [self.producto["imagen"]]
        while len(self.imagenes) < 3:
            self.imagenes.append(self.imagenes[0])
        if len(set(self.imagenes)) > 1:
            self.imagenes.append(self.imagenes[0])

    def crear_widgets(self):
        contenedor_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        contenedor_principal.pack(fill="both", expand=True, padx=50, pady=36)
        self.card = tk.Frame(contenedor_principal,bg=colores._CARD, highlightbackground=colores._CARD_BORDE, highlightthickness=1)
        self.card.pack(fill="both", expand=True)
        self.fila_superior = tk.Frame(self.card, bg=colores._CARD)
        self.fila_superior.pack(fill="both", expand=True)
        self._col_imagen(self.fila_superior)
        tk.Frame(self.fila_superior, bg=colores._SEPARADOR, width=1).pack(side="left", fill="y", pady=24)
        PanelInfoProducto(self.fila_superior, self)
        self._descripcion_y_ficha()
        OpinionesProducto(contenedor_principal, self) 

    def _descripcion_y_ficha(self):
        contenedor = tk.Frame(self.card, bg=colores._CARD)
        contenedor.pack(fill="x", padx=36, pady=(0, 30))
        tk.Frame(contenedor, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(0, 20))
        fila = tk.Frame(contenedor, bg=colores._CARD)
        fila.pack(fill="x")
        col_desc = tk.Frame(fila, bg=colores._CARD)
        col_desc.pack(side="left", fill="both", expand=True, padx=(0, 30))
        self._descripcion_completa(col_desc)
        tk.Frame(fila, bg=colores._SEPARADOR, width=1).pack(side="left", fill="y", padx=(0, 30))
        self._ficha_tecnica(fila)

    def _descripcion_completa(self, parent):
        limite = 260
        descripcion = self.producto["descripcion"] or idiomas.t("prod_sin_descripcion")
        tk.Label(parent,text=idiomas.t("prod_descripcion_titulo"),bg=colores._CARD, fg=colores.TEXTO_GRIS,font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))
        self._descripcion_expandida = False
        self.lbl_descripcion = tk.Label(parent,bg=colores._CARD, fg=colores._TEXTO,font=("Segoe UI", 13),wraplength=680, justify="left")
        self.lbl_descripcion.pack(anchor="w")
        if len(descripcion) > limite:
            texto_corto = descripcion[:limite].rstrip() + "..."
            self.lbl_descripcion.configure(text=texto_corto)
            self.btn_leer_mas = tk.Label(parent,text=idiomas.t("prod_leer_mas"),bg=colores._CARD, fg=colores.MARCA_TEAL,font=("Segoe UI", 12, "bold"),cursor="hand2")
            self.btn_leer_mas.pack(anchor="w", pady=(10, 0))
            def toggle(event=None):
                self._descripcion_expandida = not self._descripcion_expandida
                if self._descripcion_expandida:
                    self.lbl_descripcion.configure(text=descripcion)
                    self.btn_leer_mas.configure(text=idiomas.t("prod_leer_menos"))
                else:
                    self.lbl_descripcion.configure(text=texto_corto)
                    self.btn_leer_mas.configure(text=idiomas.t("prod_leer_mas"))
            self.btn_leer_mas.bind("<Button-1>", toggle)
            self.btn_leer_mas.bind("<Enter>", lambda e: self.btn_leer_mas.configure(fg=colores.MARCA_TEAL_HOVER))
            self.btn_leer_mas.bind("<Leave>", lambda e: self.btn_leer_mas.configure(fg=colores.MARCA_TEAL))
        else:
            self.lbl_descripcion.configure(text=descripcion)

    def _ficha_tecnica(self, parent):
        p = self.producto
        panel = tk.Frame(parent, bg=colores._CARD_IMG, width=230)
        panel.pack(side="left", anchor="n")
        tk.Label(panel,text=idiomas.t("prod_ficha_tecnica"),bg=colores._CARD_IMG, fg=colores.MARCA_TEAL,font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 12))
        fecha = (str(p["fecha_creacion"]).split(" ")[0] if p["fecha_creacion"] and p["fecha_creacion"] != "—" else "—")
        datos = [
            (idiomas.t("prod_marca"), p.get("marca") or idiomas.t("prod_no_especificado")),
            (idiomas.t("prod_categoria"), (p["categoria"] or "—").capitalize()),
            (idiomas.t("prod_publicado"), fecha),
            (idiomas.t("prod_garantia"), p.get("garantia") or idiomas.t("prod_no_especificado")),
        ]
        for etiq, val in datos:
            tk.Label(panel, text=etiq,bg=colores._CARD_IMG, fg=colores._FICHA_ETIQUETA,font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))
            tk.Label(panel, text=val,bg=colores._CARD_IMG, fg=colores._TEXTO,font=("Segoe UI", 11, "bold"),wraplength=210, justify="left").pack(anchor="w", pady=(0, 2))
            tk.Frame(panel, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(6, 0))
        panel.update_idletasks()
        panel.configure(width=230, height=panel.winfo_reqheight())
        panel.pack_propagate(False)

    def _col_imagen(self, parent):
        col = tk.Frame(parent, bg=colores._CARD_IMG, width=480)
        col.pack(side="left", fill="y")
        col.pack_propagate(False)
        self.marco_principal = tk.Frame(col,bg=colores._IMG_FONDO_HOVER, borderwidth=3)
        self.marco_principal.pack(padx=30,pady=(30, 14))
        self.lbl_img = tk.Label(self.marco_principal,bg="white")
        self.lbl_img.pack(padx=4,pady=4)
        self._cargar_imagen(370, 370)
        for w in (self.marco_principal, self.lbl_img):
            w.bind("<Enter>", lambda e: self._hover_img(True))
            w.bind("<Leave>", lambda e: self._hover_img(False))
        fila = tk.Frame(col, bg=colores._CARD)
        fila.pack(padx=30, pady=(0,28))
        self.btn_izq = self._crear_flecha(fila,"❮",-1)
        self.btn_izq.pack(side="left",padx=(0,8))
        contenedor = tk.Frame(fila,bg=colores._CARD)
        contenedor.pack(side="left")
        self._miniaturas(contenedor)
        self.btn_der = self._crear_flecha(fila,"❯",1)
        self.btn_der.pack(side="left",padx=(8,0))

    def _hover_img(self, entrando):
        color = colores._IMG_FONDO_HOVER_OSCURO if entrando else colores._IMG_FONDO_HOVER
        self.marco_principal.configure(bg=color)
        self.lbl_img.configure(bg=color)

    def _crear_flecha(self,parent,texto,direccion):
        lbl = tk.Label(parent,text=texto,font=("Segoe UI Symbol",18,"bold"),bg=colores._CARD,fg=colores.TEXTO_GRIS,cursor="hand2",width=2)
        lbl.bind("<Enter>",lambda e: lbl.configure(fg=colores.MARCA_TEAL, bg=colores._IMG_FONDO_HOVER))
        lbl.bind("<Leave>",lambda e: lbl.configure(fg=colores.TEXTO_GRIS,bg=colores._CARD))
        lbl.bind("<Button-1>",lambda e:self.mover_miniaturas(direccion))
        return lbl

    def _cargar_imagen(self, w, h):
        self.lbl_img.configure(text="...", image="")
        def terminar(img):
            if not self.lbl_img.winfo_exists():
                return
            img = self._fit(img,w,h,bg=self._hex_to_rgb(colores._IMG_FONDO))
            self._img_principal = ImageTk.PhotoImage(img)
            self.lbl_img.configure(image=self._img_principal, text="")
            self.lbl_img.image = self._img_principal
        self.app.obtener_imagen(self.imagenes[0],callback=terminar)

    def _miniaturas(self,parent):
        self.marcos_thumb.clear()
        self.labels_thumb.clear()
        for _ in range(3):
            marco = tk.Frame( parent, bg=colores._IMG_FONDO_HOVER, cursor="hand2")
            marco.pack(side="left",padx=6)
            lbl = tk.Label(marco,bg=colores._IMG_FONDO)
            lbl.pack(padx=3,pady=3)
            self.marcos_thumb.append(marco)
            self.labels_thumb.append(lbl)
        self.actualizar_miniaturas()

    def cambiar_imagen(self, imagen, indice):
        self.indice_actual = indice
        self.lbl_img.configure(text="...", image="")
        def terminar(img):
            if not self.lbl_img.winfo_exists():
                return
            img = self._fit(img,370,370,bg=self._hex_to_rgb(colores._IMG_FONDO))
            self._img_principal = ImageTk.PhotoImage(img)
            self.lbl_img.configure(image=self._img_principal, text="")
            self.lbl_img.image = self._img_principal
        self.app.obtener_imagen(imagen,callback=terminar)
        self.actualizar_miniaturas()

    def actualizar_miniaturas(self):
        self._imgs_thumb.clear()
        for i in range(3):
            indice = self.indice_inicio + i
            if indice >= len(self.imagenes):
                continue
            self.labels_thumb[i].configure(text="...", image="")
            if indice == self.indice_actual:
                self.marcos_thumb[i].configure(bg=colores.MARCA_TEAL)
            else:
                self.marcos_thumb[i].configure(bg=colores._IMG_FONDO_HOVER)
            def terminar(img, pos=i):
                if not self.labels_thumb[pos].winfo_exists():
                    return
                img = self._fit(img,60,60,bg=self._hex_to_rgb(colores._IMG_FONDO))
                foto = ImageTk.PhotoImage(img)
                while len(self._imgs_thumb) <= pos:
                    self._imgs_thumb.append(None)
                self._imgs_thumb[pos] = foto
                self.labels_thumb[pos].configure(image=foto,text="")
                self.labels_thumb[pos].image = foto
            self.app.obtener_imagen(self.imagenes[indice],callback=terminar)
            def entrar(e, m=self.marcos_thumb[i]):
                if m["bg"] != colores.MARCA_TEAL:
                    m.configure(bg=colores._IMG_FONDO_HOVER_OSCURO)
            def salir(e, m=self.marcos_thumb[i], ind=indice):
                if ind == self.indice_actual:
                    m.configure(bg=colores.MARCA_TEAL)
                else:
                    m.configure(bg=colores._IMG_FONDO_HOVER)
            for widget in (self.marcos_thumb[i], self.labels_thumb[i]):
                widget.bind("<Enter>", entrar)
                widget.bind("<Leave>", salir)
                widget.bind("<Button-1>",lambda e, img=self.imagenes[indice], ind=indice:self.cambiar_imagen(img, ind))

    def mover_miniaturas(self,direccion):
        imagenes_distintas = len(set(self.imagenes))
        if imagenes_distintas <= 3:
            return
        nuevo = self.indice_inicio + direccion
        if nuevo < 0:
            return
        if nuevo > len(self.imagenes) - 3:
            return
        self.indice_inicio = nuevo
        self.actualizar_miniaturas()

    @staticmethod
    def _hex_to_rgb(hex_color):
        h = hex_color.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _fit(img, W, H, bg=(255, 255, 255)):
        r = img.width / img.height
        if r > W / H:
            nw, nh = W, int(W / r)
        else:
            nh, nw = H, int(H * r)
        img = img.resize((nw, nh), Image.LANCZOS)
        fondo = Image.new("RGBA", (W, H), (*bg, 255))
        fondo.paste(img, ((W - nw) // 2, (H - nh) // 2), img)
        return fondo