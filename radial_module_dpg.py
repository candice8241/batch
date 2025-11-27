# -*- coding: utf-8 -*-
"""
XRD Azimuthal Integration Module - DearPyGUI Version
Handles azimuthal (radial) integration of 2D XRD diffraction patterns
"""

import dearpygui.dearpygui as dpg
import os
import glob
import threading
import numpy as np
from typing import List, Optional, Tuple
import traceback

# Scientific libraries
try:
    import hdf5plugin
    import h5py
    import pyFAI
    from pyFAI.integrator.azimuthal import AzimuthalIntegrator
    PYFAI_AVAILABLE = True
except ImportError:
    PYFAI_AVAILABLE = False
    print("Warning: pyFAI not available. Install with: pip install pyFAI")

from dpg_components import ColorScheme, MessageDialog
from gui_base_dpg import GUIBase


class XRDAzimuthalIntegrator:
    """Class to handle azimuthal integration of XRD diffraction data"""

    def __init__(self, poni_file: str, mask_file: Optional[str] = None):
        """
        Initialize azimuthal integrator
        
        Args:
            poni_file: Path to PONI calibration file
            mask_file: Optional path to mask file
        """
        self.poni_file = poni_file
        self.mask_file = mask_file
        self.ai = None
        self.mask = None
        self._load_calibration()
        if mask_file and os.path.exists(mask_file):
            self._load_mask()

    def _load_calibration(self):
        """Load calibration from PONI file"""
        if not PYFAI_AVAILABLE:
            raise ImportError("pyFAI is not available")
            
        if not os.path.exists(self.poni_file):
            raise FileNotFoundError(f"PONI file not found: {self.poni_file}")
            
        print(f"Loading calibration from: {self.poni_file}")
        self.ai = pyFAI.load(self.poni_file)
        print(f"  Detector: {self.ai.detector.name}")
        print(f"  Distance: {self.ai.dist * 1000:.2f} mm")
        print(f"  Wavelength: {self.ai.wavelength * 1e10:.4f} A")

    def _load_mask(self):
        """Load mask file"""
        if not os.path.exists(self.mask_file):
            print(f"Warning: Mask file not found: {self.mask_file}")
            return
            
        ext = os.path.splitext(self.mask_file)[1].lower()
        
        if ext == '.npy':
            self.mask = np.load(self.mask_file)
        elif ext in ['.edf', '.tif', '.tiff']:
            import fabio
            self.mask = fabio.open(self.mask_file).data
        else:
            print(f"Warning: Unsupported mask format: {ext}")
            
        if self.mask is not None:
            print(f"Mask loaded: {self.mask.shape}")

    def integrate_file(self, h5_file: str, output_dir: str, 
                      azimuth_range: Tuple[float, float] = (-180, 180),
                      npt: int = 4000, unit: str = '2th_deg',
                      sector_label: str = "Sector", 
                      dataset_path: str = "entry/data/data",
                      save_formats: List[str] = ['xy']) -> Tuple[str, np.ndarray, np.ndarray]:
        """
        Integrate a single HDF5 file
        
        Args:
            h5_file: Path to input HDF5 file
            output_dir: Output directory
            azimuth_range: (start, end) azimuthal angle range in degrees
            npt: Number of radial points
            unit: Unit for radial axis ('2th_deg', 'q_A^-1', 'r_mm')
            sector_label: Label for this sector
            dataset_path: Path to dataset in HDF5
            save_formats: List of output formats ('xy', 'dat', 'chi')
            
        Returns:
            Tuple of (output_path, radial_array, intensity_array)
        """
        if not PYFAI_AVAILABLE:
            raise ImportError("pyFAI is not available")
            
        # Load data
        with h5py.File(h5_file, 'r') as f:
            if dataset_path not in f:
                raise ValueError(f"Dataset '{dataset_path}' not found in {h5_file}")
            data = f[dataset_path][()]
        
        # Perform integration
        result = self.ai.integrate1d(
            data,
            npt=npt,
            unit=unit,
            azimuth_range=azimuth_range,
            mask=self.mask,
            error_model="poisson"
        )
        
        radial, intensity = result
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(h5_file))[0]
        output_base = os.path.join(output_dir, f"{base_name}_{sector_label}")
        
        # Save in requested formats
        for fmt in save_formats:
            if fmt == 'xy':
                output_file = f"{output_base}.xy"
                np.savetxt(output_file, np.column_stack([radial, intensity]),
                          fmt='%.6f', delimiter=' ', 
                          header=f"{unit}  Intensity")
            elif fmt == 'dat':
                output_file = f"{output_base}.dat"
                np.savetxt(output_file, np.column_stack([radial, intensity]),
                          fmt='%.6f', delimiter='\t')
            elif fmt == 'chi':
                output_file = f"{output_base}.chi"
                with open(output_file, 'w') as f:
                    f.write(f"# Azimuthal integration: {azimuth_range[0]}-{azimuth_range[1]} deg\n")
                    f.write(f"# Unit: {unit}\n")
                    f.write(f"# Number of points: {npt}\n")
                    for r, i in zip(radial, intensity):
                        f.write(f"{r:.6f} {i:.6f}\n")
        
        return output_base + '.xy', radial, intensity

    def batch_process(self, h5_files: List[str], output_dir: str, 
                     progress_callback=None, **kwargs) -> List[str]:
        """
        Process multiple files
        
        Args:
            h5_files: List of HDF5 file paths
            output_dir: Output directory
            progress_callback: Optional callback(current, total, filename)
            **kwargs: Additional arguments for integrate_file
            
        Returns:
            List of output file paths
        """
        output_files = []
        total = len(h5_files)
        
        for i, h5_file in enumerate(h5_files, 1):
            if progress_callback:
                progress_callback(i, total, os.path.basename(h5_file))
            
            try:
                output_path, _, _ = self.integrate_file(h5_file, output_dir, **kwargs)
                output_files.append(output_path)
            except Exception as e:
                print(f"Error processing {h5_file}: {e}")
                
        return output_files


class RadialIntegrationModule(GUIBase):
    """Azimuthal (Radial) Integration Module - DearPyGUI Version"""

    def __init__(self, parent_tag: str):
        """
        Initialize Radial Integration module
        
        Args:
            parent_tag: Parent container tag
        """
        super().__init__()
        self.parent_tag = parent_tag
        self._init_variables()
        
        # Processing state
        self.processing = False
        self.stop_processing = False
        self._cleanup_lock = threading.Lock()
        self._is_destroyed = False

    def _init_variables(self):
        """Initialize all variables"""
        self.values = {
            'poni_path': '',
            'mask_path': '',
            'input_pattern': '',
            'output_dir': '',
            'dataset_path': 'entry/data/data',
            'npt': 4000,
            'unit': '2th_deg',
            
            # Azimuthal settings
            'mode': 'single',  # 'single', 'multiple', 'bin'
            'azimuth_start': 0.0,
            'azimuth_end': 90.0,
            'sector_label': 'Sector_1',
            
            # Multiple sectors (preset)
            'preset': 'quadrants',  # 'quadrants', 'octants', 'custom'
            
            # Bin mode
            'bin_start': 0.0,
            'bin_end': 360.0,
            'bin_step': 10.0,
            
            # Output formats
            'format_xy': True,
            'format_dat': False,
            'format_chi': False,
            'output_csv': True,
        }
        
        # Custom sectors for multiple mode
        self.custom_sectors = []

    def setup_ui(self):
        """Setup the complete UI"""
        with dpg.child_window(parent=self.parent_tag, border=False, menubar=False, show=False) as module_root:

            # Reference Section
            self._create_reference_section()
            
            dpg.add_spacer(height=10)
            
            # Integration Settings Card
            self._create_integration_card()
            
            dpg.add_spacer(height=15)
            
            # Azimuthal Angle Settings Card
            self._create_azimuthal_card()
            
            dpg.add_spacer(height=15)
            
            # Output Options Card
            self._create_output_card()
            
            dpg.add_spacer(height=15)
            
            # Action Buttons
            self._create_action_buttons()

            dpg.add_spacer(height=15)

            # Progress and Log
            self._create_progress_log()

        dpg.configure_item(module_root, show=True)

    def _create_reference_section(self):
        """Create azimuthal angle reference section"""
        with dpg.child_window(height=100, border=True, menubar=False):
            dpg.add_text("Azimuthal Angle Reference", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_spacer(height=5)
            dpg.add_text("0 deg = Right (->)  |  90 deg = Top (^)  |  180 deg = Left (<-)  |  270 deg = Bottom (v)",
                        color=ColorScheme.TEXT_DARK + (255,))
            dpg.add_text("Counter-clockwise rotation from right horizontal",
                        color=ColorScheme.TEXT_LIGHT + (255,))

    def _create_integration_card(self):
        """Create integration settings card"""
        with dpg.child_window(height=280, border=True, menubar=False):
            dpg.add_text("Integration Settings", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # PONI file
            with dpg.group(horizontal=True):
                dpg.add_text("PONI File:", width=120)
                dpg.add_input_text(
                    tag="radial_poni_path",
                    width=400,
                    callback=lambda s, a: self._update_value('poni_path', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file('poni_path', [("PONI files", "*.poni")])
                )
            
            # Mask file (optional)
            with dpg.group(horizontal=True):
                dpg.add_text("Mask File:", width=120)
                dpg.add_input_text(
                    tag="radial_mask_path",
                    width=400,
                    callback=lambda s, a: self._update_value('mask_path', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file('mask_path', [("Mask files", "*.edf;*.npy;*.tif")])
                )
            
            # Input files
            with dpg.group(horizontal=True):
                dpg.add_text("Input .h5 Files:", width=120)
                dpg.add_input_text(
                    tag="radial_input_pattern",
                    width=400,
                    hint="Path or pattern (e.g., /path/*.h5)",
                    callback=lambda s, a: self._update_value('input_pattern', a)
                )
                dpg.add_button(
                    label="Browse Folder",
                    callback=lambda: self._browse_folder('input_pattern')
                )
            
            # Output directory
            with dpg.group(horizontal=True):
                dpg.add_text("Output Directory:", width=120)
                dpg.add_input_text(
                    tag="radial_output_dir",
                    width=400,
                    callback=lambda s, a: self._update_value('output_dir', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_folder('output_dir')
                )
            
            dpg.add_spacer(height=5)
            
            # Parameters
            with dpg.group(horizontal=True):
                dpg.add_text("Number of Points:", width=120)
                dpg.add_input_int(
                    tag="radial_npt",
                    default_value=4000,
                    width=100,
                    callback=lambda s, a: self._update_value('npt', a)
                )
                
                dpg.add_spacer(width=20)
                dpg.add_text("Unit:")
                dpg.add_combo(
                    ['2th_deg', 'q_A^-1', 'r_mm'],
                    tag="radial_unit",
                    default_value='2th_deg',
                    width=120,
                    callback=lambda s, a: self._update_value('unit', a)
                )
            
            # Dataset path
            with dpg.group(horizontal=True):
                dpg.add_text("HDF5 Dataset Path:", width=120)
                dpg.add_input_text(
                    tag="radial_dataset_path",
                    default_value="entry/data/data",
                    width=300,
                    callback=lambda s, a: self._update_value('dataset_path', a)
                )

    def _create_azimuthal_card(self):
        """Create azimuthal angle settings card"""
        with dpg.child_window(height=300, border=True, menubar=False):
            dpg.add_text("Azimuthal Angle Settings", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Mode selection
            dpg.add_text("Integration Mode:")
            dpg.add_radio_button(
                ['Single Sector', 'Multiple Sectors (Preset)', 'Bin Mode'],
                tag="radial_mode",
                default_value='Single Sector',
                callback=self._on_mode_changed,
                horizontal=True
            )
            
            dpg.add_spacer(height=10)
            
            # Single sector settings
            with dpg.child_window(tag="radial_single_group", height=150, 
                                 border=True, menubar=False, show=True):
                dpg.add_text("Single Sector Configuration:")
                dpg.add_separator()
                dpg.add_spacer(height=5)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Start Angle (deg):", width=120)
                    dpg.add_input_double(
                        tag="radial_azimuth_start",
                        default_value=0.0,
                        width=100,
                        format="%.1f",
                        callback=lambda s, a: self._update_value('azimuth_start', a)
                    )
                    
                    dpg.add_spacer(width=20)
                    dpg.add_text("End Angle (deg):", width=120)
                    dpg.add_input_double(
                        tag="radial_azimuth_end",
                        default_value=90.0,
                        width=100,
                        format="%.1f",
                        callback=lambda s, a: self._update_value('azimuth_end', a)
                    )
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Sector Label:", width=120)
                    dpg.add_input_text(
                        tag="radial_sector_label",
                        default_value="Sector_1",
                        width=150,
                        callback=lambda s, a: self._update_value('sector_label', a)
                    )
            
            # Multiple sectors (preset)
            with dpg.child_window(tag="radial_multiple_group", height=150,
                                 border=True, menubar=False, show=False):
                dpg.add_text("Multiple Sectors - Preset Configuration:")
                dpg.add_separator()
                dpg.add_spacer(height=5)
                
                dpg.add_text("Select Preset:")
                dpg.add_radio_button(
                    ['Quadrants (4 x 90 deg)', 'Octants (8 x 45 deg)', 'Custom Bins'],
                    tag="radial_preset",
                    default_value='Quadrants (4 x 90 deg)',
                    callback=lambda s, a: self._update_value('preset', 
                        'quadrants' if 'Quadrants' in a else 'octants' if 'Octants' in a else 'custom')
                )
            
            # Bin mode settings
            with dpg.child_window(tag="radial_bin_group", height=150,
                                 border=True, menubar=False, show=False):
                dpg.add_text("Bin Mode Configuration:")
                dpg.add_separator()
                dpg.add_spacer(height=5)
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Start Angle (deg):", width=120)
                    dpg.add_input_double(
                        tag="radial_bin_start",
                        default_value=0.0,
                        width=100,
                        format="%.1f",
                        callback=lambda s, a: self._update_value('bin_start', a)
                    )
                    
                    dpg.add_spacer(width=20)
                    dpg.add_text("End Angle (deg):", width=120)
                    dpg.add_input_double(
                        tag="radial_bin_end",
                        default_value=360.0,
                        width=100,
                        format="%.1f",
                        callback=lambda s, a: self._update_value('bin_end', a)
                    )
                
                with dpg.group(horizontal=True):
                    dpg.add_text("Bin Step (deg):", width=120)
                    dpg.add_input_double(
                        tag="radial_bin_step",
                        default_value=10.0,
                        width=100,
                        format="%.1f",
                        callback=lambda s, a: self._update_value('bin_step', a)
                    )

    def _create_output_card(self):
        """Create output options card"""
        with dpg.child_window(height=120, border=True, menubar=False):
            dpg.add_text("Output Options", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            dpg.add_text("Select Output Formats:")
            with dpg.group(horizontal=True):
                dpg.add_checkbox(
                    label=".xy (X-Y data)",
                    tag="radial_format_xy",
                    default_value=True,
                    callback=lambda s, a: self._update_value('format_xy', a)
                )
                dpg.add_checkbox(
                    label=".dat (Tab-delimited)",
                    tag="radial_format_dat",
                    default_value=False,
                    callback=lambda s, a: self._update_value('format_dat', a)
                )
                dpg.add_checkbox(
                    label=".chi (GSAS format)",
                    tag="radial_format_chi",
                    default_value=False,
                    callback=lambda s, a: self._update_value('format_chi', a)
                )
            
            dpg.add_checkbox(
                label="Generate CSV Summary",
                tag="radial_output_csv",
                default_value=True,
                callback=lambda s, a: self._update_value('output_csv', a)
            )

    def _create_action_buttons(self):
        """Create action buttons"""
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Run Integration",
                callback=self.run_integration,
                width=200,
                height=40
            )
            dpg.add_button(
                label="Stop",
                callback=self.stop_integration,
                width=100,
                height=40
            )
            dpg.add_button(
                label="Clear Log",
                callback=self.clear_log,
                width=100,
                height=40
            )

    def _create_progress_log(self):
        """Create progress bar and log section"""
        with dpg.child_window(height=300, border=True, menubar=False):
            dpg.add_text("Process Progress & Log", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            dpg.add_text("Progress:")
            dpg.add_progress_bar(tag="radial_progress", width=-1, default_value=0.0)
            
            dpg.add_spacer(height=10)
            dpg.add_text("Log:")
            dpg.add_input_text(
                tag="radial_log",
                multiline=True,
                readonly=True,
                height=180,
                width=-1
            )

    def _on_mode_changed(self, sender, app_data):
        """Handle mode change"""
        mode_map = {
            'Single Sector': 'single',
            'Multiple Sectors (Preset)': 'multiple',
            'Bin Mode': 'bin'
        }
        self.values['mode'] = mode_map.get(app_data, 'single')
        
        # Show/hide relevant UI sections
        dpg.configure_item("radial_single_group", show=(self.values['mode'] == 'single'))
        dpg.configure_item("radial_multiple_group", show=(self.values['mode'] == 'multiple'))
        dpg.configure_item("radial_bin_group", show=(self.values['mode'] == 'bin'))

    def _update_value(self, key: str, value):
        """Update internal value"""
        self.values[key] = value

    def _browse_file(self, key: str, file_types: List[Tuple[str, str]]):
        """Browse for file using DPG file dialog"""
        def callback(sender, app_data):
            selections = app_data['selections']
            if selections:
                file_path = list(selections.values())[0]
                self.values[key] = file_path
                dpg.set_value(f"radial_{key}", file_path)
        
        # Create file dialog
        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=callback,
            width=700,
            height=400,
            modal=True
        ):
            for desc, pattern in file_types:
                dpg.add_file_extension(pattern.replace('*.', '.'))

    def _browse_folder(self, key: str):
        """Browse for folder using DPG file dialog"""
        def callback(sender, app_data):
            folder_path = app_data['file_path_name']
            self.values[key] = folder_path
            dpg.set_value(f"radial_{key}", folder_path)
        
        # Create directory dialog
        with dpg.file_dialog(
            directory_selector=True,
            show=True,
            callback=callback,
            width=700,
            height=400,
            modal=True
        ):
            pass

    def log(self, message: str):
        """Add message to log"""
        if dpg.does_item_exist("radial_log"):
            current = dpg.get_value("radial_log")
            dpg.set_value("radial_log", current + message + "\n")

    def clear_log(self):
        """Clear log"""
        if dpg.does_item_exist("radial_log"):
            dpg.set_value("radial_log", "")

    def run_integration(self):
        """Run integration"""
        # Validate inputs
        if not self.values['poni_path']:
            MessageDialog.show_error("Error", "Please specify PONI calibration file")
            return
        
        if not self.values['output_dir']:
            MessageDialog.show_error("Error", "Please specify output directory")
            return
        
        if not self.values['input_pattern']:
            MessageDialog.show_error("Error", "Please specify input files or folder")
            return
        
        if not PYFAI_AVAILABLE:
            MessageDialog.show_error("Error", "pyFAI library is not available. Please install it.")
            return
        
        # Start processing in background thread
        self.processing = True
        self.stop_processing = False
        
        thread = threading.Thread(target=self._run_integration_thread, daemon=True)
        thread.start()

    def _run_integration_thread(self):
        """Background integration thread"""
        try:
            dpg.set_value("radial_progress", 0.0)
            self.log("="*60)
            self.log("Starting azimuthal integration...")
            self.log("="*60)
            
            # Get integrator
            self.log(f"Loading calibration: {self.values['poni_path']}")
            integrator = XRDAzimuthalIntegrator(
                self.values['poni_path'], 
                self.values.get('mask_path', None)
            )
            self.log("[OK] Calibration loaded")
            
            # Get h5 files
            if os.path.isdir(self.values['input_pattern']):
                h5_files = sorted(glob.glob(os.path.join(self.values['input_pattern'], "*.h5")))
            else:
                h5_files = sorted(glob.glob(self.values['input_pattern']))
            
            if not h5_files:
                self.log("[ERROR] No .h5 files found")
                return
            
            total = len(h5_files)
            self.log(f"Found {total} file(s) to process")
            
            # Create output directory
            os.makedirs(self.values['output_dir'], exist_ok=True)
            
            # Get save formats
            save_formats = []
            if self.values['format_xy']:
                save_formats.append('xy')
            if self.values['format_dat']:
                save_formats.append('dat')
            if self.values['format_chi']:
                save_formats.append('chi')
            
            if not save_formats:
                save_formats = ['xy']  # Default
            
            # Get sectors based on mode
            sectors = self._get_sectors()
            
            self.log(f"Processing mode: {self.values['mode']}")
            self.log(f"Number of sectors: {len(sectors)}")
            self.log("")
            
            # Process each file
            for i, h5_file in enumerate(h5_files, 1):
                if self.stop_processing:
                    self.log("")
                    self.log("Processing stopped by user")
                    break
                
                self.log(f"[{i}/{total}] Processing: {os.path.basename(h5_file)}")
                
                try:
                    # Process each sector
                    for sector_idx, (start, end, label) in enumerate(sectors, 1):
                        integrator.integrate_file(
                            h5_file,
                            self.values['output_dir'],
                            azimuth_range=(start, end),
                            npt=self.values['npt'],
                            unit=self.values['unit'],
                            sector_label=label,
                            dataset_path=self.values['dataset_path'],
                            save_formats=save_formats
                        )
                    
                    self.log(f"[{i}/{total}] [OK] Completed")
                    
                except Exception as e:
                    self.log(f"[{i}/{total}] [ERROR] {str(e)}")
                    print(traceback.format_exc())
                
                # Update progress
                progress = i / total
                dpg.set_value("radial_progress", progress)
            
            self.log("")
            self.log("="*60)
            self.log("[OK] Integration complete!")
            self.log(f"Output directory: {self.values['output_dir']}")
            self.log("="*60)
            
        except Exception as e:
            self.log("")
            self.log(f"[ERROR] {str(e)}")
            print(traceback.format_exc())
        finally:
            self.processing = False
            dpg.set_value("radial_progress", 1.0)

    def _get_sectors(self) -> List[Tuple[float, float, str]]:
        """
        Get list of sectors based on current mode
        
        Returns:
            List of (start_angle, end_angle, label) tuples
        """
        sectors = []
        
        if self.values['mode'] == 'single':
            # Single sector
            sectors.append((
                self.values['azimuth_start'],
                self.values['azimuth_end'],
                self.values['sector_label']
            ))
            
        elif self.values['mode'] == 'multiple':
            # Multiple sectors (preset)
            preset = self.values.get('preset', 'quadrants')
            
            if preset == 'quadrants':
                # 4 quadrants
                for i in range(4):
                    start = i * 90.0
                    end = (i + 1) * 90.0
                    label = f"Q{i+1}_{int(start)}-{int(end)}"
                    sectors.append((start, end, label))
                    
            elif preset == 'octants':
                # 8 octants
                for i in range(8):
                    start = i * 45.0
                    end = (i + 1) * 45.0
                    label = f"Oct{i+1}_{int(start)}-{int(end)}"
                    sectors.append((start, end, label))
                    
        elif self.values['mode'] == 'bin':
            # Bin mode
            start = self.values['bin_start']
            end = self.values['bin_end']
            step = self.values['bin_step']
            
            current = start
            bin_num = 1
            while current < end:
                bin_end = min(current + step, end)
                label = f"Bin{bin_num}_{int(current)}-{int(bin_end)}"
                sectors.append((current, bin_end, label))
                current = bin_end
                bin_num += 1
        
        return sectors

    def stop_integration(self):
        """Stop ongoing integration"""
        self.stop_processing = True
        self.log("")
        self.log("Stopping integration...")

    def cleanup(self):
        """Clean up resources"""
        with self._cleanup_lock:
            self._is_destroyed = True
            self.stop_processing = True


# ==============================================================================
# Main entry point for standalone testing
# ==============================================================================

def main():
    """Main function for standalone execution"""
    # Suppress warnings
    import warnings
    warnings.filterwarnings('ignore')
    
    dpg.create_context()

    # Setup theme and font
    from dpg_components import setup_dpg_theme, setup_arial_font
    setup_dpg_theme()
    try:
        setup_arial_font(size=14)
    except:
        pass

    # Create main window
    with dpg.window(tag="radial_main", label="Azimuthal Integration Module"):
        module = RadialIntegrationModule("radial_main")
        module.setup_ui()

    dpg.create_viewport(title="Radial Integration Module", width=1200, height=900)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("radial_main", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()