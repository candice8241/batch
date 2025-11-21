#!/bin/bash
# ===================================================
# Quick Packaging Script for XRD Application (Linux/Mac Simplified Version)
# ===================================================

echo ""
echo "================================================"
echo "  XRD Data Post-Processing Application - Quick Build Tool"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found. Please install Python 3.8 or later."
    exit 1
fi

echo "[1/6] Checking Python environment..."
python3 --version
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "[ERROR] pip3 not found. Please install pip."
    exit 1
fi

# Check if PyInstaller is installed
echo "[2/6] Checking PyInstaller..."
if ! python3 -m pip show pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing now..."
    python3 -m pip install pyinstaller
else
    echo "PyInstaller is already installed."
fi
echo ""

# Install core dependencies
echo "[3/6] Installing required core packages..."
echo "This may take a few minutes. Please wait patiently..."
python3 -m pip install numpy scipy pandas matplotlib h5py pyFAI fabio tqdm Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
echo ""

# Clean old build files
echo "[4/6] Cleaning old build files..."
if [ -d "build" ]; then
    echo "Deleting build folder..."
    rm -rf build
fi
if [ -d "dist" ]; then
    echo "Deleting dist folder..."
    rm -rf dist
fi
if [ -f "*.spec.bak" ]; then
    rm -f *.spec.bak
fi
echo ""

# Start packaging
echo "[5/6] Starting application build..."
echo "This may take 5–10 minutes. Please wait patiently..."
echo ""
python3 -m PyInstaller --clean xrd_app.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Build failed! Please check the error messages."
    echo ""
    echo "Common solutions:"
    echo "1. Ensure all dependencies are installed correctly"
    echo "2. Check if the xrd_app.spec file exists"
    echo "3. See the documentation: EXE_Build_Guide.md"
    echo ""
    exit 1
fi

# Verify the build result
echo ""
echo "[6/6] Verifying build result..."
if [ -f "dist/XRD_PostProcessing/XRD_PostProcessing" ]; then
    echo ""
    echo "================================================"
    echo "  🎉 Build Successful!"
    echo "================================================"
    echo ""
    echo "Executable location:"
    echo "  dist/XRD_PostProcessing/XRD_PostProcessing"
    echo ""

    # Add execute permission
    chmod +x dist/XRD_PostProcessing/XRD_PostProcessing
    echo "Execution permission granted."
    echo ""

    echo "Usage Instructions:"
    echo "  1. Copy the entire dist/XRD_PostProcessing folder to the target location"
    echo "  2. Run the command: ./dist/XRD_PostProcessing/XRD_PostProcessing"
    echo "  3. Or double-click to run from the file manager"
    echo ""

    # Show file size
    file_size=$(du -h "dist/XRD_PostProcessing/XRD_PostProcessing" | cut -f1)
    echo "File size: $file_size"
    echo ""

    # Prompt to run immediately
    read -p "Would you like to run it now? (Y/N): " run_test
    if [ "$run_test" = "Y" ] || [ "$run_test" = "y" ]; then
        cd dist/XRD_PostProcessing
        ./XRD_PostProcessing
    fi
else
    echo ""
    echo "[ERROR] Executable not found!"
    echo "Please check for errors during the build process."
    echo ""
fi

echo ""
echo "================================================"
