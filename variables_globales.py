import torch
import torchvision.transforms as transforms
from torchvision import models
import urllib.request
import os
import json
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
transform = transforms.Compose([transforms.Resize((224, 224)),transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225])])
intentos_login = {}
bloqueados = {}
url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
classes = urllib.request.urlopen(url).read().decode("utf-8").splitlines()
ENVIO_GRATIS_HABILITADO = False

# ── Sede / entrega (compartido entre VistaProducto y VistaComprar) ────────────
SEDE_DIRECCION = "Culpina 3308, Villa Soldati, Buenos Aires, Argentina"
SEDE_HORARIO = "Atención presencial: Lunes a Viernes de 9:00 a 18:00 hs."
# ── Administración de cupones ─────────────────────────────────────────────────
ADMIN_EMAILS = {"nacho.ignacio.2208@gmail.com"}  # ← poné acá tu email real de admin

# ── Idioma de la app (persiste en un archivo local; se sobreescribe con
# el idioma guardado del usuario al iniciar sesión) ────────────────────────────
ARCHIVO_IDIOMA = os.path.join(BASE_DIR, "idioma.json")
IDIOMA_ACTUAL = "es"

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