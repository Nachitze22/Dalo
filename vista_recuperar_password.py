import tkinter as tk
import customtkinter as ctk
import time
import auth
import colores
import idiomas

class Vista_recuperar_password(tk.Frame):
    def __init__(self, parent, app, email):
        super().__init__(parent, bg=colores.FONDO_PRINCIPAL)
        self.app = app
        self.email = email
        self.pack(fill="both", expand=True)
        self.variables()
        self.crear_widgets()
        self.configurar_eventos()

    def variables(self):
        self.codigo = auth.enviar_codigo(self.email)
        if not self.codigo:
            self.app.mensaje_temporal(idiomas.t("recuperar_error_email"))
            return
        self.inicio = time.time()
        self.duracion = 600

    def crear_widgets(self):
        self.widgets()

    def widgets(self):
        self.contenedor_padre = tk.Frame(self, bg=colores.FONDO_PRINCIPAL)
        self.contenedor_padre.pack(fill="both", expand=True)
        self.app.ventana_principal.update_idletasks()
        alto = self.app.ventana_principal.winfo_height()
        self.contenedor_padre.config(height=alto)
        self.contenedor = ctk.CTkFrame(self.contenedor_padre,width=420,height=475,corner_radius=20,fg_color=colores.FONDO_TARJETA_LOGIN,border_width=2,border_color=colores.MARCA_TEAL)
        self.contenedor.place(relx=0.5, rely=0.38, anchor="center")
        self.contenedor.pack_propagate(False)
        self.titulo = ctk.CTkLabel(self.contenedor,text=idiomas.t("recuperar_titulo"),font=("Segoe UI", 28, "bold"),text_color="white")
        self.titulo.pack(pady=(25, 10))
        self.subtitulo = ctk.CTkLabel(self.contenedor,text=idiomas.t("recuperar_subtitulo", email=self.email),font=("Segoe UI", 14),text_color=colores.TEXTO_GRIS, wraplength=350)
        self.subtitulo.pack(pady=(0, 20))
        self.entry_codigo = ctk.CTkEntry(self.contenedor,placeholder_text=idiomas.t("recuperar_codigo_placeholder"),width=280,height=40,corner_radius=10)
        self.entry_codigo.pack(pady=10)
        self.entry_nueva = ctk.CTkEntry(self.contenedor,placeholder_text=idiomas.t("recuperar_nueva_placeholder"),show="*",width=280,height=40,corner_radius=10)
        self.entry_nueva.pack(pady=10)
        self.label_estado = ctk.CTkLabel(self.contenedor,text="",text_color="red",font=("Segoe UI", 12))
        self.label_estado.pack(pady=5)
        self.mostrar = ctk.CTkButton(self.contenedor,text=idiomas.t("login_mostrar"),command=self.toggle_password,width=140)
        self.mostrar.pack(pady=2)
        self.cambiar_contraseña = ctk.CTkButton(self.contenedor,text=idiomas.t("recuperar_cambiar_btn"),width=280,height=40,corner_radius=10,fg_color=colores.MARCA_TEAL,hover_color=colores.MARCA_TEAL_HOVER,font=("Segoe UI", 14, "bold"),command=self.cambiar_password)
        self.cambiar_contraseña.pack(pady=(6, 3))
        self.volver_al_login = ctk.CTkButton(self.contenedor,text=idiomas.t("recuperar_volver_login"),width=280,height=40,corner_radius=10,fg_color=colores.BTN_OSCURO,hover_color=colores.BTN_OSCURO_HOVER,font=("Segoe UI", 13),command=self.app.vista_login)
        self.volver_al_login.pack(pady=3)

    def limpiar_estado(self, event=None):
            self.label_estado.configure(text="")

    def toggle_password(self):
        if self.entry_nueva.cget("show") == "":
            self.entry_nueva.configure(show="*")
        else:
            self.entry_nueva.configure(show="")

    def cambiar_password(self):
        if time.time() - self.inicio > self.duracion:
            self.label_estado.configure(text=idiomas.t("recuperar_codigo_expirado"),text_color="red")
            return
        if self.entry_codigo.get() != self.codigo:
            self.label_estado.configure(text=idiomas.t("recuperar_codigo_incorrecto"),text_color="red")
            return
        nueva = self.entry_nueva.get()
        if not nueva:
            self.label_estado.configure(text=idiomas.t("recuperar_ingresa_password"),text_color="red")
            return
        auth.actualizar_password(self.email, nueva)
        self.label_estado.configure(text=idiomas.t("recuperar_actualizada"),text_color=colores.MARCA_TEAL)
        self.app.ventana_principal.after(1500,self.app.vista_login)

    def configurar_eventos(self):
        self.entry_codigo.bind("<Key>", self.limpiar_estado)
        self.entry_nueva.bind("<Key>", self.limpiar_estado)