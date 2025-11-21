# XRD数据后处理应用程序 - EXE打包说明

## 📋 项目概述

这是一个用于X射线衍射(XRD)数据后处理的GUI应用程序，包含以下功能模块：

- **粉末XRD数据处理** (powder_module.py)
- **径向积分处理** (radial_module.py)
- **单晶XRD处理** (single_crystal_module.py)
- **批量积分处理** (batch_integration.py)
- **峰拟合分析** (peak_fitting.py, half_auto_fitting.py)
- **体积计算** (batch_cal_volume.py)
- **Birch-Murnaghan方程拟合** (birch_murnaghan_batch.py)

---

## 🚀 生成EXE文件的步骤

### 方法一：使用自动化脚本（推荐）

#### Windows系统：

1. **双击运行** `build.bat` 文件
2. 等待打包完成（可能需要几分钟）
3. 打包完成后，可执行文件位于：`dist\XRD_PostProcessing\XRD_PostProcessing.exe`

#### Linux/Mac系统：

1. 打开终端，进入项目目录
2. 赋予执行权限：
   ```bash
   chmod +x build.sh
   ```
3. 运行脚本：
   ```bash
   ./build.sh
   ```
4. 打包完成后，可执行文件位于：`dist/XRD_PostProcessing/XRD_PostProcessing`

---

### 方法二：手动打包

#### 1. 安装依赖

```bash
# 安装所有依赖包
pip install -r requirements_gui.txt

# 或者仅安装核心依赖
pip install pyinstaller numpy scipy pandas matplotlib h5py pyFAI fabio tqdm Pillow
```

#### 2. 运行PyInstaller

```bash
# 使用spec文件打包（推荐）
pyinstaller --clean xrd_app.spec

# 或者使用命令行参数直接打包
pyinstaller --name XRD_PostProcessing \
            --windowed \
            --icon="ChatGPT Image.ico" \
            --add-data "ChatGPT Image.ico:." \
            --add-data "ChatGPT Image.png:." \
            --hidden-import tkinter \
            --hidden-import pyFAI \
            --hidden-import fabio \
            main.py
```

#### 3. 查看生成的文件

打包完成后，目录结构如下：

```
dist/
└── XRD_PostProcessing/
    ├── XRD_PostProcessing.exe  (Windows)
    ├── XRD_PostProcessing      (Linux/Mac)
    ├── _internal/              (依赖库文件)
    ├── ChatGPT Image.ico
    └── ChatGPT Image.png
```

---

## 📦 各个脚本文件说明

### 主程序文件

| 文件名 | 功能描述 |
|--------|----------|
| `main.py` | GUI主入口，启动应用程序 |
| `theme_module.py` | 主题样式和UI组件定义 |
| `gui_base.py` | GUI基础类 |

### 功能模块

| 文件名 | 功能描述 |
|--------|----------|
| `powder_module.py` | 粉末XRD数据处理模块 |
| `radial_module.py` | 方位角积分模块 |
| `single_crystal_module.py` | 单晶XRD处理模块 |
| `batch_integration.py` | HDF5文件批量1D积分处理 |
| `batch_cal_volume.py` | X射线衍射分析和体积计算 |
| `peak_fitting.py` | 峰拟合（Voigt/Pseudo-Voigt） |
| `half_auto_fitting.py` | 半自动峰拟合 |
| `birch_murnaghan_batch.py` | Birch-Murnaghan方程拟合 |
| `batch_appearance.py` | 批处理外观和UI组件 |

### 打包配置文件

| 文件名 | 功能描述 |
|--------|----------|
| `xrd_app.spec` | PyInstaller打包配置文件 |
| `pyi_rth_pyFAI.py` | pyFAI库运行时钩子 |
| `requirements_gui.txt` | Python依赖包列表 |
| `build.bat` | Windows自动打包脚本 |
| `build.sh` | Linux/Mac自动打包脚本 |

---

## 🔧 自定义配置

### 修改应用图标

编辑 `xrd_app.spec` 文件，修改以下行：

```python
icon='你的图标文件.ico',  # 替换为你的图标路径
```

### 修改应用名称

编辑 `xrd_app.spec` 文件，修改以下行：

```python
name='你的应用名称',  # 修改可执行文件名
```

### 添加额外资源文件

编辑 `xrd_app.spec` 文件的 `datas` 部分：

```python
datas=[
    ('ChatGPT Image.ico', '.'),
    ('你的文件或文件夹', '目标路径'),
],
```

---

## ⚠️ 常见问题

### 1. 打包失败：找不到pyFAI

**解决方案：**
```bash
pip uninstall pyFAI
pip install pyFAI --no-binary pyFAI
```

### 2. 运行时缺少DLL文件（Windows）

**解决方案：**
安装 Visual C++ Redistributable：
- 下载链接：https://aka.ms/vs/17/release/vc_redist.x64.exe

### 3. 打包后文件体积过大

**解决方案：**
在 `xrd_app.spec` 的 `excludes` 部分添加不需要的模块：

```python
excludes=[
    'IPython',
    'notebook',
    'jupyter',
    'pytest',
    # 添加其他不需要的模块
],
```

### 4. Linux下缺少系统库

**解决方案（Ubuntu/Debian）：**
```bash
sudo apt-get install python3-tk
sudo apt-get install libgl1-mesa-glx
```

**解决方案（CentOS/RHEL）：**
```bash
sudo yum install python3-tkinter
sudo yum install mesa-libGL
```

---

## 📝 打包后的使用说明

### Windows系统

1. 将 `dist\XRD_PostProcessing` 整个文件夹复制到目标位置
2. 双击 `XRD_PostProcessing.exe` 运行程序
3. 可选：创建桌面快捷方式

### Linux/Mac系统

1. 将 `dist/XRD_PostProcessing` 整个文件夹复制到目标位置
2. 在终端中运行：
   ```bash
   cd dist/XRD_PostProcessing
   ./XRD_PostProcessing
   ```

---

## 📧 联系方式

如有问题，请联系：
- lixd@ihep.ac.cn
- fzhang@ihep.ac.cn
- yswang@ihep.ac.cn
- candicewang928@gmail.com

---

## 🎯 完整打包流程示例

### Windows完整流程：

```batch
REM 1. 安装依赖
pip install -r requirements_gui.txt

REM 2. 清理旧文件
rmdir /s /q build
rmdir /s /q dist

REM 3. 打包
pyinstaller --clean xrd_app.spec

REM 4. 测试
cd dist\XRD_PostProcessing
XRD_PostProcessing.exe
```

### Linux/Mac完整流程：

```bash
# 1. 安装依赖
pip3 install -r requirements_gui.txt

# 2. 清理旧文件
rm -rf build dist

# 3. 打包
python3 -m PyInstaller --clean xrd_app.spec

# 4. 添加执行权限
chmod +x dist/XRD_PostProcessing/XRD_PostProcessing

# 5. 测试
cd dist/XRD_PostProcessing
./XRD_PostProcessing
```

---

## 📊 技术栈

- **GUI框架**: Tkinter
- **科学计算**: NumPy, SciPy, Pandas
- **数据可视化**: Matplotlib
- **XRD处理**: pyFAI, Fabio
- **图像处理**: Pillow, OpenCV, scikit-image
- **打包工具**: PyInstaller

---

## 🔄 版本更新说明

### 当前版本特性

- ✅ 支持粉末XRD、单晶XRD、径向积分处理
- ✅ 批量HDF5文件积分
- ✅ 自动峰拟合（Voigt/Pseudo-Voigt）
- ✅ Birch-Murnaghan方程拟合
- ✅ 相变分析和晶格参数计算
- ✅ 现代化的GUI界面
- ✅ 完整的可视化功能

---

**祝您打包顺利！** 🎉
