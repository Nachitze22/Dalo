#!/usr/bin/env bash
cd "$(dirname "$0")"

if [ ! -d venv ]; then
    echo "No se encontró el entorno virtual. Corré primero: ./install.sh"
    exit 1
fi

source venv/bin/activate
python Dalo.py
estado=$?
if [ $estado -ne 0 ]; then
    echo
    echo "Dalo se cerró con un error. Revisá el mensaje de arriba."
    read -p "Presioná Enter para salir..."
fi