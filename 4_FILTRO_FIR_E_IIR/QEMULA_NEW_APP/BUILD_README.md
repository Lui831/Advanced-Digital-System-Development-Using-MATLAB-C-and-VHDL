# QEMULA Application - Build Instructions

## Overview
This folder contains the QEMULA application and the necessary files to build it into a standalone executable using PyInstaller.

## Files Created for Building:
- `qemula.spec` - PyInstaller specification file
- `build.bat` - Windows batch script to build the executable
- `setup.bat` - Windows batch script to setup the environment
- `requirements.txt` - Updated with PyInstaller dependency

## Build Instructions

### Option 1: Automated Build (Recommended)

1. **Setup Environment** (first time only):
   ```cmd
   setup.bat
   ```

2. **Build Executable**:
   ```cmd
   build.bat
   ```

### Option 2: Manual Build

1. **Install PyInstaller**:
   ```cmd
   pip install pyinstaller
   ```

2. **Install Dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

3. **Build Executable**:
   ```cmd
   pyinstaller --clean qemula.spec
   ```

## Output

After a successful build:
- The executable will be located at: `dist/QEMULA_APP.exe`
- All required files (images, modules) will be bundled within the executable
- The executable can be run on Windows machines without Python installed

## Configuration Details

The `qemula.spec` file is configured to:
- Include all images from the `./images` folder
- Bundle all frontend and backend Python modules
- Include PySide6, fastcrc, and pandas dependencies
- Create a windowed application (no console window)
- Use the QEMULA icon if available

## Troubleshooting

1. **Import Errors**: If you get import errors, check that all your modules are properly structured with `__init__.py` files.

2. **Missing Files**: If images or other files are missing in the executable, verify they exist in the correct folders.

3. **Large File Size**: The executable may be large (~100-200MB) due to PySide6 and pandas. This is normal.

4. **Console Window**: If you want to see debug output, change `console=False` to `console=True` in the `qemula.spec` file.

## Distribution

The final executable (`QEMULA_APP.exe`) can be distributed to other Windows machines without requiring Python or any dependencies to be installed.
