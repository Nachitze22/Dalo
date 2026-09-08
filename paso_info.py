import tkinter as tk
import customtkinter as ctk
import colores
import idiomas
from componentes.vender.utils_vender import (
    CATEGORIAS_DISPONIBLES, ESTADOS_PRODUCTO, TIPOS_ENVIO, validar_info_producto,
)


class PasoInfo:
    def __init__(self, parent, wizard):
        self.parent = parent
        self.wizard = wizard
        self.app = wizard.app
        self._crear_ui()

    def validar(self):
        self._recolectar()
        return validar_info_producto(self.wizard.datos)

    def guardar(self):
        pass

    def _crear_ui(self):
        scroll = ctk.CTkScrollableFrame(self.parent, fg_color=colores._CARD, height=420)
        scroll.pack(fill="both", expand=True)
        tk.Label(scroll, text=idiomas.t("paso_info_titulo"), bg=colores._CARD, fg=colores._TEXTO,
                  font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(scroll, text=idiomas.t("paso_info_desc"), bg=colores._CARD, fg=colores.TEXTO_GRIS,
                  font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 16))

        d = self.wizard.datos
        self.entry_titulo = self._campo_texto(scroll, idiomas.t("paso_info_campo_titulo"), d.get("titulo", ""))
        self.entry_subtitulo = self._campo_texto(scroll, idiomas.t("paso_info_campo_subtitulo"), d.get("subtitulo", ""))
        tk.Label(scroll, text=idiomas.t("paso_info_campo_descripcion"), bg=colores._CARD, fg=colores._TEXTO,
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 6))
        self.txt_descripcion = ctk.CTkTextbox(scroll, width=560, height=90, corner_radius=8,
                                               fg_color=colores.FONDO_PRINCIPAL, text_color=colores._TEXTO)
        self.txt_descripcion.pack(anchor="w")
        self.txt_descripcion.insert("1.0", d.get("descripcion", ""))

        fila1 = tk.Frame(scroll, bg=colores._CARD)
        fila1.pack(fill="x", pady=(16, 0))
        self.combo_categoria = self._campo_combo(fila1, idiomas.t("paso_info_categoria"), CATEGORIAS_DISPONIBLES, d.get("categoria"))
        self.entry_subcategoria = self._campo_texto_inline(fila1, idiomas.t("paso_info_subcategoria"), d.get("subcategoria", ""))

        tk.Label(scroll, text=idiomas.t("paso_info_estado_producto"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(16, 6))
        self.segmento_estado = ctk.CTkSegmentedButton(scroll, values=ESTADOS_PRODUCTO, fg_color=colores.FONDO_PRINCIPAL,
                                                        selected_color=colores.MARCA_TEAL, selected_hover_color=colores.MARCA_TEAL_HOVER)
        self.segmento_estado.set(d.get("estado_producto", ESTADOS_PRODUCTO[0]))
        self.segmento_estado.pack(anchor="w")

        fila2 = tk.Frame(scroll, bg=colores._CARD)
        fila2.pack(fill="x", pady=(16, 0))
        self.entry_marca = self._campo_texto_inline(fila2, idiomas.t("paso_info_marca"), d.get("marca", ""))
        self.entry_modelo = self._campo_texto_inline(fila2, idiomas.t("paso_info_modelo"), d.get("modelo", ""))

        fila3 = tk.Frame(scroll, bg=colores._CARD)
        fila3.pack(fill="x", pady=(16, 0))
        self.entry_color = self._campo_texto_inline(fila3, idiomas.t("paso_info_color"), d.get("color", ""))
        self.entry_material = self._campo_texto_inline(fila3, idiomas.t("paso_info_material"), d.get("material", ""))

        fila4 = tk.Frame(scroll, bg=colores._CARD)
        fila4.pack(fill="x", pady=(16, 0))
        self.entry_peso = self._campo_texto_inline(fila4, idiomas.t("paso_info_peso"), d.get("peso", ""))
        self.entry_dimensiones = self._campo_texto_inline(fila4, idiomas.t("paso_info_dimensiones"), d.get("dimensiones", ""))

        fila5 = tk.Frame(scroll, bg=colores._CARD)
        fila5.pack(fill="x", pady=(16, 0))
        self.entry_stock = self._campo_texto_inline(fila5, idiomas.t("paso_info_stock"), str(d.get("stock", "")) if d.get("stock") else "")
        sku_actual = d.get("sku") or self.app.publicaciones_db.generar_sku()
        self.entry_sku = self._campo_texto_inline(fila5, idiomas.t("paso_info_sku"), sku_actual)

        self.entry_etiquetas = self._campo_texto(scroll, idiomas.t("paso_info_etiquetas"), d.get("etiquetas", ""))
        self.entry_garantia = self._campo_texto(scroll, idiomas.t("paso_info_garantia"), d.get("garantia", ""))

        tk.Label(scroll, text=idiomas.t("paso_info_tipo_envio"), bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(16, 6))
        self.combo_envio = ctk.CTkOptionMenu(scroll, values=[t[1] for t in TIPOS_ENVIO], fg_color=colores.FONDO_PRINCIPAL,
                                              button_color=colores.MARCA_TEAL, button_hover_color=colores.MARCA_TEAL_HOVER, width=280)
        mapa_envio = {clave: etiqueta for clave, etiqueta in TIPOS_ENVIO}
        self.combo_envio.set(mapa_envio.get(d.get("tipo_envio", "retiro"), TIPOS_ENVIO[0][1]))
        self.combo_envio.pack(anchor="w")

    def _campo_texto(self, parent, etiqueta, valor):
        tk.Label(parent, text=etiqueta, bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 6))
        entry = ctk.CTkEntry(parent, width=560, height=38, corner_radius=8, fg_color=colores.FONDO_PRINCIPAL, text_color=colores._TEXTO)
        entry.pack(anchor="w")
        entry.insert(0, valor)
        return entry

    def _campo_texto_inline(self, parent, etiqueta, valor):
        col = tk.Frame(parent, bg=colores._CARD)
        col.pack(side="left", padx=(0, 20))
        tk.Label(col, text=etiqueta, bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        entry = ctk.CTkEntry(col, width=260, height=38, corner_radius=8, fg_color=colores.FONDO_PRINCIPAL, text_color=colores._TEXTO)
        entry.pack(anchor="w")
        entry.insert(0, valor)
        return entry

    def _campo_combo(self, parent, etiqueta, valores, actual):
        col = tk.Frame(parent, bg=colores._CARD)
        col.pack(side="left", padx=(0, 20))
        tk.Label(col, text=etiqueta, bg=colores._CARD, fg=colores._TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        combo = ctk.CTkOptionMenu(col, values=valores, width=260, fg_color=colores.FONDO_PRINCIPAL,
                                   button_color=colores.MARCA_TEAL, button_hover_color=colores.MARCA_TEAL_HOVER)
        combo.set(actual or valores[0])
        combo.pack(anchor="w")
        return combo

    def _recolectar(self):
        mapa_envio_inv = {etiqueta: clave for clave, etiqueta in TIPOS_ENVIO}
        try:
            stock = int(self.entry_stock.get().strip())
        except ValueError:
            stock = -1
        self.wizard.datos.update({
            "titulo": self.entry_titulo.get().strip(),
            "subtitulo": self.entry_subtitulo.get().strip(),
            "descripcion": self.txt_descripcion.get("1.0", "end").strip(),
            "categoria": self.combo_categoria.get(),
            "subcategoria": self.entry_subcategoria.get().strip(),
            "estado_producto": self.segmento_estado.get(),
            "marca": self.entry_marca.get().strip(),
            "modelo": self.entry_modelo.get().strip(),
            "color": self.entry_color.get().strip(),
            "material": self.entry_material.get().strip(),
            "peso": self.entry_peso.get().strip(),
            "dimensiones": self.entry_dimensiones.get().strip(),
            "stock": stock,
            "sku": self.entry_sku.get().strip(),
            "etiquetas": self.entry_etiquetas.get().strip(),
            "garantia": self.entry_garantia.get().strip(),
            "tipo_envio": mapa_envio_inv.get(self.combo_envio.get(), "retiro"),
        })