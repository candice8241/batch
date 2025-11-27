# -*- coding: utf-8 -*-
"""
XRD Azimuthal Integration Module - Dear PyGui Version
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

from gui_base_dpg import GUIBase


class XRDAzimuthalIntegrator:
    """Class to handle azimuthal integration of XRD diffraction data"""

    def __init__(self, poni_file: str, mask_file: Optional[str] = None):
        self.poni_file = poni_file
        self.mask_file = mask_file
        self.ai = None
        self.mask = None
        self._load_calibration()
        if mask_file and os.path.exists(mask_file):
            self._load_mask()

    def _load_calibration(self):
        if not os.path.exists(self.poni_file):
            raise FileNotFoundError(f"PONI file not found: {self.poni_file}")
        print(f"Loading calibration from: {self.poni_file}")
        self.ai = pyFAI.load(self.poni_file)
        print(f"  Detector: {self.ai.detector.name}")
        print(f"  Distance: {self.ai.dist * 1000:.2f} mm")
        print(f"  Wavelength: {self.ai.wavelength * 1e10:.4f} Å")

    def _load_mask(self):
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

    def integrate_file(self, h5_file: str, output_dir: str, **kwargs):
        """Integrate a single HDF5 file"""
        azimuth_range = kwargs.get('azimuth_range', (-180, 180))
        npt = kwargs.get('npt', 4000)
        unit = kwargs.get('unit', '2th_deg')
        sector_label = kwargs.get('sector_label', 'Sector')
        dataset_path = kwargs.get('dataset_path', 'entry/data/data')
        
        with h5py.File(h5_file, 'r') as f:
            if dataset_path not in f:
                raise ValueError(f"Dataset '{dataset_path}' not found in {h5_file}")
            data = f[dataset_path][()]
        
        result = self.ai.integrate1d(
            data,
            npt=npt,
            unit=unit,
            azimuth_range=azimuth_range,
            mask=self.mask,
            error_model="poisson"
        )
        
        radial, intensity = result
        
        base_name = os.path.splitext(os.path.basename(h5_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}_{sector_label}.xy")
        
        np.savetxt(output_file, np.column_stack([radial, intensity]),
                  fmt='%.6f', delimiter=' ', header=f"{unit}  Intensity")
        
        return output_file, radial, intensity

    def batch_process(self, h5_files: List[str], output_dir: str, 
                     progress_callback=None, **kwargs):
        """Process multiple files"""
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
    """Azimuthal Integration module - Dear PyGui version"""

    def __init__(self, parent_tag: str):
        super().__init__()
        self.parent_tag = parent_tag
        self._init_variables()
        self.processing = False
        self.stop_processing = False
        self.custom_sectors = []
        self._cleanup_lock = threading.Lock()
        self._is_destroyed = False

    def _init_variables(self):
        """Initialize all variables"""
        self.poni_path = ""
        self.mask_path = ""
        self.input_pattern = ""
        self.output_dir = ""
        self.dataset_path = "entry/data/data"
        self.npt = 4000
        self.unit = '2th_deg'
        self.azimuth_start = 0.0
        self.azimuth_end = 90.0
        self.sector_label = "Sector_1"
        self.preset = 'quadrants'
        self.mode = 'single'
        self.multiple_mode = 'custom'
        self.output_csv = True

        # Bin mode variables
        self.bin_mode = False
        self.bin_start = 0.0
        self.bin_end = 360.0
        self.bin_step = 10.0
        self.multi_bin_mode = False

        # Output formats
        self.format_xy = True
        self.format_dat = False
        self.format_chi = False

    def setup_ui(self):
        """Setup UI in the specified parent"""

        with dpg.child_window(parent=self.parent_tag, border=False):
            # Reference Section
            with dpg.group():
                dpg.add_text("🍓 Azimuthal Angle Reference:")
                dpg.add_text(
                    "0° = Right (→)  |  90° = Top (↑)  |  180° = Left (←)  |  270° = Bottom (↓)",
                    color=(107, 76, 122, 255)
                )
                dpg.add_text(
                    "Counter-clockwise rotation from right horizontal",
                    color=(150, 150, 150, 255)
                )
                dpg.add_separator()

            # Integration Settings
            with dpg.collapsing_header(label="Integration Settings", default_open=True):
                self._create_integration_settings()

            # Azimuthal Angle Settings
            with dpg.collapsing_header(label="Azimuthal Angle Settings", default_open=True):
                self._create_azimuthal_settings()

            # Output Options
            with dpg.collapsing_header(label="Output Options", default_open=True):
                self._create_output_options()

            # Progress
            with dpg.group():
                dpg.add_text("Process Progress:")
                dpg.add_progress_bar(tag="radial_progress", width=-1)

            # Log
            with dpg.collapsing_header(label="Process Log", default_open=True):
                dpg.add_input_text(
                    tag="radial_log",
                    multiline=True,
                    readonly=True,
                    height=200,
                    width=-1
                )

    def _create_integration_settings(self):
        """Create integration settings section"""
        with dpg.group():
            # PONI file
            with dpg.group(horizontal=True):
                dpg.add_text("PONI File:")
                dpg.add_input_text(
                    tag="radial_poni_path",
                    default_value=self.poni_path,
                    width=400,
                    callback=lambda s, a: setattr(self, 'poni_path', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file("radial_poni_path", [("PONI files", "*.poni")])
                )

            # Mask file
            with dpg.group(horizontal=True):
                dpg.add_text("Mask File:")
                dpg.add_input_text(
                    tag="radial_mask_path",
                    default_value=self.mask_path,
                    width=400,
                    callback=lambda s, a: setattr(self, 'mask_path', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file("radial_mask_path", [("Mask files", "*.edf;*.npy")])
                )

            # Input pattern
            with dpg.group(horizontal=True):
                dpg.add_text("Input .h5 Files:")
                dpg.add_input_text(
                    tag="radial_input_pattern",
                    default_value=self.input_pattern,
                    width=400,
                    callback=lambda s, a: setattr(self, 'input_pattern', a)
                )
                dpg.add_button(
                    label="Browse Folder",
                    callback=lambda: self._browse_folder("radial_input_pattern")
                )

            # Output directory
            with dpg.group(horizontal=True):
                dpg.add_text("Output Directory:")
                dpg.add_input_text(
                    tag="radial_output_dir",
                    default_value=self.output_dir,
                    width=400,
                    callback=lambda s, a: setattr(self, 'output_dir', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_folder("radial_output_dir")
                )

            # Parameters
            with dpg.group(horizontal=True):
                dpg.add_text("Number of Points:")
                dpg.add_input_int(
                    tag="radial_npt",
                    default_value=self.npt,
                    width=100,
                    callback=lambda s, a: setattr(self, 'npt', a)
                )

                dpg.add_text("Unit:")
                dpg.add_combo(
                    ['2th_deg', 'q_A^-1', 'r_mm'],
                    tag="radial_unit",
                    default_value=self.unit,
                    width=120,
                    callback=lambda s, a: setattr(self, 'unit', a)
                )

    def _create_azimuthal_settings(self):
        """Create azimuthal angle settings"""
        with dpg.group():
            # Mode selection
            dpg.add_text("Integration Mode:")
            dpg.add_radio_button(
                ['Single Sector', 'Multiple Sectors', 'Bin Mode'],
                tag="radial_mode",
                default_value='Single Sector',
                callback=self._on_mode_changed
            )

            # Single sector settings
            with dpg.group(tag="single_sector_group"):
                dpg.add_separator()
                dpg.add_text("Single Sector Configuration:")
                with dpg.group(horizontal=True):
                    dpg.add_text("Start Angle (°):")
                    dpg.add_input_double(
                        tag="radial_azimuth_start",
                        default_value=self.azimuth_start,
                        width=100,
                        format="%.1f",
                        callback=lambda s, a: setattr(self, 'azimuth_start', a)
                    )
                    dpg.add_text("End Angle (°):")
                    dpg.add_input_double(
                        tag="radial_azimuth_end",
                        default_value=self.azimuth_end,
                        width=100,
                        format="%.1f",
                        callback=lambda s, a: setattr(self, 'azimuth_end', a)
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Sector Label:")
                    dpg.add_input_text(
                        tag="radial_sector_label",
                        default_value=self.sector_label,
                        width=150,
                        callback=lambda s, a: setattr(self, 'sector_label', a)
                    )

            # Run button
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="🚀 Run Integration",
                    callback=self.run_integration,
                    width=200,
                    height=40
                )
                dpg.add_button(
                    label="⏹ Stop",
                    callback=self.stop_integration,
                    width=100,
                    height=40
                )

    def _create_output_options(self):
        """Create output options section"""
        with dpg.group():
            dpg.add_text("Select Output Formats:")
            with dpg.group(horizontal=True):
                dpg.add_checkbox(
                    label=".xy",
                    tag="radial_format_xy",
                    default_value=self.format_xy,
                    callback=lambda s, a: setattr(self, 'format_xy', a)
                )
                dpg.add_checkbox(
                    label=".dat",
                    tag="radial_format_dat",
                    default_value=self.format_dat,
                    callback=lambda s, a: setattr(self, 'format_dat', a)
                )
                dpg.add_checkbox(
                    label=".chi",
                    tag="radial_format_chi",
                    default_value=self.format_chi,
                    callback=lambda s, a: setattr(self, 'format_chi', a)
                )

            dpg.add_checkbox(
                label="Generate CSV Summary",
                tag="radial_output_csv",
                default_value=self.output_csv,
                callback=lambda s, a: setattr(self, 'output_csv', a)
            )

    def _on_mode_changed(self, sender, app_data):
        """Handle mode change"""
        mode_map = {
            'Single Sector': 'single',
            'Multiple Sectors': 'multiple',
            'Bin Mode': 'bin'
        }
        self.mode = mode_map.get(app_data, 'single')

        # Show/hide relevant UI sections
        # This would toggle visibility of different configuration groups

    def _browse_file(self, tag, file_types):
        """Browse for file"""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(filetypes=file_types)
        root.destroy()

        if filename:
            dpg.set_value(tag, filename)
            attr_name = tag.replace("radial_", "")
            setattr(self, attr_name, filename)

    def _browse_folder(self, tag):
        """Browse for folder"""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        foldername = filedialog.askdirectory()
        root.destroy()

        if foldername:
            dpg.set_value(tag, foldername)
            attr_name = tag.replace("radial_", "")
            setattr(self, attr_name, foldername)

    def log(self, message):
        """Add message to log"""
        current = dpg.get_value("radial_log")
        dpg.set_value("radial_log", current + message + "\n")

    def run_integration(self):
        """Run integration"""
        if not self.poni_path or not self.output_dir:
            self._show_error("Error", "Please specify PONI file and output directory")
            return

        self.processing = True
        self.stop_processing = False

        thread = threading.Thread(target=self._run_integration_thread, daemon=True)
        thread.start()

    def _run_integration_thread(self):
        """Background integration thread"""
        try:
            dpg.set_value("radial_progress", 0.0)

            # Get integrator
            integrator = XRDAzimuthalIntegrator(self.poni_path, self.mask_path)

            # Get h5 files
            if os.path.isdir(self.input_pattern):
                h5_files = sorted(glob.glob(os.path.join(self.input_pattern, "*.h5")))
            else:
                h5_files = sorted(glob.glob(self.input_pattern))

            if not h5_files:
                self.log("❌ No .h5 files found")
                return

            total = len(h5_files)
            self.log(f"📊 Processing {total} file(s)...\n")

            for i, h5_file in enumerate(h5_files, 1):
                if self.stop_processing:
                    self.log("\n⏹ Processing stopped by user")
                    break

                self.log(f"[{i}/{total}] Processing: {os.path.basename(h5_file)}")

                try:
                    integrator.integrate_file(
                        h5_file,
                        self.output_dir,
                        npt=self.npt,
                        unit=self.unit,
                        azimuth_range=(self.azimuth_start, self.azimuth_end),
                        sector_label=self.sector_label,
                        dataset_path=self.dataset_path
                    )
                    self.log(f"[{i}/{total}] ✓ Completed\n")
                except Exception as e:
                    self.log(f"[{i}/{total}] ❌ Error: {str(e)}\n")

                progress = i / total
                dpg.set_value("radial_progress", progress)

            self.log(f"\n{'='*60}")
            self.log("✅ Integration complete!")
            self.log(f"{'='*60}")

        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
        finally:
            self.processing = False
            dpg.set_value("radial_progress", 1.0)

    def stop_integration(self):
        """Stop ongoing integration"""
        self.stop_processing = True
        self.log("\n⏹ Stopping integration...")

    def _show_error(self, title, message):
        """Show error dialog"""
        with dpg.window(label=title, modal=True, show=True, tag="radial_error_modal"):
            dpg.add_text(message)
            dpg.add_button(
                label="OK",
                width=75,
                callback=lambda: dpg.delete_item("radial_error_modal")
            )

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
