@echo off
setlocal
set "PY_SCRIPT=process_qemula_audio.py"
set "VENV_DIR=.venv"

set "BASE_DIR=%~dp0"
set "TAR_FULL=%BASE_DIR%%TAR_PATH%"
set "COMPOSE_FULL=%BASE_DIR%%COMPOSE_FILE%"
set "SCRIPT_FULL=%BASE_DIR%%PY_SCRIPT%"
set "VENV_FULL=%BASE_DIR%%VENV_DIR%"
set "VENV_PY=%VENV_FULL%\Scripts\python.exe"
set "VENV_ACTIVATE=%VENV_FULL%\Scripts\activate.bat"

echo Executando script: "%SCRIPT_FULL%"
call "%VENV_ACTIVATE%" || exit /b 1
python "%SCRIPT_FULL%" %*

endlocal
