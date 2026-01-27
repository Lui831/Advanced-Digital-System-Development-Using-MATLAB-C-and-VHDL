@echo off
echo =========================================
echo Building QEMULA Application with PyInstaller
echo =========================================

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller. Please install it manually:
        echo pip install pyinstaller
        pause
        exit /b 1
    )
)

REM Clean previous build
echo Cleaning previous build...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo Installing/updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Warning: Some dependencies might not have installed correctly.
    echo Please check your requirements.txt file.
)

echo.
echo Building executable...
pyinstaller --clean qemula.spec

if errorlevel 1 (
    echo.
    echo =========================================
    echo BUILD FAILED!
    echo Check the error messages above.
    echo =========================================
    pause
    exit /b 1
) else (
    echo.
    echo =========================================
    echo BUILD SUCCESSFUL!
    echo.
    echo The executable has been created in the dist folder:
    echo %cd%\dist\QEMULA_APP.exe
    echo.
    echo You can now run your application by double-clicking the executable.
    echo =========================================

    echo pyinstaller --clean qemula.spec  
)

pause
