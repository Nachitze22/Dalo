import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import colores
import idiomas
from componentes.vender.subida_imagenes_vender import ProcesadorImagenVenta
import tempfile


class PasoFotos:
    def __init__(self, parent, wizard):
        self.parent = parent
        self.wizard = wizard
        self.app = wizard.app
        self.procesador = ProcesadorImagenVenta(self.app)
        self._miniaturas_tk = {}
        self.recortando_index = None
        self._rect_recorte = None
        self._crear_ui()

    def validar(self):
        if len(self.wizard.imagenes) < 3:
            return [idiomas.t("paso_fotos_min_3")]
        if self._hay_imagenes_duplicadas():
            return [idiomas.t("paso_fotos_duplicadas")]
        return []

    def _hay_imagenes_duplicadas(self):
        import hashlib
        hashes = []
        for item in self.wizard.imagenes:
            miniatura = item["pil"].convert("RGB").resize((64, 64))
            hashes.append(hashlib.md5(miniatura.tobytes()).hexdigest())
        return len(set(hashes)) < len(hashes)

    def guardar(self):
        pass

    # ================= UI =================
    def _crear_ui(self):
        scroll = ctk.CTkScrollableFrame(self.parent, fg_color=colores._CARD, height=420)
        scroll.pack(fill="both", expand=True)
        tk.Label(scroll, text=idiomas.t("paso_fotos_titulo"), bg=colores._CARD, fg=colores._TEXTO,font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(scroll, text=idiomas.t("paso_fotos_desc"),bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 16))
        self.dropzone = ctk.CTkFrame(scroll, corner_radius=16, fg_color=colores._VENDER_DROPZONE_BG,border_width=2, border_color=colores._VENDER_DROPZONE_BORDE)
        self.dropzone.pack(fill="x", pady=(0, 16))
        interior = tk.Frame(self.dropzone, bg=colores._VENDER_DROPZONE_BG)
        interior.pack(fill="x", padx=24, pady=20)
        tk.Label(interior, text="📸", bg=colores._VENDER_DROPZONE_BG, fg=colores.MARCA_TEAL, font=("Segoe UI Symbol", 28)).pack()
        botones = tk.Frame(interior, bg=colores._VENDER_DROPZONE_BG)
        botones.pack(pady=(10, 0))
        ctk.CTkButton(botones, text=idiomas.t("paso_fotos_subir_archivos"), height=38, corner_radius=10, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 11, "bold"), command=self._elegir_archivos).pack(side="left", padx=(0, 10))
        if self.procesador.camara_disponible():
            ctk.CTkButton(botones, text=idiomas.t("paso_fotos_tomar_foto"), height=38, corner_radius=10,fg_color=colores.BTN_OSCURO, hover_color=colores.BTN_OSCURO_HOVER,font=("Segoe UI", 11, "bold"), command=self._tomar_foto).pack(side="left")
        else:
            tk.Label(botones, text=idiomas.t("paso_fotos_camara_no_disp"),bg=colores._VENDER_DROPZONE_BG, fg=colores.TEXTO_GRIS,font=("Segoe UI", 9, "italic")).pack(side="left", padx=(10, 0))
        self.frame_miniaturas = tk.Frame(scroll, bg=colores._CARD)
        self.frame_miniaturas.pack(fill="x")
        self.frame_recorte = tk.Frame(scroll, bg=colores._CARD)
        self.frame_camara = tk.Frame(scroll, bg=colores._CARD)
        self._camara_activa = None
        self._preview_job = None
        self._render_miniaturas()

    def cerrar(self):
        self._cerrar_preview_camara()

    def _elegir_archivos(self):
        rutas = filedialog.askopenfilenames(title="",
                                             filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")])
        for ruta in rutas:
            self._procesar_nueva_imagen(ruta)

    def _tomar_foto(self):
        if not self.procesador.camara_disponible():
            self.app.mensaje_temporal(idiomas.t("paso_fotos_camara_no_disp"))
            return
        self.app.mensaje_temporal(idiomas.t("paso_fotos_accediendo_camara"))
        def al_abrir(camara):
            if camara is None:
                self.app.mensaje_temporal(idiomas.t("paso_fotos_error_camara"))
                return
            self._abrir_preview_camara(camara)
        self.procesador.abrir_camara(al_abrir)

    def _abrir_preview_camara(self, camara):
        self._camara_activa = camara
        for w in self.frame_camara.winfo_children():
            w.destroy()
        self.frame_recorte.pack_forget()
        self.frame_camara.pack(fill="x", pady=(10, 0))
        tk.Label(self.frame_camara, text=idiomas.t("paso_fotos_encuadra"),
                  bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=(0, 6))
        self.lbl_preview_camara = tk.Label(self.frame_camara, bg=colores._VENDER_THUMB_BG, width=380, height=280)
        self.lbl_preview_camara.pack(anchor="w")
        botones = tk.Frame(self.frame_camara, bg=colores._CARD)
        botones.pack(anchor="w", pady=(10, 0))
        ctk.CTkButton(botones, text=idiomas.t("paso_fotos_capturar"), height=34, corner_radius=8, fg_color=colores.MARCA_TEAL,
                      hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 11, "bold"),
                      command=self._capturar_desde_preview).pack(side="left", padx=(0, 8))
        ctk.CTkButton(botones, text=idiomas.t("paso_fotos_cancelar"), height=34, corner_radius=8, fg_color=colores.BTN_OSCURO,
                      hover_color=colores.BTN_OSCURO_HOVER, font=("Segoe UI", 11, "bold"),
                      command=self._cerrar_preview_camara).pack(side="left")
        self._actualizar_preview_camara()

    def _actualizar_preview_camara(self):
        if self._camara_activa is None or not self.lbl_preview_camara.winfo_exists():
            return
        img = self.procesador.leer_frame(self._camara_activa)
        if img is not None:
            preview = img.copy()
            preview.thumbnail((380, 280))
            foto = ImageTk.PhotoImage(preview)
            self._foto_preview = foto
            self.lbl_preview_camara.configure(image=foto, text="")
        self._preview_job = self.app.ventana_principal.after(40, self._actualizar_preview_camara)

    def _capturar_desde_preview(self):
        if self._camara_activa is None:
            return
        img = self.procesador.leer_frame(self._camara_activa)
        self._cerrar_preview_camara()
        if img is None:
            self.app.mensaje_temporal(idiomas.t("paso_fotos_error_captura"))
            return
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        img.convert("RGB").save(temp.name, format="JPEG", quality=92)
        temp.close()
        self._procesar_nueva_imagen(temp.name)

    def _cerrar_preview_camara(self):
        if self._preview_job is not None:
            self.app.ventana_principal.after_cancel(self._preview_job)
            self._preview_job = None
        self.procesador.cerrar_camara(self._camara_activa)
        self._camara_activa = None
        if self.frame_camara.winfo_exists():
            self.frame_camara.pack_forget()
            for w in self.frame_camara.winfo_children():
                w.destroy()

    def _procesar_nueva_imagen(self, ruta):
        self.app.mensaje_temporal(idiomas.t("paso_fotos_quitando_fondo"))
        def terminar(img):
            if img is None:
                self.app.mensaje_temporal(idiomas.t("paso_fotos_error_procesar"))
                return
            self.wizard.imagenes.append({"pil": img, "principal": len(self.wizard.imagenes) == 0})
            self._render_miniaturas()
        self.procesador.eliminar_fondo(ruta, terminar)

    def _render_miniaturas(self):
        for w in self.frame_miniaturas.winfo_children():
            w.destroy()
        self.frame_recorte.pack_forget()
        if not self.wizard.imagenes:
            tk.Label(self.frame_miniaturas, text=idiomas.t("paso_fotos_sin_imagenes"), bg=colores._CARD,
                      fg=colores.TEXTO_GRIS, font=("Segoe UI", 11, "italic")).pack(anchor="w", pady=20)
            return
        fila = tk.Frame(self.frame_miniaturas, bg=colores._CARD)
        fila.pack(fill="x", pady=10)
        for i, item in enumerate(self.wizard.imagenes):
            self._crear_miniatura(fila, item, i)

    def _crear_miniatura(self, parent, item, index):
        marco = ctk.CTkFrame(parent, corner_radius=14, fg_color=colores._VENDER_THUMB_BG,
                              border_width=2,
                              border_color=colores._VENDER_THUMB_PRINCIPAL if item["principal"] else colores._VENDER_THUMB_BORDE)
        marco.pack(side="left", padx=8)
        interior = tk.Frame(marco, bg=colores._VENDER_THUMB_BG)
        interior.pack(padx=10, pady=10)
        img_mini = item["pil"].copy()
        img_mini.thumbnail((110, 110))
        foto = ImageTk.PhotoImage(img_mini)
        self._miniaturas_tk[index] = foto
        tk.Label(interior, image=foto, bg=colores._VENDER_THUMB_BG).pack()
        if item["principal"]:
            tk.Label(interior, text=idiomas.t("paso_fotos_principal"), bg=colores._VENDER_THUMB_BG, fg=colores._VENDER_THUMB_PRINCIPAL,
                      font=("Segoe UI", 9, "bold")).pack(pady=(4, 0))
        acciones = tk.Frame(interior, bg=colores._VENDER_THUMB_BG)
        acciones.pack(pady=(6, 0))
        for texto, comando in [("⭐", lambda i=index: self._marcar_principal(i)),
                                ("✂", lambda i=index: self._iniciar_recorte(i)),
                                ("◀", lambda i=index: self._mover(i, -1)),
                                ("▶", lambda i=index: self._mover(i, 1)),
                                ("🗑", lambda i=index: self._eliminar(i))]:
            lbl = tk.Label(acciones, text=texto, bg=colores._VENDER_THUMB_BG, fg=colores.TEXTO_GRIS,
                            font=("Segoe UI Symbol", 12), cursor="hand2")
            lbl.pack(side="left", padx=3)
            lbl.bind("<Button-1>", lambda e, c=comando: c())
            lbl.bind("<Enter>", lambda e, l=lbl: l.configure(fg=colores.MARCA_TEAL))
            lbl.bind("<Leave>", lambda e, l=lbl: l.configure(fg=colores.TEXTO_GRIS))

    def _marcar_principal(self, index):
        for i, item in enumerate(self.wizard.imagenes):
            item["principal"] = (i == index)
        self._render_miniaturas()

    def _mover(self, index, delta):
        nuevo = index + delta
        if 0 <= nuevo < len(self.wizard.imagenes):
            self.wizard.imagenes[index], self.wizard.imagenes[nuevo] = self.wizard.imagenes[nuevo], self.wizard.imagenes[index]
            self._render_miniaturas()

    def _eliminar(self, index):
        era_principal = self.wizard.imagenes[index]["principal"]
        self.wizard.imagenes.pop(index)
        if era_principal and self.wizard.imagenes:
            self.wizard.imagenes[0]["principal"] = True
        self._render_miniaturas()

    # ================= Recorte simple =================
    def _iniciar_recorte(self, index):
        self.recortando_index = index
        for w in self.frame_recorte.winfo_children():
            w.destroy()
        self.frame_recorte.pack(fill="x", pady=(10, 0))
        tk.Label(self.frame_recorte, text=idiomas.t("paso_fotos_arrastra_recorte"),
                  bg=colores._CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=(0, 6))
        original = self.wizard.imagenes[index]["pil"]
        self._escala = min(380 / original.width, 380 / original.height, 1)
        ancho_c = int(original.width * self._escala)
        alto_c = int(original.height * self._escala)
        preview = original.copy()
        preview.thumbnail((ancho_c, alto_c))
        self._foto_recorte = ImageTk.PhotoImage(preview)
        self.canvas_recorte = tk.Canvas(self.frame_recorte, width=ancho_c, height=alto_c, bg=colores._VENDER_THUMB_BG, highlightthickness=0)
        self.canvas_recorte.pack(anchor="w")
        self.canvas_recorte.create_image(0, 0, anchor="nw", image=self._foto_recorte)
        self._rect_recorte = None
        self._inicio_drag = None
        self.canvas_recorte.bind("<ButtonPress-1>", self._empezar_drag)
        self.canvas_recorte.bind("<B1-Motion>", self._mover_drag)
        botones = tk.Frame(self.frame_recorte, bg=colores._CARD)
        botones.pack(anchor="w", pady=(10, 0))
        ctk.CTkButton(botones, text=idiomas.t("paso_fotos_aplicar_recorte"), height=34, corner_radius=8, fg_color=colores.MARCA_TEAL,
                      hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 11, "bold"), command=self._aplicar_recorte).pack(side="left", padx=(0, 8))
        ctk.CTkButton(botones, text=idiomas.t("paso_fotos_cancelar"), height=34, corner_radius=8, fg_color=colores.BTN_OSCURO,
                      hover_color=colores.BTN_OSCURO_HOVER, font=("Segoe UI", 11, "bold"),
                      command=lambda: self.frame_recorte.pack_forget()).pack(side="left")

    def _empezar_drag(self, event):
        self._inicio_drag = (event.x, event.y)
        if self._rect_recorte:
            self.canvas_recorte.delete(self._rect_recorte)
            self._rect_recorte = None

    def _mover_drag(self, event):
        if not self._inicio_drag:
            return
        if self._rect_recorte:
            self.canvas_recorte.delete(self._rect_recorte)
        x0, y0 = self._inicio_drag
        self._rect_recorte = self.canvas_recorte.create_rectangle(x0, y0, event.x, event.y, outline=colores.MARCA_TEAL, width=2)

    def _aplicar_recorte(self):
        if not self._rect_recorte or self.recortando_index is None:
            self.app.mensaje_temporal(idiomas.t("paso_fotos_marca_area"))
            return
        coords = self.canvas_recorte.coords(self._rect_recorte)
        x0, y0, x1, y1 = [c / self._escala for c in coords]
        x0, x1 = sorted([x0, x1])
        y0, y1 = sorted([y0, y1])
        original = self.wizard.imagenes[self.recortando_index]["pil"]
        x0, y0 = max(0, int(x0)), max(0, int(y0))
        x1, y1 = min(original.width, int(x1)), min(original.height, int(y1))
        if x1 - x0 < 10 or y1 - y0 < 10:
            self.app.mensaje_temporal(idiomas.t("paso_fotos_area_chica"))
            return
        self.wizard.imagenes[self.recortando_index]["pil"] = original.crop((x0, y0, x1, y1))
        self.frame_recorte.pack_forget()
        self._render_miniaturas()
        self.app.mensaje_temporal(idiomas.t("paso_fotos_recorte_aplicado"))