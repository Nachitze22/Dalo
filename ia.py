import torch
from torchvision import models
import threading
import time
import variables_globales
import productos
from better_profanity import profanity
import requests
import os
from PIL import Image
try:
    from pysentimiento import create_analyzer
except Exception:
    create_analyzer = None

class IA:
    def __init__(self, app):
        self.app = app
        self.modelo = None
        self.modelo_cargando = False
        profanity.load_censor_words()
        profanity.add_censor_words([
        "boludo",
        "pelotudo",
        "forro",
        "concha",
        "trolo",
        "mogolico",
        "mogólico",
        "puto",
        "puta",
        "cornudo",
        "gordo",
        "idiota",
        "imbecil",
        "imbécil",
        "estupido",
        "estúpido",
        "tarado",
        "gil"])
        self.modelo_odio = None
        self.modelo_odio_cargando = False
    def cargar_modelo_async(self):
        if self.modelo is not None or self.modelo_cargando:
            return
        self.modelo_cargando = True
        def load():
            modelo = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
            modelo.eval()
            modelo.to("cpu")
            self.modelo = modelo
            self.modelo_cargando = False
            print("Modelo cargado")
        threading.Thread(target=load, daemon=True).start()
    def clasificar_imagen_sync(self, producto):
        if self.modelo is None:
            self.cargar_modelo_async()
            while self.modelo is None:
                time.sleep(0.1)
        img = self.app.obtener_imagen(producto["imagen"]).convert("RGB")
        img = variables_globales.transform(img).unsqueeze(0)
        with torch.no_grad():
            outputs = self.modelo(img)
        _, predicted = outputs.max(1)
        etiqueta = variables_globales.classes[predicted.item()].lower()
        return etiqueta
    def clasificar_imagen(self, producto):
        if self.modelo is None:
            self.cargar_modelo_async()
            if not self.modelo_cargando:
                self.app.mensaje_temporal("Cargando IA...")
            return "cargando_modelo"
        try:
            img = self.app.obtener_imagen(producto["imagen"]).convert("RGB")
        except Exception as e:
            print(e)
            return "error_imagen"
        img = variables_globales.transform(img).unsqueeze(0)
        with torch.no_grad():
            outputs = self.modelo(img)
        _, predicted = outputs.max(1)
        etiqueta = variables_globales.classes[predicted.item()].lower()
        print(f"[IA] {producto['nombre']} -> {etiqueta}")
        return etiqueta
    def filtrar_hibrido(self, categoria):
        resultados = []
        for producto in self.app.productos_db.obtener_todos():
            if producto["categoria"]:
                if producto["categoria"] == categoria:
                    resultados.append(producto["id"])
                continue
            categoria_texto = productos.detectar_categoria_texto(producto["nombre"])
            if categoria_texto:
                self.app.productos_db.actualizar_categoria(producto["id"],categoria_texto)
                if categoria_texto == categoria:
                    resultados.append(producto["id"])
                continue
            etiqueta = self.clasificar_imagen_sync(producto)
            categoria_detectada = None
            for categoria_sql, palabras in productos.MAPEO_CATEGORIAS.items():
                if any(palabra in etiqueta for palabra in palabras):
                    categoria_detectada = categoria_sql
                    break
            if categoria_detectada:
                self.app.productos_db.actualizar_categoria(producto["id"],categoria_detectada)
                if categoria_detectada == categoria:
                    resultados.append(producto["id"])
        return resultados
    def nombre_ofensivo(self, nombre):
        return profanity.contains_profanity(nombre)
    def cargar_modelo_odio_async(self):
        if create_analyzer is None or self.modelo_odio is not None or self.modelo_odio_cargando:
            return
        self.modelo_odio_cargando = True
        def cargar():
            try:
                self.modelo_odio = create_analyzer(task="hate_speech", lang="es")
                print("Modelo de detección de odio cargado")
            except Exception as e:
                print(f"Error cargando modelo de odio: {e}")
            finally:
                self.modelo_odio_cargando = False
        threading.Thread(target=cargar, daemon=True).start()

    def comentario_ofensivo_ia(self, texto, callback):
        def analizar():
            if create_analyzer is None:
                self.app.ventana_principal.after(0, lambda: callback(False))
                return
            if self.modelo_odio is None:
                self.cargar_modelo_odio_async()
                while self.modelo_odio is None and self.modelo_odio_cargando:
                    time.sleep(0.1)
            if self.modelo_odio is None:
                self.app.ventana_principal.after(0, lambda: callback(False))
                return
            try:
                resultado = self.modelo_odio.predict(texto)
                es_ofensivo = (
                    resultado.probas.get("hateful", 0) > 0.5
                    or resultado.probas.get("aggressive", 0) > 0.5
                )
            except Exception as e:
                print(f"Error analizando comentario: {e}")
                es_ofensivo = False
            self.app.ventana_principal.after(0, lambda: callback(es_ofensivo))
        threading.Thread(target=analizar, daemon=True).start()

    def verificar_direccion(self, datos, callback):
        def analizar():
            direccion_completa = datos.get("direccion_completa", "")
            es_valida = True
            mensaje = "Dirección verificada correctamente."
            try:
                respuesta = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": direccion_completa, "format": "json", "limit": 1, "countrycodes": "ar"},
                    headers={"User-Agent": "Dalo-App/1.0 (verificacion-direcciones)"},
                    timeout=8,
                )
                respuesta.raise_for_status()
                resultados = respuesta.json()
                if not resultados:
                    es_valida = False
                    mensaje = "No pudimos encontrar esa dirección. Revisá los datos e intentá nuevamente."
            except Exception as e:
                print(f"Error verificando dirección: {e}")
                es_valida = True
                mensaje = "No se pudo verificar la dirección en este momento, pero fue guardada."
            self.app.ventana_principal.after(0, lambda: callback(es_valida, mensaje))
        threading.Thread(target=analizar, daemon=True).start()
    # ================= Moderación de foto de perfil =================
    FORMATOS_PERFIL_PERMITIDOS = {"JPEG", "PNG", "WEBP"}
    TAMANO_MAXIMO_PERFIL_BYTES = 5 * 1024 * 1024
    DIMENSION_MINIMA_PERFIL = 100

    def verificar_imagen_perfil(self, ruta, callback):
        def analizar():
            try:
                tamano = os.path.getsize(ruta)
                if tamano > self.TAMANO_MAXIMO_PERFIL_BYTES:
                    self.app.ventana_principal.after(0, lambda: callback(False, "La imagen no puede pesar más de 5 MB."))
                    return
                with Image.open(ruta) as img:
                    img.verify()
                with Image.open(ruta) as img:
                    formato = (img.format or "").upper()
                    ancho, alto = img.size
                if formato not in self.FORMATOS_PERFIL_PERMITIDOS:
                    self.app.ventana_principal.after(0, lambda: callback(False, "Formato no soportado. Usá JPG, PNG o WEBP."))
                    return
                if ancho < self.DIMENSION_MINIMA_PERFIL or alto < self.DIMENSION_MINIMA_PERFIL:
                    self.app.ventana_principal.after(0, lambda: callback(False, "La imagen es demasiado pequeña."))
                    return
                # TODO: acá se conectaría un modelo de moderación de contenido
                # (NSFW / ofensivo) cuando esté disponible. Hoy se valida
                # integridad, formato y tamaño.
                es_valida, mensaje = True, "Imagen verificada correctamente."
            except Exception as e:
                print(f"Error verificando imagen de perfil: {e}")
                es_valida, mensaje = True, "No se pudo analizar completamente la imagen, pero fue guardada."
            self.app.ventana_principal.after(0, lambda: callback(es_valida, mensaje))
        threading.Thread(target=analizar, daemon=True).start()
        
    # ================= Moderación de publicaciones (Paso 6 del wizard) =================
    def moderar_publicacion(self, datos, callback):
        def analizar():
            textos = " ".join(filter(None, [
                datos.get("titulo"), datos.get("subtitulo"), datos.get("descripcion"),
                datos.get("marca"), datos.get("etiquetas"),
            ]))
            es_ofensivo = False
            try:
                if self.nombre_ofensivo(textos):
                    es_ofensivo = True
            except Exception as e:
                print(f"Error en filtro de palabras (moderación publicación): {e}")

            errores = []
            if len((datos.get("titulo") or "")) < 10:
                errores.append("El título debe tener al menos 10 caracteres.")
            if len((datos.get("descripcion") or "")) < 100:
                errores.append("La descripción debe tener al menos 100 caracteres.")
            if not datos.get("imagenes") or len(datos["imagenes"]) < 3:
                errores.append("Necesitás al menos 3 imágenes del producto.")
            if not datos.get("precio") or datos["precio"] <= 0:
                errores.append("El precio debe ser mayor a cero.")
            if datos.get("stock") is None or datos.get("stock") < 0:
                errores.append("El stock ingresado no es válido.")
            if not datos.get("medios_pago"):
                errores.append("Elegí al menos un medio de pago.")
            if not datos.get("ficha_tecnica"):
                errores.append("Completá al menos un atributo en la ficha técnica.")

            if es_ofensivo:
                errores.append("Encontramos lenguaje inapropiado en el título, subtítulo o descripción.")

            def analizar_ia_odio():
                if create_analyzer is None:
                    self.app.ventana_principal.after(0, lambda: callback(len(errores) == 0, errores))
                    return
                if self.modelo_odio is None:
                    self.cargar_modelo_odio_async()
                    while self.modelo_odio is None and self.modelo_odio_cargando:
                        time.sleep(0.1)
                extra_ofensivo = False
                if self.modelo_odio is not None:
                    try:
                        resultado = self.modelo_odio.predict(textos)
                        extra_ofensivo = (
                            resultado.probas.get("hateful", 0) > 0.5
                            or resultado.probas.get("aggressive", 0) > 0.5
                        )
                    except Exception as e:
                        print(f"Error analizando publicación con IA de odio: {e}")
                if extra_ofensivo:
                    errores.append("Nuestra IA detectó posible contenido ofensivo en el texto de la publicación.")
                self.app.ventana_principal.after(0, lambda: callback(len(errores) == 0, errores))

            analizar_ia_odio()
        threading.Thread(target=analizar, daemon=True).start()