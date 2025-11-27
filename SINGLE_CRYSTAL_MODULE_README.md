# Single Crystal XRD Module - DearPyGUI Version

## Overview

The `single_crystal_module_dpg.py` is a comprehensive module for processing single crystal X-ray diffraction data. This module provides a complete workflow from data loading to structure refinement.

## Features

### 1. **Data Input**
- Support for multiple file formats:
  - CIF (Crystallographic Information File)
  - HKL (Reflection data)
  - FCF (Structure factor file)
  - CSV/DAT (Generic data)
- Configurable experiment name
- Output directory selection

### 2. **Crystal Parameters**
- Crystal system selection:
  - Cubic, Tetragonal, Orthorhombic
  - Hexagonal, Trigonal, Monoclinic, Triclinic
- Space group input
- Wavelength configuration with presets:
  - Mo Kα (0.71073 Å)
  - Cu Kα (1.54178 Å)
  - Ag Kα (0.56087 Å)

### 3. **Unit Cell Parameters**
- Input for cell lengths (a, b, c)
- Input for cell angles (α, β, γ)
- Automatic volume calculation
- Crystal system constraints applied automatically

### 4. **Data Processing Options**

#### Data Reduction:
- Absorption correction
- Lorentz correction
- Polarization correction

#### Indexing Methods:
- FFT (Fast Fourier Transform)
- DIRAX
- MOSFLM
- Auto selection

#### Refinement:
- Least Squares method
- Maximum Likelihood method
- Robust refinement
- Configurable convergence criteria

### 5. **Output Formats**
- CIF (Crystallographic Information File)
- FCF (Structure factors)
- HKL (Reflection list)
- PDF Report

### 6. **Analysis Workflow**

The module provides four main operations:

1. **Load Data**: Import diffraction data from files
2. **Index Peaks**: Determine unit cell from peak positions
3. **Refine Cell**: Optimize unit cell parameters
4. **Full Analysis**: Complete workflow including:
   - Data loading
   - Correction applications
   - Peak indexing
   - Cell refinement
   - Output generation

### 7. **Results Display**

Real-time display of analysis results:
- Lattice type
- Space group
- Cell volume with estimated standard deviations (ESDs)
- R-factor
- Number of indexed reflections

### 8. **Progress Monitoring**
- Progress bar showing current operation status
- Detailed log output with timestamped messages
- Stop functionality for long-running operations

## User Interface Layout

### Top Section
- **Data Input Card**: File selection and experiment settings
- **Crystal Parameters Card**: Crystal system, space group, and wavelength
- **Unit Cell Card**: Cell dimensions and volume calculation

### Middle Section
- **Processing Options Card**: 
  - Left panel: Data reduction and indexing options
  - Right panel: Refinement settings and output formats

### Bottom Section
- **Action Buttons**: Quick access to main operations
- **Results Table**: Real-time display of analysis results
- **Progress & Log**: Status monitoring and detailed logging

## Integration with Main Application

The module is fully integrated into the main XRD Data Post-Processing application:

```python
from single_crystal_module_dpg import SingleCrystalModule

# In main_dpg.py
module = SingleCrystalModule("content_area")
module.setup_ui()
```

## Standalone Usage

The module can also be run independently:

```bash
python3 single_crystal_module_dpg.py
```

## Technical Details

### Classes

#### `SingleCrystalDataProcessor`
Handles data processing operations:
- Data loading from various formats
- Peak indexing algorithms
- Cell parameter refinement

#### `SingleCrystalModule`
Main GUI class inheriting from `GUIBase`:
- UI setup and management
- Event handling
- Thread management for background operations
- Results display and logging

### Threading
All intensive operations run in background threads to maintain UI responsiveness:
- Data loading
- Peak indexing
- Cell refinement
- Full analysis workflow

### Error Handling
- Comprehensive try-catch blocks
- User-friendly error messages
- Detailed traceback logging for debugging

## Dependencies

Required packages:
- dearpygui
- numpy
- pandas

Optional packages for full functionality:
- fabio (for image file reading)
- h5py (for HDF5 support)

## Future Enhancements

Potential additions:
1. Direct integration with CCP4/SHELX tools
2. 3D structure visualization
3. Reciprocal space viewer
4. Automated structure solution
5. Multi-dataset merging
6. Twinning detection and handling
7. Anomalous scattering analysis

## Notes

- The current implementation includes placeholder methods for some advanced features
- Full functionality requires additional crystallographic libraries
- The module follows the same design patterns as `powder_module_dpg.py` and `radial_module_dpg.py`
- All UI elements use consistent styling from `dpg_components.py`

## Example Workflow

1. Select your data file (CIF, HKL, etc.)
2. Set output directory
3. Configure crystal parameters:
   - Choose crystal system
   - Enter/verify space group
   - Set wavelength
4. Input initial unit cell parameters (if known)
5. Configure processing options
6. Click "Full Analysis" or run steps individually
7. Monitor progress in log window
8. Review results in results table
9. Find output files in specified directory

## Support

For issues or questions, refer to the main project documentation or examine the inline code comments.
