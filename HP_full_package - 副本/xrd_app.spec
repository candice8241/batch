# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Specification File for XRD Data Post-Processing Application
This file configures how PyInstaller packages the XRD application into an executable
"""

block_cipher = None

# Define all Python modules that should be included
hiddenimports = [
    # Core Python modules
    'tkinter',
    'tkinter.ttk',
    'tkinter.font',
    'tkinter.filedialog',
    'tkinter.messagebox',

    # Scientific computing
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    'scipy',
    'scipy.optimize',
    'scipy.interpolate',
    'scipy.signal',
    'scipy.special',
    'pandas',

    # Plotting
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_tkagg',

    # Image processing
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'cv2',
    'skimage',

    # Data formats
    'h5py',
    'openpyxl',
    'xlrd',
    'xlsxwriter',

    # XRD specific
    'pyFAI',
    'pyFAI.azimuthalIntegrator',
    'fabio',

    # Peak fitting
    'lmfit',
    'peakutils',

    # Progress bars
    'tqdm',

    # Custom modules
    'theme_module',
    'powder_module',
    'radial_module',
    'single_crystal_module',
    'batch_appearance',
    'batch_cal_volume',
    'batch_integration',
    'birch_murnaghan_batch',
    'half_auto_fitting',
    'peak_fitting',
    'gui_base',
]

# Data files to include (icon, images, etc.)
datas = [
    ('ChatGPT Image.ico', '.'),  # Icon file
    ('ChatGPT Image.png', '.'),  # PNG icon
]

# Binary files and libraries
binaries = []

a = Analysis(
    ['main.py'],                    # Main entry point
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'IPython',
        'jupyter',
        'notebook',
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
    name='XRD_PostProcessing',        # Name of the executable
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                          # Use UPX compression
    console=False,                     # No console window (GUI app)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ChatGPT Image.ico',          # Application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='XRD_PostProcessing'          # Name of the output folder
)
