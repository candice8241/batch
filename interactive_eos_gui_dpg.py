#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interactive EoS Fitting GUI with Real-time Parameter Adjustment - DPG Version

Similar to EosFit7-GUI, allows manual parameter adjustment with live preview.
Converted from Tkinter to Dear PyGui.

@author: candicewang928@gmail.com
Created: 2025-11-24
Converted to DPG: 2025-11-27
"""

import numpy as np
import pandas as pd
import dearpygui.dearpygui as dpg
from crysfml_eos_module import CrysFMLEoS, EoSType, EoSParameters
from dpg_components import ColorScheme, ModernButton, MessageDialog


class InteractiveEoSGUI:
    """
    Interactive GUI for EoS fitting with real-time parameter adjustment - DPG Version

    Features:
    - Manual parameter input (V0, B0, B0')
    - Parameter lock/unlock (fix or fit)
    - Real-time curve update
    - Automatic fitting
    - Quality metrics display
    - Data loading from CSV
    """

    def __init__(self, parent_tag: str = None):
        """Initialize the GUI"""
        # Data storage
        self.V_data = None
        self.P_data = None
        self.current_params = None
        self.fitted_params = None

        # EoS fitter
        self.eos_type = EoSType.BIRCH_MURNAGHAN_3RD
        self.fitter = None
        self.last_initial_params = None

        # Results window state
        self.last_results_output = ""

        # Tags for UI elements
        self.parent_tag = parent_tag
        self.window_tag = "eos_window"
        self.plot_tag = "eos_plot"
        self.data_info_tag = "eos_data_info"
        self.results_text_tag = "eos_results_text"

        # Parameter variables
        self.param_values = {
            'V0': 11.5,
            'B0': 130.0,
            'B0_prime': 4.0
        }
        self.param_locks = {
            'V0': False,
            'B0': False,
            'B0_prime': False
        }

        # Tags for input fields
        self.param_input_tags = {}
        self.param_lock_tags = {}

        # Current EoS model
        self.current_eos_model = "Birch-Murnaghan 3rd"

    def create_window(self):
        """Create the main EoS fitting window"""
        # Check if window already exists and delete it
        if dpg.does_item_exist(self.window_tag):
            dpg.delete_item(self.window_tag)
        
        with dpg.window(
            label="Interactive EoS Fitting - CrysFML Method",
            tag=self.window_tag,
            width=1480,
            height=900,
            pos=[50, 50],
            on_close=self.on_window_close,
            show=True
        ):
            # Horizontal layout: left panel (controls) + right panel (plot + results)
            with dpg.group(horizontal=True):
                # Left panel - Controls (width ~400px)
                with dpg.child_window(width=400, tag="eos_left_panel", border=True, menubar=False):
                    self.setup_data_section()
                    self.setup_eos_selection()
                    self.setup_parameters_section()
                    self.setup_fitting_section()

                # Right panel - Plot and Results
                with dpg.child_window(tag="eos_right_panel", border=False, menubar=False):
                    self.setup_plot()
                    dpg.add_separator()
                    self.setup_results_section()
    
    def on_window_close(self):
        """Handle window close event"""
        try:
            if dpg.does_item_exist(self.window_tag):
                dpg.delete_item(self.window_tag)
        except Exception as e:
            print(f"Error closing window: {e}")

    def setup_data_section(self):
        """Setup data loading section"""
        dpg.add_text("Data", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.group():
            dpg.add_button(
                label="Load CSV File",
                callback=self.load_csv_dialog,
                width=-1,
                height=40
            )

            dpg.add_spacer(height=8)
            dpg.add_text("No data loaded", tag=self.data_info_tag,
                        color=ColorScheme.TEXT_LIGHT, wrap=380)

        dpg.add_spacer(height=15)

    def setup_eos_selection(self):
        """Setup EoS model selection"""
        dpg.add_text("EoS Model", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.group():
            dpg.add_text("Model:", color=ColorScheme.TEXT_DARK)

            eos_options = [
                "Birch-Murnaghan 2nd",
                "Birch-Murnaghan 3rd",
                "Birch-Murnaghan 4th",
                "Murnaghan",
                "Vinet",
                "Natural Strain"
            ]

            dpg.add_combo(
                eos_options,
                default_value="Birch-Murnaghan 3rd",
                callback=self.on_eos_changed,
                width=-1,
                tag="eos_model_combo"
            )

        dpg.add_spacer(height=15)

    def setup_parameters_section(self):
        """Setup parameters input section"""
        dpg.add_text("EoS Parameters", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True,
                      borders_innerV=True, borders_outerV=True):
            dpg.add_table_column(label="Parameter")
            dpg.add_table_column(label="Value")
            dpg.add_table_column(label="Lock")

            params = [
                ('V0', 'V₀ (Å³/atom)', 11.5),
                ('B0', 'B₀ (GPa)', 130.0),
                ('B0_prime', "B₀'", 4.0),
            ]

            for key, label, default in params:
                with dpg.table_row():
                    dpg.add_text(label)

                    # Value input
                    input_tag = f"eos_param_{key}"
                    self.param_input_tags[key] = input_tag
                    dpg.add_input_double(
                        default_value=default,
                        tag=input_tag,
                        width=120,
                        callback=lambda s, a, u: self.on_param_changed(u),
                        user_data=key,
                        on_enter=True
                    )

                    # Lock checkbox
                    lock_tag = f"eos_lock_{key}"
                    self.param_lock_tags[key] = lock_tag
                    dpg.add_checkbox(
                        tag=lock_tag,
                        default_value=False,
                        callback=lambda s, a, u: self.on_lock_changed(u),
                        user_data=key
                    )

        dpg.add_spacer(height=10)

        # Reset button
        dpg.add_button(
            label="Reset to Default",
            callback=self.reset_parameters,
            width=-1
        )

        dpg.add_spacer(height=15)

    def setup_fitting_section(self):
        """Setup fitting controls section"""
        dpg.add_text("Fitting Controls", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.group():
            dpg.add_button(
                label="Auto Fit (All Parameters)",
                callback=self.auto_fit_all,
                width=-1,
                height=35
            )

            dpg.add_spacer(height=5)

            dpg.add_button(
                label="Fit Unlocked Parameters",
                callback=self.fit_unlocked,
                width=-1,
                height=35
            )

            dpg.add_spacer(height=5)

            dpg.add_button(
                label="Multi-Strategy Fit",
                callback=self.fit_multiple_strategies,
                width=-1,
                height=35
            )

        dpg.add_spacer(height=15)

    def setup_plot(self):
        """Setup plot area"""
        dpg.add_text("EoS Fit Visualization", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        # Create plot
        with dpg.plot(label="P-V Curve", height=400, width=-1, tag=self.plot_tag):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Volume (Å³/atom)", tag="eos_x_axis")
            dpg.add_plot_axis(dpg.mvYAxis, label="Pressure (GPa)", tag="eos_y_axis")

            # Placeholder series (will be updated with real data)
            with dpg.plot_axis(dpg.mvYAxis, label="Pressure (GPa)", tag="eos_y_axis"):
                dpg.add_scatter_series([], [], label="Data", tag="eos_data_series")
                dpg.add_line_series([], [], label="Fit", tag="eos_fit_series")

    def setup_results_section(self):
        """Setup results display section"""
        dpg.add_text("Fit Results", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.child_window(height=200, border=True, menubar=False):
            dpg.add_text(
                "No fitting results yet.\n\nLoad data and run fitting to see results here.",
                tag=self.results_text_tag,
                wrap=600,
                color=ColorScheme.TEXT_LIGHT
            )

    # Event handlers

    def load_csv_dialog(self):
        """Open file dialog to load CSV data"""
        def callback(sender, app_data):
            file_path = app_data['file_path_name']
            self.load_csv(file_path)

        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=callback,
            file_count=1,
            width=700,
            height=400,
            default_path="."
        ):
            dpg.add_file_extension(".csv")
            dpg.add_file_extension(".*")

    def load_csv(self, file_path: str):
        """Load data from CSV file"""
        try:
            df = pd.read_csv(file_path)

            # Try to identify V and P columns
            if 'V' in df.columns and 'P' in df.columns:
                self.V_data = df['V'].values
                self.P_data = df['P'].values
            elif 'Volume' in df.columns and 'Pressure' in df.columns:
                self.V_data = df['Volume'].values
                self.P_data = df['Pressure'].values
            elif len(df.columns) >= 2:
                # Assume first two columns are V and P
                self.V_data = df.iloc[:, 0].values
                self.P_data = df.iloc[:, 1].values
            else:
                MessageDialog.show(
                    "Error",
                    "CSV file must have at least 2 columns (Volume, Pressure)",
                    MessageDialog.ERROR
                )
                return

            # Update data info
            info_text = f"Loaded {len(self.V_data)} data points from:\n{file_path}\n\n"
            info_text += f"V range: {self.V_data.min():.2f} - {self.V_data.max():.2f} Å³/atom\n"
            info_text += f"P range: {self.P_data.min():.2f} - {self.P_data.max():.2f} GPa"

            dpg.set_value(self.data_info_tag, info_text)
            dpg.configure_item(self.data_info_tag, color=ColorScheme.TEXT_DARK)

            # Update plot with data
            self.update_plot()

            # Initialize fitter
            self.fitter = CrysFMLEoS(self.V_data, self.P_data, self.eos_type)

            MessageDialog.show(
                "Success",
                f"Successfully loaded {len(self.V_data)} data points",
                MessageDialog.SUCCESS
            )

        except Exception as e:
            MessageDialog.show(
                "Error",
                f"Failed to load CSV file:\n{str(e)}",
                MessageDialog.ERROR
            )

    def on_eos_changed(self, sender, app_data):
        """Handle EoS model change"""
        self.current_eos_model = app_data

        # Map string to EoSType enum
        eos_map = {
            "Birch-Murnaghan 2nd": EoSType.BIRCH_MURNAGHAN_2ND,
            "Birch-Murnaghan 3rd": EoSType.BIRCH_MURNAGHAN_3RD,
            "Birch-Murnaghan 4th": EoSType.BIRCH_MURNAGHAN_4TH,
            "Murnaghan": EoSType.MURNAGHAN,
            "Vinet": EoSType.VINET,
            "Natural Strain": EoSType.NATURAL_STRAIN
        }

        self.eos_type = eos_map.get(app_data, EoSType.BIRCH_MURNAGHAN_3RD)

        # Reinitialize fitter if data is loaded
        if self.V_data is not None and self.P_data is not None:
            self.fitter = CrysFMLEoS(self.V_data, self.P_data, self.eos_type)
            self.reset_parameters()

    def on_param_changed(self, key):
        """Handle parameter value change"""
        value = dpg.get_value(self.param_input_tags[key])
        self.param_values[key] = value
        self.update_manual_fit()

    def on_lock_changed(self, key):
        """Handle parameter lock change"""
        locked = dpg.get_value(self.param_lock_tags[key])
        self.param_locks[key] = locked

    def reset_parameters(self):
        """Reset parameters to initial estimates"""
        if self.V_data is None or self.P_data is None:
            MessageDialog.show(
                "Warning",
                "Please load data first",
                MessageDialog.WARNING
            )
            return

        # Get initial estimates from fitter
        try:
            V0_init = self.V_data[0]  # First volume point
            B0_init = 130.0  # Reasonable default for most materials
            B0p_init = 4.0   # Typical value

            # Update UI
            dpg.set_value(self.param_input_tags['V0'], V0_init)
            dpg.set_value(self.param_input_tags['B0'], B0_init)
            dpg.set_value(self.param_input_tags['B0_prime'], B0p_init)

            # Update internal values
            self.param_values['V0'] = V0_init
            self.param_values['B0'] = B0_init
            self.param_values['B0_prime'] = B0p_init

            self.update_manual_fit()

        except Exception as e:
            MessageDialog.show(
                "Error",
                f"Failed to reset parameters:\n{str(e)}",
                MessageDialog.ERROR
            )

    def get_current_params(self):
        """Get current parameter values as EoSParameters object"""
        return EoSParameters(
            V0=self.param_values['V0'],
            B0=self.param_values['B0'],
            B0_prime=self.param_values['B0_prime']
        )

    def update_manual_fit(self):
        """Update plot with current manual parameters"""
        if self.V_data is None or self.fitter is None:
            return

        try:
            params = self.get_current_params()
            self.current_params = params

            # Calculate fit curve
            V_fit = np.linspace(self.V_data.min(), self.V_data.max(), 100)
            P_fit = self.fitter.calculate_pressure(V_fit, params)

            # Calculate residuals
            P_calc = self.fitter.calculate_pressure(self.V_data, params)
            residuals = self.P_data - P_calc
            rms = np.sqrt(np.mean(residuals**2))

            # Update plot
            self.update_plot(V_fit, P_fit)

            # Update results
            results_text = f"Manual Parameters:\n"
            results_text += f"V₀ = {params.V0:.4f} Å³/atom\n"
            results_text += f"B₀ = {params.B0:.4f} GPa\n"
            results_text += f"B₀' = {params.B0_prime:.4f}\n"
            results_text += f"\nRMS Residual = {rms:.4f} GPa"

            dpg.set_value(self.results_text_tag, results_text)
            dpg.configure_item(self.results_text_tag, color=ColorScheme.TEXT_DARK)

        except Exception as e:
            print(f"Error updating manual fit: {e}")

    def auto_fit_all(self):
        """Perform automatic fitting of all parameters"""
        if self.V_data is None or self.fitter is None:
            MessageDialog.show(
                "Warning",
                "Please load data first",
                MessageDialog.WARNING
            )
            return

        try:
            # Get initial parameters
            initial_params = self.get_current_params()

            # Perform fit
            result = self.fitter.fit(initial_params)

            if result.success:
                self.fitted_params = result.params

                # Update UI with fitted values
                dpg.set_value(self.param_input_tags['V0'], result.params.V0)
                dpg.set_value(self.param_input_tags['B0'], result.params.B0)
                dpg.set_value(self.param_input_tags['B0_prime'], result.params.B0_prime)

                # Update internal values
                self.param_values['V0'] = result.params.V0
                self.param_values['B0'] = result.params.B0
                self.param_values['B0_prime'] = result.params.B0_prime

                # Update plot and results
                V_fit = np.linspace(self.V_data.min(), self.V_data.max(), 100)
                P_fit = self.fitter.calculate_pressure(V_fit, result.params)
                self.update_plot(V_fit, P_fit)

                # Format results
                results_text = f"Fitted Parameters:\n"
                results_text += f"V₀ = {result.params.V0:.4f} ± {result.errors.get('V0', 0):.4f} Å³/atom\n"
                results_text += f"B₀ = {result.params.B0:.4f} ± {result.errors.get('B0', 0):.4f} GPa\n"
                results_text += f"B₀' = {result.params.B0_prime:.4f} ± {result.errors.get('B0_prime', 0):.4f}\n"
                results_text += f"\nRMS Residual = {result.rms:.4f} GPa\n"
                results_text += f"Chi² = {result.chi_squared:.6f}"

                dpg.set_value(self.results_text_tag, results_text)
                dpg.configure_item(self.results_text_tag, color=ColorScheme.TEXT_DARK)

                MessageDialog.show(
                    "Success",
                    f"Fit converged successfully!\nRMS = {result.rms:.4f} GPa",
                    MessageDialog.SUCCESS
                )
            else:
                MessageDialog.show(
                    "Warning",
                    "Fit did not converge. Try different initial parameters.",
                    MessageDialog.WARNING
                )

        except Exception as e:
            MessageDialog.show(
                "Error",
                f"Fitting failed:\n{str(e)}",
                MessageDialog.ERROR
            )

    def fit_unlocked(self):
        """Fit only unlocked parameters"""
        if self.V_data is None or self.fitter is None:
            MessageDialog.show(
                "Warning",
                "Please load data first",
                MessageDialog.WARNING
            )
            return

        # Get which parameters are unlocked
        free_params = {k: not v for k, v in self.param_locks.items()}

        if not any(free_params.values()):
            MessageDialog.show(
                "Warning",
                "All parameters are locked. Unlock at least one parameter to fit.",
                MessageDialog.WARNING
            )
            return

        try:
            initial_params = self.get_current_params()

            # Perform fit with fixed parameters
            result = self.fitter.fit(initial_params, free_params=free_params)

            if result.success:
                # Update only unlocked parameters
                if free_params['V0']:
                    dpg.set_value(self.param_input_tags['V0'], result.params.V0)
                    self.param_values['V0'] = result.params.V0
                if free_params['B0']:
                    dpg.set_value(self.param_input_tags['B0'], result.params.B0)
                    self.param_values['B0'] = result.params.B0
                if free_params['B0_prime']:
                    dpg.set_value(self.param_input_tags['B0_prime'], result.params.B0_prime)
                    self.param_values['B0_prime'] = result.params.B0_prime

                # Update plot
                V_fit = np.linspace(self.V_data.min(), self.V_data.max(), 100)
                P_fit = self.fitter.calculate_pressure(V_fit, result.params)
                self.update_plot(V_fit, P_fit)

                # Update results
                results_text = f"Fitted Parameters (unlocked only):\n"
                for key, label in [('V0', 'V₀'), ('B0', 'B₀'), ('B0_prime', "B₀'")]:
                    value = getattr(result.params, key)
                    err = result.errors.get(key, 0)
                    status = "fitted" if free_params[key] else "fixed"
                    results_text += f"{label} = {value:.4f} ± {err:.4f} ({status})\n"

                results_text += f"\nRMS Residual = {result.rms:.4f} GPa"

                dpg.set_value(self.results_text_tag, results_text)

                MessageDialog.show(
                    "Success",
                    f"Partial fit converged!\nRMS = {result.rms:.4f} GPa",
                    MessageDialog.SUCCESS
                )
            else:
                MessageDialog.show(
                    "Warning",
                    "Fit did not converge",
                    MessageDialog.WARNING
                )

        except Exception as e:
            MessageDialog.show(
                "Error",
                f"Fitting failed:\n{str(e)}",
                MessageDialog.ERROR
            )

    def fit_multiple_strategies(self):
        """Try multiple fitting strategies and pick the best result"""
        if self.V_data is None or self.fitter is None:
            MessageDialog.show(
                "Warning",
                "Please load data first",
                MessageDialog.WARNING
            )
            return

        try:
            best_result = None
            best_rms = float('inf')

            # Strategy 1: Current parameters
            result1 = self.fitter.fit(self.get_current_params())
            if result1.success and result1.rms < best_rms:
                best_result = result1
                best_rms = result1.rms

            # Strategy 2: Default parameters
            default_params = EoSParameters(V0=self.V_data[0], B0=130.0, B0_prime=4.0)
            result2 = self.fitter.fit(default_params)
            if result2.success and result2.rms < best_rms:
                best_result = result2
                best_rms = result2.rms

            # Strategy 3: Try with different B0 values
            for B0_try in [100.0, 150.0, 200.0]:
                params_try = EoSParameters(V0=self.V_data[0], B0=B0_try, B0_prime=4.0)
                result = self.fitter.fit(params_try)
                if result.success and result.rms < best_rms:
                    best_result = result
                    best_rms = result.rms

            if best_result and best_result.success:
                # Update UI with best results
                dpg.set_value(self.param_input_tags['V0'], best_result.params.V0)
                dpg.set_value(self.param_input_tags['B0'], best_result.params.B0)
                dpg.set_value(self.param_input_tags['B0_prime'], best_result.params.B0_prime)

                self.param_values['V0'] = best_result.params.V0
                self.param_values['B0'] = best_result.params.B0
                self.param_values['B0_prime'] = best_result.params.B0_prime

                # Update plot
                V_fit = np.linspace(self.V_data.min(), self.V_data.max(), 100)
                P_fit = self.fitter.calculate_pressure(V_fit, best_result.params)
                self.update_plot(V_fit, P_fit)

                # Update results
                results_text = f"Best Fit (Multi-Strategy):\n"
                results_text += f"V₀ = {best_result.params.V0:.4f} ± {best_result.errors.get('V0', 0):.4f}\n"
                results_text += f"B₀ = {best_result.params.B0:.4f} ± {best_result.errors.get('B0', 0):.4f}\n"
                results_text += f"B₀' = {best_result.params.B0_prime:.4f} ± {best_result.errors.get('B0_prime', 0):.4f}\n"
                results_text += f"\nRMS Residual = {best_result.rms:.4f} GPa"

                dpg.set_value(self.results_text_tag, results_text)

                MessageDialog.show(
                    "Success",
                    f"Multi-strategy fit complete!\nBest RMS = {best_rms:.4f} GPa",
                    MessageDialog.SUCCESS
                )
            else:
                MessageDialog.show(
                    "Warning",
                    "All fitting strategies failed to converge",
                    MessageDialog.WARNING
                )

        except Exception as e:
            MessageDialog.show(
                "Error",
                f"Multi-strategy fitting failed:\n{str(e)}",
                MessageDialog.ERROR
            )

    def update_plot(self, V_fit=None, P_fit=None):
        """Update the P-V plot"""
        if self.V_data is None:
            return

        # Update data points
        dpg.set_value("eos_data_series", [list(self.V_data), list(self.P_data)])

        # Update fit curve if provided
        if V_fit is not None and P_fit is not None:
            dpg.set_value("eos_fit_series", [list(V_fit), list(P_fit)])

        # Auto-fit axes
        dpg.fit_axis_data("eos_x_axis")
        dpg.fit_axis_data("eos_y_axis")


def create_eos_window():
    """Create and show the EoS fitting window"""
    gui = InteractiveEoSGUI()
    gui.create_window()
    return gui


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

    # Create window
    gui = create_eos_window()

    dpg.create_viewport(title="Interactive EoS Fitting", width=1500, height=950)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == '__main__':
    main()