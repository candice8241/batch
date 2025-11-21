@echo off
REM ===================================================
REM XRD Data Post-Processing - Windows Packaging Script
REM ===================================================

echo ========================================
echo XRD Application Packaging Tool
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8 or higher first.
    pause
    exit /b 1
)

echo [1/5] Checking Python environment...
python --version
echo.

REM Check and install PyInstaller
echo [2/5] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
) else (
    echo PyInstaller is already installed
)
echo.

REM Clean up previous build files
echo [3/5] Cleaning old build files...
if exist "build" (
    echo Deleting build folder...
    rmdir /s /q build
)
if exist "dist" (
    echo Deleting dist folder...
    rmdir /s /q dist
)
echo.

REM Start packaging
echo [4/5] Starting packaging process...
echo This may take a few minutes. Please wait...
echo.
pyinstaller --clean xrd_app.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Packaging failed! Please check the error messages.
    pause
    exit /b 1
)

echo.
echo [5/5] Packaging completed!
echo.
echo ========================================
echo Packaging Successful!
echo ========================================
echo.
echo Executable location:
echo   dist\XRD_PostProcessing\XRD_PostProcessing.exe
echo.
echo You can:
echo   1. Copy the entire dist\XRD_PostProcessing folder to any location
echo   2. Create a desktop shortcut pointing to XRD_PostProcessing.exe
echo   3. Double-click to run XRD_PostProcessing.exe
echo.

REM Ask whether to open output folder
echo Do you want to open the output folder? (Y/N)
set /p open_folder=
if /i "%open_folder%"=="Y" (
    explorer dist\XRD_PostProcessing
)

pause
