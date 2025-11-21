# -*- coding: utf-8 -*-
"""
PyInstaller hook for fabio package
Ensures all image format modules are included in the build
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of fabio
# This is crucial because fabio uses dynamic imports for image format handlers
hiddenimports = collect_submodules('fabio')

# Explicitly add all known fabio image format modules
# These are registered at runtime via fabio.fabioformats.register_default_formats()
fabio_formats = [
    'fabio.pilatusimage',        # Pilatus detector images
    'fabio.edfimage',            # ESRF Data Format
    'fabio.tifimage',            # TIFF images
    'fabio.marccdimage',         # MarCCD detector
    'fabio.cbfimage',            # Crystallographic Binary Files
    'fabio.brukerimage',         # Bruker formats
    'fabio.bruker100image',      # Bruker 100
    'fabio.mar345image',         # MAR345 image plate
    'fabio.fit2dmaskimage',      # Fit2D mask format
    'fabio.kcdimage',            # Nonius KappaCCD
    'fabio.dm3image',            # Digital Micrograph 3
    'fabio.OXDimage',            # Oxford Diffraction
    'fabio.adscimage',           # ADSC Quantum
    'fabio.raxisimage',          # Rigaku R-Axis
    'fabio.numpyimage',          # NumPy array format
    'fabio.fit2dspreadsheetimage',
    'fabio.hdf5image',           # HDF5 images
    'fabio.jpeg2kimage',         # JPEG 2000
    'fabio.mrcimage',            # MRC format
    'fabio.pnmimage',            # Portable aNyMap
    'fabio.limaimage',           # Lima format
    'fabio.speimage',            # Princeton SPE format
    'fabio.xsdimage',            # XSD format
    'fabio.binaryimage',         # Binary format
    'fabio.pixiimage',           # PIXI format
    'fabio.dtrekimage',          # d*TREK format
    'fabio.esperantoimage',      # Esperanto format
    'fabio.eigerimage',          # Dectris Eiger
    'fabio.mpaimage',            # MPA format
    'fabio.gfrimage',            # GFR format
    'fabio.fabioformats',        # Format registry (CRITICAL)
    'fabio.compression',         # Compression utilities
    'fabio.fabioutils',          # Utilities
    'fabio.openimage',           # Image opening utilities
]

# Add all format modules to hiddenimports
hiddenimports.extend(fabio_formats)

# Collect any data files (if fabio has config files, etc.)
datas = collect_data_files('fabio', include_py_files=True)
