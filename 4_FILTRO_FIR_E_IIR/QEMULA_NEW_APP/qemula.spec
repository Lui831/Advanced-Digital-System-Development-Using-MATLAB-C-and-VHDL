# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Get the directory containing this spec file
spec_root = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

# Define the main script
main_script = os.path.join(spec_root, 'main.py')

# Collect all Python files from frontend and backend directories
added_files = []

# Add images directory
images_path = os.path.join(spec_root, 'images')
if os.path.exists(images_path):
    for img_file in os.listdir(images_path):
        if img_file.endswith(('.png', '.jpg', '.jpeg', '.ico', '.gif')):
            added_files.append((os.path.join(images_path, img_file), 'images'))

# Add frontend modules
frontend_path = os.path.join(spec_root, 'frontend')
if os.path.exists(frontend_path):
    for py_file in os.listdir(frontend_path):
        if py_file.endswith('.py') and not py_file.startswith('__'):
            added_files.append((os.path.join(frontend_path, py_file), 'frontend'))

# Add backend modules  
backend_path = os.path.join(spec_root, 'backend')
if os.path.exists(backend_path):
    for py_file in os.listdir(backend_path):
        if py_file.endswith('.py') and not py_file.startswith('__'):
            added_files.append((os.path.join(backend_path, py_file), 'backend'))

# Add data directory if it exists
data_path = os.path.join(spec_root, 'data')
if os.path.exists(data_path):
    for data_file in os.listdir(data_path):
        if not data_file.startswith('__'):
            added_files.append((os.path.join(data_path, data_file), 'data'))

# Add nginx.conf if it exists
nginx_conf_path = os.path.join(spec_root, 'nginx.conf')
if os.path.exists(nginx_conf_path):
    added_files.append((nginx_conf_path, '.'))

# Hidden imports for PySide6 and other dependencies
hidden_imports = [
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'fastcrc',
    'pandas',
    'numpy',  # pandas dependency
    'threading',
    'time',
    'sys',
    'os',
    'frontend.control_tab',
    'frontend.docker_tab',
    'frontend.settings_tab',
    'frontend.transciever_spw_tab',
    'frontend.transciever_uart_tab',
    'frontend.help_tab',
    'backend.protocol_interface',
    'backend.docker',
    'backend.reciever_uart',
    'backend.reciever'
]

a = Analysis(
    [main_script],
    pathex=[spec_root],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QEMULA_APP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see console output for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_root, 'images', 'qemula.png') if os.path.exists(os.path.join(spec_root, 'images', 'qemula.png')) else None,
)
