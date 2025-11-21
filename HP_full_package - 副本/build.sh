#!/bin/bash
# ===================================================
# XRD Data Post-Processing - Linux/Mac Packaging Script
# ===================================================

echo "========================================"
echo "XRD Application Packaging Tool"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not detected. Please install Python 3.8 or higher."
    exit 1
fi

echo "[1/5] Checking Python environment..."
python3 --version
echo ""

# Check and install PyInstaller
echo "[2/5] Checking PyInstaller..."
if ! python3 -m pip show pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    python3 -m pip install pyinstaller
else
    echo "PyInstaller is already installed"
fi
echo ""

# Clean up previous build files
echo "[3/5] Cleaning up old build files..."
if [ -d "build" ]; then
    echo "Removing build folder..."
    rm -rf build
fi
if [ -d "dist" ]; then
    echo "Removing dist folder..."
    rm -rf dist
fi
echo ""

# Start packaging process
echo "[4/5] Starting application packaging..."
echo "This may take a few minutes. Please be patient..."
echo ""
python3 -m PyInstaller --clean xrd_app.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Packaging failed! Please check the error output."
    exit 1
fi

echo ""
echo "[5/5] Packaging completed!"
echo ""
echo "========================================"
echo "Packaging Successful!"
echo "========================================"
echo ""
echo "Executable location:"
echo "  dist/XRD_PostProcessing/XRD_PostProcessing"
echo ""
echo "You can:"
echo "  1. Copy the entire dist/XRD_PostProcessing folder to any location"
echo "  2. Run ./dist/XRD_PostProcessing/XRD_PostProcessing"
echo ""

# Add execute permission
chmod +x dist/XRD_PostProcessing/XRD_PostProcessing

echo "Execution permission added"
echo ""
