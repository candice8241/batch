#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment Check Script for XRD Data Post-Processing GUI
Diagnoses common issues and provides solutions
"""

import sys
import os
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Python version: {version_str}")
    
    if version.major == 3 and version.minor >= 7:
        print("✓ Python version is compatible (3.7+)")
        return True
    else:
        print("✗ Python 3.7 or higher required")
        return False

def check_display():
    """Check if graphical display is available"""
    print_header("Display Environment Check")
    display = os.environ.get('DISPLAY', '')
    
    if display:
        print(f"✓ DISPLAY variable is set: {display}")
        return True
    else:
        print("✗ DISPLAY variable is not set")
        print("\n⚠️  You are in a headless environment!")
        print("\nSolutions:")
        print("  1. Run on a machine with a desktop environment")
        print("  2. Use X11 forwarding: ssh -X user@server")
        print("  3. Use VNC or Remote Desktop")
        print("  4. WSL users: Install VcXsrv and set DISPLAY=:0")
        return False

def check_module(module_name, package_name=None):
    """Check if a Python module is installed"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - NOT INSTALLED")
        return False

def check_dependencies():
    """Check all required dependencies"""
    print_header("Dependencies Check")
    
    required = {
        'dearpygui': 'dearpygui',
        'numpy': 'numpy',
        'pandas': 'pandas',
    }
    
    optional = {
        'pyFAI': 'pyFAI',
        'h5py': 'h5py',
        'fabio': 'fabio',
        'matplotlib': 'matplotlib',
    }
    
    print("\nRequired Packages:")
    required_ok = all(check_module(mod, pkg) for mod, pkg in required.items())
    
    print("\nOptional Packages (for full functionality):")
    optional_ok = all(check_module(mod, pkg) for mod, pkg in optional.items())
    
    if not required_ok:
        print("\n⚠️  Missing required packages!")
        print("Run: pip3 install -r requirements.txt")
    
    return required_ok

def check_files():
    """Check if necessary files exist"""
    print_header("Files Check")
    
    files = [
        'main_dpg.py',
        'dpg_components.py',
        'gui_base_dpg.py',
        'powder_module_dpg.py',
        'radial_module_dpg.py',
        'single_crystal_module_dpg.py',
        'requirements.txt'
    ]
    
    all_exist = True
    for file in files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - NOT FOUND")
            all_exist = False
    
    return all_exist

def check_dearpygui_rendering():
    """Check if DearPyGUI can initialize"""
    print_header("DearPyGUI Initialization Test")
    
    try:
        import dearpygui.dearpygui as dpg
        print("✓ DearPyGUI imported successfully")
        
        # Try to create context (doesn't require display)
        dpg.create_context()
        print("✓ DearPyGUI context created")
        dpg.destroy_context()
        
        print("\n⚠️  Note: Full GUI test requires a display")
        print("   The GUI can only be tested in a graphical environment")
        return True
        
    except Exception as e:
        print(f"✗ DearPyGUI initialization failed: {e}")
        return False

def provide_solutions():
    """Provide solutions based on environment"""
    print_header("Setup Instructions")
    
    display = os.environ.get('DISPLAY', '')
    
    if not display:
        print("\n🔧 You are in a HEADLESS environment (no GUI support)")
        print("\nOption 1: Local Machine (Easiest)")
        print("  1. Copy all files to your local machine")
        print("  2. Install dependencies: pip3 install -r requirements.txt")
        print("  3. Run: python3 main_dpg.py")
        
        print("\nOption 2: Remote Server with X11")
        print("  1. On local machine: Install X server")
        print("     - Linux: Already installed")
        print("     - macOS: Install XQuartz")
        print("     - Windows: Install VcXsrv or Xming")
        print("  2. SSH with X11: ssh -X username@server")
        print("  3. Test: echo $DISPLAY (should show value)")
        print("  4. Run: python3 main_dpg.py")
        
        print("\nOption 3: Windows WSL")
        print("  1. Install VcXsrv on Windows")
        print("  2. In WSL: export DISPLAY=:0")
        print("  3. Run: python3 main_dpg.py")
    else:
        print("\n✓ You have a graphical environment!")
        print("\nTo run the application:")
        print("  1. Install dependencies: pip3 install -r requirements.txt")
        print("  2. Run: python3 main_dpg.py")
        print("  or")
        print("  Run: bash run_gui.sh")

def main():
    """Main check routine"""
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*10 + "XRD GUI Environment Diagnostic Tool" + " "*13 + "║")
    print("╚" + "═"*58 + "╝")
    
    checks = []
    
    # Run all checks
    checks.append(("Python Version", check_python_version()))
    checks.append(("Display", check_display()))
    checks.append(("Dependencies", check_dependencies()))
    checks.append(("Files", check_files()))
    checks.append(("DearPyGUI", check_dearpygui_rendering()))
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed < total:
        provide_solutions()
    else:
        print("\n🎉 All checks passed! You should be able to run the GUI.")
        print("   Run: python3 main_dpg.py")
    
    print("\n")

if __name__ == "__main__":
    main()
