#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "================================================"
echo "        Instalador de Dalo (Linux)"
echo "================================================"
echo

PKG_MANAGER=""
if command -v apt-get >/dev/null 2>&1; then PKG_MANAGER="apt"
elif command -v dnf >/dev/null 2>&1; then PKG_MANAGER="dnf"
elif command -v pacman >/dev/null 2>&1; then PKG_MANAGER="pacman"
fi

# ------------------------------------------------------------
# 1) Detectar Python 3.10+
# ------------------------------------------------------------
PYTHON_BIN=""
for candidato in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidato" >/dev/null 2>&1; then
        read major minor <<< "$("$candidato" -c 'import sys; print(sys.version_info[0], sys.version_info[1])')"
        if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON_BIN="$candidato"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "No se encontró Python 3.10 o superior."
    if [ -n "$PKG_MANAGER" ]; then
        case "$PKG_MANAGER" in
            apt)    CMD="sudo apt update && sudo apt install -y python3 python3-venv python3-pip python3-tk" ;;
            dnf)    CMD="sudo dnf install -y python3 python3-pip python3-tkinter" ;;
            pacman) CMD="sudo pacman -S --noconfirm python python-pip tk" ;;
        esac
        echo "Se puede instalar con: $CMD"
        read -p "¿Instalar ahora? [s/N] " respuesta
        if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
            eval "$CMD"
            PYTHON_BIN="python3"
        else
            echo "Instalá Python manualmente y volvé a correr este script."
            exit 1
        fi
    else
        echo "No se detectó apt/dnf/pacman. Instalá Python 3.10+ (con Tk) manualmente."
        exit 1
    fi
fi
echo "Usando: $($PYTHON_BIN --version)"

# tkinter no siempre viene con Python en instalaciones mínimas de Linux
if ! "$PYTHON_BIN" -c "import tkinter" >/dev/null 2>&1; then
    echo "Falta el módulo tkinter."
    case "$PKG_MANAGER" in
        apt)    sudo apt install -y python3-tk ;;
        dnf)    sudo dnf install -y python3-tkinter ;;
        pacman) sudo pacman -S --noconfirm tk ;;
        *)      echo "Instalá el paquete de tkinter de tu distro manualmente."; exit 1 ;;
    esac
fi

# ------------------------------------------------------------
# 2) Entorno virtual
# ------------------------------------------------------------
echo
echo "------------------------------------------------"
echo "Creando entorno virtual (venv)..."
echo "------------------------------------------------"
[ -d venv ] || "$PYTHON_BIN" -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip

# ------------------------------------------------------------
# 3) Liviana vs completa
# ------------------------------------------------------------
echo
echo "================================================"
echo "  [1] LIVIANA (recomendada, ~100-150 MB)"
echo "      Sin clasificación de imágenes por IA ni"
echo "      detección de odio por IA (el resto funciona igual)."
echo "  [2] COMPLETA (~500-650 MB + modelos IA on-demand)"
echo "================================================"
read -p "Elegí una opción [1/2] (default 1): " modo
modo=${modo:-1}

echo
echo "Instalando dependencias obligatorias..."
pip install -r requirements_core.txt

if [ "$modo" = "2" ]; then
    echo "Instalando PyTorch (CPU-only)..."
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu || pip install torch torchvision
    echo "Instalando dependencias opcionales de IA..."
    pip install pysentimiento "rembg[cpu]" opencv-python-headless tkinterdnd2 || \
        echo "ADVERTENCIA: alguna opcional falló, Dalo la maneja como ausente."
fi

echo
echo "================================================"
echo "  Instalación completa. Para abrir Dalo:"
echo "  ./iniciar_dalo.sh"
echo "================================================"