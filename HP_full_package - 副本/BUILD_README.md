# XRD 数据后处理应用程序 - 打包说明

本文档说明如何将 XRD 数据后处理应用程序打包成独立的可执行文件（.exe）。

## 📋 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细说明](#详细说明)
- [打包文件说明](#打包文件说明)
- [常见问题](#常见问题)
- [技术细节](#技术细节)

## 🖥️ 系统要求

### Windows 系统
- Windows 7 或更高版本
- Python 3.8 或更高版本
- 至少 2GB 可用磁盘空间
- 至少 4GB RAM（推荐 8GB）

### Linux/Mac 系统
- Ubuntu 18.04+, macOS 10.14+, 或其他现代 Linux 发行版
- Python 3.8 或更高版本
- 至少 2GB 可用磁盘空间
- 至少 4GB RAM（推荐 8GB）

## 🚀 快速开始

### Windows 用户

1. **双击运行打包脚本：**
   ```
   build_exe.bat
   ```
   或在命令提示符中运行：
   ```cmd
   build_exe.bat
   ```

2. **按照屏幕提示操作**
   - 脚本会自动检查 Python 环境
   - 自动安装 PyInstaller（如果需要）
   - 询问是否安装依赖包
   - 开始打包过程

3. **等待打包完成**
   - 整个过程需要 5-15 分钟
   - 完成后可执行文件位于：`dist\XRD_PostProcessing\XRD_PostProcessing.exe`

### Linux/Mac 用户

1. **在终端中运行打包脚本：**
   ```bash
   chmod +x build_exe.sh  # 如果还没有执行权限
   ./build_exe.sh
   ```

2. **按照屏幕提示操作**
   - 脚本会自动检查 Python 环境
   - 自动安装 PyInstaller（如果需要）
   - 询问是否安装依赖包
   - 开始打包过程

3. **等待打包完成**
   - 整个过程需要 5-15 分钟
   - 完成后可执行文件位于：`dist/XRD_PostProcessing/XRD_PostProcessing`

## 📚 详细说明

### 打包过程步骤

打包脚本会执行以下步骤：

1. **检查 Python 安装**
   - 验证 Python 3.8+ 是否已安装
   - 检查 pip 包管理器是否可用

2. **安装/更新 PyInstaller**
   - 如果未安装，自动安装 PyInstaller
   - 如果已安装，询问是否升级到最新版本

3. **安装依赖包（可选）**
   - 从 `requirements_gui.txt` 安装所有必需的 Python 包
   - 包括 numpy, matplotlib, pyFAI, tkinter 等

4. **清理旧文件**
   - 删除之前的 build 和 dist 目录
   - 确保全新的打包环境

5. **执行打包**
   - 使用 PyInstaller 和 `xrd_app.spec` 配置文件
   - 将所有 Python 脚本和资源文件打包成可执行文件
   - 包含所有必需的库和依赖

6. **完成**
   - 显示打包结果和文件位置
   - 可选择打开输出文件夹

### 输出文件结构

打包完成后，`dist/XRD_PostProcessing/` 文件夹包含：

```
dist/XRD_PostProcessing/
├── XRD_PostProcessing.exe (或 XRD_PostProcessing)  # 主程序
├── resources/                                        # 资源文件夹
│   ├── app_icon.ico
│   └── README.md
├── ChatGPT Image.ico                                 # 应用图标
├── ChatGPT Image.png                                 # 应用图片
├── _internal/                                        # PyInstaller 内部文件
│   ├── Python 运行时
│   ├── 所有依赖库
│   └── 其他必需文件
└── 其他 .pyd/.so 文件                                # 编译的模块
```

**重要：** 必须保持整个文件夹完整！可执行文件依赖于其他文件和 _internal 文件夹。

## 📁 打包文件说明

### 核心打包文件

| 文件名 | 用途 | 说明 |
|--------|------|------|
| `xrd_app.spec` | PyInstaller 配置文件 | 定义如何打包应用程序 |
| `build_exe.bat` | Windows 打包脚本 | 自动化打包流程（Windows）|
| `build_exe.sh` | Linux/Mac 打包脚本 | 自动化打包流程（Linux/Mac）|
| `requirements_gui.txt` | Python 依赖列表 | 所有必需的 Python 包 |

### 应用程序源文件

- `main.py` - 主程序入口
- `theme_module.py` - 主题和界面组件
- `powder_module.py` - 粉末 XRD 模块
- `radial_module.py` - 径向 XRD 模块
- `single_crystal_module.py` - 单晶 XRD 模块
- `batch_integration.py` - 批量积分模块
- `batch_cal_volume.py` - 批量体积计算
- `birch_murnaghan_batch.py` - Birch-Murnaghan 批处理
- `peak_fitting.py` - 峰拟合功能
- `half_auto_fitting.py` - 半自动拟合
- `pyi_rth_pyFAI.py` - pyFAI 运行时钩子

## ❓ 常见问题

### 1. 打包失败：找不到 Python

**问题：** `Python is not installed or not in PATH`

**解决方案：**
- 确保已安装 Python 3.8+
- Windows：重新安装 Python，勾选"Add Python to PATH"
- Linux/Mac：使用包管理器安装 python3

### 2. 打包失败：缺少依赖包

**问题：** `ModuleNotFoundError: No module named 'xxx'`

**解决方案：**
```bash
# 安装所有依赖
pip install -r requirements_gui.txt

# 或单独安装缺失的包
pip install <包名>
```

### 3. 可执行文件运行失败

**问题：** 双击 .exe 文件没有反应或立即关闭

**解决方案：**
- 从命令行运行以查看错误信息：
  ```cmd
  cd dist\XRD_PostProcessing
  XRD_PostProcessing.exe
  ```
- 检查是否有杀毒软件拦截
- 确保整个文件夹完整（包括 _internal 文件夹）

### 4. 打包后的文件太大

**问题：** 输出文件夹超过 500MB

**说明：** 这是正常的，因为包含了完整的 Python 运行时和所有科学计算库（numpy, scipy, matplotlib, pyFAI 等）。

**优化方案：**
- 可以编辑 `xrd_app.spec` 文件排除不需要的模块
- 使用 UPX 压缩（已在 spec 文件中启用）

### 5. Windows Defender 或杀毒软件警告

**问题：** 杀毒软件将可执行文件标记为可疑

**说明：** 这是 PyInstaller 打包程序的常见误报。

**解决方案：**
- 将文件添加到杀毒软件白名单
- 暂时禁用杀毒软件进行打包
- 如果分发给他人，建议进行代码签名

### 6. Linux: tkinter 相关错误

**问题：** `ImportError: No module named '_tkinter'`

**解决方案：**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (使用 Homebrew)
brew install python-tk
```

### 7. pyFAI 或 fabio 安装失败

**问题：** 在安装依赖时 pyFAI 或 fabio 失败

**解决方案：**
- Windows：安装 Microsoft C++ Build Tools
- Linux：安装编译工具
  ```bash
  # Ubuntu/Debian
  sudo apt-get install build-essential python3-dev

  # Fedora
  sudo dnf install gcc gcc-c++ python3-devel
  ```

## 🔧 技术细节

### PyInstaller 工作原理

PyInstaller 通过以下方式创建独立可执行文件：

1. **分析依赖：** 扫描 Python 代码，识别所有导入的模块
2. **收集文件：** 收集 Python 解释器、标准库和第三方包
3. **打包资源：** 包含数据文件、图标、配置文件等
4. **生成可执行文件：** 创建启动程序，在运行时解压和加载 Python 环境
5. **优化：** 使用 UPX 压缩减小文件大小

### spec 文件关键配置

```python
# 隐藏导入：确保包含所有必需模块
hiddenimports=[
    'tkinter', 'numpy', 'matplotlib', 'pyFAI', ...
]

# 数据文件：包含非代码文件
datas=[
    ('resources/*.ico', 'resources'),
    ('*.png', '.'),
]

# 控制台模式：GUI 应用设置为 False
console=False

# 图标：设置应用程序图标
icon='resources/app_icon.ico'
```

### 自定义打包选项

如果需要修改打包行为，编辑 `xrd_app.spec` 文件：

- **添加新的隐藏导入：** 在 `hiddenimports` 列表中添加
- **包含额外文件：** 在 `datas` 列表中添加
- **排除不需要的模块：** 在 `excludes` 列表中添加
- **启用/禁用控制台：** 修改 `console=True/False`
- **更改应用名称：** 修改 `name='XRD_PostProcessing'`

### 调试打包问题

如果遇到问题，可以启用调试模式：

1. 编辑 `xrd_app.spec`，设置 `debug=True`
2. 编辑打包脚本，将 `console=False` 改为 `console=True`
3. 重新打包并从命令行运行，查看详细错误信息

## 📞 支持

如有问题或需要帮助，请联系：

- 📧 lixd@ihep.ac.cn
- 📧 fzhang@ihep.ac.cn
- 📧 yswang@ihep.ac.cn

## 📄 许可证

本项目遵循项目根目录中的 LICENSE 文件。

---

**祝打包成功！✨**
