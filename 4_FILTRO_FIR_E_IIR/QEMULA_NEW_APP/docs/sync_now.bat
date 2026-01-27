@echo off
echo QEMULA Document Sync - Sincronizacao Manual
echo ===========================================

cd /d "%~dp0"

echo Verificando estrutura de arquivos...

if not exist "doc_sync\" (
    echo ERRO: Pasta doc_sync\ nao encontrada
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: Ambiente virtual nao encontrado
    pause
    exit /b 1
)

echo ✅ Estrutura verificada com sucesso
echo.
echo Executando sincronizacao de documentos...
echo.

cd doc_sync
..\.venv\Scripts\python.exe sync_integration.py --sync

echo.
echo Sincronizacao concluida!
echo.
pause
