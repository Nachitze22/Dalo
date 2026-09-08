import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

CARPETA_AVATARES = "dalo/avatares"


def subir_foto_perfil(ruta_local, usuario_id):
    if not cloudinary.config().cloud_name:
        print("Faltan variables de entorno de Cloudinary")
        return None, None
    try:
        resultado = cloudinary.uploader.upload(
            ruta_local,
            folder=CARPETA_AVATARES,
            public_id=f"usuario_{usuario_id}",
            overwrite=True,
            invalidate=True,
            resource_type="image",
            transformation=[{"width": 300, "height": 300, "crop": "fill", "gravity": "face"}],
        )
        return resultado.get("secure_url"), resultado.get("public_id")
    except Exception as e:
        print(f"Error subiendo foto de perfil a Cloudinary: {e}")
        return None, None


def eliminar_foto_perfil(public_id):
    if not public_id:
        return
    try:
        cloudinary.uploader.destroy(public_id, resource_type="image", invalidate=True)
    except Exception as e:
        print(f"Error eliminando foto de perfil de Cloudinary: {e}")

CARPETA_PRODUCTOS = "dalo/productos"


def subir_imagen_producto(ruta_local, identificador, orden):
    if not cloudinary.config().cloud_name:
        print("Faltan variables de entorno de Cloudinary")
        return None, None
    try:
        resultado = cloudinary.uploader.upload(
            ruta_local,
            folder=CARPETA_PRODUCTOS,
            public_id=f"prod_{identificador}_{orden}",
            overwrite=True,
            invalidate=True,
            resource_type="image",
            transformation=[{"width": 1000, "height": 1000, "crop": "limit"}],
        )
        return resultado.get("secure_url"), resultado.get("public_id")
    except Exception as e:
        print(f"Error subiendo imagen de producto a Cloudinary: {e}")
        return None, None


def eliminar_imagen_producto(public_id):
    if not public_id:
        return
    try:
        cloudinary.uploader.destroy(public_id, resource_type="image", invalidate=True)
    except Exception as e:
        print(f"Error eliminando imagen de producto de Cloudinary: {e}")