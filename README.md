# XRD Data Post-Processing Suite

A comprehensive GUI application for X-ray diffraction (XRD) data analysis and processing, built with DearPyGUI.

<img alt="XRD Processing" src="https://img.shields.io/badge/XRD-Processing-blue">
<img alt="Python 3.7+" src="https://img.shields.io/badge/python-3.7+-green">
<img alt="DearPyGUI" src="https://img.shields.io/badge/GUI-DearPyGUI-orange">

## 🌟 Features

### Three Integrated Modules:

#### 1. **Powder XRD Module** 📊
- Batch 1D integration of 2D diffraction patterns
- Peak fitting and analysis
- Phase identification
- Volume calculation
- Equation of State (EoS) fitting
- Multiple output formats (.xy, .dat, .chi, .fxye)

#### 2. **Radial XRD Module** 🔄
- Azimuthal integration with customizable angle ranges
- Single sector, multiple sectors, and bin modes
- Quadrant and octant presets
- Support for PONI calibration files
- Mask file support

#### 3. **Single Crystal XRD Module** 💎
- Single crystal diffraction data processing
- Peak indexing (FFT, DIRAX, MOSFLM methods)
- Unit cell refinement
- Crystal system constraints (7 systems supported)
- Multiple output formats (CIF, HKL, FCF)

## 🚀 Quick Start

### 📖 Read This First!
**如果界面打不开，请先阅读：**
- 中文用户: [START_HERE.md](START_HERE.md) ⭐
- English users: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

### 🔍 Check Your Environment
```bash
# Run diagnostic tool
python3 check_environment.py
```

### 📦 Installation

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the application
python3 main_dpg.py
```

### 🐧 Linux/macOS Quick Start
```bash
chmod +x run_gui.sh
./run_gui.sh
```

### 🪟 Windows Quick Start
```bash
pip install -r requirements.txt
python main_dpg.py
```

## 📋 Requirements

- **Python**: 3.7 or higher
- **Display**: Graphical environment (X11/Wayland/Windows desktop)
- **Dependencies**: See `requirements.txt`

### Core Dependencies
- `dearpygui` - Modern GUI framework
- `numpy`, `pandas`, `scipy` - Scientific computing
- `pyFAI` - XRD integration (optional but recommended)
- `h5py`, `fabio` - Data file formats

## 🖥️ Supported Environments

| Environment | Status | Notes |
|-------------|--------|-------|
| Local Desktop (Linux) | ✅ Works | Recommended |
| Local Desktop (Windows) | ✅ Works | Native support |
| Local Desktop (macOS) | ✅ Works | Requires XQuartz |
| Remote Server (X11) | ⚠️ Works | Requires X11 forwarding |
| WSL + VcXsrv | ⚠️ Works | Requires setup |
| Headless Server | ❌ No GUI | Use alternative |

## 📁 Project Structure

```
workspace/
├── main_dpg.py                      # Main application entry
├── gui_base_dpg.py                  # Base GUI class
├── dpg_components.py                # Reusable GUI components
│
├── powder_module_dpg.py             # Powder XRD module
├── radial_module_dpg.py             # Radial integration module  
├── single_crystal_module_dpg.py    # Single crystal module (NEW!)
│
├── requirements.txt                 # Python dependencies
├── check_environment.py             # Environment diagnostic tool
├── run_gui.sh                       # Launch script (Linux/Mac)
│
├── START_HERE.md                    # Quick start guide (中文)
├── INSTALLATION_GUIDE.md            # Detailed installation
├── SINGLE_CRYSTAL_MODULE_README.md  # Single crystal docs
└── README.md                        # This file
```

## 🎨 Screenshots & UI

### Main Window
- Three-tab interface for different XRD techniques
- Modern, clean design
- Responsive layout

### Powder XRD
- Integration settings
- Peak fitting controls
- Volume calculation
- Progress monitoring

### Radial XRD  
- Azimuthal angle reference
- Multiple integration modes
- Sector configuration
- Batch processing

### Single Crystal XRD
- Data input panel
- Crystal parameters
- Unit cell management
- Processing options
- Real-time results table

## 🔧 Troubleshooting

### Problem: "打不开UI界面" / "Cannot open GUI"

**Solution**: Run the diagnostic tool first!
```bash
python3 check_environment.py
```

Common issues:
1. **No display** → Run on local machine or use X11 forwarding
2. **Missing packages** → Run `pip3 install -r requirements.txt`
3. **Wrong Python version** → Need Python 3.7+

### Detailed Solutions

See:
- [START_HERE.md](START_HERE.md) - 中文快速解决方案
- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Complete English guide

## 🧪 Testing Individual Modules

Each module can be run standalone:

```bash
# Test powder module
python3 powder_module_dpg.py

# Test radial module
python3 radial_module_dpg.py

# Test single crystal module
python3 single_crystal_module_dpg.py
```

## 📚 Documentation

| File | Description |
|------|-------------|
| `START_HERE.md` | 快速启动指南（中文）- 解决"打不开界面"问题 |
| `INSTALLATION_GUIDE.md` | Complete installation guide (English) |
| `SINGLE_CRYSTAL_MODULE_README.md` | Single crystal module documentation |
| `README.md` | This file - Project overview |

## 🛠️ Development

### Code Structure
- **MVC Pattern**: Separation of GUI and logic
- **Modular Design**: Each module is independent
- **Thread-safe**: Background processing for heavy operations
- **Extensible**: Easy to add new features

### Adding New Modules
1. Inherit from `GUIBase`
2. Implement `setup_ui()` method
3. Add to `main_dpg.py` tab system
4. Follow existing module patterns

## 📊 Features by Module

### Powder XRD
- ✅ 1D integration (pyFAI)
- ✅ Peak fitting (pseudo-Voigt, Gaussian)
- ✅ Interactive fitting GUI
- ✅ Volume calculation from peak positions
- ✅ EoS fitting (Birch-Murnaghan)
- ✅ Batch processing
- ✅ Multiple output formats

### Radial XRD
- ✅ Azimuthal integration
- ✅ PONI calibration support
- ✅ Mask file support
- ✅ Single/Multiple/Bin modes
- ✅ Preset configurations
- ✅ Custom sector definition
- ✅ Batch processing

### Single Crystal XRD
- ✅ Data loading (CIF, HKL, FCF)
- ✅ Peak indexing
- ✅ Unit cell refinement
- ✅ 7 crystal systems
- ✅ Space group handling
- ✅ Wavelength presets
- ✅ Multiple output formats
- ✅ Real-time results display

## 🤝 Contributing

Contributions are welcome! Please:
1. Follow existing code style
2. Test your changes
3. Update documentation
4. Submit pull requests

## 📄 License

[Add your license information here]

## 👥 Authors

[Add author information here]

## 🙏 Acknowledgments

- **DearPyGUI**: Modern Python GUI framework
- **pyFAI**: Fast Azimuthal Integration
- **NumPy/SciPy**: Scientific computing

## 📮 Support

For issues:
1. Run `python3 check_environment.py`
2. Check [START_HERE.md](START_HERE.md) or [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
3. Review error messages carefully
4. Verify all dependencies are installed

## 🔄 Version History

- **v2.0** (Latest) - DearPyGUI version with all three modules
- **v1.0** - Initial Tkinter version

## 🎯 Roadmap

Future enhancements:
- [ ] 3D structure visualization
- [ ] Automated report generation
- [ ] Database integration
- [ ] Cloud processing support
- [ ] Mobile companion app

---

**Happy XRD processing! 🔬✨**

For quick help: `python3 check_environment.py`