import tkinter as tk
import customtkinter as ctk
import colores
import idiomas
import phonenumbers

class VistaSeleccionarDireccion:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.seleccion_id = self._id_actual()
        self.crear_widgets()

    def _id_actual(self):
        actual = getattr(self.app, "direccion_envio_seleccionada", None)
        return actual.get("id") if actual else None

    def _provincias(self):
        # Nombres de provincias argentinas; se mantienen en español ya que
        # son nombres propios de lugares reales, independientemente del
        # idioma de la interfaz.
        return [
            "Buenos Aires", "Ciudad Autónoma de Buenos Aires", "Catamarca", "Chaco",
            "Chubut", "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy",
            "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén", "Río Negro",
            "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe",
            "Santiago del Estero", "Tierra del Fuego", "Tucumán",
        ]

    def crear_widgets(self):
        contenedor = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        contenedor.pack(fill="both", expand=True, padx=50, pady=36)
        tk.Label(contenedor, text=idiomas.t("dir_elegir_titulo"), bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 22, "bold")).pack(pady=20)
        self.card = ctk.CTkFrame(contenedor, corner_radius=18, fg_color=colores._DIRECCIONES_MODAL_FONDO, border_width=1, border_color=colores._DIRECCIONES_MODAL_BORDE, width=560)
        self.card.pack()
        self.pad = tk.Frame(self.card, bg=colores._DIRECCIONES_MODAL_FONDO)
        self.pad.pack(padx=30, pady=26)
        self.frame_lista = tk.Frame(self.pad, bg=colores._DIRECCIONES_MODAL_FONDO, width=500)
        self.frame_lista.pack(fill="x")
        self._renderizar_lista()
        botones = tk.Frame(self.pad, bg=colores._DIRECCIONES_MODAL_FONDO)
        botones.pack(fill="x", pady=(20, 0))
        ctk.CTkButton(botones, text=idiomas.t("dir_agregar_nueva"), corner_radius=12, height=42, fg_color="transparent", hover_color=colores._DIRECCIONES_ITEM_BG, border_width=1, border_color=colores._DIRECCIONES_BTN_AGREGAR, text_color=colores._DIRECCIONES_BTN_AGREGAR, font=("Segoe UI", 12, "bold"), command=self._ir_a_nueva_direccion).pack(fill="x", pady=(0, 10))
        ctk.CTkButton(botones, text=idiomas.t("dir_confirmar"), corner_radius=12, height=42, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 13, "bold"), command=self._confirmar).pack(fill="x")

    def _renderizar_lista(self):
        for w in self.frame_lista.winfo_children():
            w.destroy()
        for direccion in self.app.direcciones_guardadas:
            self._crear_fila(direccion)

    def _crear_fila(self, direccion):
        seleccionada = direccion["id"] == self.seleccion_id
        bg = colores._DIRECCIONES_ITEM_BG_SELECCIONADO if seleccionada else colores._DIRECCIONES_ITEM_BG
        borde = colores._DIRECCIONES_ITEM_BORDE_SELECCIONADO if seleccionada else colores._DIRECCIONES_ITEM_BORDE
        tarjeta = ctk.CTkFrame(self.frame_lista, corner_radius=12, fg_color=bg, border_width=2, border_color=borde, cursor="hand2")
        tarjeta.pack(fill="x", pady=6)
        interior = tk.Frame(tarjeta, bg=bg)
        interior.pack(fill="both", expand=True, padx=16, pady=12)
        fila_sup = tk.Frame(interior, bg=bg)
        fila_sup.pack(fill="x", anchor="w")
        radio = tk.Canvas(fila_sup, width=18, height=18, bg=bg, highlightthickness=0)
        radio.pack(side="left", padx=(0, 10))
        color_radio = colores.MARCA_TEAL if seleccionada else colores._CHECKOUT_RADIO_INACTIVO
        radio.create_oval(2, 2, 16, 16, outline=color_radio, width=2)
        if seleccionada:
            radio.create_oval(6, 6, 12, 12, fill=colores.MARCA_TEAL, outline="")
        textos = tk.Frame(fila_sup, bg=bg)
        textos.pack(side="left", fill="x", expand=True)
        tk.Label(textos, text=direccion["etiqueta"], bg=bg, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 13, "bold"), anchor="w").pack(anchor="w")
        subt = f"CP: {direccion['cp']}" if direccion.get("cp") else direccion.get("direccion_completa", "")
        if direccion.get("localidad"):
            subt = f"{subt} - {direccion['localidad']}" if subt else direccion["localidad"]
        tk.Label(textos, text=subt, bg=bg, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10), anchor="w").pack(anchor="w")
        if direccion.get("tipo") == "sede":
            tk.Label(fila_sup, text=idiomas.t("dir_sede_tag"), bg=colores._DIRECCIONES_TAG_BG, fg=colores._DIRECCIONES_TAG_TEXTO, font=("Segoe UI", 8, "bold")).pack(side="right")
        else:
            btn_eliminar = tk.Label(fila_sup, text="🗑", bg=bg, fg=colores._CARRITO_ELIMINAR, font=("Segoe UI Symbol", 12), cursor="hand2")
            btn_eliminar.pack(side="right", padx=(6, 0))
            btn_eliminar.bind("<Enter>", lambda e, b=btn_eliminar: b.configure(fg=colores._CARRITO_ELIMINAR_HOVER))
            btn_eliminar.bind("<Leave>", lambda e, b=btn_eliminar: b.configure(fg=colores._CARRITO_ELIMINAR))
            btn_eliminar.bind("<Button-1>", lambda e, d=direccion: self._eliminar(d["id"]))
            btn_editar = tk.Label(fila_sup, text="✎", bg=bg, fg=colores.TEXTO_GRIS, font=("Segoe UI Symbol", 12), cursor="hand2")
            btn_editar.pack(side="right", padx=(6, 0))
            btn_editar.bind("<Enter>", lambda e, b=btn_editar: b.configure(fg=colores.MARCA_TEAL))
            btn_editar.bind("<Leave>", lambda e, b=btn_editar: b.configure(fg=colores.TEXTO_GRIS))
            btn_editar.bind("<Button-1>", lambda e, d=direccion: self._editar(d["id"]))
        widgets = [tarjeta, interior, fila_sup, radio, textos] + textos.winfo_children()
        for w in widgets:
            w.bind("<Button-1>", lambda e, d=direccion: self._seleccionar(d["id"]))

    def _seleccionar(self, id_direccion):
        self.seleccion_id = id_direccion
        self._renderizar_lista()

    def _eliminar(self, id_direccion):
        sesion = self.app.auth.cargar_sesion()
        usuario_id = self.app.auth.obtener_id_por_email(sesion) if sesion else None
        if self.app.direcciones_db.eliminar_direccion_por_id_combinado(id_direccion, usuario_id):
            self.app.cargar_direcciones()
            self.seleccion_id = self._id_actual()
            self.app.mensaje_temporal(idiomas.t("dir_eliminada"))
            self._renderizar_lista()
        else:
            self.app.mensaje_temporal(idiomas.t("dir_no_se_pudo_eliminar"))

    def _editar(self, id_direccion):
        if not str(id_direccion).startswith("dir_"):
            return
        try:
            direccion_id = int(str(id_direccion).replace("dir_", "", 1))
        except ValueError:
            return
        datos = self.app.direcciones_db.obtener_direccion_por_id(direccion_id)
        if not datos:
            self.app.mensaje_temporal(idiomas.t("dir_no_se_pudo_cargar"))
            return
        self.app.cambiar_vista(lambda: self.app.mostrar_nueva_direccion(datos))

    def _confirmar(self):
        direccion = next((d for d in self.app.direcciones_guardadas if d["id"] == self.seleccion_id), None)
        if not direccion:
            self.app.mensaje_temporal(idiomas.t("dir_elegi_para_continuar"))
            return
        self.app.direccion_envio_seleccionada = direccion
        if hasattr(self.app, "header"):
            self.app.header.actualizar_texto_envio_a()
        self.app.mensaje_temporal(idiomas.t("dir_actualizada"))
        self.app.volver()

    def _ir_a_nueva_direccion(self):
        self.app.cambiar_vista(self.app.mostrar_nueva_direccion)


class VistaNuevaDireccion:
    def __init__(self, parent, app, direccion_editar=None):
        self.parent = parent
        self.app = app
        self.direccion_editar = direccion_editar
        self.datos_pendientes = None
        self.verificando = False
        self.crear_widgets()

    # ================= Construcción =================
    def crear_widgets(self):
        self.contenedor = tk.Frame(self.parent, bg=colores.FONDO_PRINCIPAL)
        self.contenedor.pack(fill="both", expand=True, padx=50, pady=36)
        titulo = idiomas.t("dir_editar_titulo") if self.direccion_editar else idiomas.t("dir_nueva_titulo")
        tk.Label(self.contenedor, text=titulo, bg=colores.FONDO_PRINCIPAL, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 22, "bold")).pack(pady=(0, 20))
        self.frame_formulario = tk.Frame(self.contenedor, bg=colores.FONDO_PRINCIPAL)
        self.frame_formulario.pack(fill="both", expand=True)
        self.frame_confirmacion = tk.Frame(self.contenedor, bg=colores.FONDO_PRINCIPAL)
        self._crear_formulario()

    def _crear_formulario(self):
        self.card = ctk.CTkFrame(self.frame_formulario, corner_radius=18, fg_color=colores._DIRECCION_FORM_CARD, border_width=1, border_color=colores._CARD_BORDE)
        self.card.pack(expand=True)
        self.pad = tk.Frame(self.card, bg=colores._DIRECCION_FORM_CARD)
        self.pad.pack(padx=34, pady=30)
        self._campo_direccion()
        self._campo_no_numero()
        self._campos_provincia_localidad()
        self._campos_cp_departamento()
        self._campo_indicaciones()
        self._datos_receptor()
        self._boton_continuar()
        self._precargar_datos()

    def _campo_direccion(self):
        tk.Label(self.pad, text=idiomas.t("dir_campo_direccion"), bg=colores._DIRECCION_FORM_CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_direccion = ctk.CTkEntry(self.pad, text_color = "white", placeholder_text=idiomas.t("dir_placeholder_direccion"), width=560, height=38, corner_radius=8, fg_color=colores._DIRECCION_FORM_INPUT_BG, border_color=colores._CARD_BORDE)
        self.entry_direccion.pack(anchor="w", pady=(0, 10))

    def _campo_no_numero(self):
        self.sin_numero = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.pad, text=idiomas.t("dir_sin_numero"), variable=self.sin_numero, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, text_color=colores.TEXTO_GRIS, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18).pack(anchor="w", pady=(0, 20))

    def _campos_provincia_localidad(self):
        fila = tk.Frame(self.pad, bg=colores._DIRECCION_FORM_CARD)
        fila.pack(fill="x", pady=(0, 18))
        col1 = tk.Frame(fila, bg=colores._DIRECCION_FORM_CARD)
        col1.pack(side="left", padx=(0, 20))
        tk.Label(col1, text=idiomas.t("dir_provincia"), bg=colores._DIRECCION_FORM_CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.combo_provincia = ctk.CTkOptionMenu(col1, values=VistaSeleccionarDireccion(None, None)._provincias() if False else self._provincias(), width=260, height=38, corner_radius=8, fg_color=colores._DIRECCION_FORM_INPUT_BG, button_color=colores.MARCA_TEAL, button_hover_color=colores.MARCA_TEAL_HOVER)
        self.combo_provincia.set("Buenos Aires")
        self.combo_provincia.pack(anchor="w")
        col2 = tk.Frame(fila, bg=colores._DIRECCION_FORM_CARD)
        col2.pack(side="left")
        tk.Label(col2, text=idiomas.t("dir_localidad"), bg=colores._DIRECCION_FORM_CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_localidad = ctk.CTkEntry(col2, text_color="white", width=260, height=38, corner_radius=8, fg_color=colores._DIRECCION_FORM_INPUT_BG, border_color=colores._CARD_BORDE)
        self.entry_localidad.pack(anchor="w")

    def _provincias(self):
        return [
            "Buenos Aires", "Ciudad Autónoma de Buenos Aires", "Catamarca", "Chaco",
            "Chubut", "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy",
            "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén", "Río Negro",
            "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe",
            "Santiago del Estero", "Tierra del Fuego", "Tucumán",
        ]

    def _campos_cp_departamento(self):
        fila = tk.Frame(self.pad, bg=colores._DIRECCION_FORM_CARD)
        fila.pack(fill="x", pady=(0, 18))
        col1 = tk.Frame(fila, bg=colores._DIRECCION_FORM_CARD)
        col1.pack(side="left", padx=(0, 20))
        tk.Label(col1, text=idiomas.t("dir_codigo_postal"), bg=colores._DIRECCION_FORM_CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_cp = ctk.CTkEntry(col1, text_color="white",placeholder_text=idiomas.t("dir_placeholder_cp"), width=260, height=38, corner_radius=8, fg_color=colores._DIRECCION_FORM_INPUT_BG, border_color=colores._CARD_BORDE)
        self.entry_cp.pack(anchor="w")
        col2 = tk.Frame(fila, bg=colores._DIRECCION_FORM_CARD)
        col2.pack(side="left")
        tk.Label(col2, text=idiomas.t("dir_departamento"), bg=colores._DIRECCION_FORM_CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_depto = ctk.CTkEntry(col2, text_color="white",placeholder_text=idiomas.t("dir_placeholder_depto"), width=260, height=38, corner_radius=8, fg_color=colores._DIRECCION_FORM_INPUT_BG, border_color=colores._CARD_BORDE)
        self.entry_depto.pack(anchor="w")

    def _campo_indicaciones(self):
        tk.Label(self.pad, text=idiomas.t("dir_indicaciones"), bg=colores._DIRECCION_FORM_CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.txt_indicaciones = ctk.CTkTextbox(self.pad, width=560, height=70, corner_radius=8, fg_color=colores._DIRECCION_FORM_INPUT_BG, text_color=colores._TEXTO, font=("Segoe UI", 11))
        self.txt_indicaciones.pack(anchor="w", pady=(0, 20))

    def _datos_receptor(self):
        tk.Label(self.pad, text=idiomas.t("dir_datos_receptor"), bg=colores._DIRECCION_FORM_CARD, fg=colores._TEXTO, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(self.pad, text=idiomas.t("dir_llamaremos"), bg=colores._DIRECCION_FORM_CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 14))
        tk.Label(self.pad, text=idiomas.t("dir_nombre_apellido"), bg=colores._DIRECCION_FORM_CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_nombre = ctk.CTkEntry(self.pad, text_color= "white", width=560, height=38, corner_radius=8, fg_color=colores._DIRECCION_FORM_INPUT_BG, border_color=colores._CARD_BORDE)
        self.entry_nombre.pack(anchor="w", pady=(0, 14))
        tk.Label(self.pad, text=idiomas.t("dir_telefono"), bg=colores._DIRECCION_FORM_CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        self.entry_telefono = ctk.CTkEntry(self.pad, text_color="white",placeholder_text=idiomas.t("dir_placeholder_telefono"), width=560, height=38, corner_radius=8, fg_color=colores._DIRECCION_FORM_INPUT_BG, border_color=colores._CARD_BORDE)
        self.entry_telefono.pack(anchor="w", pady=(0, 20))

    def _boton_continuar(self):
        texto = idiomas.t("dir_guardar_cambios") if self.direccion_editar else idiomas.t("dir_continuar")
        self.btn_continuar = ctk.CTkButton(self.pad, text=texto, corner_radius=10, height=42, width=160, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 13, "bold"), command=self._continuar_a_confirmacion)
        self.btn_continuar.pack(anchor="e")

    def _precargar_datos(self):
        if not self.direccion_editar:
            return
        d = self.direccion_editar
        self.entry_direccion.insert(0, d.get("etiqueta") or "")
        self.entry_localidad.insert(0, d.get("localidad") or "")
        if d.get("provincia"):
            self.combo_provincia.set(d["provincia"])
        self.entry_cp.insert(0, d.get("cp") or "")
        self.entry_depto.insert(0, d.get("departamento") or "")
        if d.get("indicaciones"):
            self.txt_indicaciones.insert("1.0", d["indicaciones"])
        self.entry_nombre.insert(0, d.get("nombre_receptor") or "")
        self.entry_telefono.insert(0, d.get("telefono_receptor") or "")

    # ================= Paso 1 → 2: validar y armar resumen =================
    def _continuar_a_confirmacion(self):
        direccion = self.entry_direccion.get().strip()
        localidad = self.entry_localidad.get().strip()
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        if not direccion:
            self.app.mensaje_temporal(idiomas.t("dir_ingresa_direccion"))
            return
        if not localidad:
            self.app.mensaje_temporal(idiomas.t("dir_ingresa_localidad"))
            return
        if not nombre or not telefono:
            self.app.mensaje_temporal(idiomas.t("dir_completa_datos_receptor"))
            return
        if not self._telefono_valido(telefono):
            self.app.mensaje_temporal(idiomas.t("dir_telefono_invalido"))
            return
        provincia = self.combo_provincia.get()
        self.datos_pendientes = {
            "etiqueta": direccion,
            "direccion_completa": f"{direccion}, {localidad}, {provincia}",
            "cp": self.entry_cp.get().strip(),
            "localidad": localidad,
            "provincia": provincia,
            "departamento": self.entry_depto.get().strip(),
            "indicaciones": self.txt_indicaciones.get("1.0", "end").strip(),
            "nombre_receptor": nombre,
            "telefono_receptor": telefono,
        }
        self._mostrar_confirmacion()

    # ================= Paso 2: confirmación estilo Mercado Libre =================
    def _mostrar_confirmacion(self):
        for w in self.frame_confirmacion.winfo_children():
            w.destroy()
        self.frame_formulario.pack_forget()
        self.frame_confirmacion.pack(fill="both", expand=True)
        d = self.datos_pendientes
        card = ctk.CTkFrame(self.frame_confirmacion, corner_radius=18, fg_color=colores._DIRECCION_CONFIRM_CARD, border_width=1, border_color=colores.MARCA_TEAL)
        card.pack(expand=True)
        pad = tk.Frame(card, bg=colores._DIRECCION_CONFIRM_CARD)
        pad.pack(padx=36, pady=30)
        URL_ICONO_BUSCADOR = "https://res.cloudinary.com/czevmfkz/image/upload/v1785327083/6c26be14-56cc-45ba-b1ee-f3e837359831_ra05ag.png"
        self.app._icono_imagen(pad, URL_ICONO_BUSCADOR, 35, 35, bg=colores._DIRECCION_CONFIRM_CARD).pack()
        tk.Label(pad, text=idiomas.t("dir_confirmar_pregunta"), bg=colores._DIRECCION_CONFIRM_CARD, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 18, "bold")).pack(pady=(0, 4))
        tk.Label(pad, text=idiomas.t("dir_confirmar_desc"), bg=colores._DIRECCION_CONFIRM_CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 11), wraplength=440, justify="center").pack(pady=(0, 20))
        resumen = ctk.CTkFrame(pad, corner_radius=12, fg_color=colores._DIRECCION_FORM_INPUT_BG, border_width=1, border_color=colores._CARD_BORDE)
        resumen.pack(fill="x", pady=(0, 20))
        contenido_resumen = tk.Frame(resumen, bg=colores._DIRECCION_FORM_INPUT_BG)
        contenido_resumen.pack(fill="x", padx=20, pady=16)
        filas = [
            (idiomas.t("dir_resumen_direccion"), d["etiqueta"]),
            (idiomas.t("dir_resumen_localidad"), d["localidad"]),
            (idiomas.t("dir_resumen_provincia"), d["provincia"]),
            (idiomas.t("dir_resumen_cp"), d["cp"] or "—"),
            (idiomas.t("dir_resumen_depto"), d["departamento"] or "—"),
            (idiomas.t("dir_resumen_indicaciones"), d["indicaciones"] or "—"),
            (idiomas.t("dir_resumen_receptor"), f"{d['nombre_receptor']} · {d['telefono_receptor']}"),
        ]
        for etiqueta, valor in filas:
            fila = tk.Frame(contenido_resumen, bg=colores._DIRECCION_FORM_INPUT_BG)
            fila.pack(fill="x", pady=4, anchor="w")
            tk.Label(fila, text=etiqueta, bg=colores._DIRECCION_FORM_INPUT_BG, fg=colores._DIRECCION_CONFIRM_ETIQUETA, font=("Segoe UI", 10, "bold"), width=18, anchor="w").pack(side="left")
            tk.Label(fila, text=valor, bg=colores._DIRECCION_FORM_INPUT_BG, fg=colores.TEXTO_BLANCO, font=("Segoe UI", 11), wraplength=280, justify="left", anchor="w").pack(side="left", fill="x", expand=True)
        self.lbl_estado_verificacion = tk.Label(pad, text="", bg=colores._DIRECCION_CONFIRM_CARD, fg=colores.TEXTO_GRIS, font=("Segoe UI", 10, "italic"))
        self.lbl_estado_verificacion.pack(pady=(0, 14))
        botones = tk.Frame(pad, bg=colores._DIRECCION_CONFIRM_CARD)
        botones.pack(fill="x")
        self.btn_editar_datos = ctk.CTkButton(botones, text=idiomas.t("dir_editar_datos"), corner_radius=10, height=42, fg_color="transparent", hover_color=colores._DIRECCION_FORM_INPUT_BG, border_width=1, border_color=colores.TEXTO_GRIS, text_color=colores.TEXTO_BLANCO, font=("Segoe UI", 12, "bold"), command=self._volver_a_editar)
        self.btn_editar_datos.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.btn_confirmar_final = ctk.CTkButton(botones, text=idiomas.t("dir_confirmar_direccion"), corner_radius=10, height=42, fg_color=colores.MARCA_TEAL, hover_color=colores.MARCA_TEAL_HOVER, font=("Segoe UI", 12, "bold"), command=self._confirmar_direccion)
        self.btn_confirmar_final.pack(side="left", fill="x", expand=True)

    def _volver_a_editar(self):
        self.frame_confirmacion.pack_forget()
        self.frame_formulario.pack(fill="both", expand=True)

    # ================= Paso 3: verificación con IA + guardado =================
    def _confirmar_direccion(self):
        if self.verificando:
            return
        self.verificando = True
        self.btn_editar_datos.configure(state="disabled")
        self.btn_confirmar_final.configure(state="disabled", text=idiomas.t("dir_verificando_btn"))
        self.lbl_estado_verificacion.configure(text=idiomas.t("dir_verificando"), fg=colores._DIRECCION_CONFIRM_ICONO_IA)

        def resultado(es_valida, mensaje):
            self.verificando = False
            if not self.lbl_estado_verificacion.winfo_exists():
                return
            if es_valida:
                self._guardar_direccion_final(mensaje)
            else:
                self.lbl_estado_verificacion.configure(text=f"⚠️  {mensaje}", fg=colores._ROJO_STOCK)
                self.btn_editar_datos.configure(state="normal")
                self.btn_confirmar_final.configure(state="normal", text=idiomas.t("dir_confirmar_direccion"))

        self.app.ia.verificar_direccion(self.datos_pendientes, resultado)

    def _guardar_direccion_final(self, mensaje_ia):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("dir_necesita_login_guardar"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        usuario_id = self.app.auth.obtener_id_por_email(sesion)
        d = self.datos_pendientes
        if self.direccion_editar:
            self.app.direcciones_db.editar_direccion(self.direccion_editar["id"], usuario_id, **d)
            id_combinado = f"dir_{self.direccion_editar['id']}"
        else:
            nuevo_id = self.app.direcciones_db.agregar_direccion(usuario_id=usuario_id, **d)
            id_combinado = f"dir_{nuevo_id}"
        self.app.cargar_direcciones()
        seleccionada = next((dir_ for dir_ in self.app.direcciones_guardadas if dir_["id"] == id_combinado), None)
        if seleccionada:
            self.app.direccion_envio_seleccionada = seleccionada
        if hasattr(self.app, "header"):
            self.app.header.actualizar_texto_envio_a()
        if self.app.historial:
            self.app.historial.pop()
        self.app.mensaje_temporal(mensaje_ia)
        self.app.volver()

    @staticmethod
    def _telefono_valido(telefono):
        telefono = (telefono or "").strip()
        if not telefono:
            return False
        try:
            numero = phonenumbers.parse(telefono, "AR")
        except phonenumbers.NumberParseException:
            return False
        return phonenumbers.is_valid_number(numero)