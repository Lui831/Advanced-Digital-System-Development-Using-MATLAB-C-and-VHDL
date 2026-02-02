@echo off
setlocal

if not exist venv (
  python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install tensorflow numpy matplotlib scipy
python pinn_newton_cooling.py

endlocal
