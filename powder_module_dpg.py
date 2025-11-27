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
        with dpg.child_window(parent=self.parent_tag, border=False):
            # Integration Settings Card
            self._create_integration_card()

            dpg.add_spacer(height=12)

            # Action Buttons
            self._create_action_buttons()

            dpg.add_spacer(height=12)

            # Volume Calculation Card
            self._create_volume_calculation_card()

            dpg.add_spacer(height=12)

            # Progress and Log
            self._create_progress_log()

    def _create_integration_card(self):
        """Create integration settings card"""
        with dpg.child_window(border=False):
            # Outer card frame to mirror previous UI styling
            card_tag = CardFrame(parent=dpg.last_container(),
                                 label="Integration Settings & Output Options").tag

            with dpg.group(parent=card_tag, horizontal=True):
                # Left column - Integration settings
                with dpg.child_window(parent=dpg.last_container(), width=620, border=False):
                    dpg.add_text("Integration Settings", color=ColorScheme.PRIMARY + (255,))
                    dpg.add_spacer(height=6)

                    # PONI File
                    self._create_file_input("PONI File", "poni_path",
                                          [".poni"], "poni_input")

                    # Mask File
                    self._create_file_input("Mask File", "mask_path",
                                          [".edf", ".npy"], "mask_input")

                    # Input File
                    self._create_file_input("Input .h5 File", "input_pattern",
                                          [".h5"], "input_h5")

                    # Output Directory
                    self._create_folder_input("Output Directory", "output_dir",
                                            "output_dir_input")

                    # Dataset Path
                    dpg.add_text("Dataset Path:", color=ColorScheme.TEXT_LIGHT + (255,))
                    dpg.add_input_text(tag="dataset_path_input",
                                     default_value=self.values['dataset_path'],
                                     width=-1)

                    dpg.add_spacer(height=8)

                    # Parameters row
                    with dpg.group(horizontal=True):
                        # Number of Points
                        with dpg.group():
                            dpg.add_text("Number of Points:", color=ColorScheme.TEXT_LIGHT + (255,))
                            dpg.add_input_int(tag="npt_input",
                                            default_value=self.values['npt'],
                                            width=160, min_value=500, max_value=10000,
                                            min_clamped=True, max_clamped=True)

                        dpg.add_spacer(width=30)

                        # Unit selection
                        with dpg.group():
                            dpg.add_text("Unit:", color=ColorScheme.TEXT_LIGHT + (255,))
                            dpg.add_radio_button(
                                ["2θ (°)", "Q (Å⁻¹)", "r (mm)"],
                                tag="unit_radio",
                                default_value="2θ (°)",
                                horizontal=True
                            )

                # Right column - Output Options inside its own card
                output_card = CardFrame(parent=dpg.last_container(),
                                        label="Output Options",
                                        tag="output_options_card")
                with dpg.group(parent=output_card.tag):
                    dpg.add_spacer(height=4)
                    dpg.add_text("Select Output Formats:",
                                 color=ColorScheme.TEXT_LIGHT + (255,))
                    dpg.add_spacer(height=6)

                    # Format checkboxes grouped like the reference UI
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label=".xy", tag="format_xy",
                                         default_value=True)
                        dpg.add_checkbox(label=".dat", tag="format_dat")
                        dpg.add_checkbox(label=".chi", tag="format_chi")
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label=".fxye", tag="format_fxye")
                        dpg.add_checkbox(label=".svg", tag="format_svg")
                        dpg.add_checkbox(label=".png", tag="format_png")

                    dpg.add_spacer(height=10)
                    dpg.add_text("Stacked Plot Options:",
                                 color=ColorScheme.TEXT_LIGHT + (255,))
                    dpg.add_checkbox(label="Create Stacked Plot",
                                     tag="create_stacked_plot")

                    with dpg.group(horizontal=True):
                        dpg.add_text("Offset:", color=ColorScheme.TEXT_LIGHT + (255,))
                        dpg.add_input_text(tag="stacked_offset",
                                         default_value="auto",
                                         width=120)

                    dpg.add_text("(use 'auto' or number)",
                                 color=ColorScheme.TEXT_LIGHT + (255,))

    def _create_action_buttons(self):
        """Create action buttons"""
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=10)
            ModernButton(
                parent=dpg.last_container(),
                text="Run Integration",
                callback=self.run_integration,
                bg_color=ColorScheme.PRIMARY,
                hover_color=ColorScheme.PRIMARY_HOVER,
                width=210,
                height=42
            )
            dpg.add_spacer(width=14)
            ModernButton(
                parent=dpg.last_container(),
                text="Interactive Fitting",
                callback=self.open_interactive_fitting,
                bg_color=ColorScheme.SECONDARY,
                hover_color=ColorScheme.PRIMARY_HOVER,
                width=210,
                height=42
            )

    def _create_volume_calculation_card(self):
        """Create volume calculation card"""
        with dpg.child_window(border=False):
            card_tag = CardFrame(parent=dpg.last_container(),
                                 label="Volume Calculation & Lattice Fitting").tag

            with dpg.group(parent=card_tag, horizontal=True):
                # Left - Input fields
                with dpg.child_window(parent=dpg.last_container(), width=600, border=False):
                    # Input CSV
                    self._create_file_input("Input CSV (Volume Calculation)",
                                          "phase_volume_csv", [".csv"],
                                          "volume_csv_input")

                    # Output Directory
                    self._create_folder_input("Output Directory",
                                            "phase_volume_output",
                                            "volume_output_input")

                # Right - Crystal system and wavelength
                system_card = CardFrame(parent=dpg.last_container(), label="Crystal System")
                with dpg.group(parent=system_card.tag):
                    dpg.add_radio_button(
                        ["FCC", "BCC", "Hexagonal", "Tetragonal"],
                        tag="crystal_system",
                        default_value="FCC"
                    )

                    dpg.add_spacer(height=8)

                    with dpg.group(horizontal=True):
                        dpg.add_text("Wavelength:", color=ColorScheme.TEXT_LIGHT + (255,))
                        dpg.add_input_float(tag="wavelength_input",
                                          default_value=0.4133,
                                          width=110, format="%.4f")
                        dpg.add_text("Å", color=ColorScheme.TEXT_LIGHT + (255,))

            dpg.add_spacer(height=8)

            # Action buttons
            with dpg.group(parent=card_tag, horizontal=True):
                dpg.add_spacer(width=10)
                ModernButton(
                    parent=dpg.last_container(),
                    text="Calculate Lattice Parameters",
                    callback=self.run_phase_analysis,
                    bg_color=ColorScheme.PRIMARY,
                    hover_color=ColorScheme.PRIMARY_HOVER,
                    width=280,
                    height=42
                )
                dpg.add_spacer(width=14)
                ModernButton(
                    parent=dpg.last_container(),
                    text="Open Interactive EoS GUI",
                    callback=self.open_interactive_eos_gui,
                    bg_color=ColorScheme.SECONDARY,
                    hover_color=ColorScheme.PRIMARY_HOVER,
                    width=260,
                    height=42
                )

    def _create_progress_log(self):
        """Create progress indicator and log area"""
        with dpg.child_window(border=True, height=250, menubar=False):
            dpg.add_text("Process Log", color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()

            # Progress bar
            dpg.add_progress_bar(tag="progress_bar", width=-1, height=30)

            dpg.add_spacer(height=10)

            # Log text area
            self.log_widget = ScrolledText(
                parent=dpg.last_container(),
                height=150,
                readonly=True,
                tag="log_text"
            )

    def _create_file_input(self, label: str, value_key: str,
                          file_types: list, tag: str):
        """Create file input with browse button"""
        dpg.add_text(label + ":", color=ColorScheme.TEXT_LIGHT + (255,))
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag=tag, width=-120,
                             default_value=self.values[value_key])
            ModernButton(
                parent=dpg.last_container(),
                text="Browse",
                callback=lambda: self._browse_file(tag, file_types),
                bg_color=ColorScheme.SECONDARY,
                hover_color=ColorScheme.PRIMARY_HOVER,
                width=90,
                height=32
            )
        dpg.add_spacer(height=5)

    def _create_folder_input(self, label: str, value_key: str, tag: str):
        """Create folder input with browse button"""
        dpg.add_text(label + ":", color=ColorScheme.TEXT_LIGHT + (255,))
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag=tag, width=-120,
                             default_value=self.values[value_key])
            ModernButton(
                parent=dpg.last_container(),
                text="Browse",
                callback=lambda: self._browse_folder(tag),
                bg_color=ColorScheme.SECONDARY,
                hover_color=ColorScheme.PRIMARY_HOVER,
                width=90,
                height=32
            )
        dpg.add_spacer(height=5)

    def _browse_file(self, input_tag: str, file_types: list):
        """Browse for file"""
        def callback(file_path):
            dpg.set_value(input_tag, file_path)

        FilePicker.open_file(callback, ",".join(file_types))

    def _browse_folder(self, input_tag: str):
        """Browse for folder"""
        def callback(folder_path):
            dpg.set_value(input_tag, folder_path)

        FilePicker.open_folder(callback)

    def log(self, message: str):
        """Add log message"""
        try:
            self.log_widget.insert(message + "\n")
        except:
            print(message)

    def update_progress(self, value: float):
        """Update progress bar (0.0 to 1.0)"""
        try:
            dpg.set_value("progress_bar", value)
        except:
            pass

    def run_integration(self):
        """Run 1D integration"""
        # Get values from UI
        poni_path = dpg.get_value("poni_input")
        mask_path = dpg.get_value("mask_input")
        input_pattern = dpg.get_value("input_h5")
        output_dir = dpg.get_value("output_dir_input")

        if not all([poni_path, input_pattern, output_dir]):
            MessageDialog.show_error("Error",
                "Please fill all required fields:\n- PONI File\n- Input File\n- Output Directory")
            return

        # Start integration in background thread
        thread = threading.Thread(target=self._run_integration_thread, daemon=True)
        thread.start()

    def _run_integration_thread(self):
        """Background thread for integration"""
        try:
            self.log("Starting Batch Integration")
            self.update_progress(0.1)

            # Get parameters
            poni_path = dpg.get_value("poni_input")
            mask_path = dpg.get_value("mask_input") or None
            input_pattern = dpg.get_value("input_h5")
            output_dir = dpg.get_value("output_dir_input")
            npt = dpg.get_value("npt_input")

            # Get unit
            unit_text = dpg.get_value("unit_radio")
            unit_map = {
                '2θ (°)': '2th_deg',
                'Q (Å⁻¹)': 'q_A^-1',
                'r (mm)': 'r_mm'
            }
            unit = unit_map.get(unit_text, '2th_deg')

            # Get formats
            formats = []
            if dpg.get_value("format_xy"): formats.append('xy')
            if dpg.get_value("format_dat"): formats.append('dat')
            if dpg.get_value("format_chi"): formats.append('chi')
            if dpg.get_value("format_fxye"): formats.append('fxye')
            if dpg.get_value("format_svg"): formats.append('svg')
            if dpg.get_value("format_png"): formats.append('png')
            if not formats:
                formats = ['xy']

            self.log(f"Input: {os.path.basename(input_pattern)}")
            self.log(f"Parameters: {npt} points, unit={unit}")
            self.log(f"Formats: {', '.join(formats)}")

            self.update_progress(0.3)

            # Create integrator
            integrator = BatchIntegrator(poni_path, mask_path)

            self.update_progress(0.5)

            # Run integration
            integrator.batch_integrate(
                input_pattern=input_pattern,
                output_dir=output_dir,
                npt=npt,
                unit=unit,
                dataset_path=dpg.get_value("dataset_path_input"),
                formats=formats,
                create_stacked_plot=dpg.get_value("create_stacked_plot"),
                stacked_plot_offset=dpg.get_value("stacked_offset")
            )

            self.update_progress(1.0)
            self.log("[OK] Integration completed successfully!")

            MessageDialog.show_success(
                "Success",
                "Integration completed successfully!",
                f"Output saved to: {output_dir}"
            )

        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
            MessageDialog.show_error("Error", f"Integration failed:\n{str(e)}")
        finally:
            self.update_progress(0.0)

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
        csv_path = dpg.get_value("volume_csv_input")
        output_dir = dpg.get_value("volume_output_input")

        if not csv_path or not output_dir:
            MessageDialog.show_error("Error",
                "Please specify:\n- Input CSV file\n- Output directory")
            return

        thread = threading.Thread(target=self._run_phase_analysis_thread, daemon=True)
        thread.start()

    def _run_phase_analysis_thread(self):
        """Background thread for phase analysis"""
        try:
            self.log("Starting Volume Calculation & Lattice Fitting")
            self.update_progress(0.1)

            csv_path = dpg.get_value("volume_csv_input")
            output_dir = dpg.get_value("volume_output_input")
            crystal_system = dpg.get_value("crystal_system")
            wavelength = dpg.get_value("wavelength_input")

            os.makedirs(output_dir, exist_ok=True)

            self.log(f"📄 Input CSV: {os.path.basename(csv_path)}")
            self.log(f"🔷 Crystal system: {crystal_system}")
            self.log(f"📏 Wavelength: {wavelength} Å")

            self.update_progress(0.3)

            # Map crystal system
            system_map = {
                'FCC': 'cubic_FCC',
                'BCC': 'cubic_BCC',
                'Hexagonal': 'Hexagonal',
                'Tetragonal': 'Tetragonal'
            }
            system = system_map.get(crystal_system, 'cubic_FCC')

            analyzer = XRDAnalyzer(wavelength=wavelength, n_pressure_points=4)

            self.update_progress(0.5)

            results = analyzer.analyze(
                csv_path=csv_path,
                original_system=system,
                new_system=system,
                auto_mode=True
            )

            self.update_progress(0.9)

            if results:
                self.log("[OK] Volume calculation completed!")
                if 'transition_pressure' in results:
                    self.log(f"Transition pressure: {results['transition_pressure']:.2f} GPa")

                self.update_progress(1.0)

                MessageDialog.show_success(
                    "Success",
                    "Volume calculation completed!",
                    f"Results saved to: {output_dir}"
                )
            else:
                raise Exception("Analysis returned no results")

        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
            MessageDialog.show_error("Error",
                f"Volume calculation failed:\n{str(e)}")
        finally:
            self.update_progress(0.0)

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