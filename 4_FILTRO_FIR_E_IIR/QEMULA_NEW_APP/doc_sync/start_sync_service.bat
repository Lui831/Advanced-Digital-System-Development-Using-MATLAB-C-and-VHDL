@echo off
echo QEMULA Auto-Sync Service - Inicializacao Automatica
echo ====================================================

cd /d "%~dp0\.."

REM Verificar se Python esta disponivel
.venv\Scripts\python.exe --version >nul 2>&1
if errorlevel 1 (
    echo Erro: Python nao encontrado no ambiente virtual
    echo Verifique se o ambiente virtual esta configurado corretamente
    pause
    exit /b 1
)

REM Verificar se os arquivos necessarios existem
if not exist "doc_sync\docs_sync.py" (
    echo Erro: doc_sync\docs_sync.py nao encontrado
    pause
    exit /b 1
)

if not exist "doc_sync\qemula_auto_sync.py" (
    echo Erro: doc_sync\qemula_auto_sync.py nao encontrado
    pause
    exit /b 1
)

if not exist "docs\" (
    echo Erro: Pasta docs\ nao encontrada
    pause
    exit /b 1
)

if not exist "frontend\help_tab.py" (
    echo Erro: frontend\help_tab.py nao encontrado
    pause
    exit /b 1
)

echo Iniciando QEMULA Auto-Sync Service...
echo.
echo Para parar o servico, feche esta janela ou pressione Ctrl+C
echo.

REM Executar servico de sincronizacao
cd doc_sync
..\venv\Scripts\python.exe qemula_auto_sync.py

echo.
echo Servico encerrado.
pause
