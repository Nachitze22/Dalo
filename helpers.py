import tkinter as tk
import colores

class Helpers:
    def limitar_texto(self, texto, max_chars=30):
        if len(texto) <= max_chars:
            return texto
        return texto[:max_chars - 3] + "..."
    def ajustar_ancho(self, event):
        self.canvas.itemconfig(self.canvas_window,width=event.width)
    def mensaje_temporal(self, texto):
        label = tk.Label(self.ventana_principal,text=texto,bg=colores.FONDO_PRINCIPAL,fg="white",font=("Arial", 12))
        label.place(relx=0.5,rely=0.96,anchor="center")
        self.ventana_principal.after(2000,label.destroy)
    def formatear_precio(self, precio, moneda):
        simbolos = {
            "ARS": "$",
            "USD": "US$",
            "EUR": "€",
            "GBP": "£",
            "BRL": "R$",
            "MXN": "MX$"
        }
        simbolo = simbolos.get(moneda, moneda)
        if moneda == "ARS":
            return f"{simbolo}{precio:,.0f}".replace(",", ".")
        return f"{simbolo}{precio:,.2f}"
    def calcular_descuento_oferta(self, precio, precio_oferta):
        if not precio_oferta or precio_oferta <= 0 or precio_oferta >= precio:
            return None
        return round((1 - precio_oferta / precio) * 100)
    def detalle_oferta(self, producto, oferta):
        tipo = oferta.get("tipo")
        pct = int(oferta["valor"]) if oferta.get("valor") and tipo == "descuento" else None
        medio_pago_texto = None
        if tipo == "medio_pago":
            medio = oferta.get("medio_pago") or "el medio de pago seleccionado"
            if oferta.get("valor"):
                medio_pago_texto = f"{int(oferta['valor'])}% con {medio}"
            else:
                medio_pago_texto = f"Descuento especial con {medio}"
        cuotas_texto = None
        if oferta.get("cuotas_cantidad"):
            interes_txt = "sin interés" if not oferta.get("cuotas_interes") else "con interés"
            cuotas_texto = f"{oferta['cuotas_cantidad']} cuotas {interes_txt}"
        valido_hasta = f"Válido hasta el {oferta['fecha_fin']}" if oferta.get("fecha_fin") else None
        return {
            "pct": pct,
            "medio_pago_texto": medio_pago_texto,
            "cuotas_texto": cuotas_texto,
            "es_2x1": tipo == "2x1",
            "extra": oferta.get("etiqueta_personalizada"),
            "valido_hasta": valido_hasta,
        }