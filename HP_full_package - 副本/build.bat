@echo off
chcp 65001 >nul
REM ===================================================
REM Quick Packaging Script for XRD Application (Simplified Version)
REM ===================================================

echo.
echo ================================================
echo   XRD Data Post‑Processing App - Quick Build Tool
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [1/6] Checking Python environment...
python --version
echo.

REM Check for PyInstaller
echo [2/6] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found, installing...
    pip install pyinstaller
) else (
    echo PyInstaller is already installed
)
echo.

REM Install core dependencies
echo [3/6] Installing required core packages...
echo This may take a few minutes. Please wait patiently...
pip install numpy scipy pandas matplotlib h5py pyFAI fabio tqdm Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

REM Clean old build files
echo [4/6] Cleaning old build files...
if exist "build" (
    echo Deleting build folder...
    rmdir /s /q build
)
if exist "dist" (
    echo Deleting dist folder...
    rmdir /s /q dist
)
if exist "*.spec.bak" (
    del /q *.spec.bak
)
echo.

REM Start building
echo [5/6] Building application...
echo This may take 5–10 minutes. Please wait patiently...
echo.
pyinstaller --clean xrd_app.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Please check the error messages.
    echo.
    echo Common solutions:
    echo 1. Ensure all dependencies are installed correctly
    echo 2. Check whether xrd_app.spec exists
    echo 3. Refer to documentation: EXE Build Instructions.md
    echo.
    pause
    exit /b 1
)

REM Verify build result
echo.
echo [6/6] Checking build result...
if exist "dist\XRD_PostProcessing\XRD_PostProcessing.exe" (
    echo.
    echo ================================================
    echo    Build Successful!
    echo ================================================
    echo.
    echo Executable location:
    echo   dist\XRD_PostProcessing\XRD_PostProcessing.exe
    echo.
    echo Instructions:
    echo   1. Copy the entire dist\XRD_PostProcessing folder to the target location
    echo   2. Double‑click XRD_PostProcessing.exe to run
    echo   3. You may create a desktop shortcut for convenience
    echo.
    echo File Size:
    for %%A in ("dist\XRD_PostProcessing\XRD_PostProcessing.exe") do echo   %%~zA bytes
    echo.

    REM Ask user whether to open output folder
    set /p open_folder=Open output folder? (Y/N):
    if /i "%open_folder%"=="Y" (
        explorer dist\XRD_PostProcessing
    )
) else (
    echo.
    echo [ERROR] Executable file not found!
    echo Please check for errors during the build process.
    echo.
)

echo.
echo ================================================
pause
