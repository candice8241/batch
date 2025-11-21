# -*- coding: utf-8 -*-
"""
PyInstaller hook for pyFAI package
Ensures all pyFAI submodules and data files are included
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules
hiddenimports = collect_submodules('pyFAI')

# Explicitly add critical pyFAI modules that may be dynamically loaded
pyfai_modules = [
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
    'pyFAI.ext.bilinear',
    'pyFAI.ext.splitBBox',
    'pyFAI.ext.splitPixel',
    'pyFAI.ext.histogram',
    'pyFAI.method_registry',
    'pyFAI.engines',
    'pyFAI.engines.preproc',
    'pyFAI.integrator',
    'pyFAI.worker',
    'pyFAI.multi_geometry',
]

hiddenimports.extend(pyfai_modules)

# Collect data files (calibration files, detector configurations, etc.)
datas = collect_data_files('pyFAI', include_py_files=False)
