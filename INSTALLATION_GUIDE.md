# XRD Data Post-Processing GUI - Installation & Running Guide

## 🔍 Quick Diagnosis

First, check your environment:

```bash
python3 check_environment.py
```

This will identify any issues and provide specific solutions.

---

## 📋 Requirements

### System Requirements
- **Python**: 3.7 or higher
- **Operating System**: Linux, macOS, or Windows
- **Display**: Graphical environment (X11, Wayland, or Windows desktop)

### Python Packages
All dependencies are listed in `requirements.txt`

---

## 🚀 Installation Methods

### Method 1: Quick Start (Recommended)

#### On Linux/macOS:
```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Make launcher executable
chmod +x run_gui.sh

# 3. Run the application
./run_gui.sh
```

#### On Windows:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main_dpg.py
```

### Method 2: Manual Installation

```bash
# Core dependencies
pip3 install dearpygui>=1.9.0
pip3 install numpy pandas scipy

# XRD processing libraries (optional but recommended)
pip3 install pyFAI fabio h5py hdf5plugin

# Additional tools
pip3 install matplotlib Pillow
```

---

## 🖥️ Running in Different Environments

### Local Desktop Machine ✅ (Easiest)

Just run directly:
```bash
python3 main_dpg.py
```

### Remote Server (SSH) 🌐

You need X11 forwarding:

#### On Linux/macOS Client:
```bash
# Connect with X11 forwarding
ssh -X username@server

# Verify display
echo $DISPLAY  # Should show something like "localhost:10.0"

# Run application
python3 main_dpg.py
```

#### On Windows Client:
1. Install [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or [Xming](https://sourceforge.net/projects/xming/)
2. Start X server
3. Use PuTTY with X11 forwarding enabled, or:
```bash
ssh -X username@server
python3 main_dpg.py
```

### Windows WSL (Windows Subsystem for Linux) 🪟

#### WSL2:
```bash
# 1. On Windows: Install VcXsrv
#    Download from: https://sourceforge.net/projects/vcxsrv/

# 2. Start VcXsrv with:
#    - Multiple windows
#    - Display number: 0
#    - Disable access control: ✓

# 3. In WSL terminal:
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
export LIBGL_ALWAYS_INDIRECT=1

# 4. Run application
python3 main_dpg.py

# Optional: Add to ~/.bashrc for persistence:
echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '"'"'{print $2}'"'"'):0' >> ~/.bashrc
```

#### WSL1:
```bash
export DISPLAY=:0
python3 main_dpg.py
```

### Docker Container 🐳

If running in Docker, you need to share X11 socket:

```bash
# Linux
docker run -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd):/workspace \
  your-image python3 /workspace/main_dpg.py

# Allow X server connections first:
xhost +local:docker
```

---

## 🐛 Troubleshooting

### Problem 1: "No module named 'dearpygui'"

**Solution:**
```bash
pip3 install dearpygui
# or
pip3 install -r requirements.txt
```

### Problem 2: "cannot connect to X server" or Black Screen

**Possible causes:**
- No X server running
- DISPLAY variable not set
- X11 forwarding not enabled

**Solutions:**

#### Check DISPLAY:
```bash
echo $DISPLAY
# Should output something like ":0" or "localhost:10.0"
```

#### If empty, set it:
```bash
export DISPLAY=:0  # Local
# or
export DISPLAY=localhost:10.0  # SSH
```

#### Test X server:
```bash
# Install x11-apps if not available
sudo apt-get install x11-apps  # Debian/Ubuntu
sudo yum install xorg-x11-apps  # RHEL/CentOS

# Test
xclock  # Should display a clock
```

### Problem 3: "ModuleNotFoundError: No module named 'pyFAI'"

**Solution:**

This is optional. The GUI will still run, but some features may be limited.

```bash
pip3 install pyFAI fabio h5py
```

### Problem 4: GUI is very slow

**Solutions:**
1. Update graphics drivers
2. Check if running through remote connection (inherently slower)
3. Reduce window size in code if needed

### Problem 5: Import errors in modules

**Solution:**

Ensure all files are in the same directory:
```bash
ls -1 *_dpg.py
# Should show:
# gui_base_dpg.py
# main_dpg.py
# powder_module_dpg.py
# radial_module_dpg.py
# single_crystal_module_dpg.py
```

---

## 📦 Standalone Module Testing

You can test individual modules:

```bash
# Test powder module
python3 powder_module_dpg.py

# Test radial module
python3 radial_module_dpg.py

# Test single crystal module
python3 single_crystal_module_dpg.py
```

---

## 🔧 Environment Variables

Useful environment variables:

```bash
# Display
export DISPLAY=:0

# For WSL2
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# For better OpenGL compatibility
export LIBGL_ALWAYS_INDIRECT=1

# For HiDPI displays
export GDK_SCALE=2
export GDK_DPI_SCALE=0.5
```

---

## 📚 Additional Resources

### DearPyGUI Documentation
- Official: https://dearpygui.readthedocs.io/
- GitHub: https://github.com/hoffstadt/DearPyGui

### X11 Setup
- Linux: Pre-installed on most distributions
- macOS: Install [XQuartz](https://www.xquartz.org/)
- Windows: Install [VcXsrv](https://sourceforge.net/projects/vcxsrv/)

---

## ✅ Verification

After installation, verify everything works:

```bash
# Run environment check
python3 check_environment.py

# If all checks pass, run the GUI
python3 main_dpg.py
```

You should see:
- A window titled "XRD Data Post-Processing - Loading..."
- A splash screen with progress bar
- Main application with three tabs: Powder XRD, Single Crystal XRD, Radial XRD

---

## 💡 Tips

1. **First Time Setup**: Run `check_environment.py` to diagnose issues
2. **Remote Work**: X11 forwarding works but is slower than local
3. **WSL Users**: VcXsrv is the easiest solution
4. **Mac Users**: XQuartz is required for X11 support
5. **Performance**: Local execution is always fastest

---

## 🆘 Still Having Issues?

If you're still having problems:

1. Run the diagnostic: `python3 check_environment.py`
2. Check the output for specific error messages
3. Verify you're in a graphical environment: `echo $DISPLAY`
4. Test basic X11: `xclock` (if available)
5. Check Python version: `python3 --version` (need 3.7+)

---

## 📝 Quick Reference

| Environment | Command |
|-------------|---------|
| Local Linux/Mac | `python3 main_dpg.py` |
| Local Windows | `python main_dpg.py` |
| SSH (Linux/Mac) | `ssh -X user@host` then `python3 main_dpg.py` |
| WSL2 | Set DISPLAY first, then `python3 main_dpg.py` |
| Docker | Share X11 socket, then run |

---

Good luck! 🚀
