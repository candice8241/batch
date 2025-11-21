#!/bin/bash
################################################################################
# XRD Data Post-Processing Application - Linux/Mac EXE Packaging Script
################################################################################
# This script packages the XRD application into a standalone executable
# using PyInstaller. The resulting executable can run on Linux/Mac systems
# without requiring Python installation.
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "================================================================================"
    echo "                    XRD Application EXE Packaging Tool"
    echo "================================================================================"
    echo ""
    echo "This script will create a standalone executable for the XRD application"
    echo ""
}

print_footer() {
    echo ""
    echo "================================================================================"
    echo "                        Thank you for using XRD Tools!"
    echo "================================================================================"
    echo ""
}

# ---------------------------
# Start packaging process
# ---------------------------
print_header

# ---------------------------
# Step 1: Check Python
# ---------------------------
print_info "Step 1/6: Checking Python installation..."
echo ""

if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_success "Found $PYTHON_VERSION"
echo ""

# ---------------------------
# Step 2: Check pip
# ---------------------------
print_info "Step 2/6: Checking pip..."
echo ""

if ! python3 -m pip --version &> /dev/null; then
    print_error "pip is not available"
    echo ""
    echo "Please install pip:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-pip"
    echo "  macOS: python3 -m ensurepip --upgrade"
    echo "  Fedora: sudo dnf install python3-pip"
    exit 1
fi

PIP_VERSION=$(python3 -m pip --version)
print_success "Found $PIP_VERSION"
echo ""

# ---------------------------
# Step 3: Install/Upgrade PyInstaller
# ---------------------------
print_info "Step 3/6: Checking PyInstaller..."
echo ""

if python3 -m pip show pyinstaller &> /dev/null; then
    PYINSTALLER_VERSION=$(python3 -m pip show pyinstaller | grep Version | awk '{print $2}')
    print_success "PyInstaller $PYINSTALLER_VERSION is already installed"
    echo ""

    read -p "Do you want to upgrade PyInstaller to the latest version? (y/N): " UPGRADE_PYINSTALLER
    if [[ "$UPGRADE_PYINSTALLER" =~ ^[Yy]$ ]]; then
        print_info "Upgrading PyInstaller..."
        python3 -m pip install --upgrade pyinstaller
    fi
else
    print_info "PyInstaller not found. Installing..."
    python3 -m pip install pyinstaller
    if [ $? -ne 0 ]; then
        print_error "Failed to install PyInstaller"
        exit 1
    fi
fi
echo ""

# ---------------------------
# Step 4: Install dependencies
# ---------------------------
print_info "Step 4/6: Checking dependencies..."
echo ""

if [ -f "requirements_gui.txt" ]; then
    print_success "Found requirements_gui.txt"
    read -p "Do you want to install/update all dependencies? (y/N): " INSTALL_DEPS
    if [[ "$INSTALL_DEPS" =~ ^[Yy]$ ]]; then
        print_info "Installing dependencies..."
        python3 -m pip install -r requirements_gui.txt
        if [ $? -ne 0 ]; then
            print_warning "Some dependencies may have failed to install"
            echo "You can continue, but the application may not work correctly"
            echo ""
            read -p "Continue anyway? (y/N): " CONTINUE
            if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi
else
    print_warning "requirements_gui.txt not found"
    echo "Dependencies must be installed manually"
fi
echo ""

# ---------------------------
# Step 5: Clean old build files
# ---------------------------
print_info "Step 5/6: Cleaning old build files..."
echo ""

if [ -d "build" ]; then
    print_info "Removing build folder..."
    rm -rf build
fi

if [ -d "dist" ]; then
    print_info "Removing dist folder..."
    rm -rf dist
fi

if [ -f "XRD_PostProcessing.spec" ]; then
    print_info "Removing old spec file..."
    rm -f XRD_PostProcessing.spec
fi

print_success "Cleanup completed"
echo ""

# ---------------------------
# Step 6: Build executable
# ---------------------------
print_info "Step 6/6: Building executable..."
echo ""
echo "This process may take 5-15 minutes depending on your system"
echo "Please be patient and do not close this terminal..."
echo ""

# Check if spec file exists
if [ ! -f "xrd_app.spec" ]; then
    print_error "xrd_app.spec file not found!"
    echo ""
    echo "The spec file is required for packaging."
    echo "Please ensure xrd_app.spec is in the current directory."
    exit 1
fi

# Run PyInstaller with the spec file
python3 -m PyInstaller --clean --noconfirm xrd_app.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "================================================================================"
    print_error "Packaging failed!"
    echo "================================================================================"
    echo ""
    echo "Common issues:"
    echo "  1. Missing dependencies - Install all packages from requirements_gui.txt"
    echo "  2. Missing system libraries - Install tkinter (python3-tk)"
    echo "  3. Insufficient disk space - Ensure at least 2GB free space"
    echo "  4. Permission issues - Check write permissions"
    echo ""
    echo "Check the error messages above for more details"
    exit 1
fi

# ---------------------------
# Build Success
# ---------------------------
echo ""
echo "================================================================================"
echo "                          BUILD SUCCESSFUL!"
echo "================================================================================"
echo ""
echo "Executable created at:"
echo "  $(pwd)/dist/XRD_PostProcessing/XRD_PostProcessing"
echo ""

# Calculate package size
if [ -d "dist/XRD_PostProcessing" ]; then
    PACKAGE_SIZE=$(du -sh dist/XRD_PostProcessing | cut -f1)
    echo "Package size:"
    echo "  Approximately $PACKAGE_SIZE"
    echo ""
fi

echo "Next steps:"
echo "  1. Test the executable by running: ./dist/XRD_PostProcessing/XRD_PostProcessing"
echo "  2. The entire dist/XRD_PostProcessing folder is needed (not just the executable)"
echo "  3. You can copy the entire folder to any compatible system"
echo "  4. Make sure the executable has execute permissions (chmod +x)"
echo "  5. No Python installation required on target computers"
echo ""

# Add execute permission
if [ -f "dist/XRD_PostProcessing/XRD_PostProcessing" ]; then
    chmod +x dist/XRD_PostProcessing/XRD_PostProcessing
    print_success "Execute permission added to the executable"
    echo ""
fi

# ---------------------------
# Optional: Open dist folder
# ---------------------------
read -p "Would you like to open the dist folder now? (y/N): " OPEN_FOLDER
if [[ "$OPEN_FOLDER" =~ ^[Yy]$ ]]; then
    if [ -d "dist/XRD_PostProcessing" ]; then
        # Try different file managers
        if command -v xdg-open &> /dev/null; then
            xdg-open "dist/XRD_PostProcessing"
        elif command -v open &> /dev/null; then
            open "dist/XRD_PostProcessing"
        elif command -v nautilus &> /dev/null; then
            nautilus "dist/XRD_PostProcessing"
        else
            echo "Please manually navigate to: dist/XRD_PostProcessing"
        fi
    fi
fi

print_footer
