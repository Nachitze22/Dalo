import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import colores
import idiomas


class PasoPreview:
    def __init__(self, parent, wizard):
        self.parent = parent
        self.wizard = wizard
        self.app = wizard.app
        self._fotos_tk = []
        self._crear_ui()

    def validar(self):
        return []

    def guardar(self):
        pass

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

    def _crear_ui(self):
        tk.Label(self.parent, text=idiomas.t("paso_preview_titulo"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(self.parent, text=idiomas.t("paso_preview_desc"), bg=colores._CARD,
                  fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 16))

        scroll = ctk.CTkScrollableFrame(self.parent, fg_color=colores._CARD, height=420)
        scroll.pack(fill="both", expand=True)
        fila = tk.Frame(scroll, bg=colores._CARD)
        fila.pack(fill="x")

        bg_imagen = self._hex_a_rgb(colores._IMG_FONDO)

        col_img = tk.Frame(fila, bg=colores._IMG_FONDO, width=280)
        col_img.pack(side="left", fill="y", padx=(0, 24))
        col_img.pack_propagate(False)

        principal = next((i for i in self.wizard.imagenes if i["principal"]), self.wizard.imagenes[0])
        preview_img = self._ajustar_imagen(principal["pil"], 240, 240, bg=bg_imagen)
        foto = ImageTk.PhotoImage(preview_img)
        self._fotos_tk.append(foto)
        tk.Label(col_img, image=foto, bg=colores._IMG_FONDO).pack(pady=(20, 10))

        galeria = tk.Frame(col_img, bg=colores._IMG_FONDO)
        galeria.pack()
        for item in self.wizard.imagenes[:5]:
            mini = self._ajustar_imagen(item["pil"], 44, 44, bg=bg_imagen)
            foto_mini = ImageTk.PhotoImage(mini)
            self._fotos_tk.append(foto_mini)
            tk.Label(galeria, image=foto_mini, bg=colores._IMG_FONDO, highlightbackground=colores.BORDE_TARJETA, highlightthickness=1).pack(side="left", padx=2)

        col_info = tk.Frame(fila, bg=colores._CARD)
        col_info.pack(side="left", fill="both", expand=True)
        d = self.wizard.datos
        tk.Label(col_info, text=(d["categoria"] or "GENERAL").upper(), bg=colores._CARD, fg=colores.MARCA_TEAL,
                  font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(col_info, text=d["titulo"], bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 20, "bold"),
                  wraplength=420, justify="left").pack(anchor="w", pady=(4, 2))
        tk.Label(col_info, text=d["subtitulo"], bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 10))

        precio_final = d.get("precio_oferta") if d.get("tiene_oferta") and d.get("precio_oferta") else d["precio"]
        if d.get("tiene_oferta") and d.get("precio_oferta"):
            tk.Label(col_info, text=self.app.formatear_precio(d["precio"], "ARS"), bg=colores._CARD,
                      fg=colores._OFERTA_PRECIO_TACHADO, font=("Segoe UI", 12, "overstrike")).pack(anchor="w")
        tk.Label(col_info, text=self.app.formatear_precio(precio_final, "ARS"), bg=colores._CARD, fg=colores.MARCA_TEAL,
                  font=("Segoe UI", 26, "bold")).pack(anchor="w", pady=(0, 4))
        if d.get("cuotas_cantidad"):
            interes = idiomas.t("paso_precio_con_interes") if d.get("cuotas_interes") else idiomas.t("paso_precio_sin_interes")
            tk.Label(col_info, text=f"{d['cuotas_cantidad']} · {interes}", bg=colores._CARD, fg=colores.TEXTO_GRIS,
                      font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 10))

        tk.Label(col_info, text=idiomas.t("paso_preview_descripcion_titulo"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 4))
        tk.Label(col_info, text=d["descripcion"][:300] + ("..." if len(d["descripcion"]) > 300 else ""),
                  bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11), wraplength=440, justify="left").pack(anchor="w")

        tk.Label(col_info, text=idiomas.t("paso_preview_ficha_titulo"), bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(14, 4))
        for clave, valor in d.get("ficha_tecnica", {}).items():
            tk.Label(col_info, text=f"{clave}: {valor}", bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 10)).pack(anchor="w")

        nivel = self.app.publicaciones_db.nivel_vendedor(self.app.auth.obtener_id_por_email(self.app.auth.cargar_sesion()))
        tk.Label(col_info, text=idiomas.t("paso_preview_vendido_por", n=nivel['nivel']), bg=colores._CARD, fg=colores._RATING_TEXTO, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(14, 0))

        self._texto_btn = idiomas.t("paso_preview_guardar_cambios") if self.wizard.producto_id_editar else idiomas.t("paso_preview_publicar")
        self.btn_publicar = ctk.CTkButton(self.parent, text=self._texto_btn, height=48, corner_radius=14, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 13, "bold"), command=self._publicar)
        self.btn_publicar.pack(fill="x", pady=(16, 0))

    def _publicar(self):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("paso_preview_necesita_login"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        usuario_id = self.app.auth.obtener_id_por_email(sesion)
        self.btn_publicar.configure(state="disabled", text=idiomas.t("paso_preview_subiendo"))
        imagenes_pil = [item["pil"] for item in self.wizard.imagenes]

        from componentes.vender.subida_imagenes_vender import ProcesadorImagenVenta
        procesador = ProcesadorImagenVenta(self.app)
        identificador = self.wizard.producto_id_editar or usuario_id

        def al_subir(resultados):
            urls = [r["url"] for r in resultados if r]
            if not urls:
                self.app.mensaje_temporal(idiomas.t("paso_preview_error_subida"))
                self.btn_publicar.configure(state="normal", text=self._texto_btn)
                return
            indice_principal = next((i for i, item in enumerate(self.wizard.imagenes) if item["principal"]), 0)
            imagen_principal = urls[indice_principal] if indice_principal < len(urls) else urls[0]
            datos = dict(self.wizard.datos)
            datos["imagenes"] = urls
            datos["imagen_principal"] = imagen_principal
            if self.wizard.producto_id_editar:
                ok = self.app.publicaciones_db.actualizar_publicacion(self.wizard.producto_id_editar, usuario_id, datos)
                mensaje = idiomas.t("paso_preview_actualizado") if ok else idiomas.t("paso_preview_error_guardar")
            else:
                self.app.publicaciones_db.crear_publicacion(usuario_id, datos)
                mensaje = idiomas.t("paso_preview_publicado")
            self.app.mensaje_temporal(mensaje)
            self.app.historial.clear()
            self.app.cambiar_vista(self.app.mostrar_panel_vendedor)

        procesador.subir_imagenes(imagenes_pil, identificador, al_subir)