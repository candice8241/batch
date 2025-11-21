@echo off
REM ===============================================================================
REM XRD Data Post-Processing Application - Windows EXE Packaging Script
REM ===============================================================================
REM This script packages the XRD application into a standalone Windows executable
REM using PyInstaller. The resulting .exe file can run on any Windows system
REM without requiring Python installation.
REM ===============================================================================

chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo                    XRD Application EXE Packaging Tool
echo ================================================================================
echo.
echo This script will create a standalone Windows executable for the XRD application
echo.

REM ---------------------------
REM Step 1: Check Python
REM ---------------------------
echo [Step 1/6] Checking Python installation...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Found %PYTHON_VERSION%
echo.

REM ---------------------------
REM Step 2: Check pip
REM ---------------------------
echo [Step 2/6] Checking pip...
echo.

python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    echo.
    echo Please ensure pip is installed with your Python installation
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python -m pip --version') do set PIP_VERSION=%%i
echo [OK] Found !PIP_VERSION!
echo.

REM ---------------------------
REM Step 3: Install/Upgrade PyInstaller
REM ---------------------------
echo [Step 3/6] Checking PyInstaller...
echo.

pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
) else (
    for /f "tokens=2" %%i in ('pip show pyinstaller ^| findstr "Version:"') do set PYINSTALLER_VERSION=%%i
    echo [OK] PyInstaller !PYINSTALLER_VERSION! is already installed

    echo.
    set /p UPGRADE_PYINSTALLER="Do you want to upgrade PyInstaller to the latest version? (Y/N): "
    if /i "!UPGRADE_PYINSTALLER!"=="Y" (
        echo Upgrading PyInstaller...
        python -m pip install --upgrade pyinstaller
    )
)
echo.

REM ---------------------------
REM Step 4: Install dependencies
REM ---------------------------
echo [Step 4/6] Checking dependencies...
echo.

if exist "requirements_gui.txt" (
    echo Found requirements_gui.txt
    set /p INSTALL_DEPS="Do you want to install/update all dependencies? (Y/N): "
    if /i "!INSTALL_DEPS!"=="Y" (
        echo Installing dependencies...
        python -m pip install -r requirements_gui.txt
        if errorlevel 1 (
            echo [WARNING] Some dependencies may have failed to install
            echo You can continue, but the application may not work correctly
            echo.
            set /p CONTINUE="Continue anyway? (Y/N): "
            if /i not "!CONTINUE!"=="Y" (
                exit /b 1
            )
        )
    )
) else (
    echo [WARNING] requirements_gui.txt not found
    echo Dependencies must be installed manually
)
echo.

REM ---------------------------
REM Step 5: Clean old build files
REM ---------------------------
echo [Step 5/6] Cleaning old build files...
echo.

if exist "build" (
    echo Removing build folder...
    rmdir /s /q build
)

if exist "dist" (
    echo Removing dist folder...
    rmdir /s /q dist
)

if exist "XRD_PostProcessing.spec" (
    echo Removing old spec file...
    del /q XRD_PostProcessing.spec
)

echo [OK] Cleanup completed
echo.

REM ---------------------------
REM Step 6: Build executable
REM ---------------------------
echo [Step 6/6] Building executable...
echo.
echo This process may take 5-15 minutes depending on your system
echo Please be patient and do not close this window...
echo.

REM Check if spec file exists
if not exist "xrd_app.spec" (
    echo [ERROR] xrd_app.spec file not found!
    echo.
    echo The spec file is required for packaging.
    echo Please ensure xrd_app.spec is in the current directory.
    pause
    exit /b 1
)

REM Run PyInstaller with the spec file
python -m PyInstaller --clean --noconfirm xrd_app.spec

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo [ERROR] Packaging failed!
    echo ================================================================================
    echo.
    echo Common issues:
    echo   1. Missing dependencies - Install all packages from requirements_gui.txt
    echo   2. Antivirus interference - Temporarily disable antivirus software
    echo   3. Insufficient disk space - Ensure at least 2GB free space
    echo   4. Permission issues - Run as Administrator
    echo.
    echo Check the error messages above for more details
    pause
    exit /b 1
)

REM ---------------------------
REM Build Success
REM ---------------------------
echo.
echo ================================================================================
echo                          BUILD SUCCESSFUL!
echo ================================================================================
echo.
echo Executable created at:
echo   %CD%\dist\XRD_PostProcessing\XRD_PostProcessing.exe
echo.
echo Package size:
for /f "tokens=*" %%i in ('powershell -command "(Get-ChildItem -Path 'dist\XRD_PostProcessing' -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB"') do (
    echo   Approximately %%i MB
)
echo.
echo Next steps:
echo   1. Test the executable by running: dist\XRD_PostProcessing\XRD_PostProcessing.exe
echo   2. The entire dist\XRD_PostProcessing folder is needed (not just the .exe)
echo   3. You can copy the entire folder to any Windows computer
echo   4. Create a desktop shortcut to XRD_PostProcessing.exe for easy access
echo   5. No Python installation required on target computers
echo.

REM ---------------------------
REM Optional: Open dist folder
REM ---------------------------
set /p OPEN_FOLDER="Would you like to open the dist folder now? (Y/N): "
if /i "!OPEN_FOLDER!"=="Y" (
    if exist "dist\XRD_PostProcessing" (
        explorer "dist\XRD_PostProcessing"
    )
)

echo.
echo ================================================================================
echo                        Thank you for using XRD Tools!
echo ================================================================================
echo.
pause
