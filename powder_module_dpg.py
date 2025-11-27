# -*- coding: utf-8 -*-
"""
Powder XRD Module - DPG Version
Contains integration, peak fitting, phase analysis, and Birch-Murnaghan fitting

This is the DPG (Dear PyGui) version of powder_module.py
"""

import dearpygui.dearpygui as dpg
import threading
import os
import numpy as np
import pandas as pd

from dpg_components import (
    ColorScheme, ModernButton, CardFrame, FilePicker,
    MessageDialog, ScrolledText, CustomSpinbox, SpinboxStyleButton
)
from gui_base_dpg import GUIBase
from batch_integration import BatchIntegrator

# Optional import - interactive fitting GUI (DPG version)
try:
    from half_auto_fitting_dpg import PeakFittingGUI, DataProcessor
    INTERACTIVE_FITTING_AVAILABLE = True
except ImportError:
    INTERACTIVE_FITTING_AVAILABLE = False
    print("Warning: Interactive fitting GUI not available")

from batch_cal_volume import XRayDiffractionAnalyzer as XRDAnalyzer


class PowderXRDModule(GUIBase):
    """Powder XRD processing module - DPG Version"""

    def __init__(self, parent_tag: str):
        """
        Initialize Powder XRD module

        Args:
            parent_tag: Parent container tag
        """
        super().__init__()
        self.parent_tag = parent_tag
        self.current_module = "integration"

        # Storage for input values
        self.values = {
            'poni_path': '',
            'mask_path': '',
            'input_pattern': '',
            'output_dir': '',
            'dataset_path': 'entry/data/data',
            'npt': 4000,
            'unit': '2th_deg',
            'fit_method': 'pseudo',

            # Output formats
            'format_xy': True,
            'format_dat': False,
            'format_chi': False,
            'format_fxye': False,
            'format_svg': False,
            'format_png': False,

            # Stacked plot
            'create_stacked_plot': False,
            'stacked_plot_offset': 'auto',

            # Phase analysis
            'phase_volume_csv': '',
            'phase_volume_output': '',
            'phase_volume_system': 'FCC',
            'phase_wavelength': 0.4133,
            'phase_n_points': 4,
        }

        # Thread tracking
        self.running_threads = []
        self.is_shutting_down = False

    def setup_ui(self):
        """Setup the complete powder XRD UI"""
        with dpg.child_window(parent=self.parent_tag, border=False, height=-1, width=-1):
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
                dpg.add_text("PONI File:", width=150)
                dpg.add_input_text(
                    tag="powder_poni_path",
                    default_value=self.values['poni_path'],
                    width=400,
                    callback=lambda s, a: self.values.update({'poni_path': a})
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file("powder_poni_path", [("PONI files", "*.poni")])
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Mask File:", width=150)
                dpg.add_input_text(
                    tag="powder_mask_path",
                    default_value=self.values['mask_path'],
                    width=400,
                    callback=lambda s, a: self.values.update({'mask_path': a})
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file("powder_mask_path", [("EDF files", "*.edf")])
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Input .h5 File:", width=150)
                dpg.add_input_text(
                    tag="powder_input_pattern",
                    default_value=self.values['input_pattern'],
                    width=400,
                    callback=lambda s, a: self.values.update({'input_pattern': a})
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file("powder_input_pattern", [("HDF5 files", "*.h5")])
                )

            with dpg.group(horizontal=True):
                dpg.add_text("Output Directory:", width=150)
                dpg.add_input_text(
                    tag="powder_output_dir",
                    default_value=self.values['output_dir'],
                    width=400,
                    callback=lambda s, a: self.values.update({'output_dir': a})
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_folder("powder_output_dir")
                )

            dpg.add_spacer(height=10)

            # Parameters
            with dpg.group(horizontal=True):
                dpg.add_text("Number of Points:", width=150)
                dpg.add_input_int(
                    tag="powder_npt",
                    default_value=self.values['npt'],
                    width=100,
                    callback=lambda s, a: self.values.update({'npt': a})
                )

                dpg.add_spacer(width=20)
                dpg.add_text("Unit:")
                dpg.add_combo(
                    ['2θ (°)', 'Q (Å⁻¹)', 'r (mm)'],
                    tag="powder_unit",
                    default_value='2θ (°)',
                    width=120,
                    callback=lambda s, a: self.values.update({'unit': a})
                )

            dpg.add_spacer(height=10)

            # Output formats
            dpg.add_text("Select Output Formats:")
            with dpg.group(horizontal=True):
                dpg.add_checkbox(
                    label=".xy",
                    tag="powder_format_xy",
                    default_value=self.values['format_xy'],
                    callback=lambda s, a: self.values.update({'format_xy': a})
                )
                dpg.add_checkbox(
                    label=".dat",
                    tag="powder_format_dat",
                    default_value=self.values['format_dat'],
                    callback=lambda s, a: self.values.update({'format_dat': a})
                )
                dpg.add_checkbox(
                    label=".chi",
                    tag="powder_format_chi",
                    default_value=self.values['format_chi'],
                    callback=lambda s, a: self.values.update({'format_chi': a})
                )
                dpg.add_checkbox(
                    label=".fxye",
                    tag="powder_format_fxye",
                    default_value=self.values['format_fxye'],
                    callback=lambda s, a: self.values.update({'format_fxye': a})
                )
                dpg.add_checkbox(
                    label=".svg",
                    tag="powder_format_svg",
                    default_value=self.values['format_svg'],
                    callback=lambda s, a: self.values.update({'format_svg': a})
                )
                dpg.add_checkbox(
                    label=".png",
                    tag="powder_format_png",
                    default_value=self.values['format_png'],
                    callback=lambda s, a: self.values.update({'format_png': a})
                )

            dpg.add_spacer(height=10)

            # Stacked plot options
            with dpg.group(horizontal=True):
                dpg.add_checkbox(
                    label="Create Stacked Plot",
                    tag="powder_create_stacked_plot",
                    default_value=self.values['create_stacked_plot'],
                    callback=lambda s, a: self.values.update({'create_stacked_plot': a})
                )
                dpg.add_text("Offset:")
                dpg.add_input_text(
                    tag="powder_stacked_plot_offset",
                    default_value=self.values['stacked_plot_offset'],
                    width=100,
                    callback=lambda s, a: self.values.update({'stacked_plot_offset': a})
                )

            dpg.add_spacer(height=10)

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
                dpg.add_text("Input CSV (Volume Calculation):", width=250)
                dpg.add_input_text(
                    tag="powder_phase_volume_csv",
                    default_value=self.values['phase_volume_csv'],
                    width=400,
                    callback=lambda s, a: self.values.update({'phase_volume_csv': a})
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file("powder_phase_volume_csv", [("CSV files", "*.csv")])
                )

            # Output directory
            with dpg.group(horizontal=True):
                dpg.add_text("Output Directory:", width=250)
                dpg.add_input_text(
                    tag="powder_phase_volume_output",
                    default_value=self.values['phase_volume_output'],
                    width=400,
                    callback=lambda s, a: self.values.update({'phase_volume_output': a})
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_folder("powder_phase_volume_output")
                )

            dpg.add_spacer(height=10)

            # Crystal system
            dpg.add_text("Crystal System:")
            with dpg.group(horizontal=True):
                dpg.add_radio_button(
                    ['FCC', 'BCC', 'Hexagonal', 'Tetragonal', 'Orthorhombic', 'Monoclinic', 'Triclinic'],
                    tag="powder_phase_volume_system",
                    default_value=self.values['phase_volume_system'],
                    horizontal=True,
                    callback=lambda s, a: self.values.update({'phase_volume_system': a})
                )

            dpg.add_spacer(height=10)

            # Wavelength
            with dpg.group(horizontal=True):
                dpg.add_text("Wavelength (Å):", width=150)
                dpg.add_input_double(
                    tag="powder_phase_wavelength",
                    default_value=self.values['phase_wavelength'],
                    width=100,
                    format="%.4f",
                    callback=lambda s, a: self.values.update({'phase_wavelength': a})
                )

            dpg.add_spacer(height=10)

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
            if attr_name in self.values:
                self.values[attr_name] = filename

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
            if attr_name in self.values:
                self.values[attr_name] = foldername

    def log(self, message):
        """Thread-safe log message"""
        if self.is_shutting_down:
            return

        current_text = dpg.get_value("powder_log_text")
        dpg.set_value("powder_log_text", current_text + message + "\n")

    def run_integration(self):
        """Run 1D integration"""
        poni_path = dpg.get_value("powder_poni_path")
        input_pattern = dpg.get_value("powder_input_pattern")
        output_dir = dpg.get_value("powder_output_dir")
        
        if not poni_path or not input_pattern or not output_dir:
            self._show_error("Error", "Please fill all required fields")
            return

        thread = threading.Thread(target=self._run_integration_thread, daemon=True)
        thread.start()

    def _run_integration_thread(self):
        """Background thread for integration"""
        # Get formats
        formats = []
        if dpg.get_value("powder_format_xy"): formats.append('xy')
        if dpg.get_value("powder_format_dat"): formats.append('dat')
        if dpg.get_value("powder_format_chi"): formats.append('chi')
        if dpg.get_value("powder_format_fxye"): formats.append('fxye')
        if dpg.get_value("powder_format_svg"): formats.append('svg')
        if dpg.get_value("powder_format_png"): formats.append('png')
        if not formats: formats = ['xy']

        # Convert unit
        unit_text = dpg.get_value("powder_unit")
        unit_conversion = {
            '2θ (°)': '2th_deg',
            'Q (Å⁻¹)': 'q_A^-1',
            'r (mm)': 'r_mm'
        }
        pyfai_unit = unit_conversion.get(unit_text, '2th_deg')

        try:
            dpg.set_value("powder_progress_bar", 0.0)

            poni_path = dpg.get_value("powder_poni_path")
            mask_path = dpg.get_value("powder_mask_path")
            input_pattern = dpg.get_value("powder_input_pattern")
            output_dir = dpg.get_value("powder_output_dir")
            npt = dpg.get_value("powder_npt")

            # Get h5 files
            if os.path.isdir(input_pattern):
                target_dir = input_pattern
            elif os.path.isfile(input_pattern) and input_pattern.lower().endswith('.h5'):
                target_dir = os.path.dirname(input_pattern)
            else:
                raise ValueError(f"Invalid input: {input_pattern}")

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

            integrator = BatchIntegrator(poni_path, mask_path)

            for i, h5_file in enumerate(h5_files, 1):
                self.log(f"[{i}/{total_files}] Processing: {os.path.basename(h5_file)}")

                integrator.batch_integrate(
                    input_pattern=h5_file,
                    output_dir=output_dir,
                    npt=npt,
                    unit=pyfai_unit,
                    dataset_path=self.values['dataset_path'] if self.values['dataset_path'] else None,
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

    def open_interactive_fitting(self):
        """Open interactive fitting window"""
        if not INTERACTIVE_FITTING_AVAILABLE:
            MessageDialog.show_error(
                "Not Available",
                "Interactive fitting GUI is not available.\n"
                "Please check that half_auto_fitting_dpg.py is present."
            )
            return

        try:
            # Check if window already exists
            if dpg.does_item_exist("peak_fitting_window"):
                # Window exists, just show and focus it
                dpg.show_item("peak_fitting_window")
                dpg.focus_item("peak_fitting_window")
                return
            
            # Create peak fitting window
            from half_auto_fitting_dpg import create_peak_fitting_window
            gui = create_peak_fitting_window()
            
            # Ensure window is visible
            if dpg.does_item_exist("peak_fitting_window"):
                dpg.show_item("peak_fitting_window")

        except Exception as e:
            import traceback
            error_msg = f"Failed to open interactive fitting window:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}"
            MessageDialog.show_error("Error", error_msg)
            print(f"Error opening interactive fitting: {error_msg}")

    def run_phase_analysis(self):
        """Run volume calculation and lattice parameter fitting"""
        csv_path = dpg.get_value("powder_phase_volume_csv")
        output_dir = dpg.get_value("powder_phase_volume_output")
        
        if not csv_path or not output_dir:
            self._show_error("Error", "Please fill all required fields")
            return

        thread = threading.Thread(target=self._run_phase_analysis_thread, daemon=True)
        thread.start()

    def _run_phase_analysis_thread(self):
        """Background thread for phase analysis"""
        # Implementation similar to integration thread
        # This is a placeholder - implement full logic based on original code
        pass

    def open_interactive_eos_gui(self):
        """Open interactive EoS GUI"""
        try:
            # Check if window already exists
            if dpg.does_item_exist("eos_window"):
                # Window exists, just show and focus it
                dpg.show_item("eos_window")
                dpg.focus_item("eos_window")
                return
            
            # Create EoS fitting window
            from interactive_eos_gui_dpg import create_eos_window
            gui = create_eos_window()
            
            # Ensure window is visible
            if dpg.does_item_exist("eos_window"):
                dpg.show_item("eos_window")

        except Exception as e:
            import traceback
            error_msg = f"Failed to open EoS fitting window:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}"
            MessageDialog.show_error("Error", error_msg)
            print(f"Error opening EoS GUI: {error_msg}")

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
        with threading.Lock():
            self.is_shutting_down = True