import tkinter as tk
import customtkinter as ctk
import os
from PIL import Image, ImageTk
import requests
from io import BytesIO
import colores
import idiomas

class Header(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg=colores.FONDO_HEADER,height=125)
        self.crear_widgets()

    def crear_widgets(self):
        self.crear_envio_a()
        self.lineas_delimitadoras()
        self.boton_volver()
        self.categorias()
        self.crear_barra_navegacion()
        self.crear_buscador_entry()
        self.logo_marca_imagen()
        self.ui_perfil()
        self.crear_boton_vender()
        self.crear_region()
        self.configurar_eventos()

    def categorias(self):
        self.label_categorias = tk.Label(self, text=f"{idiomas.t('categorias_label')} ▶", bg=colores.FONDO_HEADER, fg="black", font=("Arial", 14))
        self.label_categorias.place(x=190, y=84)
        if hasattr(self, "submenu") and self.submenu.winfo_exists():
            self.submenu.destroy()
        self.submenu = tk.Frame(self.app.ventana_principal, bg=colores.MENU_FONDO, bd=1, relief="solid")
        self.submenu.place(x=180, y=125)
        self.submenu.lower()
        categorias_data = [
            ("carteras", 50),
            ("mochilas", 50),
            ("remeras", 50),
            ("pantalones", 50),
            ("camisas", 100)]
        for categoria, ipad in categorias_data:
            texto = idiomas.t(f"cat_{categoria}").capitalize()
            tk.Button(self.submenu, text=texto, command=lambda c=categoria: self.abrir_categoria(c), bg=colores.MENU_FONDO, fg="black", font=("Arial", 13), relief="flat", anchor="w", cursor="hand2").pack(fill="x", ipadx=ipad, padx=5)

    def crear_envio_a(self):
        self.frame_envio_a = tk.Frame(self, bg=colores.FONDO_HEADER, cursor="hand2")
        self.frame_envio_a.place(x=25, y=75)
        URL_ICONO_PIN = "https://res.cloudinary.com/czevmfkz/image/upload/v1785144398/b35a06cd-49c8-4ba8-af05-615e2981ca9c_paq3zk.png"
        self.app._icono_imagen(self.frame_envio_a, URL_ICONO_PIN, 15, 30, bg=colores.FONDO_HEADER).pack(side="left",pady=3, padx=(0, 5))
        self.lbl_enviar_a_titulo = tk.Label(self.frame_envio_a, text=idiomas.t("enviar_a_titulo"), bg=colores.FONDO_HEADER,fg=colores._ENVIAR_A_ETIQUETA, font=("Arial", 10))
        self.lbl_enviar_a_titulo.pack(anchor="w", side="top")
        self.lbl_direccion_envio = tk.Label(self.frame_envio_a, text=self._texto_direccion_corta(), bg=colores.FONDO_HEADER, fg=colores._ENVIAR_A_DIRECCION, font=("Arial", 11, "bold"))
        self.lbl_direccion_envio.pack()
        for w in [self.frame_envio_a] + list(self.frame_envio_a.winfo_children()):
            w.bind("<Button-1>", self._abrir_panel_direccion)

    def _texto_direccion_corta(self):
        etiqueta = self.app.direccion_envio_seleccionada.get("etiqueta", idiomas.t("elegir_direccion")) if self.app.direccion_envio_seleccionada else idiomas.t("elegir_direccion")
        return f"{self.app.limitar_texto(etiqueta, 16)} ▾"

    def _abrir_panel_direccion(self, event=None):
        self.app.cambiar_vista(self.app.mostrar_seleccionar_direccion)

    def actualizar_texto_envio_a(self):
        if self.lbl_direccion_envio.winfo_exists():
            self.lbl_direccion_envio.configure(text=self._texto_direccion_corta())

    def lineas_delimitadoras(self):
        lineas = [(180, 0, 2, 125, colores.LINEA_DIVISOR),(180, 70, 1800, 2, colores.LINEA_DIVISOR),(1080, 0, 2, 125, colores.LINEA_DIVISOR),(320, 70, 2, 60, colores.LINEA_DIVISOR),(605, 70, 2, 60, colores.LINEA_DIVISOR),(705, 70, 2, 60, colores.LINEA_DIVISOR),(795, 70, 2, 60, colores.LINEA_DIVISOR),(967, 70, 2, 60, colores.LINEA_DIVISOR),(0, 123, 2000, 2, colores.TEXTO_NEGRO)]
        for x, y, w, h, color in lineas:
            tk.Frame(self, bg=color, width=w, height=h).place(x=x, y=y)

    def boton_volver(self):
        self.btn_volver = tk.Label(self,text="←",bg=colores.FONDO_HEADER,fg="black",font=("Segoe UI", 18, "bold"),cursor="hand2")
        self.btn_volver.place(x = 0, y = 0)

    def abrir_categoria(self, categoria):
        self.app.cambiar_vista(lambda: self.app.mostrar_categoria_ia(categoria))

    def mostrar_menu(self, event=None):
            self.label_categorias.config(text=f"{idiomas.t('categorias_label')} ▼")
            self.submenu.lift()

    def ocultar_si_fuera(self, event=None):
        def verificar():
            x, y = self.app.ventana_principal.winfo_pointerxy()
            widget = self.app.ventana_principal.winfo_containing(x, y)
            if widget is None or (widget != self.label_categorias and not str(widget).startswith(str(self.submenu))):
                self.label_categorias.config(text=f"{idiomas.t('categorias_label')} ▶")
                self.submenu.lower()
        self.app.ventana_principal.after(100, verificar)

    def analisis_lo_mas_vendido(self):
        self.app.cambiar_vista(self.app.mostrar_mas_vendidos)
    def analisis_ofertas(self):
        self.app.cambiar_vista(self.app.mostrar_ofertas)
    def analisis_ayuda(self):
        self.app.cambiar_vista(self.app.mostrar_ayuda)

    def analisis_lista_de_deseos(self):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("necesita_login_deseos"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        self.app.cambiar_vista(self.app.mostrar_deseos)
    def analisis_cupones(self):
        if self.app.es_admin():
            self.app.cambiar_vista(self.app.mostrar_admin_cupones)
        else:
            self.app.mensaje_temporal(idiomas.t("cupon_checkout_info"))

    def crear_barra_navegacion(self):
        self.botones_nav = {}
        botones = [
            ("nav_mas_vendido", self.analisis_lo_mas_vendido, 330, 79, 260),
            ("nav_ofertas", self.analisis_ofertas, 615, 79, 80),
            ("nav_ayuda", self.analisis_ayuda, 715, 79, 70),
            ("nav_deseos", self.analisis_lista_de_deseos, 805, 79, 150),
            ("nav_cupones", self.analisis_cupones, 976, 79, 100),
            ("nav_registrarse", self.analisis_registrate, 1090, 79, 90),
        ]
        for clave, comando, x, y, ancho in botones:
            texto = idiomas.t(clave)
            fuente = idiomas.fuente_ajustada(texto, ancho, tam_base=14)
            btn = tk.Button(self, text=texto, command=comando, relief="flat", bg=colores.FONDO_HEADER, fg="black", font=fuente)
            btn.place(x=x, y=y)
            self.botones_nav[clave] = btn
        self.btn_config = tk.Button(self, text="⚙️", command=self.analisis_configuración, relief="flat", bg=colores.FONDO_HEADER, fg="black", font=("Arial", 14))
        self.btn_config.place(x=1190, y=79)
        tag = tk.Label(self, text=" HOT ",bg="RED", fg="White", font=("Segoe UI", 10, "bold"))
        tag.place(x = 550, y = 60)
        self.btn_carrito = tk.Button(self,text="🛒",command=self.analisis_carrito_de_compra,relief="flat",bg=colores.FONDO_HEADER,fg="black",font=("Arial", 19), cursor="hand2")
        self.btn_carrito.place(x=1228, y=72)
        self.lbl_badge_carrito = tk.Label(self,text="",bg=colores._CARRITO_BADGE_BG,fg=colores.TEXTO_BLANCO,font=("Segoe UI", 8, "bold"),width=2)
        self.actualizar_badge_carrito()
        self.lbl_badge_deseos = tk.Label(self,text="",bg=colores._CARRITO_BADGE_BG,fg=colores.TEXTO_BLANCO,font=("Segoe UI", 8, "bold"),width=2)
        self.actualizar_badge_deseos()

    def actualizar_badge_carrito(self):
        cantidad = len(self.app.carrito_de_compra_pedidos)
        if cantidad > 0:
            self.lbl_badge_carrito.configure(text=str(cantidad) if cantidad < 10 else "9+")
            self.lbl_badge_carrito.place(x=1250, y=68)
        else:
            self.lbl_badge_carrito.place_forget()

    def actualizar_badge_deseos(self):
        cantidad = len(self.app.lista_de_deseos_lista)
        if cantidad > 0:
            self.lbl_badge_deseos.configure(text=str(cantidad) if cantidad < 10 else "9+")
            self.lbl_badge_deseos.place(x=948, y=72)
        else:
            self.lbl_badge_deseos.place_forget()

    def crear_buscador_entry(self):
        ANCHO_BUSCADOR = 875
        ALTO_BUSCADOR = 40
        X_BUSCADOR = 195
        Y_BUSCADOR = 15
        RADIO_ENTRY = 14    
        DIAMETRO_LUPA = 32
        MARGEN_DERECHO = 18 
        self.entrada = ctk.CTkEntry(master=self,placeholder_text=idiomas.t("buscador_placeholder"),placeholder_text_color=colores.MENU_FONDO_OSCURO,fg_color=colores.TEXTO_BLANCO,text_color=colores.TEXTO_NEGRO,font=("Segoe UI", 13),width=ANCHO_BUSCADOR,height=ALTO_BUSCADOR,corner_radius=RADIO_ENTRY,border_width=2,border_color=colores.BORDE_ENTRADA)
        self.entrada.place(x=X_BUSCADOR, y=Y_BUSCADOR)
        self.circulo_lupa = ctk.CTkFrame(
        self.entrada, width=DIAMETRO_LUPA, height=DIAMETRO_LUPA,corner_radius=DIAMETRO_LUPA // 2, fg_color=colores.TEXTO_BLANCO,border_width=2, border_color=colores.MARCA_TEAL,cursor="hand2",)
        self.circulo_lupa.place(relx=1.0, x=-MARGEN_DERECHO, rely=0.5, anchor="e")
        URL_ICONO_BUSCADOR = "https://res.cloudinary.com/czevmfkz/image/upload/v1785327083/6c26be14-56cc-45ba-b1ee-f3e837359831_ra05ag.png"
        self.lbl_lupa = self.app._icono_imagen(self.circulo_lupa, URL_ICONO_BUSCADOR, 16, 16, bg=colores.TEXTO_BLANCO)
        self.lbl_lupa.place(relx=0.5, rely=0.5, anchor="center")
        self.lbl_lupa.configure(cursor="hand2")
        self.divisor_lupa = tk.Frame(self.entrada, bg=colores.BORDE_ENTRADA, width=1, height=20)
        self.divisor_lupa.place(relx=1.0, x=-(MARGEN_DERECHO + DIAMETRO_LUPA + 10), rely=0.5, anchor="center")
        self._crear_panel_sugerencias()
        self.entrada.bind("<Return>", self.ejecutar_busqueda)
        self.entrada.bind("<KeyRelease>", self._actualizar_sugerencias)
        self.entrada.bind("<FocusIn>", self._al_enfocar_buscador)
        self.entrada.bind("<FocusOut>", self._al_desenfocar_buscador)
        for w in (self.circulo_lupa, self.lbl_lupa):
            w.bind("<Button-1>", self._click_lupa)
            w.bind("<Enter>", lambda e: self._hover_lupa(True))
            w.bind("<Leave>", lambda e: self._hover_lupa(False))
    # ================= Buscador: estética del botón de lupa =================
    def _hover_lupa(self, entrando):
        if not self.circulo_lupa.winfo_exists():
            return
        self.circulo_lupa.configure(border_color=colores.MARCA_TEAL_HOVER if entrando else colores.MARCA_TEAL)
    def _click_lupa(self, event=None):
        if self.circulo_lupa.winfo_exists():
            self.circulo_lupa.configure(border_color=colores.MARCA_TEAL_PRESS)
            self.after(120, lambda: self.circulo_lupa.winfo_exists() and self.circulo_lupa.configure(border_color=colores.MARCA_TEAL_HOVER))
        self.ejecutar_busqueda(event)
    def _al_enfocar_buscador(self, event=None):
        if self.entrada.winfo_exists():
            self.entrada.configure(border_color=colores.MARCA_TEAL)
        self._actualizar_sugerencias(event)
    def _al_desenfocar_buscador(self, event=None):
        if self.entrada.winfo_exists():
            self.entrada.configure(border_color=colores.BORDE_ENTRADA)
        self._ocultar_sugerencias_diferido(event)
    def _click_fuera_buscador(self, event=None):
        if not (hasattr(self, "entrada") and self.entrada.winfo_exists()):
            return
        ruta = str(event.widget)
        if (ruta.startswith(str(self.entrada)) or
            ruta.startswith(str(self.circulo_lupa)) or
            ruta.startswith(str(self.frame_sugerencias))):
            return
        self.entrada.configure(border_color=colores.BORDE_ENTRADA)
        self.frame_sugerencias.lower()
    # ================= Buscador: sugerencias / historial =================
    def _crear_panel_sugerencias(self):
        self.frame_sugerencias = tk.Frame(self.app.ventana_principal, bg=colores.MENU_FONDO, bd=1, relief="solid")
        self.frame_sugerencias.place(x=195, y=57, width=875)
        self.frame_sugerencias.lower()

    def _actualizar_sugerencias(self, event=None):
        for w in self.frame_sugerencias.winfo_children():
            w.destroy()
        texto = self.entrada.get().strip()
        if texto:
            self._poblar_sugerencias_texto(texto)
        else:
            self._poblar_historial()

    def _fila_sugerencia(self, parent, texto_visible, texto_valor):
        fila = tk.Frame(parent, bg=colores.MENU_FONDO)
        fila.pack(fill="x")
        URL_ICONO_BUSCADOR = "https://res.cloudinary.com/czevmfkz/image/upload/v1785327083/6c26be14-56cc-45ba-b1ee-f3e837359831_ra05ag.png"
        self.app._icono_imagen(fila,URL_ICONO_BUSCADOR,15,15,bg=colores.MENU_FONDO).pack(side="left", padx=(10, 6), pady=6)
        label = tk.Label(fila,text=texto_visible,bg=colores.MENU_FONDO,fg="black",font=("Arial", 12),anchor="w",cursor="hand2")
        label.pack(side="left", fill="x", expand=True)
        def elegir(event=None):
            self._elegir_sugerencia(texto_valor)
        fila.bind("<Button-1>", elegir)
        label.bind("<Button-1>", elegir)
        fila.bind("<Enter>", lambda e: fila.configure(bg=colores.BOTON_LETRA))
        label.bind("<Enter>", lambda e: fila.configure(bg=colores.BOTON_LETRA))
        fila.bind("<Leave>", lambda e: fila.configure(bg=colores.MENU_FONDO))
        label.bind("<Leave>", lambda e: fila.configure(bg=colores.MENU_FONDO))
        return fila

    def _poblar_sugerencias_texto(self, texto):
        nombres = self.app.productos_db.sugerir_productos(texto, limite=6)
        if not nombres:
            self.frame_sugerencias.lower()
            return
        for nombre in nombres:
            self._fila_sugerencia(self.frame_sugerencias, nombre, nombre)
        self.frame_sugerencias.lift()

    def _poblar_historial(self):
        historial = self.app.historial_busquedas
        if not historial:
            self.frame_sugerencias.lower()
            return
        tk.Label(self.frame_sugerencias, text=idiomas.t("busquedas_recientes"), bg=colores.MENU_FONDO, fg=colores.TEXTO_NEGRO, font=("Arial", 10, "italic"), anchor="w", padx=10, pady=4).pack(fill="x")
        for texto in historial:
            self._fila_sugerencia(self.frame_sugerencias, f"{texto}", texto)
        btn_borrar = tk.Label(self.frame_sugerencias, text=idiomas.t("borrar_historial"), bg=colores.MENU_FONDO, fg=colores._BORRAR, font=("Arial", 11, "bold"), anchor="w", cursor="hand2", padx=10, pady=6)
        btn_borrar.pack(fill="x")
        btn_borrar.bind("<Button-1>", self._borrar_historial)
        btn_borrar.bind("<Enter>", lambda e: btn_borrar.configure(fg=colores._CARRITO_ELIMINAR_HOVER))
        btn_borrar.bind("<Leave>", lambda e: btn_borrar.configure(fg=colores._CARRITO_ELIMINAR))
        self.frame_sugerencias.lift()

    def _elegir_sugerencia(self, texto):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, texto)
        self._buscar(texto)

    def _borrar_historial(self, event=None):
        self.app.borrar_historial_busqueda()
        self.app.mensaje_temporal(idiomas.t("historial_borrado"))
        self._actualizar_sugerencias()

    def _ocultar_sugerencias_diferido(self, event=None):
        def verificar():
            x, y = self.app.ventana_principal.winfo_pointerxy()
            widget = self.app.ventana_principal.winfo_containing(x, y)
            if widget is None or (
                widget != self.entrada and
                not str(widget).startswith(str(self.frame_sugerencias))):
                self.frame_sugerencias.lower()
        self.app.ventana_principal.after(150, verificar)

    def ejecutar_busqueda(self, event=None):
        texto = self.entrada.get().strip()
        if not texto:
            self.app.mensaje_temporal(idiomas.t("ingresa_algo_buscar"))
            return
        self._buscar(texto)

    def _buscar(self, texto):
        self.frame_sugerencias.lower()
        self.app.agregar_a_historial_busqueda(texto)
        self.app.cambiar_vista(lambda: self.app.mostrar_busqueda(texto))

    def analisis_registrate(self):
        sesion = self.app.auth.cargar_sesion()
        if sesion:
            self.app.usuario = sesion
            self.app.mensaje_temporal(idiomas.t("ya_registrado", sesion=sesion))
        else:
            self.app.cambiar_vista(self.app.vista_login)

    def analisis_configuración(self):
        self.app.cambiar_vista(self.app.mostrar_configuracion)

    def analisis_carrito_de_compra(self):
        self.app.cambiar_vista(self.app.mostrar_carrito)

    def logo_marca_imagen(self):
        self.logo_label = tk.Label(self,bg=colores.FONDO_HEADER,borderwidth=0,highlightthickness=0)
        self.logo_label.place(x=30, y=10)
        url = "https://res.cloudinary.com/czevmfkz/image/upload/v1783256271/Logo_imagen2_tvh4nk.png"
        self.app.carga_task_iniciada()
        def terminar(logo):
            try:
                if logo is None or not self.logo_label.winfo_exists():
                    return
                logo = logo.resize((115, 60), Image.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(logo)
                self.logo_label.configure(image=self.logo_img)
            except Exception as e:
                print("No se pudo cargar el logo:", e)
            finally:
                self.app.carga_task_finalizada()
        self.app.obtener_imagen(url, callback=terminar)

    def ui_perfil(self):
        self.perfil = tk.Label(self, text=f"👤 {idiomas.t('mi_cuenta_label')} ▶", bg=colores.FONDO_HEADER, fg="black", padx= 0,font=("Arial", 13))
        self.perfil.place(x=1085, y=45)
        self.menu_perfil = tk.Frame(self.app.ventana_principal, bg=colores.MENU_FONDO_OSCURO, bd=1, relief="solid")
        self.menu_perfil.place(x=1081, y=71)
        self.menu_perfil.lower()
        self.botones_menu_perfil = {}
        botones_perfil = [("menu_mi_cuenta", self.abrir_perfil), ("menu_mis_pedidos", self.mis_pedidos), ("menu_cerrar_sesion", self.cerrar_sesion_ui)]
        for clave, c in botones_perfil:
            btn = tk.Button(self.menu_perfil, text=idiomas.t(clave), command=c, bg=colores.MENU_FONDO, fg="black", relief="flat", anchor="w", font=("Arial", 12))
            btn.pack(fill="x", ipadx=43, padx=1)
            self.botones_menu_perfil[clave] = btn

    def abrir_perfil(self):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.cambiar_vista(self.app.vista_login)
            return
        self.app.usuario = sesion
        self.app.cambiar_vista(self.app.mostrar_cuenta)

    def mis_pedidos(self):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("necesita_login_pedidos"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        self.app.usuario = sesion
        self.app.cambiar_vista(lambda: self.app.mostrar_cuenta("compras"))

    def cerrar_sesion_ui(self):
        sesion = self.app.auth.cargar_sesion()
        if not sesion or self.app.usuario == "Invitado":
            self.app.mensaje_temporal(idiomas.t("sin_usuario_logeado"))
            return
        self.app.auth.cerrar_sesion()
        self.app.usuario = "Invitado"
        self.app.lista_de_deseos_lista.clear()
        self.actualizar_badge_deseos()
        self.app.carrito_de_compra_pedidos.clear()
        self.app.cargar_direcciones()
        self.app.cambiar_vista(self.app.vista_login)
        self.app.mensaje_temporal(idiomas.t("sesion_cerrada"))

    def mostrar_menu_perfil(self, event=None):
        self.perfil.config(text=f"👤 {idiomas.t('mi_cuenta_label')} ▼")
        self.menu_perfil.lift()

    def ocultar_menu_perfil(self, event=None):
        def verificar():
            x, y = self.app.ventana_principal.winfo_pointerxy()
            widget = self.app.ventana_principal.winfo_containing(x, y)
            if widget is None or (
                widget != self.perfil and
                not str(widget).startswith(str(self.menu_perfil))):
                self.perfil.config(text=f"👤 {idiomas.t('mi_cuenta_label')} ▶")
                self.menu_perfil.lower()
        self.app.ventana_principal.after(100, verificar)

    def crear_boton_vender(self):
        self.label_central_ventas = ctk.CTkFrame(master=self,width=165,height=38,fg_color=colores.MARCA_TEAL,corner_radius=15)
        self.label_central_ventas.place(x=1100, y=5)
        self.canvas = tk.Canvas(self.label_central_ventas,width=30,height=30,bg=colores.MARCA_TEAL,highlightthickness=0)
        self.canvas.place(x=20, y=4)
        self.canvas.create_oval(3, 3, 27, 27, outline="black", width=2)
        self.canvas.create_line(15, 9, 15, 21, fill="black", width=2)
        self.canvas.create_line(9, 15, 21, 15, fill="black", width=2)
        self.ventas = tk.Label(self.label_central_ventas, bg=colores.MARCA_TEAL, text = idiomas.t("vender_label"), font = ("Segoe UI", 16, "bold"),highlightthickness = 0)
        self.ventas.place(x = 55, y = 0)

    def entrar_boton_vender(self, e):
        self.label_central_ventas.configure(fg_color=colores.MARCA_TEAL_HOVER)
        self.canvas.configure(bg=colores.MARCA_TEAL_HOVER)
        self.ventas.configure(bg=colores.MARCA_TEAL_HOVER, fg = "White")
    def salir_boton_vender(self, e):
        self.label_central_ventas.configure(fg_color=colores.MARCA_TEAL)
        self.canvas.configure(bg=colores.MARCA_TEAL)
        self.ventas.configure(bg = colores.MARCA_TEAL, fg = "Black")
    def presionar_boton_vender(self, e):
        self.label_central_ventas.place(x=1100, y=7)
        self.label_central_ventas.configure(fg_color=colores.MARCA_TEAL_PRESS)
        self.canvas.configure(bg=colores.MARCA_TEAL_PRESS)
        self.ventas.configure(bg=colores.MARCA_TEAL_PRESS)
    def soltar_boton_vender(self, e):
        self.label_central_ventas.place(x=1100, y=5) 
        self.entrar_boton_vender(e)
    def _enlazar_boton_vender_recursivo(self, widget):
        try:
            widget.configure(cursor="hand2")
        except tk.TclError:
            pass
        widget.bind("<Enter>", self.entrar_boton_vender)
        widget.bind("<Leave>", self.salir_boton_vender)
        widget.bind("<ButtonPress-1>", self.presionar_boton_vender)
        widget.bind("<ButtonRelease-1>", self.soltar_boton_vender)
        for child in widget.winfo_children():
            self._enlazar_boton_vender_recursivo(child)

    def _click_boton_vender(self, event):
        if not (hasattr(self, "label_central_ventas") and self.label_central_ventas.winfo_exists()):
            return
        x1 = self.label_central_ventas.winfo_rootx()
        y1 = self.label_central_ventas.winfo_rooty()
        x2 = x1 + self.label_central_ventas.winfo_width()
        y2 = y1 + self.label_central_ventas.winfo_height()
        if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
            self.funcion_boton_vender(event)
    def funcion_boton_vender(self, event=None):
        sesion = self.app.auth.cargar_sesion()
        if not sesion:
            self.app.mensaje_temporal(idiomas.t("necesita_login_vender"))
            self.app.cambiar_vista(self.app.vista_login)
            return
        self.app.cambiar_vista(self.app.mostrar_panel_vendedor)

    def crear_region(self):
        self.paises = {
            "AR": "https://res.cloudinary.com/czevmfkz/image/upload/v1783256269/Bandera_Argentina_beswm5.png",
            "US": "https://res.cloudinary.com/czevmfkz/image/upload/v1783256270/Bandera_Estados_Unidos_kmqbab.png",
            "FR": "https://res.cloudinary.com/czevmfkz/image/upload/v1783256270/Bandera_Francia_ysoktj.png"}
        self.region_actual = "AR"
        self.banderas = {}
        self._filas_region = {}
        self.region_frame = tk.Frame(self, bg=colores.FONDO_HEADER)
        self.region_frame.place(x=1200, y=45)
        self.bandera_label = tk.Label(self.region_frame,bg=colores.FONDO_HEADER)
        self.bandera_label.pack(side="left")
        self.region_texto = tk.Label(self.region_frame,text=self.region_actual,bg=colores.FONDO_HEADER,font=("Arial", 13))
        self.region_texto.pack(side="left", padx=3)
        self.region_btn = tk.Label(self.region_frame,text="▶",bg=colores.FONDO_HEADER,font=("Arial", 12),cursor="hand2")
        self.region_btn.pack(side="left")
        self.menu_region = tk.Frame(self.app.ventana_principal, bg=colores.MENU_FONDO_OSCURO, bd=1, relief="solid")
        self.menu_region.place(x=1200, y=71)
        self.menu_region.lower()
        for codigo in self.paises:
            fila = tk.Frame(self.menu_region, bg=colores.MENU_FONDO)
            fila.pack(fill="x")
            lbl_bandera = tk.Label(fila,bg=colores.MENU_FONDO)
            lbl_bandera.pack(side="left", padx=7, pady=2)
            tk.Button(fila,text=codigo,command=lambda c=codigo: self.cambiar_region(c),bg=colores.MENU_FONDO,fg="black",relief="flat",font=("Arial", 12)).pack(side="left")
            self._filas_region[codigo] = lbl_bandera
        for codigo, url in self.paises.items():
            self._cargar_bandera(codigo, url)

    def _cargar_bandera(self, codigo, url):
        self.app.carga_task_iniciada()
        def terminar(img):
            try:
                if img is None:
                    return
                img = img.resize((20, 14), Image.LANCZOS)
                foto = ImageTk.PhotoImage(img)
                self.banderas[codigo] = foto
                if codigo in self._filas_region and self._filas_region[codigo].winfo_exists():
                    self._filas_region[codigo].configure(image=foto)
                    self._filas_region[codigo].image = foto
                if codigo == self.region_actual and self.bandera_label.winfo_exists():
                    self.bandera_label.configure(image=foto)
                    self.bandera_label.image = foto
            except Exception as e:
                print(f"Error cargando bandera {codigo}: {e}")
            finally:
                self.app.carga_task_finalizada()
        self.app.obtener_imagen(url, callback=terminar)

    def cambiar_region(self, codigo):
        self.region_actual = codigo
        if codigo in self.banderas:
            self.bandera_label.config(image=self.banderas[codigo])
            self.bandera_label.image = self.banderas[codigo]
        self.region_texto.config(text=codigo)

    def mostrar_region(self, event=None):
            self.region_btn.config(text="▼")
            self.menu_region.lift()

    def ocultar_region(self, event=None):
        def verificar():
            x, y = self.app.ventana_principal.winfo_pointerxy()
            widget = self.app.ventana_principal.winfo_containing(x, y)
            if widget is None or (
                widget != self.region_frame and
                not str(widget).startswith(str(self.menu_region))):
                self.region_btn.config(text="▶")
                self.menu_region.lower()
        self.app.ventana_principal.after(100, verificar)

    def configurar_eventos(self):
        self.app.ventana_principal.bind_all("<Button-1>", self._click_fuera_buscador, add="+")
        self.app.ventana_principal.bind_all("<Button-1>", self._click_boton_vender, add="+")
        self.btn_volver.bind("<Button-1>", lambda e: self.app.volver())
        self.btn_volver.place_forget()
        self.label_categorias.bind("<Enter>", self.mostrar_menu)
        self.label_categorias.bind("<Leave>", self.ocultar_si_fuera)
        self.submenu.bind("<Leave>", self.ocultar_si_fuera)
        self.submenu.bind("<Enter>", self.mostrar_menu)
        self.perfil.bind("<Enter>", self.mostrar_menu_perfil)
        self.perfil.bind("<Leave>", self.ocultar_menu_perfil)
        self.menu_perfil.bind("<Enter>", self.mostrar_menu_perfil)
        self.menu_perfil.bind("<Leave>", self.ocultar_menu_perfil)
        self._enlazar_boton_vender_recursivo(self.label_central_ventas)
        binds = [self.region_frame,self.menu_region,self.region_btn,self.bandera_label,self.region_texto]
        for bind in binds:
            bind.bind("<Enter>", self.mostrar_region)
            bind.bind("<Leave>", self.ocultar_region)