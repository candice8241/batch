#!/bin/bash
# XRD Data Post-Processing GUI Launcher

echo "╔════════════════════════════════════════════════════════╗"
echo "║  XRD Data Post-Processing - DearPyGUI Application     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if running in a graphical environment
if [ -z "$DISPLAY" ]; then
    echo "⚠️  Warning: No display detected (DISPLAY variable not set)"
    echo ""
    echo "You are running in a headless environment. Options:"
    echo ""
    echo "1️⃣  Local Machine (Recommended):"
    echo "   → Run this on your local machine with a desktop environment"
    echo ""
    echo "2️⃣  Remote Server with X11 Forwarding:"
    echo "   → SSH with X11: ssh -X user@server"
    echo "   → Or use VNC/Remote Desktop"
    echo ""
    echo "3️⃣  WSL (Windows Subsystem for Linux):"
    echo "   → Install VcXsrv or X410"
    echo "   → Set DISPLAY: export DISPLAY=:0"
    echo ""
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Check if dependencies are installed
echo "📦 Checking dependencies..."

if python3 -c "import dearpygui" 2>/dev/null; then
    echo "✓ DearPyGUI installed"
else
    echo "✗ DearPyGUI not found"
    echo ""
    echo "Installing dependencies from requirements.txt..."
    pip3 install -r requirements.txt
    echo ""
fi

# Launch the application
echo ""
echo "🚀 Launching GUI application..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 main_dpg.py
