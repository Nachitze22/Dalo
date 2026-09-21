import os
import tempfile
import threading
from PIL import Image
import cloudinary_utils
try:
    from rembg import remove as _rembg_remove
except BaseException as e:
    print(f"rembg no disponible, se omitirá la eliminación de fondo: {e}")
    _rembg_remove = None
try:
    import cv2
except Exception:
    cv2 = None

class ProcesadorImagenVenta:
    def __init__(self, app):
        self.app = app

    # ================= Eliminación de fondo =================
    def eliminar_fondo(self, ruta_local, callback):
        """Corre en un thread. callback recibe una PIL.Image RGBA (con fondo
        removido si fue posible, o la imagen original si no)."""
        def procesar():
            try:
                imagen = Image.open(ruta_local).convert("RGBA")
                if _rembg_remove is not None:
                    with open(ruta_local, "rb") as f:
                        datos = f.read()
                    resultado = _rembg_remove(datos)
                    from io import BytesIO
                    imagen = Image.open(BytesIO(resultado)).convert("RGBA")
            except Exception as e:
                print(f"No se pudo eliminar el fondo (se usa imagen original): {e}")
                try:
                    imagen = Image.open(ruta_local).convert("RGBA")
                except Exception as e2:
                    print(f"Error abriendo imagen: {e2}")
                    self.app.ventana_principal.after(0, lambda: callback(None))
                    return
            self.app.ventana_principal.after(0, lambda: callback(imagen))
        threading.Thread(target=procesar, daemon=True).start()

    # ================= Cámara (captura simple, sin preview en vivo) =================
    def camara_disponible(self):
        return cv2 is not None

    def abrir_camara(self, callback):
        """Abre la cámara en un thread. callback recibe el objeto VideoCapture o None."""
        def abrir():
            camara = None
            try:
                backend = cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") else cv2.CAP_ANY
                camara = cv2.VideoCapture(0, backend)
                if not camara.isOpened():
                    camara.release()
                    camara = cv2.VideoCapture(0)
                if not camara.isOpened():
                    camara = None
            except Exception as e:
                print(f"Error abriendo cámara: {e}")
                camara = None
            self.app.ventana_principal.after(0, lambda: callback(camara))
        threading.Thread(target=abrir, daemon=True).start()

    def leer_frame(self, camara):
        """Se llama desde el hilo principal en un loop con .after(). Devuelve PIL.Image o None."""
        if camara is None or not camara.isOpened():
            return None
        ok, frame = camara.read()
        if not ok or frame is None:
            return None
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)

    def cerrar_camara(self, camara):
        if camara is not None:
            try:
                camara.release()
            except Exception:
                pass

    # ================= Subida / borrado en Cloudinary =================
    def subir_imagenes(self, imagenes_pil, identificador, callback):
        """imagenes_pil: lista de PIL.Image ya procesadas (fondo removido / recortadas).
        callback recibe lista de dicts {url, public_id} en el mismo orden, con None
        en los que fallaron."""
        def subir():
            resultados = [None] * len(imagenes_pil)
            for i, img in enumerate(imagenes_pil):
                try:
                    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                    img.convert("RGBA").save(temp.name, format="PNG")
                    temp.close()
                    url, public_id = cloudinary_utils.subir_imagen_producto(temp.name, identificador, i + 1)
                    if url:
                        resultados[i] = {"url": url, "public_id": public_id}
                    os.remove(temp.name)
                except Exception as e:
                    print(f"Error subiendo imagen {i} de la publicación: {e}")
            self.app.ventana_principal.after(0, lambda: callback(resultados))
        threading.Thread(target=subir, daemon=True).start()

    def eliminar_imagenes(self, public_ids):
        def borrar():
            for pid in public_ids:
                if pid:
                    cloudinary_utils.eliminar_imagen_producto(pid)
        threading.Thread(target=borrar, daemon=True).start()