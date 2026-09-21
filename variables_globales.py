import os
import json
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

intentos_login = {}
bloqueados = {}
ENVIO_GRATIS_HABILITADO = False

SEDE_DIRECCION = "Culpina 3308, Villa Soldati, Buenos Aires, Argentina"
SEDE_HORARIO = "Atención presencial: Lunes a Viernes de 9:00 a 18:00 hs."

ADMIN_EMAILS = os.getenv('ADMIN_EMAILS', '').split(',')

ARCHIVO_IDIOMA = os.path.join(BASE_DIR, "idioma.json")
IDIOMA_ACTUAL = "es"

_transform = None
_classes = None


def obtener_transform():
    """Carga torchvision recién cuando se necesita clasificar una imagen,
    no al arrancar la app."""
    global _transform
    if _transform is None:
        import torchvision.transforms as transforms
        _transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    return _transform


def obtener_classes():
    """Descarga la lista de clases de ImageNet la primera vez que hace
    falta, no al importar el módulo (evita bloquear el arranque sin
    internet)."""
    global _classes
    if _classes is None:
        import urllib.request
        url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
        try:
            _classes = urllib.request.urlopen(url, timeout=10).read().decode("utf-8").splitlines()
        except Exception as e:
            print(f"No se pudieron descargar las clases de ImageNet: {e}")
            _classes = []
    return _classes


def cargar_idioma_guardado():
    global IDIOMA_ACTUAL
    try:
        if os.path.exists(ARCHIVO_IDIOMA):
            with open(ARCHIVO_IDIOMA, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if datos.get("idioma") in ("es", "en", "fr"):
                    IDIOMA_ACTUAL = datos["idioma"]
    except Exception as e:
        print(f"No se pudo cargar el idioma guardado: {e}")
    return IDIOMA_ACTUAL


def guardar_idioma(idioma):
    global IDIOMA_ACTUAL
    if idioma not in ("es", "en", "fr"):
        return
    IDIOMA_ACTUAL = idioma
    try:
        with open(ARCHIVO_IDIOMA, "w", encoding="utf-8") as f:
            json.dump({"idioma": idioma}, f)
    except Exception as e:
        print(f"No se pudo guardar el idioma: {e}")


cargar_idioma_guardado()