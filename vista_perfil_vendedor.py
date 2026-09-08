import hashlib
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import colores
import idiomas


class VistaPerfilVendedor:
    RADIO_GRANDE = 20
    RADIO_MEDIO = 16
    RADIO_CHICO = 14

    def __init__(self, parent, app, vendedor_id):
        self.parent = parent
        self.app = app
        self.vendedor_id = vendedor_id
        self._avatar_foto = None
        self.contenedor_principal = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor_principal.pack(fill="both", expand=True, padx=50, pady=36)

        self.vendedor = self.app.auth.obtener_usuario_por_id(vendedor_id)
        if not self.vendedor:
            self._mostrar_no_encontrado()
            return

        self.card = ctk.CTkFrame(self.contenedor_principal, corner_radius=self.RADIO_GRANDE, fg_color=colores._CARD, border_width=1, border_color=colores._CARD_BORDE)
        self.card.pack(fill="both", expand=True)
        self.pad = tk.Frame(self.card, bg=colores._CARD)
        self.pad.pack(fill="both", expand=True, padx=40, pady=36)
        self.construir()

    def _mostrar_no_encontrado(self):
        contenedor = tk.Frame(self.contenedor_principal, bg=colores.FONDO_PRINCIPAL)
        contenedor.pack(expand=True, pady=80)
        tk.Label(contenedor, text="🙁", bg=colores.FONDO_PRINCIPAL, fg=colores._CARRITO_VACIO_ICONO, font=("Segoe UI Symbol", 46)).pack()
        tk.Label(contenedor, text=idiomas.t("perfil_vend_no_encontrado"), bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 14, "bold")).pack(pady=(12, 0))

    # ================= Construcción =================
    def construir(self):
        for w in self.pad.winfo_children():
            w.destroy()
        self._crear_header()
        self._crear_estadisticas()
        tk.Frame(self.pad, bg=colores._SEPARADOR, height=1).pack(fill="x", pady=(24, 20))
        self._crear_publicaciones()

    # ----- Header con avatar -----
    def _crear_header(self):
        fila = tk.Frame(self.pad, bg=colores._CARD)
        fila.pack(fill="x")
        nombre = self.vendedor.get("nombre_visible") or self.vendedor["email"].split("@")[0].capitalize()

        self.avatar_canvas = tk.Canvas(fila, width=80, height=80, bg=colores._CARD, highlightthickness=0)
        self.avatar_canvas.pack(side="left", padx=(0, 22))
        self._dibujar_avatar_inicial(nombre)
        self._cargar_avatar()

        textos = tk.Frame(fila, bg=colores._CARD)
        textos.pack(side="left", anchor="w")
        tk.Label(textos, text=idiomas.t("perfil_vend_titulo"), bg=colores._CARD, fg=colores.MARCA_TEAL, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(textos, text=nombre, bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 26, "bold")).pack(anchor="w", pady=(2, 0))
        nivel = self.app.publicaciones_db.nivel_vendedor(self.vendedor_id)
        tk.Label(textos, text=nivel["nivel"], bg=colores._CARD, fg=colores._VENDER_NIVEL_ORO, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(6, 0))
        fecha = self.vendedor.get("fecha_creacion")
        fecha_txt = str(fecha).split(" ")[0] if fecha else "—"
        tk.Label(textos, text=idiomas.t("perfil_vend_desde", fecha=fecha_txt), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

    def _dibujar_avatar_inicial(self, nombre):
        letra = nombre[0].upper() if nombre else "?"
        self.avatar_canvas.delete("all")
        self.avatar_canvas.create_oval(2, 2, 78, 78, fill=colores._CUENTA_AVATAR_BG, outline="")
        self.avatar_canvas.create_text(40, 41, text=letra, fill=colores._TEXTO, font=("Segoe UI", 26, "bold"))

    def _cargar_avatar(self):
        def mostrar(img):
            if img is None or not self.avatar_canvas.winfo_exists():
                return
            img = img.convert("RGBA").resize((80, 80), Image.LANCZOS)
            mascara = Image.new("L", (80, 80), 0)
            ImageDraw.Draw(mascara).ellipse((0, 0, 80, 80), fill=255)
            img.putalpha(mascara)
            self._avatar_foto = ImageTk.PhotoImage(img)
            self.avatar_canvas.delete("all")
            self.avatar_canvas.create_image(40, 40, image=self._avatar_foto)
            self.avatar_canvas.create_oval(2, 2, 78, 78, outline=colores.MARCA_TEAL, width=2)

        url = self.vendedor.get("foto_perfil")
        if url and str(url).startswith("http"):
            self.app.obtener_imagen(url, callback=mostrar)
            return
        email_hash = hashlib.md5(self.vendedor["email"].strip().lower().encode("utf-8")).hexdigest()
        gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?s=160&d=404"
        self.app.obtener_imagen(gravatar_url, callback=mostrar)

    # ----- Estadísticas -----
    def _crear_estadisticas(self):
        resumen = self.app.productos_db.obtener_resumen_calificacion_vendedor(self.vendedor_id)
        nivel = self.app.publicaciones_db.nivel_vendedor(self.vendedor_id)
        cantidad_activas = len(self.app.publicaciones_db.obtener_publicaciones_vendedor_publicas(self.vendedor_id))
        stats = [
            ("⭐", f"{resumen['promedio']:.1f}" if resumen["total"] else "—", idiomas.t("perfil_vend_calificacion")),
            ("💬", str(resumen["total"]), idiomas.t("perfil_vend_opiniones")),
            ("📦", str(cantidad_activas), idiomas.t("perfil_vend_publicaciones_activas")),
            ("🏅", f"{nivel['reputacion']}%", idiomas.t("perfil_vend_reputacion")),
        ]
        grid = tk.Frame(self.pad, bg=colores._CARD)
        grid.pack(fill="x", pady=(24, 0))
        for i in range(4):
            grid.grid_columnconfigure(i, weight=1, uniform="stats_vendedor")
        for i, (icono, valor, etiqueta) in enumerate(stats):
            box = ctk.CTkFrame(grid, corner_radius=14, fg_color=colores._CUENTA_BTN_FONDO, border_width=1, border_color=colores._CUENTA_CARD_BORDE)
            box.grid(row=0, column=i, sticky="nsew", padx=6)
            contenido = tk.Frame(box, bg=colores._CUENTA_BTN_FONDO)
            contenido.pack(padx=16, pady=16)
            tk.Label(contenido, text=icono, bg=colores._CUENTA_BTN_FONDO, fg=colores.MARCA_TEAL, font=("Segoe UI Symbol", 20)).pack()
            tk.Label(contenido, text=valor, bg=colores._CUENTA_BTN_FONDO, fg=colores._TEXTO, font=("Segoe UI", 18, "bold")).pack(pady=(4, 0))
            tk.Label(contenido, text=etiqueta, bg=colores._CUENTA_BTN_FONDO, fg=colores.TEXTO_GRIS, font=("Segoe UI", 9)).pack()

    # ----- Publicaciones activas -----
    def _crear_publicaciones(self):
        tk.Label(self.pad, text=idiomas.t("perfil_vend_publicaciones_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 12))
        ids = self.app.publicaciones_db.obtener_publicaciones_vendedor_publicas(self.vendedor_id)
        if not ids:
            tk.Label(self.pad, text=idiomas.t("perfil_vend_sin_publicaciones"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(anchor="w", pady=10)
            return
        from componentes.grid_productos import GridProductos
        frame_grid = tk.Frame(self.pad, bg=colores._CARD)
        frame_grid.pack(fill="both", expand=True)
        GridProductos(frame_grid, self.app, ids)