# -*- coding: utf-8 -*-
"""
Powder XRD Module - DPG Version
Contains integration, peak fitting, phase analysis, and Birch-Murnaghan fitting

This is the DPG (Dear PyGui) version of powder_module.py
"""

import dearpygui.dearpygui as dpg
import threading
import os
from dpg_components import FilePicker, MessageDialog
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
            'unit': '2θ (°)',
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
        self._create_theme()

        with dpg.child_window(parent=self.parent_tag, border=False, width=-1) as module_root:
            dpg.bind_item_theme(module_root, "powder_square_theme")
            with dpg.collapsing_header(label="🦊 Integration Settings & Output Options", default_open=True):
                self._create_integration_section()

            with dpg.collapsing_header(label="🐱 Volume Calculation & Lattice Fitting", default_open=True):
                self._create_volume_section()

            with dpg.group():
                dpg.add_text("Process Progress:")
                dpg.add_progress_bar(tag="powder_progress_bar", width=-1)

            with dpg.collapsing_header(label="Process Log", default_open=True):
                with dpg.child_window(width=-1, height=220, border=True):
                    dpg.add_input_text(
                        tag="powder_log_text",
                        multiline=True,
                        readonly=True,
                        height=-1,
                        width=-1
                    )

    def _create_theme(self):
        """Create a square-corner theme for inputs and panels"""
        if dpg.does_item_exist("powder_square_theme"):
            return

        with dpg.theme(tag="powder_square_theme"):
            for component in (dpg.mvInputText, dpg.mvInputInt, dpg.mvInputFloat, dpg.mvButton, dpg.mvRadioButton, dpg.mvCheckbox):
                with dpg.theme_component(component):
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)
                    dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (248, 242, 252), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10, category=dpg.mvThemeCat_Core)

    def _create_integration_section(self):
        """Create integration settings and output options"""
        with dpg.group():
            with dpg.group(horizontal=True, horizontal_spacing=18):
                with dpg.child_window(width=780, height=230, border=True):
                    with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp,
                                   borders_innerV=False, borders_innerH=True):
                        dpg.add_table_column(init_width_or_weight=0.2)
                        dpg.add_table_column(init_width_or_weight=0.65)
                        dpg.add_table_column(init_width_or_weight=0.15)

                        self._add_labeled_file_row("PONI File:", "powder_poni_path",
                                                   self.values['poni_path'], [".poni"])
                        self._add_labeled_file_row("Mask File:", "powder_mask_path",
                                                   self.values['mask_path'], [".edf", ".npy"])
                        self._add_labeled_file_row("Import .h5 File:", "powder_input_pattern",
                                                   self.values['input_pattern'], [".h5"])
                        self._add_labeled_folder_row("Output Directory:", "powder_output_dir",
                                                     self.values['output_dir'])

                        with dpg.table_row():
                            dpg.add_text("Dataset Path:")
                            dpg.add_input_text(
                                tag="dataset_path_input",
                                default_value=self.values['dataset_path'],
                                width=-1
                            )
                            dpg.add_spacer(width=1)

                    dpg.add_spacer(height=8)

                    with dpg.group(horizontal=True, horizontal_spacing=22):
                        with dpg.group(horizontal=True):
                            dpg.add_text("Number of Points:")
                            dpg.add_input_int(
                                tag="npt_input",
                                default_value=self.values['npt'],
                                width=110
                            )

                        with dpg.group(horizontal=True):
                            dpg.add_text("Unit:")
                            dpg.add_radio_button(
                                items=['2θ (°)', 'Q (Å⁻¹)', 'r (mm)'],
                                tag="unit_combo",
                                default_value=self.values['unit'],
                                horizontal=True
                            )

                with dpg.child_window(width=280, height=230, border=True) as output_panel:
                    dpg.add_text("Output Options")
                    dpg.add_separator()
                    dpg.add_text("Select Output Formats:")
                    with dpg.table(header_row=False, borders_innerH=False, borders_innerV=False,
                                   policy=dpg.mvTable_SizingStretchProp):
                        dpg.add_table_column(init_width_or_weight=0.5)
                        dpg.add_table_column(init_width_or_weight=0.5)
                        with dpg.table_row():
                            dpg.add_checkbox(label=".xy", tag="format_xy", default_value=self.values['format_xy'])
                            dpg.add_checkbox(label=".dat", tag="format_dat", default_value=self.values['format_dat'])
                        with dpg.table_row():
                            dpg.add_checkbox(label=".chi", tag="format_chi", default_value=self.values['format_chi'])
                            dpg.add_checkbox(label=".fxye", tag="format_fxye", default_value=self.values['format_fxye'])
                        with dpg.table_row():
                            dpg.add_checkbox(label=".svg", tag="format_svg", default_value=self.values['format_svg'])
                            dpg.add_checkbox(label=".png", tag="format_png", default_value=self.values['format_png'])

                    dpg.add_spacer(height=6)
                    dpg.add_text("Stacked Plot Options:")
                    dpg.add_checkbox(
                        label="Create Stacked Plot?",
                        tag="create_stacked_plot",
                        default_value=self.values['create_stacked_plot']
                    )
                    with dpg.group(horizontal=True):
                        dpg.add_text("Offset:")
                        dpg.add_input_text(
                            tag="stacked_offset",
                            default_value=self.values['stacked_plot_offset'],
                            width=90
                        )
                    dpg.bind_item_theme(output_panel, "powder_square_theme")

            dpg.add_spacer(height=12)

            with dpg.group(horizontal=True, horizontal_spacing=18):
                dpg.add_spacer(width=10)
                dpg.add_button(
                    label="🦊  Run Integration",
                    callback=self.run_integration,
                    width=230
                )
                dpg.add_button(
                    label="🐱  Interactive Fitting",
                    callback=self.open_interactive_fitting,
                    width=230
                )

    def _create_volume_section(self):
        """Create volume calculation and lattice fitting UI"""
        with dpg.group():
            with dpg.group(horizontal=True, horizontal_spacing=18):
                with dpg.child_window(width=780, height=170, border=True):
                    with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp,
                                   borders_innerH=True, borders_innerV=False):
                        dpg.add_table_column(init_width_or_weight=0.2)
                        dpg.add_table_column(init_width_or_weight=0.65)
                        dpg.add_table_column(init_width_or_weight=0.15)

                        self._add_labeled_file_row(
                            "Input CSV (Volume Calculation):",
                            "volume_csv_input",
                            self.values['phase_volume_csv'],
                            [".csv"]
                        )
                        self._add_labeled_folder_row(
                            "Output Directory:",
                            "volume_output_input",
                            self.values['phase_volume_output']
                        )

                with dpg.child_window(width=330, height=170, border=True) as volume_panel:
                    dpg.add_text("Crystal System:")
                    dpg.add_radio_button(
                        ['FCC', 'BCC', 'Hexagonal', 'Tetragonal', 'Orthorhombic', 'Monoclinic', 'Triclinic'],
                        tag="crystal_system",
                        default_value=self.values['phase_volume_system'],
                        horizontal=True
                    )

                    dpg.add_spacer(height=10)
                    with dpg.group(horizontal=True):
                        dpg.add_text("Wavelength:")
                        dpg.add_input_float(
                            tag="wavelength_input",
                            default_value=self.values['phase_wavelength'],
                            width=100,
                            format="%.4f"
                        )
                        dpg.add_text("Å")

                    dpg.bind_item_theme(volume_panel, "powder_square_theme")

            dpg.add_spacer(height=10)

            with dpg.group(horizontal=True, horizontal_spacing=18):
                dpg.add_spacer(width=10)
                dpg.add_button(
                    label="🐹  Calculate Lattice Parameters",
                    callback=self.run_phase_analysis,
                    width=270
                )
                dpg.add_button(
                    label="🦄  Open Interactive EoS GUI",
                    callback=self.open_interactive_eos_gui,
                    width=260
                )

    def _add_labeled_file_row(self, label: str, tag: str, default_value: str, file_types: list):
        """Add a table row with a label, text field, and browse button for files"""
        with dpg.table_row():
            dpg.add_text(label)
            dpg.add_input_text(tag=tag, default_value=default_value, width=-1)
            dpg.add_button(label="Browse", width=80, callback=lambda: self._browse_file(tag, file_types))

    def _add_labeled_folder_row(self, label: str, tag: str, default_value: str):
        """Add a table row with a label, text field, and browse button for folders"""
        with dpg.table_row():
            dpg.add_text(label)
            dpg.add_input_text(tag=tag, default_value=default_value, width=-1)
            dpg.add_button(label="Browse", width=80, callback=lambda: self._browse_folder(tag))

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
            current_text = dpg.get_value("powder_log_text")
            dpg.set_value("powder_log_text", current_text + message + "\n")
        except Exception:
            print(message)

    def update_progress(self, value: float):
        """Update progress bar (0.0 to 1.0)"""
        try:
            dpg.set_value("powder_progress_bar", value)
        except:
            pass

    def run_integration(self):
        """Run 1D integration"""
        # Get values from UI
        poni_path = dpg.get_value("powder_poni_path")
        mask_path = dpg.get_value("powder_mask_path")
        input_pattern = dpg.get_value("powder_input_pattern")
        output_dir = dpg.get_value("powder_output_dir")

        if not all([poni_path, mask_path, input_pattern, output_dir]):
            MessageDialog.show_error(
                "Error",
                "Please fill all required fields:\n- PONI File\n- Mask File\n- Input File\n- Output Directory"
            )
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
            poni_path = dpg.get_value("powder_poni_path")
            mask_path = dpg.get_value("powder_mask_path") or None
            input_pattern = dpg.get_value("powder_input_pattern")
            output_dir = dpg.get_value("powder_output_dir")
            npt = dpg.get_value("npt_input")

            # Get unit
            unit_text = dpg.get_value("unit_combo")
            unit_map = {
                '2θ (°)': '2th_deg',
                'Q (Å⁻¹)': 'q_A^-1',
                'r (mm)': 'r_mm'
            }
            unit = unit_map.get(unit_text, '2th_deg')

            # Get formats
            formats = []
            if dpg.get_value("format_dat"): formats.append('dat')
            if dpg.get_value("format_xy"): formats.append('xy')
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

            self.log(f"Input CSV: {os.path.basename(csv_path)}")
            self.log(f"Crystal system: {crystal_system}")
            self.log(f"Wavelength: {wavelength} Å")

            self.update_progress(0.3)

            # Map crystal system
            system_map = {
                'FCC': 'cubic_FCC',
                'BCC': 'cubic_BCC',
                'Hexagonal': 'Hexagonal',
                'Tetragonal': 'Tetragonal',
                'Orthorhombic': 'Orthorhombic',
                'Monoclinic': 'Monoclinic',
                'Triclinic': 'Triclinic'
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
