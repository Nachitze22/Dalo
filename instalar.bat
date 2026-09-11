@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo        Instalador de Dalo
echo ================================================
echo.

REM ------------------------------------------------------------
REM 1) Verificar si Python esta instalado (y version minima 3.10)
REM ------------------------------------------------------------
set PYTHON_OK=0
where python >nul 2>nul
if %errorlevel%==0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VERSION=%%v
    echo Python detectado: !PY_VERSION!
    set PYTHON_OK=1
)

if !PYTHON_OK!==0 (
    echo Python no fue encontrado en este equipo.
    echo Descargando el instalador oficial de Python 3.12...
    set PY_INSTALLER=%TEMP%\python_installer.exe
    powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe' -OutFile '%PY_INSTALLER%' -UseBasicParsing } catch { exit 1 }"
    if not exist "%PY_INSTALLER%" (
        echo.
        echo ERROR: no se pudo descargar el instalador de Python.
        echo Revisa tu conexion a internet e intenta nuevamente.
        pause
        exit /b 1
    )

    echo Instalando Python en segundo plano ^(silencioso^)...
    "%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_test=0
    del "%PY_INSTALLER%" >nul 2>nul

    REM Refrescar PATH de la sesion actual
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"

    where python >nul 2>nul
    if !errorlevel! neq 0 (
        echo.
        echo ERROR: Python se instalo pero no se detecta en el PATH.
        echo Cerra esta ventana, abri una consola nueva y volve a correr instalar.bat
        pause
        exit /b 1
    )
    echo Python instalado correctamente.
)

echo.
echo ------------------------------------------------
echo Creando entorno virtual ^(venv^)...
echo ------------------------------------------------
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo.
echo ------------------------------------------------
echo Actualizando pip...
echo ------------------------------------------------
python -m pip install --upgrade pip

echo.
echo ------------------------------------------------
echo Instalando PyTorch ^(build CPU-only, liviana^)...
echo   ^(si instalaramos torch normal bajaria soporte CUDA
echo    de mas de 1.5 GB que no usas sin placa de video^)
echo ------------------------------------------------
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
if %errorlevel% neq 0 (
    echo.
    echo ADVERTENCIA: fallo la instalacion CPU-only de torch.
    echo Reintentando con la version estandar de PyPI...
    pip install torch torchvision
)

echo.
echo ------------------------------------------------
echo Instalando el resto de las dependencias...
echo ------------------------------------------------
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ADVERTENCIA: alguna dependencia opcional pudo haber fallado.
    echo Reintentando solo con las dependencias obligatorias...
    for /f "usebackq delims=" %%l in ("requirements_core.txt") do (
        pip install %%l
    )
)

echo.
echo ================================================
echo   Instalacion completa.
echo   Para abrir Dalo, ejecuta: iniciar_dalo.bat
echo ================================================
pause