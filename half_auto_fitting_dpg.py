# -*- coding: utf-8 -*-
"""
Interactive Peak Fitting with GUI - DPG Version

Enhanced encapsulated version converted from Tkinter to Dear PyGui.

@author: candicewang928@gmail.com
Converted to DPG: 2025-11-27
"""

import numpy as np
import dearpygui.dearpygui as dpg
from scipy.optimize import curve_fit
from scipy.special import wofz
from scipy.signal import savgol_filter, find_peaks
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import UnivariateSpline
from sklearn.cluster import DBSCAN
import os
import pandas as pd
import warnings

from dpg_components import ColorScheme, ModernButton, MessageDialog

warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


# ==============================================================================
# Data Processing Classes
# ==============================================================================

class DataProcessor:
    """Data smoothing and processing utilities"""

    @staticmethod
    def gaussian_smoothing(y, sigma=2):
        """
        Apply Gaussian smoothing

        Parameters:
        -----------
        y : array
            Input data
        sigma : float
            Gaussian kernel width

        Returns:
        --------
        array : Smoothed data
        """
        return gaussian_filter1d(y, sigma=sigma)

    @staticmethod
    def savgol_smoothing(y, window_length=11, polyorder=3):
        """
        Apply Savitzky-Golay smoothing

        Parameters:
        -----------
        y : array
            Input data
        window_length : int
            Window size (must be odd)
        polyorder : int
            Polynomial order

        Returns:
        --------
        array : Smoothed data
        """
        if len(y) < window_length:
            window_length = len(y) if len(y) % 2 == 1 else len(y) - 1
            if window_length < 3:
                return y

        if window_length % 2 == 0:
            window_length += 1

        polyorder = min(polyorder, window_length - 1)

        return savgol_filter(y, window_length, polyorder)

    @classmethod
    def apply_smoothing(cls, y, method='gaussian', **kwargs):
        """
        Apply smoothing with specified method

        Parameters:
        -----------
        y : array
            Input data
        method : str
            'gaussian' or 'savgol'
        **kwargs : Additional parameters for smoothing method

        Returns:
        --------
        array : Smoothed data
        """
        if method == 'gaussian':
            sigma = kwargs.get('sigma', 2)
            return cls.gaussian_smoothing(y, sigma)
        elif method == 'savgol':
            window_length = kwargs.get('window_length', 11)
            polyorder = kwargs.get('polyorder', 3)
            return cls.savgol_smoothing(y, window_length, polyorder)
        else:
            return y


class PeakProfile:
    """Peak profile functions"""

    @staticmethod
    def pseudo_voigt(x, amplitude, center, sigma, gamma, eta):
        """Pseudo-Voigt profile (mix of Gaussian and Lorentzian)"""
        gaussian = np.exp(-((x - center) ** 2) / (2 * sigma ** 2))
        lorentzian = gamma**2 / ((x - center)**2 + gamma**2)
        return amplitude * (eta * lorentzian + (1 - eta) * gaussian)

    @staticmethod
    def voigt(x, amplitude, center, sigma, gamma):
        """Voigt profile"""
        z = ((x - center) + 1j * gamma) / (sigma * np.sqrt(2))
        profile = np.real(wofz(z)) / (sigma * np.sqrt(2 * np.pi))
        return amplitude * profile

    @staticmethod
    def calculate_fwhm(sigma, gamma, eta):
        """Calculate FWHM for pseudo-Voigt"""
        fwhm_g = 2.355 * sigma
        fwhm_l = 2 * gamma
        return eta * fwhm_l + (1 - eta) * fwhm_g


class PeakDetector:
    """Automatic peak detection"""

    @staticmethod
    def auto_find_peaks(x, y):
        """
        Automatically find peaks in data

        Parameters:
        -----------
        x : array
            X data
        y : array
            Y data

        Returns:
        --------
        list : Peak positions (x values)
        """
        # Smooth data for peak detection
        y_smooth = DataProcessor.gaussian_smoothing(y, sigma=2)

        # Calculate peak prominence threshold
        prominence = (np.max(y_smooth) - np.min(y_smooth)) * 0.05

        # Find peaks
        peaks, properties = find_peaks(
            y_smooth,
            prominence=prominence,
            distance=5
        )

        # Convert indices to x positions
        peak_positions = x[peaks].tolist()

        return peak_positions


# ==============================================================================
# Main GUI Class
# ==============================================================================

class PeakFittingGUI:
    """Interactive peak fitting GUI - DPG Version"""

    def __init__(self):
        """Initialize the GUI"""
        # Data storage
        self.x_original = None
        self.y_original = None
        self.x_current = None
        self.y_current = None

        # Background points
        self.bg_points = []
        self.bg_selection_mode = False

        # Peak positions
        self.peak_positions = []

        # Fitted results
        self.fitted_params = []

        # File management
        self.current_file = None
        self.file_list = []
        self.current_file_index = -1

        # UI tags
        self.window_tag = "peak_fitting_window"
        self.plot_tag = "peak_plot"
        self.data_series_tag = "data_series"
        self.bg_series_tag = "bg_series"
        self.peak_series_tag = "peak_series"
        self.info_text_tag = "info_text"
        self.results_text_tag = "results_text"

        # Smoothing parameters
        self.smooth_method = "gaussian"
        self.smooth_sigma = 2.0
        self.smooth_window = 11
        self.smooth_poly = 3

    def create_window(self):
        """Create the main window"""
        # Check if window already exists and delete it
        if dpg.does_item_exist(self.window_tag):
            dpg.delete_item(self.window_tag)
        
        with dpg.window(
            label="Interactive Peak Fitting",
            tag=self.window_tag,
            width=1600,
            height=1000,
            pos=[30, 30],
            on_close=self.on_window_close,
            show=True
        ):
            with dpg.group(horizontal=True):
                # Left panel - Controls
                with dpg.child_window(width=350, tag="peak_left_panel", border=True, menubar=False):
                    self._create_control_panel()
                    self._create_background_panel()
                    self._create_smoothing_panel()

                # Right panel - Plot and Results
                with dpg.child_window(tag="peak_right_panel", border=False, menubar=False):
                    self._create_plot_area()
                    dpg.add_separator()
                    self._create_results_panel()
    
    def on_window_close(self):
        """Handle window close event"""
        try:
            if dpg.does_item_exist(self.window_tag):
                dpg.delete_item(self.window_tag)
        except Exception as e:
            print(f"Error closing window: {e}")

    def _create_control_panel(self):
        """Create file loading and navigation controls"""
        dpg.add_text("File Operations", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.group():
            dpg.add_button(
                label="Load Data File",
                callback=self.load_file_dialog,
                width=-1,
                height=40
            )

            dpg.add_spacer(height=10)

            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="◀ Previous",
                    callback=self.prev_file,
                    width=165
                )
                dpg.add_button(
                    label="Next ▶",
                    callback=self.next_file,
                    width=165
                )

            dpg.add_spacer(height=10)

            dpg.add_text("No file loaded", tag=self.info_text_tag,
                        color=ColorScheme.TEXT_LIGHT, wrap=330)

        dpg.add_spacer(height=15)

    def _create_background_panel(self):
        """Create background subtraction controls"""
        dpg.add_text("Background Subtraction", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.group():
            dpg.add_button(
                label="Select Background Points (Click on plot)",
                callback=self.toggle_bg_selection,
                width=-1,
                tag="bg_select_button"
            )

            dpg.add_spacer(height=5)

            dpg.add_button(
                label="Auto-Select Background",
                callback=self.auto_select_background,
                width=-1
            )

            dpg.add_spacer(height=5)

            dpg.add_button(
                label="Subtract Background",
                callback=self.subtract_background,
                width=-1
            )

            dpg.add_spacer(height=5)

            dpg.add_button(
                label="Clear Background",
                callback=self.clear_background,
                width=-1
            )

        dpg.add_spacer(height=15)

    def _create_smoothing_panel(self):
        """Create data smoothing controls"""
        dpg.add_text("Data Smoothing", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.group():
            dpg.add_text("Method:")
            dpg.add_radio_button(
                ["Gaussian", "Savitzky-Golay", "None"],
                default_value="Gaussian",
                callback=self.on_smooth_method_changed,
                tag="smooth_method_radio"
            )

            dpg.add_spacer(height=10)

            # Gaussian parameters
            with dpg.group(tag="gaussian_params"):
                dpg.add_text("Sigma:")
                dpg.add_slider_float(
                    default_value=2.0,
                    min_value=0.5,
                    max_value=10.0,
                    callback=self.on_smooth_param_changed,
                    tag="smooth_sigma_slider",
                    width=-1
                )

            # Savitzky-Golay parameters
            with dpg.group(tag="savgol_params", show=False):
                dpg.add_text("Window Length:")
                dpg.add_slider_int(
                    default_value=11,
                    min_value=5,
                    max_value=51,
                    callback=self.on_smooth_param_changed,
                    tag="smooth_window_slider",
                    width=-1
                )

                dpg.add_text("Polynomial Order:")
                dpg.add_slider_int(
                    default_value=3,
                    min_value=1,
                    max_value=5,
                    callback=self.on_smooth_param_changed,
                    tag="smooth_poly_slider",
                    width=-1
                )

            dpg.add_spacer(height=10)

            dpg.add_button(
                label="Apply Smoothing",
                callback=self.apply_smoothing_to_data,
                width=-1
            )

            dpg.add_spacer(height=5)

            dpg.add_button(
                label="Reset to Original",
                callback=self.reset_to_original_data,
                width=-1
            )

        dpg.add_spacer(height=15)

        # Peak detection
        dpg.add_text("Peak Detection & Fitting", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.group():
            dpg.add_button(
                label="Auto-Find Peaks",
                callback=self.auto_find_peaks,
                width=-1,
                height=35
            )

            dpg.add_spacer(height=5)

            dpg.add_button(
                label="Fit Peaks",
                callback=self.fit_peaks,
                width=-1,
                height=35
            )

            dpg.add_spacer(height=5)

            dpg.add_button(
                label="Clear Peaks",
                callback=self.clear_peaks,
                width=-1
            )

    def _create_plot_area(self):
        """Create plot area"""
        dpg.add_text("Data Visualization", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.plot(label="Peak Fitting Plot", height=550, width=-1, tag=self.plot_tag):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="X", tag="peak_x_axis")

            with dpg.plot_axis(dpg.mvYAxis, label="Intensity", tag="peak_y_axis"):
                dpg.add_line_series([], [], label="Data", tag=self.data_series_tag)
                dpg.add_line_series([], [], label="Background", tag=self.bg_series_tag)
                dpg.add_scatter_series([], [], label="Peaks", tag=self.peak_series_tag)

    def _create_results_panel(self):
        """Create results display panel"""
        dpg.add_text("Fitting Results", color=ColorScheme.TEXT_DARK)
        dpg.add_separator()

        with dpg.child_window(height=250, border=True, menubar=False):
            dpg.add_text(
                "Load data and fit peaks to see results here.",
                tag=self.results_text_tag,
                wrap=800,
                color=ColorScheme.TEXT_LIGHT
            )

    # Event handlers

    def load_file_dialog(self):
        """Open file dialog to load data"""
        def callback(sender, app_data):
            file_path = app_data['file_path_name']
            self.load_file_by_path(file_path)

        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=callback,
            width=700,
            height=400,
            default_path="."
        ):
            dpg.add_file_extension(".xy")
            dpg.add_file_extension(".txt")
            dpg.add_file_extension(".csv")
            dpg.add_file_extension(".*")

    def load_file_by_path(self, filepath):
        """Load data from file path"""
        try:
            # Try to read data (space or comma separated)
            try:
                data = np.loadtxt(filepath)
            except:
                data = pd.read_csv(filepath).values

            if data.shape[1] < 2:
                MessageDialog.show(
                    "Error",
                    "File must have at least 2 columns (X, Y)",
                    MessageDialog.ERROR
                )
                return

            self.x_original = data[:, 0]
            self.y_original = data[:, 1]
            self.x_current = self.x_original.copy()
            self.y_current = self.y_original.copy()

            # Update file info
            self.current_file = filepath
            self._scan_folder(filepath)

            # Update UI
            info_text = f"Loaded: {os.path.basename(filepath)}\n"
            info_text += f"Data points: {len(self.x_original)}\n"
            info_text += f"X range: {self.x_original.min():.2f} - {self.x_original.max():.2f}\n"
            info_text += f"Y range: {self.y_original.min():.2f} - {self.y_original.max():.2f}"

            if self.file_list:
                info_text += f"\n\nFile {self.current_file_index + 1} of {len(self.file_list)}"

            dpg.set_value(self.info_text_tag, info_text)
            dpg.configure_item(self.info_text_tag, color=ColorScheme.TEXT_DARK)

            # Clear previous state
            self.bg_points = []
            self.peak_positions = []
            self.fitted_params = []

            # Update plot
            self.update_plot()

        except Exception as e:
            MessageDialog.show(
                "Error",
                f"Failed to load file:\n{str(e)}",
                MessageDialog.ERROR
            )

    def _scan_folder(self, filepath):
        """Scan folder for similar files"""
        try:
            folder = os.path.dirname(filepath)
            ext = os.path.splitext(filepath)[1]

            files = [f for f in os.listdir(folder) if f.endswith(ext)]
            files.sort()

            self.file_list = [os.path.join(folder, f) for f in files]

            if filepath in self.file_list:
                self.current_file_index = self.file_list.index(filepath)
            else:
                self.file_list = [filepath]
                self.current_file_index = 0

        except Exception as e:
            self.file_list = [filepath]
            self.current_file_index = 0

    def prev_file(self):
        """Load previous file in folder"""
        if not self.file_list or self.current_file_index <= 0:
            MessageDialog.show("Info", "No previous file", MessageDialog.INFO)
            return

        self.current_file_index -= 1
        self.load_file_by_path(self.file_list[self.current_file_index])

    def next_file(self):
        """Load next file in folder"""
        if not self.file_list or self.current_file_index >= len(self.file_list) - 1:
            MessageDialog.show("Info", "No next file", MessageDialog.INFO)
            return

        self.current_file_index += 1
        self.load_file_by_path(self.file_list[self.current_file_index])

    def toggle_bg_selection(self):
        """Toggle background point selection mode"""
        self.bg_selection_mode = not self.bg_selection_mode

        if self.bg_selection_mode:
            dpg.configure_item("bg_select_button", label="Click on plot to add points (Active)")
            MessageDialog.show(
                "Info",
                "Click on plot to add background points.\nClick button again to finish.",
                MessageDialog.INFO
            )
        else:
            dpg.configure_item("bg_select_button", label="Select Background Points (Click on plot)")

    def auto_select_background(self):
        """Automatically select background points"""
        if self.x_current is None:
            MessageDialog.show("Warning", "Load data first", MessageDialog.WARNING)
            return

        try:
            # Simple auto-selection: take minimum points in sliding window
            n_points = 15
            window_size = len(self.x_current) // n_points

            bg_x = []
            bg_y = []

            for i in range(n_points):
                start = i * window_size
                end = min(start + window_size, len(self.x_current))

                if end > start:
                    idx = start + np.argmin(self.y_current[start:end])
                    bg_x.append(self.x_current[idx])
                    bg_y.append(self.y_current[idx])

            self.bg_points = list(zip(bg_x, bg_y))
            self.update_plot()

            MessageDialog.show(
                "Success",
                f"Selected {len(self.bg_points)} background points automatically",
                MessageDialog.SUCCESS
            )

        except Exception as e:
            MessageDialog.show("Error", f"Auto-selection failed:\n{str(e)}", MessageDialog.ERROR)

    def subtract_background(self):
        """Subtract background from data"""
        if not self.bg_points or self.x_current is None:
            MessageDialog.show("Warning", "Select background points first", MessageDialog.WARNING)
            return

        try:
            bg_x = [p[0] for p in self.bg_points]
            bg_y = [p[1] for p in self.bg_points]

            # Sort by x
            sorted_indices = np.argsort(bg_x)
            bg_x = np.array(bg_x)[sorted_indices]
            bg_y = np.array(bg_y)[sorted_indices]

            # Interpolate background
            spline = UnivariateSpline(bg_x, bg_y, k=3, s=None)
            bg_interp = spline(self.x_current)

            # Subtract
            self.y_current = self.y_current - bg_interp

            # Ensure non-negative
            self.y_current = np.maximum(self.y_current, 0)

            self.update_plot()

            MessageDialog.show(
                "Success",
                "Background subtracted successfully",
                MessageDialog.SUCCESS
            )

        except Exception as e:
            MessageDialog.show("Error", f"Background subtraction failed:\n{str(e)}", MessageDialog.ERROR)

    def clear_background(self):
        """Clear background points"""
        self.bg_points = []
        self.update_plot()

    def on_smooth_method_changed(self, sender, app_data):
        """Handle smoothing method change"""
        method_map = {
            "Gaussian": "gaussian",
            "Savitzky-Golay": "savgol",
            "None": "none"
        }
        self.smooth_method = method_map.get(app_data, "gaussian")

        # Show/hide appropriate parameter controls
        dpg.configure_item("gaussian_params", show=(self.smooth_method == "gaussian"))
        dpg.configure_item("savgol_params", show=(self.smooth_method == "savgol"))

    def on_smooth_param_changed(self, sender, app_data):
        """Handle smoothing parameter change"""
        self.smooth_sigma = dpg.get_value("smooth_sigma_slider")
        self.smooth_window = dpg.get_value("smooth_window_slider")
        self.smooth_poly = dpg.get_value("smooth_poly_slider")

    def apply_smoothing_to_data(self):
        """Apply smoothing to current data"""
        if self.y_current is None:
            MessageDialog.show("Warning", "Load data first", MessageDialog.WARNING)
            return

        try:
            if self.smooth_method == "gaussian":
                self.y_current = DataProcessor.gaussian_smoothing(
                    self.y_current, sigma=self.smooth_sigma
                )
            elif self.smooth_method == "savgol":
                self.y_current = DataProcessor.savgol_smoothing(
                    self.y_current,
                    window_length=self.smooth_window,
                    polyorder=self.smooth_poly
                )

            self.update_plot()

            MessageDialog.show(
                "Success",
                "Smoothing applied successfully",
                MessageDialog.SUCCESS
            )

        except Exception as e:
            MessageDialog.show("Error", f"Smoothing failed:\n{str(e)}", MessageDialog.ERROR)

    def reset_to_original_data(self):
        """Reset to original unprocessed data"""
        if self.x_original is None:
            return

        self.x_current = self.x_original.copy()
        self.y_current = self.y_original.copy()
        self.bg_points = []
        self.peak_positions = []
        self.fitted_params = []

        self.update_plot()

        dpg.set_value(self.results_text_tag, "Data reset to original")

    def auto_find_peaks(self):
        """Automatically find peaks in data"""
        if self.x_current is None:
            MessageDialog.show("Warning", "Load data first", MessageDialog.WARNING)
            return

        try:
            self.peak_positions = PeakDetector.auto_find_peaks(
                self.x_current, self.y_current
            )

            self.update_plot()

            MessageDialog.show(
                "Success",
                f"Found {len(self.peak_positions)} peaks",
                MessageDialog.SUCCESS
            )

        except Exception as e:
            MessageDialog.show("Error", f"Peak detection failed:\n{str(e)}", MessageDialog.ERROR)

    def fit_peaks(self):
        """Fit peaks with pseudo-Voigt profiles"""
        if not self.peak_positions or self.x_current is None:
            MessageDialog.show("Warning", "Find peaks first", MessageDialog.WARNING)
            return

        try:
            self.fitted_params = []
            results_text = f"Fitted {len(self.peak_positions)} peaks:\n\n"

            for i, peak_x in enumerate(self.peak_positions):
                # Find nearest data point
                idx = np.argmin(np.abs(self.x_current - peak_x))

                # Estimate initial parameters
                amplitude = self.y_current[idx]
                center = peak_x
                sigma = 0.1
                gamma = 0.1
                eta = 0.5

                # Define fit window (±3σ around peak)
                window = 3.0
                mask = np.abs(self.x_current - center) < window
                x_fit = self.x_current[mask]
                y_fit = self.y_current[mask]

                if len(x_fit) < 5:
                    continue

                try:
                    # Fit peak
                    popt, pcov = curve_fit(
                        PeakProfile.pseudo_voigt,
                        x_fit, y_fit,
                        p0=[amplitude, center, sigma, gamma, eta],
                        bounds=([0, center-window, 0, 0, 0],
                               [np.inf, center+window, window, window, 1])
                    )

                    self.fitted_params.append(popt)

                    # Calculate FWHM
                    fwhm = PeakProfile.calculate_fwhm(popt[2], popt[3], popt[4])

                    # Format results
                    results_text += f"Peak {i+1}:\n"
                    results_text += f"  Center: {popt[1]:.4f}\n"
                    results_text += f"  Amplitude: {popt[0]:.2f}\n"
                    results_text += f"  FWHM: {fwhm:.4f}\n\n"

                except:
                    results_text += f"Peak {i+1}: Fit failed\n\n"

            dpg.set_value(self.results_text_tag, results_text)
            dpg.configure_item(self.results_text_tag, color=ColorScheme.TEXT_DARK)

            MessageDialog.show(
                "Success",
                f"Fitted {len(self.fitted_params)} peaks successfully",
                MessageDialog.SUCCESS
            )

        except Exception as e:
            MessageDialog.show("Error", f"Peak fitting failed:\n{str(e)}", MessageDialog.ERROR)

    def clear_peaks(self):
        """Clear all peaks"""
        self.peak_positions = []
        self.fitted_params = []
        self.update_plot()
        dpg.set_value(self.results_text_tag, "Peaks cleared")

    def update_plot(self):
        """Update the plot with current data"""
        if self.x_current is None:
            return

        # Update data series
        dpg.set_value(self.data_series_tag, [list(self.x_current), list(self.y_current)])

        # Update background points
        if self.bg_points:
            bg_x = [p[0] for p in self.bg_points]
            bg_y = [p[1] for p in self.bg_points]
            dpg.set_value(self.bg_series_tag, [bg_x, bg_y])
        else:
            dpg.set_value(self.bg_series_tag, [[], []])

        # Update peak positions
        if self.peak_positions:
            peak_y = []
            for px in self.peak_positions:
                idx = np.argmin(np.abs(self.x_current - px))
                peak_y.append(self.y_current[idx])

            dpg.set_value(self.peak_series_tag, [self.peak_positions, peak_y])
        else:
            dpg.set_value(self.peak_series_tag, [[], []])

        # Auto-fit axes
        dpg.fit_axis_data("peak_x_axis")
        dpg.fit_axis_data("peak_y_axis")


def create_peak_fitting_window():
    """Create and show the peak fitting window"""
    gui = PeakFittingGUI()
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
    gui = create_peak_fitting_window()

    dpg.create_viewport(title="Interactive Peak Fitting", width=1650, height=1050)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == '__main__':
    main()