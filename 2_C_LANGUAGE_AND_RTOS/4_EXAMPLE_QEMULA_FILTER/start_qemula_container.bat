@echo off
setlocal
set "TAR_PATH=qemula_system.tar"
set "COMPOSE_FILE=docker-compose.yml"
set "PY_SCRIPT=qemula_interface.py"
set "VENV_DIR=.venv"

set "BASE_DIR=%~dp0"
set "TAR_FULL=%BASE_DIR%%TAR_PATH%"
set "COMPOSE_FULL=%BASE_DIR%%COMPOSE_FILE%"
set "SCRIPT_FULL=%BASE_DIR%%PY_SCRIPT%"
set "VENV_FULL=%BASE_DIR%%VENV_DIR%"
set "VENV_PY=%VENV_FULL%\Scripts\python.exe"

if not exist "%TAR_FULL%" (
  echo Arquivo .tar nao encontrado: "%TAR_FULL%"
  exit /b 1
)
if not exist "%COMPOSE_FULL%" (
  echo docker-compose.yml nao encontrado: "%COMPOSE_FULL%"
  exit /b 1
)
if not exist "%SCRIPT_FULL%" (
  echo Script Python nao encontrado: "%SCRIPT_FULL%"
  exit /b 1
)

echo Carregando imagem Docker: "%TAR_FULL%"
docker load -i "%TAR_FULL%" || exit /b 1

echo Inicializando container com docker compose
docker compose version >nul 2>&1
if %errorlevel%==0 (
  docker compose -f "%COMPOSE_FULL%" up -d || exit /b 1
) else (
  docker-compose -f "%COMPOSE_FULL%" up -d || exit /b 1
)

if not exist "%VENV_PY%" (
  echo Criando venv em: "%VENV_FULL%"
  where py >nul 2>&1
  if %errorlevel%==0 (
    py -3 -m venv "%VENV_FULL%" || exit /b 1
  ) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
      python -m venv "%VENV_FULL%" || exit /b 1
    ) else (
      echo Python nao encontrado no PATH.
      exit /b 1
    )
  )
)

echo Instalando dependencias: fastcrc, csv
"%VENV_PY%" -m pip install --upgrade pip || exit /b 1
"%VENV_PY%" -m pip install fastcrc pandas numpy || exit /b 1

echo Executando script: "%SCRIPT_FULL%"
"%VENV_PY%" "%SCRIPT_FULL%"

endlocal
