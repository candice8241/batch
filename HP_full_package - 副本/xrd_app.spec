# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for XRD Data Post-Processing Application
用于打包XRD数据后处理GUI应用程序
"""

block_cipher = None

# 分析所有需要打包的Python文件
a = Analysis(
    ['main.py'],  # 主入口文件
    pathex=[],
    binaries=[],
    datas=[
        ('ChatGPT Image.ico', '.'),  # 应用图标
        ('ChatGPT Image.png', '.'),  # 应用图片资源
        ('resources', 'resources'),  # 资源文件夹（如果有）
    ],
    hiddenimports=[
        # GUI相关
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',

        # 科学计算
        'numpy',
        'scipy',
        'scipy.optimize',
        'scipy.signal',
        'scipy.special',
        'scipy.interpolate',
        'pandas',

        # 绘图
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_tkagg',

        # XRD专用库
        'pyFAI',
        'pyFAI.azimuthalIntegrator',
        'fabio',
        'h5py',

        # 图像处理
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'skimage',
        'cv2',

        # 峰拟合
        'lmfit',
        'peakutils',

        # 进度条
        'tqdm',

        # Excel支持
        'openpyxl',
        'xlrd',
        'xlsxwriter',

        # 自定义模块
        'theme_module',
        'powder_module',
        'radial_module',
        'single_crystal_module',
        'batch_appearance',
        'batch_integration',
        'batch_cal_volume',
        'birch_murnaghan_batch',
        'peak_fitting',
        'half_auto_fitting',
        'gui_base',
        'pyi_rth_pyFAI',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_pyFAI.py'],  # pyFAI运行时钩子
    excludes=[
        # 排除不需要的模块以减小体积
        'IPython',
        'notebook',
        'jupyter',
        'pytest',
        'sphinx',
        'pyqt5',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='XRD_PostProcessing',  # 可执行文件名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口（GUI应用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ChatGPT Image.ico',  # 应用图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='XRD_PostProcessing',  # 输出文件夹名称
)
