@echo off
echo =========================================
echo QEMULA Application - Setup Environment
echo =========================================

echo Installing PyInstaller and dependencies...
pip install pyinstaller

echo.
echo Installing application requirements...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To build the executable, run: build.bat
echo.
pause
