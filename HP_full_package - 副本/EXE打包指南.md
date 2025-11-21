# XRD 数据后处理应用程序 - EXE 打包完整指南

## 📋 目录
1. [项目概述](#项目概述)
2. [打包所需文件清单](#打包所需文件清单)
3. [环境准备](#环境准备)
4. [依赖安装](#依赖安装)
5. [打包步骤](#打包步骤)
6. [常见问题](#常见问题)
7. [优化建议](#优化建议)

---

## 项目概述

**项目名称**: XRD Data Post-Processing
**应用类型**: Python GUI 桌面应用
**主要功能**: X射线衍射（XRD）数据后处理
**技术栈**: Python + Tkinter + NumPy + Matplotlib + pyFAI

---

## 打包所需文件清单

### ✅ 核心文件（必需）

#### 1. Python 源代码文件
```
主程序:
├── main.py                      # 程序入口
├── gui_base.py                  # GUI 基础类
└── theme_module.py              # 主题模块

功能模块:
├── powder_module.py             # 粉末 XRD 模块
├── radial_module.py             # 径向积分模块
├── single_crystal_module.py     # 单晶 XRD 模块
├── batch_appearance.py          # 批处理外观
├── batch_cal_volume.py          # 批量体积计算
├── batch_integration.py         # 批量积分
├── birch_murnaghan_batch.py     # Birch-Murnaghan 批处理
├── half_auto_fitting.py         # 半自动拟合
└── peak_fitting.py              # 峰拟合
```

#### 2. 配置文件
```
├── xrd_app.spec                 # PyInstaller 配置文件（关键）
├── requirements_gui.txt         # Python 依赖列表
└── build.bat / build.sh         # 自动化打包脚本
```

#### 3. 资源文件
```
├── ChatGPT Image.ico            # 应用程序图标（Windows）
└── ChatGPT Image.png            # 图标备份（跨平台）
```

### 📦 打包工具

```
PyInstaller >= 5.0.0             # 核心打包工具
```

---

## 环境准备

### Windows 系统

#### 1. 安装 Python
- **推荐版本**: Python 3.8 - 3.11
- **下载地址**: https://www.python.org/downloads/
- **安装选项**:
  - ✅ 勾选 "Add Python to PATH"
  - ✅ 选择 "Install for all users"（可选）

#### 2. 验证安装
```cmd
python --version
pip --version
```

### Linux/Mac 系统

#### 1. 检查 Python
```bash
python3 --version
pip3 --version
```

#### 2. 安装缺失的包（如需要）
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk python3-pip

# macOS
brew install python-tk
```

---

## 依赖安装

### 方法一：使用 requirements.txt（推荐）

```bash
# Windows
pip install -r requirements_gui.txt

# Linux/Mac
pip3 install -r requirements_gui.txt
```

### 方法二：手动安装核心依赖

#### 必需的核心包
```bash
pip install pyinstaller>=5.0.0
pip install numpy>=1.20.0
pip install scipy>=1.7.0
pip install pandas>=1.3.0
pip install matplotlib>=3.4.0
pip install Pillow>=8.0.0
pip install h5py>=3.0.0
pip install pyFAI>=0.21.0
pip install fabio>=0.14.0
pip install tqdm>=4.60.0
```

#### 可选的扩展包
```bash
pip install openpyxl>=3.0.0       # Excel 支持
pip install xlrd>=2.0.0
pip install xlsxwriter>=3.0.0
pip install scikit-image>=0.18.0  # 图像处理
pip install opencv-python>=4.5.0
pip install lmfit>=1.0.0          # 峰拟合
pip install peakutils>=1.3.0
```

### 使用国内镜像加速（可选）

```bash
# 使用清华镜像源
pip install -r requirements_gui.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像源
pip install -r requirements_gui.txt -i https://mirrors.aliyun.com/pypi/simple/
```

---

## 打包步骤

### 🚀 快速打包（推荐新手）

#### Windows 用户
1. 双击运行 `build.bat`
2. 等待打包完成（5-10 分钟）
3. 在 `dist/XRD_PostProcessing/` 目录找到 EXE 文件

#### Linux/Mac 用户
1. 打开终端，进入项目目录
2. 执行：`bash build.sh`
3. 等待打包完成
4. 在 `dist/XRD_PostProcessing/` 目录找到可执行文件

### 🔧 手动打包（高级用户）

#### 第一步：清理旧文件
```bash
# Windows
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

# Linux/Mac
rm -rf build dist
```

#### 第二步：执行打包
```bash
# 使用 spec 文件打包
pyinstaller --clean xrd_app.spec
```

#### 第三步：验证结果
```bash
# Windows
dir dist\XRD_PostProcessing

# Linux/Mac
ls -lh dist/XRD_PostProcessing/
```

### 📝 自定义打包参数

如果需要修改 spec 文件，可以调整以下参数：

```python
# 在 xrd_app.spec 中：

# 1. 修改输出名称
name='YourAppName'

# 2. 添加隐藏导入
hiddenimports=[
    'your_module',
    ...
]

# 3. 包含额外数据文件
datas=[
    ('data_folder', 'data'),
    ('config.ini', '.'),
]

# 4. 是否显示控制台（调试用）
console=True  # 显示控制台
console=False # 隐藏控制台（GUI应用推荐）
```

---

## 常见问题

### ❌ 问题 1: PyInstaller 找不到模块

**错误信息**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**:
1. 在 `xrd_app.spec` 的 `hiddenimports` 列表中添加缺失的模块
2. 或者安装缺失的包：`pip install xxx`

### ❌ 问题 2: 打包后运行报错

**错误信息**:
```
Failed to execute script main
```

**解决方案**:
1. 使用 `console=True` 重新打包，查看错误信息
2. 检查所有相对路径是否正确
3. 确保资源文件（图标、图片）已包含在 datas 中

### ❌ 问题 3: 图标无法显示

**原因**:
- 图标文件路径硬编码（如 main.py 中的绝对路径）

**解决方案**:
修改 `main.py`，使用相对路径：

```python
import os
import sys

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller 创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 使用方法
icon_path = get_resource_path('ChatGPT Image.ico')
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)
```

### ❌ 问题 4: EXE 文件过大

**原因**:
- 包含了不必要的库

**解决方案**:
1. 在 `xrd_app.spec` 的 `excludes` 中排除不需要的包：
```python
excludes=[
    'pytest',
    'IPython',
    'jupyter',
    'notebook',
    'PyQt5',  # 如果不使用
]
```

2. 使用 UPX 压缩：
```python
upx=True  # 在 EXE() 和 COLLECT() 中启用
```

### ❌ 问题 5: pyFAI/fabio 安装失败

**原因**:
- 这些包需要编译，Windows 上可能缺少编译工具

**解决方案**:
1. 安装预编译版本：
```bash
pip install pyFAI --only-binary :all:
pip install fabio --only-binary :all:
```

2. 或使用 conda：
```bash
conda install -c conda-forge pyfai fabio
```

---

## 优化建议

### 🎯 减小 EXE 体积

1. **使用虚拟环境**（推荐）
```bash
# 创建干净的虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 只安装必需的包
pip install -r requirements_gui.txt

# 在虚拟环境中打包
pyinstaller --clean xrd_app.spec
```

2. **启用 UPX 压缩**
- 下载 UPX: https://github.com/upx/upx/releases
- 解压到系统 PATH 或 PyInstaller 目录
- spec 文件中设置 `upx=True`

3. **排除不必要的库**
```python
excludes=[
    'IPython',
    'notebook',
    'pytest',
    'sphinx',
    'setuptools',
]
```

### ⚡ 提升启动速度

1. **减少隐藏导入**
- 只导入真正需要的模块

2. **延迟加载**
- 将大型库的导入移到使用时

3. **使用单文件模式**（可选）
```bash
pyinstaller --onefile main.py
```
注意：单文件模式启动更慢，但分发更方便

### 🔒 代码保护

如果需要保护源代码：
```python
# 在 spec 文件中启用加密
block_cipher = pyi_crypto.PyiBlockCipher(key='your-secret-key')
```

---

## 完整的打包流程示例

### Windows 完整步骤

```cmd
# 1. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements_gui.txt
pip install pyinstaller

# 3. 清理旧文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

# 4. 执行打包
pyinstaller --clean xrd_app.spec

# 5. 测试运行
dist\XRD_PostProcessing\XRD_PostProcessing.exe

# 6. 打包分发
# 压缩整个 dist\XRD_PostProcessing 文件夹为 ZIP
```

### Linux/Mac 完整步骤

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip3 install -r requirements_gui.txt
pip3 install pyinstaller

# 3. 清理旧文件
rm -rf build dist

# 4. 执行打包
pyinstaller --clean xrd_app.spec

# 5. 赋予执行权限
chmod +x dist/XRD_PostProcessing/XRD_PostProcessing

# 6. 测试运行
./dist/XRD_PostProcessing/XRD_PostProcessing

# 7. 打包分发
tar -czf XRD_PostProcessing.tar.gz dist/XRD_PostProcessing/
```

---

## 分发注意事项

### Windows
- 分发整个 `dist\XRD_PostProcessing` 文件夹
- 用户可以创建 EXE 的快捷方式到桌面
- 确保用户有 Visual C++ Redistributable（大多数系统已安装）

### Linux
- 分发整个 `dist/XRD_PostProcessing` 文件夹
- 确保可执行文件有执行权限
- 可能需要安装系统依赖：`sudo apt-get install libsm6 libxext6 libxrender-dev`

### macOS
- 如需创建 .app 包，修改 spec 文件使用 BUNDLE 模式
- 需要签名和公证才能在新版 macOS 上运行

---

## 附录：完整的 spec 文件模板

详见项目中的 `xrd_app.spec` 文件。

---

## 技术支持

如遇到问题，请检查：
1. Python 版本（推荐 3.8-3.11）
2. 所有依赖是否正确安装
3. spec 文件配置是否正确
4. 查看打包日志中的错误信息

**联系方式**:
- lixd@ihep.ac.cn
- fzhang@ihep.ac.cn
- yswang@ihep.ac.cn

---

**最后更新**: 2025-11-21
