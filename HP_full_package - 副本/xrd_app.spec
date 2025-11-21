# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for XRD Data Post-Processing Application
This spec file defines how to package the XRD application into a standalone executable
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the directory where this spec file is located
spec_root = os.path.abspath(SPECPATH)

# Collect all necessary data files and hidden imports
pyFAI_datas = collect_data_files('pyFAI')
fabio_datas = collect_data_files('fabio')

# Hidden imports that PyInstaller might miss
hidden_imports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.font',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'PIL',
    'PIL._tkinter_finder',
    'numpy',
    'scipy',
    'scipy.optimize',
    'scipy.interpolate',
    'scipy.ndimage',
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_tkagg',
    'pandas',
    'h5py',
    'pyFAI',
    'pyFAI.azimuthalIntegrator',
    'fabio',
    'tqdm',
    'openpyxl',
    'xlrd',
    'xlsxwriter',
    'skimage',
    'cv2',
    'lmfit',
    'peakutils',
]

# Add all submodules of key packages
hidden_imports += collect_submodules('pyFAI')
hidden_imports += collect_submodules('fabio')
hidden_imports += collect_submodules('matplotlib')

# Define all source files to include
source_files = [
    ('main.py', '.'),
    ('gui_base.py', '.'),
    ('theme_module.py', '.'),
    ('powder_module.py', '.'),
    ('radial_module.py', '.'),
    ('single_crystal_module.py', '.'),
    ('batch_integration.py', '.'),
    ('batch_cal_volume.py', '.'),
    ('batch_appearance.py', '.'),
    ('birch_murnaghan_batch.py', '.'),
    ('peak_fitting.py', '.'),
    ('half_auto_fitting.py', '.'),
    ('pyi_rth_pyFAI.py', '.'),
]

# Add resource files (icons, images, etc.)
resource_files = [
    ('resources/app_icon.ico', 'resources'),
    ('resources/README.md', 'resources'),
    ('ChatGPT Image.ico', '.'),
    ('ChatGPT Image.png', '.'),
]

# Combine all data files
datas = source_files + resource_files + pyFAI_datas + fabio_datas

a = Analysis(
    ['main.py'],
    pathex=[spec_root],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_pyFAI.py'],
    excludes=[
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='XRD_PostProcessing',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False to hide console window for GUI app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app_icon.ico',  # Application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='XRD_PostProcessing',
)
