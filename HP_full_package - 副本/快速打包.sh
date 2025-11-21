#!/bin/bash
# ===================================================
# XRD应用程序快速打包脚本（Linux/Mac简化版）
# ===================================================

echo ""
echo "================================================"
echo "  XRD数据后处理应用 - 快速打包工具"
echo "================================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.8或更高版本"
    exit 1
fi

echo "[1/6] 检查Python环境..."
python3 --version
echo ""

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "[错误] 未找到pip3，请先安装pip"
    exit 1
fi

# 检查PyInstaller
echo "[2/6] 检查PyInstaller..."
if ! python3 -m pip show pyinstaller &> /dev/null; then
    echo "PyInstaller未安装，正在安装..."
    python3 -m pip install pyinstaller
else
    echo "PyInstaller已安装"
fi
echo ""

# 安装核心依赖
echo "[3/6] 安装核心依赖包..."
echo "这可能需要几分钟，请耐心等待..."
python3 -m pip install numpy scipy pandas matplotlib h5py pyFAI fabio tqdm Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
echo ""

# 清理旧文件
echo "[4/6] 清理旧的打包文件..."
if [ -d "build" ]; then
    echo "删除 build 文件夹..."
    rm -rf build
fi
if [ -d "dist" ]; then
    echo "删除 dist 文件夹..."
    rm -rf dist
fi
if [ -f "*.spec.bak" ]; then
    rm -f *.spec.bak
fi
echo ""

# 开始打包
echo "[5/6] 开始打包应用程序..."
echo "这可能需要5-10分钟，请耐心等待..."
echo ""
python3 -m PyInstaller --clean xrd_app.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 打包失败！请检查错误信息。"
    echo ""
    echo "常见解决方案："
    echo "1. 确保所有依赖包已正确安装"
    echo "2. 检查xrd_app.spec文件是否存在"
    echo "3. 查看完整文档：生成EXE说明.md"
    echo ""
    exit 1
fi

# 检查打包结果
echo ""
echo "[6/6] 检查打包结果..."
if [ -f "dist/XRD_PostProcessing/XRD_PostProcessing" ]; then
    echo ""
    echo "================================================"
    echo "  🎉 打包成功！"
    echo "================================================"
    echo ""
    echo "可执行文件位置:"
    echo "  dist/XRD_PostProcessing/XRD_PostProcessing"
    echo ""

    # 添加执行权限
    chmod +x dist/XRD_PostProcessing/XRD_PostProcessing
    echo "已添加执行权限"
    echo ""

    echo "使用说明："
    echo "  1. 将整个 dist/XRD_PostProcessing 文件夹复制到目标位置"
    echo "  2. 运行命令: ./dist/XRD_PostProcessing/XRD_PostProcessing"
    echo "  3. 或在文件管理器中双击运行"
    echo ""

    # 显示文件大小
    file_size=$(du -h "dist/XRD_PostProcessing/XRD_PostProcessing" | cut -f1)
    echo "文件大小: $file_size"
    echo ""

    # 询问是否立即运行
    read -p "是否立即运行测试？(Y/N): " run_test
    if [ "$run_test" = "Y" ] || [ "$run_test" = "y" ]; then
        cd dist/XRD_PostProcessing
        ./XRD_PostProcessing
    fi
else
    echo ""
    echo "[错误] 未找到可执行文件！"
    echo "请检查打包过程中是否有错误信息。"
    echo ""
fi

echo ""
echo "================================================"
