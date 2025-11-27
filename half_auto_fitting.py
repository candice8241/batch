# -*- coding: utf-8 -*-
"""
Interactive Peak Fitting with GUI - Dear PyGui Version
Simplified framework demonstrating migration approach
"""

import dearpygui.dearpygui as dpg
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
import os
import tempfile


class DataProcessor:
    """Handles data smoothing and preprocessing operations"""

    @staticmethod
    def gaussian_smoothing(y, sigma=2):
        """Apply Gaussian smoothing to data"""
        return gaussian_filter1d(y, sigma=sigma)

    @staticmethod
    def apply_smoothing(y, method='gaussian', **kwargs):
        """Apply smoothing to data using specified method"""
        if method == 'gaussian':
            sigma = kwargs.get('sigma', 2)
            return DataProcessor.gaussian_smoothing(y, sigma=sigma)
        return y


class PeakProfile:
    """Peak profile mathematical functions"""

    @staticmethod
    def pseudo_voigt(x, amplitude, center, sigma, gamma, eta):
        """Pseudo-Voigt profile"""
        gaussian = amplitude * np.exp(-(x - center)**2 / (2 * sigma**2)) / (sigma * np.sqrt(2 * np.pi))
        lorentzian = amplitude * gamma**2 / ((x - center)**2 + gamma**2) / (np.pi * gamma)
        return eta * lorentzian + (1 - eta) * gaussian


class PeakDetector:
    """Automatic peak detection"""

    @staticmethod
    def auto_find_peaks(x, y, height_threshold=0.1, distance=10):
        """Automatically find peaks in data"""
        # Normalize data
        y_norm = (y - np.min(y)) / (np.max(y) - np.min(y))

        # Find peaks
        peaks, properties = find_peaks(
            y_norm,
            height=height_threshold,
            distance=distance,
            prominence=0.05
        )

        return peaks, properties


class PeakFittingGUI:
    """
    Interactive Peak Fitting GUI - Dear PyGui Version
    Simplified framework demonstrating key migration concepts
    """

    def __init__(self):
        """Initialize Peak Fitting GUI"""
        self.x_data = None
        self.y_data = None
        self.y_smoothed = None
        self.peaks = []
        self.fit_results = []

        # Temporary directory for plot images
        self.temp_dir = tempfile.mkdtemp()

        # Create context and viewport
        dpg.create_context()
        self.setup_ui()

    def setup_ui(self):
        """Setup main user interface"""
        # Configure viewport
        dpg.create_viewport(
            title="Interactive Peak Fitting - Enhanced",
            width=1400,
            height=850,
            resizable=True
        )

        # Create main window
        with dpg.window(
            label="Peak Fitting",
            tag="main_window",
            width=1400,
            height=850,
            no_close=True
        ):
            # Top control panel
            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=-1):
                    self._create_control_panel()

                # Right side: Plot display area
                with dpg.child_window(width=-1, height=-1):
                    self._create_plot_area()

        dpg.set_primary_window("main_window", True)

    def _create_control_panel(self):
        """Create left control panel"""
        dpg.add_text("📊 Peak Fitting Controls", color=(107, 76, 122))
        dpg.add_separator()

        # File operations
        with dpg.collapsing_header(label="File Operations", default_open=True):
            dpg.add_button(
                label="Load Data",
                callback=self.load_data,
                width=-1
            )
            dpg.add_button(
                label="Save Results",
                callback=self.save_results,
                width=-1
            )

        # Smoothing controls
        with dpg.collapsing_header(label="Smoothing", default_open=True):
            dpg.add_text("Smoothing Method:")
            dpg.add_radio_button(
                ['None', 'Gaussian', 'Savitzky-Golay'],
                tag="smoothing_method",
                default_value='Gaussian',
                callback=self.apply_smoothing
            )
            dpg.add_text("Smoothing Sigma:")
            dpg.add_slider_float(
                tag="smoothing_sigma",
                default_value=2.0,
                min_value=0.5,
                max_value=10.0,
                callback=self.apply_smoothing,
                width=-1
            )

        # Peak detection
        with dpg.collapsing_header(label="Peak Detection", default_open=True):
            dpg.add_text("Height Threshold:")
            dpg.add_slider_float(
                tag="peak_threshold",
                default_value=0.1,
                min_value=0.0,
                max_value=1.0,
                format="%.2f",
                width=-1
            )
            dpg.add_text("Minimum Distance:")
            dpg.add_slider_int(
                tag="peak_distance",
                default_value=10,
                min_value=1,
                max_value=50,
                width=-1
            )
            dpg.add_button(
                label="🔍 Auto Detect Peaks",
                callback=self.auto_detect_peaks,
                width=-1
            )

        # Fitting controls
        with dpg.collapsing_header(label="Fitting", default_open=True):
            dpg.add_text("Profile Type:")
            dpg.add_combo(
                ['Pseudo-Voigt', 'Gaussian', 'Lorentzian'],
                tag="profile_type",
                default_value='Pseudo-Voigt',
                width=-1
            )
            dpg.add_button(
                label="🎯 Fit Peaks",
                callback=self.fit_peaks,
                width=-1
            )
            dpg.add_button(
                label="🗑️ Clear Fits",
                callback=self.clear_fits,
                width=-1
            )

        # Status
        dpg.add_separator()
        dpg.add_text("Status:", tag="status_text")
        dpg.add_text("No data loaded", tag="status_message", color=(150, 150, 150))

    def _create_plot_area(self):
        """Create plot display area"""
        dpg.add_text("📈 Data Plot", color=(107, 76, 122))
        dpg.add_separator()

        # Plot will be displayed as image
        # Create a placeholder for the plot image
        dpg.add_text("Load data to display plot", tag="plot_placeholder")

        # Texture registry for plot images
        with dpg.texture_registry(show=False):
            # Will be populated when plot is generated
            pass

        # Image display area
        dpg.add_image(
            texture_tag="plot_texture",
            tag="plot_image",
            show=False
        )

    def load_data(self):
        """Load XRD data from file"""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(
            filetypes=[
                ("XY files", "*.xy"),
                ("DAT files", "*.dat"),
                ("CHI files", "*.chi"),
                ("All files", "*.*")
            ]
        )
        root.destroy()

        if not filename:
            return

        try:
            # Load data
            data = np.loadtxt(filename)
            self.x_data = data[:, 0]
            self.y_data = data[:, 1]

            dpg.set_value("status_message", f"Loaded: {os.path.basename(filename)}")
            dpg.configure_item("status_message", color=(0, 255, 0))

            # Apply initial smoothing and update plot
            self.apply_smoothing()

        except Exception as e:
            dpg.set_value("status_message", f"Error: {str(e)}")
            dpg.configure_item("status_message", color=(255, 0, 0))

    def apply_smoothing(self, sender=None, app_data=None):
        """Apply smoothing to data"""
        if self.x_data is None or self.y_data is None:
            return

        method = dpg.get_value("smoothing_method")
        sigma = dpg.get_value("smoothing_sigma")

        if method == 'None':
            self.y_smoothed = self.y_data.copy()
        elif method == 'Gaussian':
            self.y_smoothed = DataProcessor.apply_smoothing(
                self.y_data,
                method='gaussian',
                sigma=sigma
            )
        else:
            self.y_smoothed = self.y_data.copy()

        self.update_plot()

    def auto_detect_peaks(self):
        """Automatically detect peaks"""
        if self.y_smoothed is None:
            dpg.set_value("status_message", "Load data first!")
            return

        threshold = dpg.get_value("peak_threshold")
        distance = dpg.get_value("peak_distance")

        self.peaks, _ = PeakDetector.auto_find_peaks(
            self.x_data,
            self.y_smoothed,
            height_threshold=threshold,
            distance=distance
        )

        dpg.set_value("status_message", f"Found {len(self.peaks)} peaks")
        dpg.configure_item("status_message", color=(0, 200, 200))

        self.update_plot()

    def fit_peaks(self):
        """Fit detected peaks"""
        if len(self.peaks) == 0:
            dpg.set_value("status_message", "No peaks detected!")
            return

        dpg.set_value("status_message", f"Fitting {len(self.peaks)} peaks...")
        # Placeholder for actual fitting implementation
        # This would involve curve_fit and peak profile functions

        self.update_plot()

    def clear_fits(self):
        """Clear all fits"""
        self.fit_results = []
        self.peaks = []
        dpg.set_value("status_message", "Cleared all fits")
        self.update_plot()

    def update_plot(self):
        """Update plot display"""
        if self.x_data is None or self.y_smoothed is None:
            return

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot data
        ax.plot(self.x_data, self.y_data, 'o-', label='Original', alpha=0.3, markersize=3)
        ax.plot(self.x_data, self.y_smoothed, '-', label='Smoothed', linewidth=2)

        # Mark peaks
        if len(self.peaks) > 0:
            ax.plot(
                self.x_data[self.peaks],
                self.y_smoothed[self.peaks],
                'r*',
                markersize=15,
                label='Detected Peaks'
            )

        ax.set_xlabel('2θ (°)', fontsize=12)
        ax.set_ylabel('Intensity', fontsize=12)
        ax.set_title('XRD Pattern with Peak Detection', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Save figure to temporary file
        plot_path = os.path.join(self.temp_dir, "current_plot.png")
        fig.savefig(plot_path, dpi=100, bbox_inches='tight')
        plt.close(fig)

        # Load image into Dear PyGui
        try:
            import PIL.Image as Image
            img = Image.open(plot_path)
            img = img.convert("RGBA")
            width, height = img.size
            data = np.array(img).flatten() / 255.0

            # Update or create texture
            if dpg.does_item_exist("plot_texture"):
                dpg.delete_item("plot_texture")

            with dpg.texture_registry():
                dpg.add_raw_texture(
                    width=width,
                    height=height,
                    default_value=data,
                    tag="plot_texture",
                    format=dpg.mvFormat_Float_rgba
                )

            # Show image
            if dpg.does_item_exist("plot_placeholder"):
                dpg.delete_item("plot_placeholder")

            dpg.configure_item("plot_image", show=True)

        except Exception as e:
            print(f"Error updating plot: {e}")

    def save_results(self):
        """Save fitting results"""
        if self.fit_results is None or len(self.fit_results) == 0:
            dpg.set_value("status_message", "No results to save!")
            return

        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        root.destroy()

        if filename:
            # Save results to CSV
            # Placeholder for actual implementation
            dpg.set_value("status_message", f"Results saved to {os.path.basename(filename)}")

    def run(self):
        """Run the application"""
        dpg.setup_dearpygui()
        dpg.show_viewport()

        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

        # Clean up temporary directory
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass


def main():
    """Main entry point"""
    app = PeakFittingGUI()
    app.run()


if __name__ == "__main__":
    main()