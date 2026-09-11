@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist venv (
    echo No se encontro el entorno virtual.
    echo Corre primero instalar.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python Dalo.py
if %errorlevel% neq 0 (
    echo.
    echo Dalo se cerro con un error. Revisa el mensaje de arriba.
    pause
)