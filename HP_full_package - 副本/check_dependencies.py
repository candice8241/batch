#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖检查脚本 - XRD Data Post-Processing Application
在打包前运行此脚本，确保所有必需的依赖都已正确安装
"""

import sys
import importlib
from importlib.metadata import version, PackageNotFoundError

# ANSI 颜色代码（Windows 10+ 和 Linux/Mac 支持）
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
except ImportError:
    GREEN = RED = YELLOW = BLUE = RESET = ''

# 必需的核心依赖
REQUIRED_PACKAGES = {
    'pyinstaller': '5.0.0',
    'numpy': '1.20.0',
    'scipy': '1.7.0',
    'pandas': '1.3.0',
    'matplotlib': '3.4.0',
    'Pillow': '8.0.0',
    'h5py': '3.0.0',
    'pyFAI': '0.21.0',
    'fabio': '0.14.0',
    'tqdm': '4.60.0',
}

# 推荐的可选依赖
OPTIONAL_PACKAGES = {
    'openpyxl': '3.0.0',
    'xlrd': '2.0.0',
    'xlsxwriter': '3.0.0',
    'scikit-image': '0.18.0',
    'opencv-python': '4.5.0',
    'lmfit': '1.0.0',
    'peakutils': '1.3.0',
}

# Python 内置模块（需要检查可导入性）
BUILTIN_MODULES = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.font',
    'ctypes',
]

# 项目自定义模块
CUSTOM_MODULES = [
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


def check_python_version():
    """检查 Python 版本"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{'Python 环境检查':^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

    print(f"Python 版本: {version_str}")

    if version_info.major == 3 and 8 <= version_info.minor <= 11:
        print(f"{GREEN}✓ Python 版本符合要求 (3.8-3.11){RESET}\n")
        return True
    else:
        print(f"{YELLOW}⚠ 警告: 推荐使用 Python 3.8-3.11，当前版本可能存在兼容性问题{RESET}\n")
        return False


def check_package_version(package_name, min_version):
    """
    检查包是否安装及版本是否符合要求

    Args:
        package_name: 包名
        min_version: 最低版本要求

    Returns:
        tuple: (是否安装, 版本号, 状态消息)
    """
    try:
        # 特殊处理 opencv-python
        check_name = 'cv2' if package_name == 'opencv-python' else package_name

        # 尝试导入
        importlib.import_module(check_name)

        # 获取版本
        try:
            installed_version = version(package_name)
        except PackageNotFoundError:
            # 某些包的导入名和安装名不同
            if package_name == 'Pillow':
                installed_version = version('Pillow')
            elif package_name == 'opencv-python':
                installed_version = version('opencv-python')
            else:
                installed_version = "Unknown"

        return True, installed_version, "OK"

    except ImportError:
        return False, None, "Not Installed"
    except Exception as e:
        return False, None, f"Error: {str(e)}"


def check_builtin_module(module_name):
    """
    检查内置模块是否可导入

    Args:
        module_name: 模块名

    Returns:
        tuple: (是否可用, 状态消息)
    """
    try:
        importlib.import_module(module_name)
        return True, "OK"
    except ImportError as e:
        return False, str(e)


def check_custom_module(module_name):
    """
    检查自定义模块是否存在

    Args:
        module_name: 模块名

    Returns:
        tuple: (是否存在, 状态消息)
    """
    import os

    # 检查 .py 文件是否存在
    if os.path.exists(f"{module_name}.py"):
        try:
            importlib.import_module(module_name)
            return True, "OK"
        except Exception as e:
            return False, f"Import Error: {str(e)}"
    else:
        return False, "File Not Found"


def print_results(title, results):
    """打印检查结果"""
    print(f"\n{BLUE}{title}{RESET}")
    print(f"{BLUE}{'-'*60}{RESET}")

    max_name_len = max(len(name) for name in results.keys()) if results else 20

    for name, (status, info) in results.items():
        status_symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        print(f"{status_symbol} {name:<{max_name_len}} : {info}")


def main():
    """主检查流程"""
    print(f"\n{BLUE}{'*'*60}{RESET}")
    print(f"{BLUE}{'XRD 应用程序依赖检查工具':^66}{RESET}")
    print(f"{BLUE}{'*'*60}{RESET}")

    # 检查 Python 版本
    python_ok = check_python_version()

    # 检查必需依赖
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{'必需依赖检查':^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    required_results = {}
    required_passed = 0

    for package, min_ver in REQUIRED_PACKAGES.items():
        installed, version_str, status = check_package_version(package, min_ver)

        if installed:
            info = f"{GREEN}{version_str} (>= {min_ver}){RESET}"
            required_passed += 1
        else:
            info = f"{RED}{status} (需要 >= {min_ver}){RESET}"

        required_results[package] = (installed, info)

    print_results("", required_results)

    # 检查可选依赖
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{'可选依赖检查':^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    optional_results = {}
    optional_passed = 0

    for package, min_ver in OPTIONAL_PACKAGES.items():
        installed, version_str, status = check_package_version(package, min_ver)

        if installed:
            info = f"{GREEN}{version_str} (>= {min_ver}){RESET}"
            optional_passed += 1
        else:
            info = f"{YELLOW}{status} (推荐安装){RESET}"

        optional_results[package] = (installed, info)

    print_results("", optional_results)

    # 检查内置模块
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{'Python 内置模块检查':^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    builtin_results = {}
    builtin_passed = 0

    for module in BUILTIN_MODULES:
        available, msg = check_builtin_module(module)

        if available:
            info = f"{GREEN}可用{RESET}"
            builtin_passed += 1
        else:
            info = f"{RED}不可用 - {msg}{RESET}"

        builtin_results[module] = (available, info)

    print_results("", builtin_results)

    # 检查自定义模块
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{'自定义模块检查':^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    custom_results = {}
    custom_passed = 0

    for module in CUSTOM_MODULES:
        available, msg = check_custom_module(module)

        if available:
            info = f"{GREEN}OK{RESET}"
            custom_passed += 1
        else:
            info = f"{RED}{msg}{RESET}"

        custom_results[module] = (available, info)

    print_results("", custom_results)

    # 总结
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{'检查总结':^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    total_required = len(REQUIRED_PACKAGES)
    total_optional = len(OPTIONAL_PACKAGES)
    total_builtin = len(BUILTIN_MODULES)
    total_custom = len(CUSTOM_MODULES)

    print(f"必需依赖: {required_passed}/{total_required} 已安装")
    print(f"可选依赖: {optional_passed}/{total_optional} 已安装")
    print(f"内置模块: {builtin_passed}/{total_builtin} 可用")
    print(f"自定义模块: {custom_passed}/{total_custom} 可用")

    # 判断是否可以打包
    can_build = (
        python_ok and
        required_passed == total_required and
        builtin_passed == total_builtin and
        custom_passed == total_custom
    )

    print()
    if can_build:
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}✓ 所有必需组件已就绪，可以开始打包!{RESET}")
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"\n运行以下命令开始打包:")
        print(f"  Windows: {BLUE}build.bat{RESET}")
        print(f"  Linux/Mac: {BLUE}bash build.sh{RESET}")
    else:
        print(f"{RED}{'='*60}{RESET}")
        print(f"{RED}✗ 存在缺失的依赖，请先安装!{RESET}")
        print(f"{RED}{'='*60}{RESET}")
        print(f"\n安装缺失的依赖:")
        print(f"  {BLUE}pip install -r requirements_gui.txt{RESET}")

        # 列出缺失的包
        missing = [pkg for pkg, (status, _) in required_results.items() if not status]
        if missing:
            print(f"\n缺失的必需包:")
            for pkg in missing:
                print(f"  - {pkg}")

        return 1

    print()
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}检查已取消{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}发生错误: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
