import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import colores
import idiomas


class VistaPanelVendedor:
    RADIO_GRANDE = 20
    RADIO_MEDIO = 16

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self._imagenes = {}
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self._mostrar_requiere_login()
            return
        self.usuario_id = self.app.auth.obtener_id_por_email(sesion)
        self.contenedor_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor_principal.pack(fill="both", expand=True, padx=50, pady=36)
        self.card = ctk.CTkFrame(self.contenedor_principal, corner_radius=self.RADIO_GRANDE, fg_color=colores._CARD,
                                  border_width=1, border_color=colores._CARD_BORDE)
        self.card.pack(fill="both", expand=True)
        self.pad = tk.Frame(self.card, bg=colores._CARD)
        self.pad.pack(fill="both", expand=True, padx=40, pady=34)
        self.construir()

    def _mostrar_requiere_login(self):
        contenedor = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        contenedor.pack(fill="both", expand=True, padx=50, pady=90)
        tk.Label(contenedor, text=idiomas.t("panel_vend_necesita_login"), bg=colores.FONDO_PRINCIPAL,
                  fg=colores._TEXTO, font=("Segoe UI", 16, "bold")).pack()
        ctk.CTkButton(contenedor, text=idiomas.t("panel_vend_iniciar_sesion"), fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER,
                      command=lambda: self.app.cambiar_vista(self.app.vista_login)).pack(pady=16)

    def construir(self):
        for w in self.pad.winfo_children():
            w.destroy()
        self._crear_header()
        publicaciones = self.app.publicaciones_db.obtener_publicaciones_vendedor(self.usuario_id)
        activas = [p for p in publicaciones if p.get("activo", 1)]
        if not activas:
            self._crear_estado_vacio()
        else:
            self._crear_lista(activas)
        self._crear_notificaciones()
        self._crear_preguntas()

    def _crear_header(self):
        fila = tk.Frame(self.pad, bg=colores._CARD)
        fila.pack(fill="x", pady=(0, 10))
        col = tk.Frame(fila, bg=colores._CARD)
        col.pack(side="left")
        nivel = self.app.publicaciones_db.nivel_vendedor(self.usuario_id)
        tk.Label(col, text=idiomas.t("panel_vend_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(col, text=f"{nivel['nivel']}", bg=colores._CARD,
                  fg=colores._VENDER_NIVEL_ORO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(4, 0))
        ctk.CTkButton(fila, text=idiomas.t("panel_vend_nueva_pub"), height=42, corner_radius=12, fg_color=colores.MARCA_TEAL,
                      hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 12, "bold"),
                      command=lambda: self.app.cambiar_vista(self.app.mostrar_vender)).pack(side="right")
        tk.Frame(self.pad, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(16, 20))

    def _crear_estado_vacio(self):
        contenedor = tk.Frame(self.pad, bg=colores._CARD)
        contenedor.pack(expand=True, pady=60)
        tk.Label(contenedor, text="🛍", bg=colores._CARD, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 52)).pack()
        tk.Label(contenedor, text=idiomas.t("panel_vend_sin_productos"), bg=colores._CARD, fg=colores._TEXTO,
                  font=("Segoe UI", 15, "bold")).pack(pady=(16, 6))
        ctk.CTkButton(contenedor, text=idiomas.t("panel_vend_crear_primera"), height=40, corner_radius=12, fg_color=colores.MARCA_TEAL,
                      hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 12, "bold"),
                      command=lambda: self.app.cambiar_vista(self.app.mostrar_vender)).pack()

    def _crear_lista(self, publicaciones):
        for pub in publicaciones:
            self._fila_publicacion(pub)

    def _fila_publicacion(self, pub):
        tarjeta = ctk.CTkFrame(self.pad, corner_radius=self.RADIO_MEDIO, fg_color=colores._CUENTA_PEDIDO_ITEM_BG,
                                border_width=1, border_color=colores._CUENTA_PEDIDO_BORDE, cursor="hand2")
        tarjeta.pack(fill="x", pady=6)
        contenido = tk.Frame(tarjeta, bg=colores._CUENTA_PEDIDO_ITEM_BG)
        contenido.pack(fill="x", padx=20, pady=16)

        lbl_img = tk.Label(contenido, bg=colores._IMG_FONDO, width=64, height=64)
        lbl_img.pack(side="left", padx=(0, 18))
        self._cargar_imagen(lbl_img, pub.get("imagen"))

        info = tk.Frame(contenido, bg=colores._CUENTA_PEDIDO_ITEM_BG)
        info.pack(side="left", fill="both", expand=True)
        fila_titulo = tk.Frame(info, bg=colores._CUENTA_PEDIDO_ITEM_BG)
        fila_titulo.pack(fill="x", anchor="w")
        tk.Label(fila_titulo, text=pub["nombre"], bg=colores._CUENTA_PEDIDO_ITEM_BG, fg=colores._TEXTO,
                  font=("Segoe UI", 13, "bold")).pack(side="left")
        estado = pub.get("estado_publicacion") or "activo"
        bg_badge = colores._VENDER_BADGE_ACTIVO_BG if estado == "activo" else colores._VENDER_BADGE_PAUSADO_BG
        fg_badge = colores._VENDER_BADGE_ACTIVO_TXT if estado == "activo" else colores._VENDER_BADGE_PAUSADO_TXT
        etiqueta_estado = idiomas.t("panel_vend_activo") if estado == "activo" else idiomas.t("panel_vend_pausado")
        tk.Label(fila_titulo, text=f"  {etiqueta_estado}  ", bg=bg_badge, fg=fg_badge,
                  font=("Segoe UI", 9, "bold")).pack(side="left", padx=(10, 0))

        stats = self.app.publicaciones_db.obtener_estadisticas(pub["id"])
        tk.Label(info, text=idiomas.t("panel_vend_stats", v=stats['visitas'], f=stats['favoritos'], s=stats['ventas'], st=pub.get('stock', 0)),
                  bg=colores._CUENTA_PEDIDO_ITEM_BG, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))
        tk.Label(info, text=self.app.formatear_precio(pub["precio"], pub.get("moneda") or "ARS"), bg=colores._CUENTA_PEDIDO_ITEM_BG,
                  fg=colores.MARCA_TEAL, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(4, 0))

        acciones = tk.Frame(contenido, bg=colores._CUENTA_PEDIDO_ITEM_BG)
        acciones.pack(side="right")
        self._boton_accion(acciones, idiomas.t("panel_vend_ver"), lambda: self.app.cambiar_vista(lambda pid=pub["id"]: self.app.mostrar_producto(pid)))
        self._boton_accion(acciones, idiomas.t("panel_vend_editar"), lambda: self.app.cambiar_vista(lambda pid=pub["id"]: self.app.mostrar_vender(pid)))
        if estado == "activo":
            self._boton_accion(acciones, idiomas.t("panel_vend_pausar"), lambda pid=pub["id"]: self._pausar(pid))
        else:
            self._boton_accion(acciones, idiomas.t("panel_vend_activar"), lambda pid=pub["id"]: self._activar(pid))
        self._boton_accion(acciones, idiomas.t("panel_vend_duplicar"), lambda pid=pub["id"]: self._duplicar(pid))
        self._boton_accion(acciones, idiomas.t("panel_vend_eliminar"), lambda pid=pub["id"]: self._eliminar(pid), color=colores._CARRITO_ELIMINAR)

    def _boton_accion(self, parent, texto, comando, color=None):
        lbl = tk.Label(parent, text=texto, bg=colores._CUENTA_PEDIDO_ITEM_BG, fg=color or colores.TEXTO_GRIS,
                        font=("Segoe UI", 10, "bold"), cursor="hand2")
        lbl.pack(side="left", padx=8)
        lbl.bind("<Button-1>", lambda e: comando())
        lbl.bind("<Enter>", lambda e: lbl.configure(fg=colores.MARCA_TEAL))
        lbl.bind("<Leave>", lambda e: lbl.configure(fg=color or colores.TEXTO_GRIS))
        return lbl

    def _pausar(self, producto_id):
        self.app.publicaciones_db.pausar_publicacion(producto_id, self.usuario_id)
        self.app.mensaje_temporal(idiomas.t("panel_vend_pausada"))
        self.construir()

    def _activar(self, producto_id):
        self.app.publicaciones_db.activar_publicacion(producto_id, self.usuario_id)
        self.app.mensaje_temporal(idiomas.t("panel_vend_activada"))
        self.construir()

    def _duplicar(self, producto_id):
        nuevo_id = self.app.publicaciones_db.duplicar_publicacion(producto_id, self.usuario_id)
        if nuevo_id:
            self.app.mensaje_temporal(idiomas.t("panel_vend_duplicada"))
        self.construir()

    def _eliminar(self, producto_id):
        self.app.publicaciones_db.eliminar_publicacion(producto_id, self.usuario_id)
        self.app.mensaje_temporal(idiomas.t("panel_vend_eliminada"))
        self.construir()

    # ================= Notificaciones / Preguntas =================
    def _crear_notificaciones(self):
        notifs = self.app.publicaciones_db.obtener_notificaciones(self.usuario_id, limite=5)
        if not notifs:
            return
        tk.Frame(self.pad, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(20, 14))
        tk.Label(self.pad, text=idiomas.t("panel_vend_notificaciones"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
        for n in notifs:
            fila = tk.Frame(self.pad, bg=colores._CARD)
            fila.pack(fill="x", pady=2, anchor="w")
            if not n["leida"]:
                tk.Label(fila, text="●", bg=colores._CARD, fg=colores._VENDER_NOTIF_PUNTO, font=("Segoe UI", 8)).pack(side="left", padx=(0, 6))
            tk.Label(fila, text=n["mensaje"], bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(side="left")
        self.app.publicaciones_db.marcar_notificaciones_leidas(self.usuario_id)

    def _crear_preguntas(self):
        preguntas = self.app.publicaciones_db.obtener_preguntas_vendedor(self.usuario_id)
        pendientes = [p for p in preguntas if not p.get("respuesta")]
        if not pendientes:
            return
        tk.Frame(self.pad, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(20, 14))
        tk.Label(self.pad, text=idiomas.t("panel_vend_preguntas_titulo"), bg=colores._CARD, fg=colores._TEXTO,
                  font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
        for p in pendientes[:5]:
            fila = tk.Frame(self.pad, bg=colores._CARD)
            fila.pack(fill="x", pady=3, anchor="w")
            tk.Label(fila, text=f'"{p["pregunta"]}"  —  {p["producto_nombre"]}', bg=colores._CARD, fg=colores.TEXTO_GRIS,
                      font=("Segoe UI", 10, "italic")).pack(anchor="w")

    # ================= Imagen =================
    def _cargar_imagen(self, label, url):
        if not url:
            return
        def terminar(img):
            if img is None or not label.winfo_exists():
                return
            img = img.convert("RGBA")
            img.thumbnail((64, 64))
            fondo = Image.new("RGBA", (64, 64), (*self._hex_a_rgb(colores._IMG_FONDO), 255))
            fondo.paste(img, ((64 - img.width) // 2, (64 - img.height) // 2), img)
            foto = ImageTk.PhotoImage(fondo)
            self._imagenes[id(label)] = foto
            label.configure(image=foto, text="")
        self.app.obtener_imagen(url, callback=terminar)

    @staticmethod
    def _hex_a_rgb(hex_color):
        h = hex_color.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))