@echo off
echo QEMULA Document Sync - Servico de Sincronizacao
echo ================================================

cd /d "%~dp0"

REM Verificar se Python esta disponivel
if exist ".venv\Scripts\python.exe" (
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    echo Erro: Ambiente virtual nao encontrado
    echo Execute setup.bat primeiro para configurar o ambiente
    pause
    exit /b 1
)

REM Verificar estrutura de arquivos
if not exist "doc_sync\" (
    echo Erro: Pasta doc_sync\ nao encontrada
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

echo Iniciando servico de sincronizacao...
echo.
echo Comandos disponiveis:
echo   sync     - Sincronizar documentos manualmente
echo   service  - Iniciar servico automatico
echo   status   - Verificar status dos documentos
echo   help     - Mostrar ajuda
echo.

:MENU
set /p "choice=Digite o comando desejado (ou 'quit' para sair): "

if /i "%choice%"=="quit" (
    echo Encerrando...
    goto :EOF
)

if /i "%choice%"=="sync" (
    echo.
    echo Executando sincronizacao manual...
    cd doc_sync
    ..\venv\Scripts\python.exe sync_integration.py --sync
    cd ..
    echo.
    goto :MENU
)

if /i "%choice%"=="service" (
    echo.
    echo Iniciando servico automatico...
    echo Pressione Ctrl+C para parar o servico
    echo.
    cd doc_sync
    ..\venv\Scripts\python.exe qemula_auto_sync.py
    cd ..
    echo.
    goto :MENU
)

if /i "%choice%"=="status" (
    echo.
    echo Verificando status da documentacao...
    cd doc_sync
    ..\venv\Scripts\python.exe sync_integration.py --status
    cd ..
    echo.
    goto :MENU
)

if /i "%choice%"=="help" (
    echo.
    echo QEMULA Document Sync - Sistema de Sincronizacao
    echo ================================================
    echo.
    echo Comandos disponiveis:
    echo   sync     - Sincroniza documentos .docx com help_tab.py
    echo   service  - Inicia monitoramento automatico de mudancas
    echo   status   - Mostra status atual dos documentos
    echo   help     - Exibe esta ajuda
    echo   quit     - Sair do programa
    echo.
    echo O sistema monitora a pasta docs/ e atualiza automaticamente
    echo o frontend/help_tab.py quando documentos .docx sao modificados.
    echo.
    goto :MENU
)

echo Comando nao reconhecido: %choice%
echo Digite 'help' para ver os comandos disponiveis.
echo.
goto :MENU
