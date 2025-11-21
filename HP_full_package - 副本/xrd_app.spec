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
    'scipy.ndimage',
    'pandas',

    # Plotting
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.figure',

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

    # XRD specific - pyFAI modules
    'pyFAI',
    'pyFAI.azimuthalIntegrator',
    'pyFAI.geometry',
    'pyFAI.detectors',
    'pyFAI.calibrant',
    'pyFAI.units',
    'pyFAI.io',
    'pyFAI.utils',
    'pyFAI.utils.decorators',
    'pyFAI.utils.mathutil',
    'pyFAI.utils.stringutil',
    'pyFAI.ext',
    'pyFAI.method_registry',
    'pyFAI.engines',
    'pyFAI.engines.preproc',

    # fabio - main module
    'fabio',
    'fabio.fabioimage',
    'fabio.openimage',

    # fabio - all image format modules (CRITICAL - these are dynamically imported)
    'fabio.pilatusimage',      # Pilatus detector
    'fabio.edfimage',          # EDF format
    'fabio.tifimage',          # TIFF format
    'fabio.marccdimage',       # MarCCD detector
    'fabio.cbfimage',          # CBF format
    'fabio.brukerimage',       # Bruker format
    'fabio.bruker100image',
    'fabio.mar345image',       # MAR345 detector
    'fabio.fit2dmaskimage',    # Fit2D mask
    'fabio.kcdimage',          # KCD format
    'fabio.dm3image',          # Digital Micrograph
    'fabio.OXDimage',          # Oxford Diffraction
    'fabio.adscimage',         # ADSC detector
    'fabio.raxisimage',        # Rigaku R-Axis
    'fabio.numpyimage',        # NumPy arrays
    'fabio.fit2dspreadsheetimage',
    'fabio.hdf5image',         # HDF5 format
    'fabio.jpeg2kimage',       # JPEG2000
    'fabio.mrcimage',          # MRC format
    'fabio.pnmimage',          # PNM format
    'fabio.limaimage',
    'fabio.speimage',          # SPE format
    'fabio.xsdimage',          # XSD format
    'fabio.binaryimage',
    'fabio.pixiimage',
    'fabio.dtrekimage',
    'fabio.esperantoimage',
    'fabio.eigerimage',        # Dectris Eiger
    'fabio.mpaimage',
    'fabio.gfrimage',
    'fabio.eigerimage',
    'fabio.fabioformats',      # Format registry
    'fabio.compression',       # Compression support

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
    hookspath=['hooks'],            # Custom hooks for fabio and pyFAI
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
