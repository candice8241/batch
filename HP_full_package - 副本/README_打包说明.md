# XRD 数据后处理应用程序 - 快速打包指南

## 📦 快速开始

### Windows 用户

```cmd
# 1. 检查依赖
python check_dependencies.py

# 2. 一键打包
build.bat
```

### Linux/Mac 用户

```bash
# 1. 检查依赖
python3 check_dependencies.py

# 2. 一键打包
bash build.sh
```

## 📋 核心文件清单

### ✅ 必需文件（已包含）

```
打包配置:
├── xrd_app.spec              # PyInstaller 配置（核心）
├── build.bat                 # Windows 打包脚本
├── build.sh                  # Linux/Mac 打包脚本
├── requirements_gui.txt      # Python 依赖列表
├── check_dependencies.py     # 依赖检查工具
└── hooks/                    # PyInstaller hook 文件（重要！）
    ├── hook-fabio.py         # fabio 动态导入处理
    └── hook-pyFAI.py         # pyFAI 动态导入处理

资源文件:
├── ChatGPT Image.ico         # 应用图标
└── ChatGPT Image.png         # 图标备份

Python 源码:
├── main.py                   # 主程序入口
├── gui_base.py               # GUI 基础
├── theme_module.py           # 主题模块
├── powder_module.py          # 粉末 XRD
├── radial_module.py          # 径向积分
├── single_crystal_module.py  # 单晶 XRD
├── batch_appearance.py
├── batch_cal_volume.py
├── batch_integration.py
├── birch_murnaghan_batch.py
├── half_auto_fitting.py
└── peak_fitting.py
```

## 🔧 打包前准备

### 1. 安装 Python

- **版本要求**: Python 3.8 - 3.11
- **下载**: https://www.python.org/downloads/
- **注意**: 安装时勾选 "Add Python to PATH"

### 2. 安装依赖

```bash
# 方法一：使用 requirements.txt（推荐）
pip install -r requirements_gui.txt

# 方法二：手动安装核心包
pip install pyinstaller numpy scipy pandas matplotlib h5py pyFAI fabio tqdm Pillow

# 使用国内镜像加速（可选）
pip install -r requirements_gui.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 验证依赖

```bash
python check_dependencies.py
```

看到 "✓ 所有必需组件已就绪" 即可开始打包。

## 🚀 执行打包

### 自动打包（推荐）

**Windows**:
```cmd
build.bat
```

**Linux/Mac**:
```bash
bash build.sh
```

### 手动打包

```bash
# 清理旧文件
rm -rf build dist

# 执行打包
pyinstaller --clean xrd_app.spec

# 查看结果
ls -lh dist/XRD_PostProcessing/
```

## 📂 打包输出

```
dist/
└── XRD_PostProcessing/
    ├── XRD_PostProcessing.exe  (Windows)
    ├── XRD_PostProcessing      (Linux/Mac)
    ├── ChatGPT Image.ico
    ├── ChatGPT Image.png
    └── [各种依赖库文件...]
```

**重要**: 分发时需要整个 `XRD_PostProcessing` 文件夹，不能只复制 EXE 文件！

## 🐛 常见问题

### ⚠️ 问题 1: ModuleNotFoundError: No module named 'fabio.pilatusimage'

**这是最常见的错误！**

**原因**: fabio 库动态导入图像格式模块，PyInstaller 无法自动检测。

**解决方案**:
- ✅ 已在 `xrd_app.spec` 中添加所有 fabio 格式模块
- ✅ 已创建 `hooks/hook-fabio.py` 自动处理
- 🔧 使用更新后的配置重新打包即可

详细说明请查看：**`常见打包错误解决方案.md`**

### 问题 2: PyInstaller 找不到

```bash
pip install pyinstaller
```

### 问题 3: 打包后运行报错

1. 修改 `xrd_app.spec`，将 `console=False` 改为 `console=True`
2. 重新打包查看错误信息
3. 通常是缺少隐藏导入，在 `hiddenimports` 中添加

### 问题 4: 图标不显示

原因：`main.py` 中使用了硬编码的绝对路径

解决：修改 `main.py`，使用 `get_resource_path()` 函数（见详细文档）

### 问题 5: EXE 过大

1. 使用虚拟环境打包（只包含必需的库）
2. 启用 UPX 压缩（spec 文件中 `upx=True`）
3. 排除不必要的包（修改 `excludes` 列表）

### 问题 6: pyFAI/fabio 安装失败

Windows 用户可能需要：

```bash
# 使用预编译版本
pip install pyFAI --only-binary :all:
pip install fabio --only-binary :all:

# 或使用 conda
conda install -c conda-forge pyfai fabio
```

## 📖 详细文档

更多信息请参考：
- **完整指南**: `EXE打包指南.md`
- **错误解决**: `常见打包错误解决方案.md` ⭐ 强烈推荐
- **配置详解**: `xrd_app.spec` 文件注释

## 📧 技术支持

- lixd@ihep.ac.cn
- fzhang@ihep.ac.cn
- yswang@ihep.ac.cn

---

**最后更新**: 2025-11-21
