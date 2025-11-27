# -*- coding: utf-8 -*-
"""
Powder XRD Module - Migrated to Dear PyGui
Contains integration, peak fitting, phase analysis, and Birch-Murnaghan fitting
"""

import dearpygui.dearpygui as dpg
import threading
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import shutil
import glob

from batch_integration import BatchIntegrator
from half_auto_fitting import DataProcessor
from batch_cal_volume import XRayDiffractionAnalyzer as XRDAnalyzer
from crysfml_eos_module import CrysFMLEoS, EoSType, MultiEoSFitter
from theme_module import GUIBase


class PowderXRDModule(GUIBase):
    """Powder XRD processing module - Dear PyGui version"""

    def __init__(self):
        """Initialize Powder XRD module"""
        super().__init__()
        self.current_module = "integration"

        # Initialize variables
        self._init_variables()

        # Track running threads
        self.running_threads = []
        self._is_shutting_down = False
        self._cleanup_lock = threading.Lock()

    def _init_variables(self):
        """Initialize all variables"""
        # Integration and fitting variables
        self.poni_path = ""
        self.mask_path = ""
        self.input_pattern = ""
        self.output_dir = ""
        self.dataset_path = "entry/data/data"
        self.npt = 4000
        self.unit = '2θ (°)'
        self.fit_method = 'pseudo'

        # Output format options
        self.format_xy = True
        self.format_dat = False
        self.format_chi = False
        self.format_fxye = False
        self.format_svg = False
        self.format_png = False

        # Stacked plot options
        self.create_stacked_plot = False
        self.stacked_plot_offset = 'auto'

        # Phase analysis variables
        self.phase_peak_csv = ""
        self.phase_volume_csv = ""
        self.phase_volume_system = 'FCC'
        self.phase_volume_output = ""
        self.phase_wavelength = 0.4133
        self.phase_n_points = 4

        # EoS variables
        self.bm_input_file = ""
        self.bm_output_dir = ""
        self.bm_order = '3'
        self.eos_model = 'BM-3rd'

    def setup_ui(self, parent_tag):
        """Setup the complete powder XRD UI in the specified parent"""

        with dpg.child_window(parent=parent_tag, border=False):
            # Integration Settings Section
            with dpg.collapsing_header(label="🦊 Integration Settings & Output Options", default_open=True):
                self._create_integration_section()

            # Volume Calculation Section
            with dpg.collapsing_header(label="🐱 Volume Calculation & Lattice Fitting", default_open=True):
                self._create_volume_section()

            # Progress Section
            with dpg.group():
                dpg.add_text("Process Progress:")
                dpg.add_progress_bar(tag="powder_progress_bar", width=-1)

            # Log Section
            with dpg.collapsing_header(label="🐰 Process Log", default_open=True):
                dpg.add_input_text(
                    tag="powder_log_text",
                    multiline=True,
                    readonly=True,
                    height=200,
                    width=-1
                )

    def _create_integration_section(self):
        """Create integration settings UI"""
        with dpg.group():
            # File inputs
            with dpg.group(horizontal=True):
                dpg.add_text("PONI File:")
                dpg.add_input_text(
                    tag="powder_poni_path",
                    default_value=self.poni_path,
                    width=400,
                    callback=lambda s, a: setattr(self, 'poni_path', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file("powder_poni_path", [("PONI files", "*.poni")])
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Mask File:")
                dpg.add_input_text(
                    tag="powder_mask_path",
                    default_value=self.mask_path,
                    width=400,
                    callback=lambda s, a: setattr(self, 'mask_path', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file("powder_mask_path", [("EDF files", "*.edf")])
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Input .h5 File:")
                dpg.add_input_text(
                    tag="powder_input_pattern",
                    default_value=self.input_pattern,
                    width=400,
                    callback=lambda s, a: setattr(self, 'input_pattern', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file("powder_input_pattern", [("HDF5 files", "*.h5")])
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Output Directory:")
                dpg.add_input_text(
                    tag="powder_output_dir",
                    default_value=self.output_dir,
                    width=400,
                    callback=lambda s, a: setattr(self, 'output_dir', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_folder("powder_output_dir")
                )

            # Parameters
            with dpg.group(horizontal=True):
                dpg.add_text("Number of Points:")
                dpg.add_input_int(
                    tag="powder_npt",
                    default_value=self.npt,
                    width=100,
                    callback=lambda s, a: setattr(self, 'npt', a)
                )

                dpg.add_text("Unit:")
                dpg.add_combo(
                    ['2θ (°)', 'Q (Å⁻¹)', 'r (mm)'],
                    tag="powder_unit",
                    default_value=self.unit,
                    width=120,
                    callback=lambda s, a: setattr(self, 'unit', a)
                )

            # Output formats
            dpg.add_text("Select Output Formats:")
            with dpg.group(horizontal=True):
                dpg.add_checkbox(
                    label=".xy",
                    tag="powder_format_xy",
                    default_value=self.format_xy,
                    callback=lambda s, a: setattr(self, 'format_xy', a)
                )
                dpg.add_checkbox(
                    label=".dat",
                    tag="powder_format_dat",
                    default_value=self.format_dat,
                    callback=lambda s, a: setattr(self, 'format_dat', a)
                )
                dpg.add_checkbox(
                    label=".chi",
                    tag="powder_format_chi",
                    default_value=self.format_chi,
                    callback=lambda s, a: setattr(self, 'format_chi', a)
                )
                dpg.add_checkbox(
                    label=".fxye",
                    tag="powder_format_fxye",
                    default_value=self.format_fxye,
                    callback=lambda s, a: setattr(self, 'format_fxye', a)
                )
                dpg.add_checkbox(
                    label=".svg",
                    tag="powder_format_svg",
                    default_value=self.format_svg,
                    callback=lambda s, a: setattr(self, 'format_svg', a)
                )
                dpg.add_checkbox(
                    label=".png",
                    tag="powder_format_png",
                    default_value=self.format_png,
                    callback=lambda s, a: setattr(self, 'format_png', a)
                )

            # Stacked plot options
            with dpg.group(horizontal=True):
                dpg.add_checkbox(
                    label="Create Stacked Plot",
                    tag="powder_create_stacked_plot",
                    default_value=self.create_stacked_plot,
                    callback=lambda s, a: setattr(self, 'create_stacked_plot', a)
                )
                dpg.add_text("Offset:")
                dpg.add_input_text(
                    tag="powder_stacked_plot_offset",
                    default_value=self.stacked_plot_offset,
                    width=100,
                    callback=lambda s, a: setattr(self, 'stacked_plot_offset', a)
                )

            # Action buttons
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="🐿️ Run Integration",
                    callback=self.run_integration,
                    width=200
                )
                dpg.add_button(
                    label="📊 Interactive Fitting",
                    callback=self.open_interactive_fitting,
                    width=200
                )

    def _create_volume_section(self):
        """Create volume calculation UI"""
        with dpg.group():
            # Input CSV
            with dpg.group(horizontal=True):
                dpg.add_text("Input CSV (Volume Calculation):")
                dpg.add_input_text(
                    tag="powder_phase_volume_csv",
                    default_value=self.phase_volume_csv,
                    width=400,
                    callback=lambda s, a: setattr(self, 'phase_volume_csv', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file("powder_phase_volume_csv", [("CSV files", "*.csv")])
                )

            # Output directory
            with dpg.group(horizontal=True):
                dpg.add_text("Output Directory:")
                dpg.add_input_text(
                    tag="powder_phase_volume_output",
                    default_value=self.phase_volume_output,
                    width=400,
                    callback=lambda s, a: setattr(self, 'phase_volume_output', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_folder("powder_phase_volume_output")
                )

            # Crystal system
            dpg.add_text("Crystal System:")
            with dpg.group(horizontal=True):
                dpg.add_radio_button(
                    ['FCC', 'BCC', 'Hexagonal', 'Tetragonal', 'Orthorhombic', 'Monoclinic', 'Triclinic'],
                    tag="powder_phase_volume_system",
                    default_value=self.phase_volume_system,
                    horizontal=True,
                    callback=lambda s, a: setattr(self, 'phase_volume_system', a)
                )

            # Wavelength
            with dpg.group(horizontal=True):
                dpg.add_text("Wavelength (Å):")
                dpg.add_input_double(
                    tag="powder_phase_wavelength",
                    default_value=self.phase_wavelength,
                    width=100,
                    format="%.4f",
                    callback=lambda s, a: setattr(self, 'phase_wavelength', a)
                )

            # Action buttons
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="🐼 Calculate Lattice Parameters",
                    callback=self.run_phase_analysis,
                    width=280
                )
                dpg.add_button(
                    label="🌌 Open Interactive EoS GUI",
                    callback=self.open_interactive_eos_gui,
                    width=240
                )

    def _browse_file(self, tag, file_types):
        """Browse for file using native file dialog"""
        # Dear PyGui doesn't have built-in file dialogs, need to use tkinter or external library
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(filetypes=file_types)
        root.destroy()

        if filename:
            dpg.set_value(tag, filename)
            # Update corresponding attribute
            attr_name = tag.replace("powder_", "")
            setattr(self, attr_name, filename)

    def _browse_folder(self, tag):
        """Browse for folder using native folder dialog"""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        foldername = filedialog.askdirectory()
        root.destroy()

        if foldername:
            dpg.set_value(tag, foldername)
            # Update corresponding attribute
            attr_name = tag.replace("powder_", "")
            setattr(self, attr_name, foldername)

    def log(self, message):
        """Thread-safe log message"""
        if self._is_shutting_down:
            return

        current_text = dpg.get_value("powder_log_text")
        dpg.set_value("powder_log_text", current_text + message + "\n")

    def run_integration(self):
        """Run 1D integration"""
        if not self.poni_path or not self.mask_path or not self.input_pattern or not self.output_dir:
            self._show_error("Error", "Please fill all required fields")
            return

        thread = threading.Thread(target=self._run_integration_thread, daemon=True)
        thread.start()

    def _run_integration_thread(self):
        """Background thread for integration"""
        formats = []
        if self.format_xy: formats.append('xy')
        if self.format_dat: formats.append('dat')
        if self.format_chi: formats.append('chi')
        if self.format_fxye: formats.append('fxye')
        if self.format_svg: formats.append('svg')
        if self.format_png: formats.append('png')
        if not formats: formats = ['xy']

        # Convert unit
        unit_conversion = {
            '2θ (°)': '2th_deg',
            'Q (Å⁻¹)': 'q_A^-1',
            'r (mm)': 'r_mm'
        }
        pyfai_unit = unit_conversion.get(self.unit, self.unit)

        try:
            dpg.set_value("powder_progress_bar", 0.0)

            # Get h5 files
            if os.path.isdir(self.input_pattern):
                target_dir = self.input_pattern
            elif os.path.isfile(self.input_pattern) and self.input_pattern.lower().endswith('.h5'):
                target_dir = os.path.dirname(self.input_pattern)
            else:
                raise ValueError(f"Invalid input: {self.input_pattern}")

            h5_files = sorted([os.path.join(target_dir, f)
                              for f in os.listdir(target_dir)
                              if f.lower().endswith('.h5')])

            if not h5_files:
                raise ValueError(f"No .h5 files found in directory: {target_dir}")

            total_files = len(h5_files)
            self.log(f"\n{'='*60}")
            self.log(f"🔁 Starting Batch Integration")
            self.log(f"📁 Directory: {target_dir}")
            self.log(f"📊 Total files to process: {total_files}")
            self.log(f"{'='*60}\n")

            integrator = BatchIntegrator(self.poni_path, self.mask_path)

            for i, h5_file in enumerate(h5_files, 1):
                self.log(f"[{i}/{total_files}] Processing: {os.path.basename(h5_file)}")

                integrator.batch_integrate(
                    input_pattern=h5_file,
                    output_dir=self.output_dir,
                    npt=self.npt,
                    unit=pyfai_unit,
                    dataset_path=self.dataset_path if self.dataset_path else None,
                    formats=formats,
                    create_stacked_plot=False
                )

                progress = i / total_files
                dpg.set_value("powder_progress_bar", progress)

                self.log(f"[{i}/{total_files}] ✓ Completed\n")

            self.log(f"\n{'='*60}")
            self.log(f"✅ All integrations completed!")
            self.log(f"{'='*60}\n")

            self._show_success("Integration Complete", f"{total_files} file(s) processed successfully")

        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self._show_error("Error", str(e))
        finally:
            dpg.set_value("powder_progress_bar", 1.0)

    def run_phase_analysis(self):
        """Run volume calculation and lattice parameter fitting"""
        if not self.phase_volume_csv or not self.phase_volume_output:
            self._show_error("Error", "Please fill all required fields")
            return

        thread = threading.Thread(target=self._run_phase_analysis_thread, daemon=True)
        thread.start()

    def _run_phase_analysis_thread(self):
        """Background thread for phase analysis"""
        # Implementation similar to integration thread
        # This is a placeholder - implement full logic based on original code
        pass

    def open_interactive_fitting(self):
        """Open interactive peak fitting GUI"""
        # Create new window for interactive fitting
        # This would need to be implemented based on half_auto_fitting.py
        pass

    def open_interactive_eos_gui(self):
        """Open interactive EoS GUI"""
        # Create new window for EoS
        pass

    def _show_error(self, title, message):
        """Show error dialog"""
        # Dear PyGui modal popup
        with dpg.window(label=title, modal=True, show=True, tag="error_modal",
                       no_title_bar=False, popup=True):
            dpg.add_text(message)
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.delete_item("error_modal"))

    def _show_success(self, title, message):
        """Show success dialog"""
        with dpg.window(label=title, modal=True, show=True, tag="success_modal",
                       no_title_bar=False, popup=True):
            dpg.add_text("✅ " + message)
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.delete_item("success_modal"))

    def cleanup(self):
        """Clean up resources"""
        with self._cleanup_lock:
            self._is_shutting_down = True