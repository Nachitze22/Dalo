import tkinter as tk
import customtkinter as ctk
import time
import auth
from componentes.vista_recuperar_password import Vista_recuperar_password
import colores
import idiomas

class Vista_login(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=colores.FONDO_PRINCIPAL)
        self.app = app
        self.pack(fill="both", expand=True)
        self.crear_widgets()

    def crear_widgets(self):
        self.widgets()
        self.configurar_eventos()

    def widgets(self):
        self.contenedor_padre = tk.Frame(self,bg=colores.FONDO_PRINCIPAL)
        self.contenedor_padre.pack(fill="both", expand=True)
        self.app.ventana_principal.update_idletasks()
        alto = self.app.ventana_principal.winfo_height()
        self.contenedor_padre.config(height=alto)
        self.contenedor = ctk.CTkFrame(self.contenedor_padre,width=420,height=525,corner_radius=20,fg_color=colores.FONDO_TARJETA_LOGIN,border_width=2,border_color=colores.MARCA_TEAL)
        self.contenedor.place(relx=0.5,rely=0.40,anchor="center")
        self.contenedor.pack_propagate(False)
        self.titulo = ctk.CTkLabel(self.contenedor,text=idiomas.t("login_titulo"),font=("Segoe UI", 28, "bold"),text_color="white")
        self.titulo.pack(pady=(25, 10))
        self.subtitulo = ctk.CTkLabel(self.contenedor,text=idiomas.t("login_subtitulo"),font=("Segoe UI", 14),text_color=colores.TEXTO_GRIS)
        self.subtitulo.pack(pady=(0, 20))
        self.entry_nombre = ctk.CTkEntry(self.contenedor,placeholder_text=idiomas.t("login_nombre_placeholder"),width=280,height=40,corner_radius=10)
        self.entry_nombre.pack(pady=10)
        self.entry_email = ctk.CTkEntry(self.contenedor,placeholder_text=idiomas.t("login_email_placeholder"),width=280,height=40,corner_radius=10)
        self.entry_email.pack(pady=10)
        self.entry_password = ctk.CTkEntry(self.contenedor,placeholder_text=idiomas.t("login_password_placeholder"),show="*",width=280,height=40,corner_radius=10)
        self.entry_password.pack(pady=10)
        self.label_estado = ctk.CTkLabel(self.contenedor,text="",text_color="red",font=("Segoe UI", 12), wraplength=280)
        self.label_estado.pack(pady=5)
        self.mostrar = ctk.CTkButton(self.contenedor,text=idiomas.t("login_mostrar"),command=self.toggle_password,width=140)
        self.mostrar.pack(pady=2)
        self.btn_login = ctk.CTkButton(self.contenedor,text=idiomas.t("login_ingresar"),width=280,height=40,corner_radius=10,fg_color=colores.MARCA_TEAL,hover_color=colores.MARCA_TEAL_HOVER,font=("Segoe UI", 14, "bold"),command=self.login)
        self.btn_login.pack(pady=(6, 3))
        self.btn_registro = ctk.CTkButton(self.contenedor,text=idiomas.t("login_crear_cuenta"),width=280,height=40,corner_radius=10,fg_color=colores.BTN_OSCURO,hover_color=colores.BTN_OSCURO_HOVER,font=("Segoe UI", 13),command=self.registrar)
        self.btn_registro.pack(pady=3)
        self.btn_recuperar = ctk.CTkButton(self.contenedor,text=idiomas.t("login_olvide_password"),width=280,height=35,corner_radius=10,fg_color="#444",hover_color="#555",font=("Segoe UI", 12),command=self.recuperar_password)
        self.btn_recuperar.pack(pady=(3, 8))

    def limpiar_estado(self, event=None):
        self.label_estado.configure(text="")

    def toggle_password(self):
        if self.entry_password.cget("show") == "":
            self.entry_password.configure(show="*")
        else:
            self.entry_password.configure(show="")

    def login(self):
        email = self.entry_email.get().strip()
        password = self.entry_password.get()
        intentos_login = self.app.variables_globales.intentos_login
        bloqueados = self.app.variables_globales.bloqueados
        if email in bloqueados:
            restante = int(bloqueados[email] - time.time())
            if restante > 0:
                self.label_estado.configure(text=idiomas.t("login_espera", s=restante), text_color="red")
                return
            else:
                del bloqueados[email]
                intentos_login[email] = 0
        user = auth.obtener_usuario(email)
        if user and auth.verificar_password(password, user[1]):
            auth.guardar_sesion(email)
            self.app.usuario = email
            self.app.cargar_direcciones()
            self.app.cargar_lista_deseos()
            intentos_login[email] = 0
            nombre = auth.obtener_nombre_visible(email)
            usuario_id = auth.obtener_id_por_email(email)
            idioma_usuario = auth.obtener_idioma(usuario_id)
            self.app.cambiar_idioma(idioma_usuario)
            self.app.mensaje_temporal(idiomas.t("login_bienvenido", nombre=nombre))
            self.app.cambiar_vista(self.app.mostrar_inicio)
        else:
            intentos_login[email] = intentos_login.get(email, 0) + 1
            if intentos_login[email] >= 3:
                bloqueados[email] = time.time() + 30
                self.label_estado.configure(text=idiomas.t("login_intentos_bloqueado"),text_color="red")
            else:
                self.label_estado.configure(text=idiomas.t("login_datos_incorrectos", n=intentos_login[email]),text_color="red")

    def registrar(self):
        nombre = self.entry_nombre.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get()
        if not nombre or not email or not password:
            self.label_estado.configure(text=idiomas.t("login_completa_todo"))
            return
        if len(nombre) < 5:
            self.label_estado.configure(text=idiomas.t("login_nombre_corto"))
            return
        if len(nombre) > 15:
            self.label_estado.configure(text=idiomas.t("login_nombre_largo"))
            return
        if self.app.ia.nombre_ofensivo(nombre):
            self.label_estado.configure(text=idiomas.t("login_nombre_apropiado"))
            return
        if "@" not in email:
            self.label_estado.configure(text=idiomas.t("login_email_invalido"))
            return
        if auth.obtener_usuario(email):
            self.label_estado.configure(text=idiomas.t("login_usuario_existe"))
            return
        codigo = auth.iniciar_registro(email, auth.hash_password(password), nombre)
        if not codigo:
            self.label_estado.configure(text=idiomas.t("login_error_codigo"), text_color="red")
            return
        self.app.mensaje_temporal(idiomas.t("login_codigo_enviado"))
        self.app.cambiar_vista(lambda: self.app.mostrar_verificar_registro(email))

    def recuperar_password(self):
        email = self.entry_email.get()
        if not email:
            self.label_estado.configure(text=idiomas.t("login_ingresa_email"),text_color="red")
            return
        if not auth.obtener_usuario(email):
            self.label_estado.configure(text=idiomas.t("login_email_no_existe"),text_color="red")
            return
        self.app.limpiar_contenido()
        Vista_recuperar_password(self.app.main_frame,self.app,email)

    def configurar_eventos(self):
        self.entry_nombre.bind("<Key>", self.limpiar_estado)
        self.entry_email.bind("<Key>", self.limpiar_estado)
        self.entry_password.bind("<Key>", self.limpiar_estado)
        self.entry_password.bind("<Return>", lambda e: self.login())