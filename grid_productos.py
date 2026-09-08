import tkinter as tk
from PIL import Image, ImageTk
import colores
import idiomas
import requests
from io import BytesIO
from componentes.panel_info_producto import PanelInfoProducto

class GridProductos:
    LIMITE_PAGINA = 20
    def __init__(self, parent, app, productos):
        self.parent = parent
        self.app = app
        self.productos = productos 
        self.pos = 0  
        self.indice_mostrado = 0  
        self.variables()
        self.crear_widgets()

    def variables(self):
        self.imagenes_productos = []
        self.ancho_tarjeta = 220
        self.columnas = 5
        self.ancho_ventana = self.app.ventana_principal.winfo_width()
        self.margen_total = 80

    def crear_widgets(self):
        self.contenedor = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor.pack(fill="both", expand=True)
        for col in range(self.columnas):
            self.contenedor.grid_columnconfigure(col, weight=1, uniform="col")
        self.app.ventana_principal.update_idletasks()
        self.frame_paginacion = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.frame_paginacion.pack(fill="x", pady=(10, 24))
        self.cargar_siguiente_pagina()

    # ================= Paginación =================
    def cargar_siguiente_pagina(self):
        siguiente_tanda = self.productos[self.indice_mostrado:self.indice_mostrado + self.LIMITE_PAGINA]
        self.indice_mostrado += len(siguiente_tanda)
        if siguiente_tanda:
            self.tarjetas(siguiente_tanda)
        self._actualizar_paginacion()

    def _actualizar_paginacion(self):
        for w in self.frame_paginacion.winfo_children():
            w.destroy()
        hay_mas = self.indice_mostrado < len(self.productos)
        hubo_paginacion = len(self.productos) > self.LIMITE_PAGINA
        if hay_mas:
            btn = tk.Button(
                self.frame_paginacion,
                text=idiomas.t("grid_ver_mas"),
                command=self.cargar_siguiente_pagina,
                bg=colores.MARCA_TEAL,
                fg="white",
                activebackground=colores.MARCA_TEAL_HOVER,
                activeforeground="white",
                font=("Arial", 12, "bold"),
                relief="flat",
                cursor="hand2",
                padx=24,
                pady=9,
            )
            btn.pack()
            btn.bind("<Enter>", lambda e: btn.configure(bg=colores.MARCA_TEAL_HOVER))
            btn.bind("<Leave>", lambda e: btn.configure(bg=colores.MARCA_TEAL))
        elif hubo_paginacion:
            tk.Label(
                self.frame_paginacion,
                text=idiomas.t("grid_no_hay_mas"),
                bg=colores.FONDO_PRINCIPAL,
                fg=colores.TEXTO_GRIS,
                font=("Arial", 11, "italic"),
            ).pack(pady=8)

    def hover_on(self, e, frame):
        frame.configure(highlightbackground=colores.MARCA_TEAL_HOVER, highlightthickness=4)

    def hover_off(self, e, frame):
        x, y = e.widget.winfo_pointerxy()
        widget = e.widget.winfo_containing(x, y)
        if widget and str(widget).startswith(str(frame)):
            return
        frame.configure(highlightbackground= "white")

    def tarjetas(self, ids_pagina):
        for id_producto in ids_pagina:
            producto = self.app.productos_db.obtener_producto(id_producto)
            if producto is None:
                continue
            nombre = producto["nombre"]
            imagen = producto["imagen"]
            fila = self.pos // self.columnas
            columna = self.pos % self.columnas
            self.pos += 1
            tarjeta = tk.Frame(self.contenedor,bg="white",width=self.ancho_tarjeta,height=340,highlightbackground=colores.BORDE_TARJETA,highlightthickness=5,cursor="hand2")
            tarjeta.grid(row=fila, column=columna, padx=10, pady=20, sticky="n")
            tarjeta.grid_propagate(False)
            tarjeta.bind("<Enter>", lambda e, f=tarjeta: self.hover_on(e, f))
            tarjeta.bind("<Leave>", lambda e, f=tarjeta: self.hover_off(e, f))
            zona_imagen = tk.Frame(tarjeta,bg="white",width=self.ancho_tarjeta,height=230)
            zona_imagen.pack()
            zona_imagen.pack_propagate(False)
            zona_info = tk.Frame(tarjeta,bg="white",width=self.ancho_tarjeta,height=110)
            zona_info.pack()
            zona_info.pack_propagate(False)
            lbl_img = tk.Label(zona_imagen,text=idiomas.t("grid_cargando"),bg="white",fg="gray",font=("Arial", 11))
            lbl_img.place(relx=0.5, rely=0.5, anchor="center")
            self.app.carga_task_iniciada()
            def imagen_lista(img, label=lbl_img):
                try:
                    if not label.winfo_exists():
                        return
                    if img is None:
                        label.configure(text=idiomas.t("grid_sin_imagen"), image="")
                        return
                    img = self.procesar_imagen(img,int(self.ancho_tarjeta * 0.9),int(self.ancho_tarjeta * 0.9))
                    foto = ImageTk.PhotoImage(img)
                    self.imagenes_productos.append(foto)
                    label.configure(image=foto, text="")
                    label.image = foto
                finally:
                    self.app.carga_task_finalizada()
            self.app.obtener_imagen(imagen, callback=imagen_lista)
            def zoom_in(e, label):
                label.configure(pady=5)
            def zoom_out(e, label):
                label.configure(pady=0)
            lbl_img.bind("<Enter>", lambda e, l=lbl_img: zoom_in(e, l))
            lbl_img.bind("<Leave>", lambda e, l=lbl_img: zoom_out(e, l))
            nombre_lbl = tk.Label(zona_info,text=nombre,bg="white",fg="black",font=("Arial", 11, "bold"),wraplength=180,justify="center",height=2)
            nombre_lbl.pack(pady=(5, 0))
            precio = self.app.formatear_precio(producto["precio"],producto["moneda"])
            oferta = self.app.productos_db.obtener_oferta_activa(id_producto)
            if oferta and oferta["tipo"] == "descuento" and oferta.get("valor"):
                descuento = int(oferta["valor"])
                precio_oferta_valor = producto["precio"] * (1 - descuento / 100)
                precio_oferta_fmt = self.app.formatear_precio(precio_oferta_valor, producto["moneda"])
                tk.Label(zona_imagen,text=f" -{descuento}% ",bg=colores._OFERTA_BADGE_BG,fg=colores.TEXTO_BLANCO,font=("Arial", 9, "bold")).place(x=0, y=0)
                tk.Label(zona_info,text=precio,bg="white",fg=colores._OFERTA_PRECIO_TACHADO,font=("Arial", 9, "overstrike")).pack(pady=(4, 0))
                precio_lbl = tk.Label(zona_info,text=precio_oferta_fmt,bg="white",fg=colores.MARCA_TEAL_HOVER,font=("Arial", 12, "bold"))
                precio_lbl.pack()
            elif oferta:
                etiquetas_cortas = {"2x1": "2x1", "medio_pago": "Desc.", "cuotas": "Cuotas"}
                texto_tag = etiquetas_cortas.get(oferta["tipo"], "Oferta")
                tk.Label(zona_imagen,text=f" {texto_tag} ",bg=colores._OFERTA_TAG_BG,fg=colores.TEXTO_BLANCO,font=("Arial", 9, "bold")).place(x=0, y=0)
                precio_lbl = tk.Label(zona_info,text=precio,bg="white",fg=colores.MARCA_TEAL_HOVER,font=("Arial", 12, "bold"))
                precio_lbl.pack(pady=(4, 0))
            else:
                precio_lbl = tk.Label(zona_info,text=precio,bg="white",fg=colores.MARCA_TEAL_HOVER,font=("Arial", 12, "bold"))
                precio_lbl.pack(pady=(4, 0))
            en_deseos_inicial = id_producto in self.app.lista_de_deseos_lista
            corazon = tk.Label(zona_info,text="❤️" if en_deseos_inicial else "🤍",font=("Arial", 15),bg="white",fg="red" if en_deseos_inicial else "black",cursor="hand2")
            corazon.place(x=155, y=62 if en_deseos_inicial else 60)
            carrito = tk.Label(zona_info,text="🛒",font=("Arial", 15),bg="white",cursor="hand2")
            carrito.place(x=185, y=60)
            def toggle_deseo(event, producto_id=id_producto, icono=corazon):
                sesion = self.app.auth.cargar_sesion()
                if not sesion:
                    self.app.mensaje_temporal(idiomas.t("grid_necesita_login_deseos"))
                    self.app.cambiar_vista(self.app.vista_login)
                    return
                usuario_id = self.app.auth.obtener_id_por_email(sesion)
                ahora_en_deseos = self.app.productos_db.toggle_deseo(usuario_id, producto_id)
                if ahora_en_deseos:
                    if producto_id not in self.app.lista_de_deseos_lista:
                        self.app.lista_de_deseos_lista.append(producto_id)
                    icono.config(text="❤️", fg="red")
                    icono.place_configure(y=62)
                    self.app.mensaje_temporal(idiomas.t("grid_agregado_deseos"))
                else:
                    if producto_id in self.app.lista_de_deseos_lista:
                        self.app.lista_de_deseos_lista.remove(producto_id)
                    icono.config(text="🤍", fg="black")
                    icono.place_configure(y=60)
                    self.app.mensaje_temporal(idiomas.t("grid_eliminado_deseos"))
                self.app.actualizar_deseos_ui()
            corazon.bind("<Button-1>", toggle_deseo)
            def agregar_carrito(event, producto_id=id_producto, icono=carrito):
                if not self.app.auth.cargar_sesion():
                    self.app.mensaje_temporal(idiomas.t("grid_necesita_login_carrito"))
                    self.app.cambiar_vista(self.app.vista_login)
                    return
                if producto_id not in self.app.carrito_de_compra_pedidos:
                    self.app.carrito_de_compra_pedidos[producto_id] = 1
                    icono.place_configure(y=62)
                    self.app.mensaje_temporal(idiomas.t("grid_agregado_carrito"))
                else:
                    self.app.carrito_de_compra_pedidos.pop(producto_id, None)
                    icono.place_configure(y=60)
                    self.app.mensaje_temporal(idiomas.t("grid_eliminado_carrito"))
                self.app.actualizar_carrito_ui()
            carrito.bind("<Button-1>", agregar_carrito)
            def abrir_producto(event, producto_id=id_producto):
                self.app.cambiar_vista(lambda: self.app.mostrar_producto(producto_id))
            tarjeta.bind("<Button-1>", abrir_producto)
            lbl_img.bind("<Button-1>", abrir_producto)

    def procesar_imagen(self, img, ancho_max, alto_max):
        img = img.convert("RGBA")
        img_ratio = img.width / img.height
        box_ratio = ancho_max / alto_max
        if img_ratio > box_ratio:
            nuevo_ancho = ancho_max
            nuevo_alto = int(ancho_max / img_ratio)
        else:
            nuevo_alto = alto_max
            nuevo_ancho = int(alto_max * img_ratio)
        img = img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
        fondo = Image.new("RGBA", (ancho_max, alto_max), (255, 255, 255, 255))
        x = (ancho_max - nuevo_ancho) // 2
        y = (alto_max - nuevo_alto) // 2
        fondo.paste(img, (x, y), img)
        return fondo