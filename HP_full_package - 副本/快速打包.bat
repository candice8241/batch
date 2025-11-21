@echo off
chcp 65001 >nul
REM ===================================================
REM XRD应用程序快速打包脚本（简化版）
REM ===================================================

echo.
echo ================================================
echo   XRD数据后处理应用 - 快速打包工具
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo [1/6] 检查Python环境...
python --version
echo.

REM 检查PyInstaller
echo [2/6] 检查PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller未安装，正在安装...
    pip install pyinstaller
) else (
    echo PyInstaller已安装
)
echo.

REM 安装核心依赖
echo [3/6] 安装核心依赖包...
echo 这可能需要几分钟，请耐心等待...
pip install numpy scipy pandas matplotlib h5py pyFAI fabio tqdm Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

REM 清理旧文件
echo [4/6] 清理旧的打包文件...
if exist "build" (
    echo 删除 build 文件夹...
    rmdir /s /q build
)
if exist "dist" (
    echo 删除 dist 文件夹...
    rmdir /s /q dist
)
if exist "*.spec.bak" (
    del /q *.spec.bak
)
echo.

REM 开始打包
echo [5/6] 开始打包应用程序...
echo 这可能需要5-10分钟，请耐心等待...
echo.
pyinstaller --clean xrd_app.spec

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！请检查错误信息。
    echo.
    echo 常见解决方案：
    echo 1. 确保所有依赖包已正确安装
    echo 2. 检查xrd_app.spec文件是否存在
    echo 3. 查看完整文档：生成EXE说明.md
    echo.
    pause
    exit /b 1
)

REM 检查打包结果
echo.
echo [6/6] 检查打包结果...
if exist "dist\XRD_PostProcessing\XRD_PostProcessing.exe" (
    echo.
    echo ================================================
    echo   🎉 打包成功！
    echo ================================================
    echo.
    echo 可执行文件位置:
    echo   dist\XRD_PostProcessing\XRD_PostProcessing.exe
    echo.
    echo 使用说明：
    echo   1. 将整个 dist\XRD_PostProcessing 文件夹复制到目标位置
    echo   2. 双击 XRD_PostProcessing.exe 运行程序
    echo   3. 可以创建桌面快捷方式方便使用
    echo.
    echo 文件大小：
    for %%A in ("dist\XRD_PostProcessing\XRD_PostProcessing.exe") do echo   %%~zA 字节
    echo.

    REM 询问是否打开输出文件夹
    set /p open_folder=是否打开输出文件夹？(Y/N):
    if /i "%open_folder%"=="Y" (
        explorer dist\XRD_PostProcessing
    )
) else (
    echo.
    echo [错误] 未找到可执行文件！
    echo 请检查打包过程中是否有错误信息。
    echo.
)

echo.
echo ================================================
pause
