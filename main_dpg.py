# -*- coding: utf-8 -*-
"""
Main GUI Application - DPG Version
XRD Data Post-Processing Suite - Entry point and main window

This is the DPG (Dear PyGui) version of main.py, replacing Tkinter with Dear PyGui
"""

import dearpygui.dearpygui as dpg
import os
import sys
from pathlib import Path

from dpg_components import (
    ColorScheme, ModernButton, ModernTab, CuteSheepProgressBar,
    setup_dpg_theme, MessageDialog
)
from gui_base_dpg import GUIBase

# Import modules
try:
    from powder_module_dpg import PowderXRDModule
    POWDER_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import powder_module_dpg: {e}")
    POWDER_MODULE_AVAILABLE = False


class XRDProcessingGUI(GUIBase):
    """Main GUI application for XRD data processing - DPG Version"""

    def __init__(self):
        """Initialize main GUI"""
        super().__init__()

        # Initialize modules (will be loaded lazily)
        self.powder_module = None
        self.radial_module = None
        self.single_crystal_module = None

        # Current tab
        self.current_tab = "powder"

        # Tab references
        self.tabs = {}

    def setup_ui(self):
        """Setup main user interface"""
        # Create main window
        with dpg.window(
            tag="primary_window",
            label="XRD Data Post-Processing",
            width=1100,
            height=950,
            no_close=False,
            no_collapse=True
        ):
            # Header section
            with dpg.group(horizontal=False):
                with dpg.group(horizontal=True):
                    dpg.add_text("", color=ColorScheme.PRIMARY + (255,))  # Emoji placeholder
                    dpg.add_text(
                        "XRD Data Post-Processing",
                        color=ColorScheme.TEXT_DARK + (255,)
                    )
                dpg.add_separator()

            # Tab bar
            with dpg.group(horizontal=True, tag="tab_bar"):
                # Powder XRD tab
                self.tabs['powder'] = ModernTab(
                    parent="tab_bar",
                    text="Powder XRD",
                    callback=lambda: self.switch_tab("powder"),
                    is_active=True,
                    tag="tab_powder"
                )

                # Single Crystal tab
                self.tabs['single'] = ModernTab(
                    parent="tab_bar",
                    text="Single Crystal XRD",
                    callback=lambda: self.switch_tab("single"),
                    is_active=False,
                    tag="tab_single"
                )

                # Radial XRD tab
                self.tabs['radial'] = ModernTab(
                    parent="tab_bar",
                    text="Radial XRD",
                    callback=lambda: self.switch_tab("radial"),
                    is_active=False,
                    tag="tab_radial"
                )

            dpg.add_separator()

            # Scrollable content area
            with dpg.child_window(
                tag="content_area",
                border=False,
                width=-1,
                height=-1
            ):
                pass

        # Show powder tab by default
        self.switch_tab("powder")

    def switch_tab(self, tab_name: str):
        """
        Switch between main tabs

        Args:
            tab_name: Name of tab to switch to ('powder', 'single', 'radial')
        """
        # Update tab active states
        for name, tab in self.tabs.items():
            tab.set_active(name == tab_name)

        self.current_tab = tab_name

        # Clear content area
        dpg.delete_item("content_area", children_only=True)

        # Load appropriate module
        if tab_name == "powder":
            self._load_powder_module()
        elif tab_name == "radial":
            self._load_radial_module()
        elif tab_name == "single":
            self._load_single_crystal_module()

    def _load_powder_module(self):
        """Load powder XRD module"""
        if POWDER_MODULE_AVAILABLE:
            try:
                if self.powder_module is None:
                    self.powder_module = PowderXRDModule("content_area")
                
                self.powder_module.setup_ui()
                
            except Exception as e:
                # Fallback to placeholder if module fails to load
                self._show_module_error("Powder XRD Module", str(e))
        else:
            self._show_module_placeholder("Powder XRD Module", 
                "powder_module_dpg.py",
                ["1D Integration", "Peak Fitting", "Phase Analysis", 
                 "Volume Calculation", "EoS Fitting"])

    def _load_radial_module(self):
        """Load radial XRD module"""
        try:
            from radial_module_dpg import RadialIntegrationModule
            
            if self.radial_module is None:
                self.radial_module = RadialIntegrationModule("content_area")
            
            self.radial_module.setup_ui()
            
        except Exception as e:
            # Fallback to error display if module fails to load
            self._show_module_error("Radial XRD Module", str(e))

    def _load_single_crystal_module(self):
        """Load single crystal module (placeholder)"""
        self._show_module_placeholder("Single Crystal XRD", 
            "single_crystal_module_dpg.py", 
            ["Coming soon..."])
    
    def _show_module_placeholder(self, title: str, filename: str, features: list):
        """Show placeholder for module not yet loaded"""
        with dpg.child_window(parent="content_area", border=True, menubar=False):
            dpg.add_text(title, color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            if len(features) == 1 and features[0] == "Coming soon...":
                dpg.add_text("Coming soon...", color=ColorScheme.TEXT_LIGHT + (255,))
            else:
                dpg.add_text(
                    "This module provides the following functionality:",
                    color=ColorScheme.TEXT_DARK + (255,)
                )
                for feature in features:
                    dpg.add_text(f"  • {feature}", color=ColorScheme.TEXT_DARK + (255,))
                
                dpg.add_spacer(height=20)
                dpg.add_text(
                    f"Note: Full module implementation available in {filename}",
                    color=ColorScheme.TEXT_LIGHT + (255,)
                )
    
    def _show_module_error(self, title: str, error: str):
        """Show error message for module that failed to load"""
        with dpg.child_window(parent="content_area", border=True, menubar=False):
            dpg.add_text(title, color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_text(
                f"Error loading module: {error}",
                color=ColorScheme.ERROR + (255,)
            )
            dpg.add_spacer(height=20)
            dpg.add_text(
                "Please check that all dependencies are installed.",
                color=ColorScheme.TEXT_LIGHT + (255,)
            )


def show_startup_window(callback):
    """
    Show startup splash screen with progress animation

    Args:
        callback: Function to call after startup completes
    """
    with dpg.window(
        label="Loading...",
        tag="splash_window",
        width=480,
        height=280,
        no_title_bar=False,
        no_resize=True,
        no_move=False,
        modal=True,
        popup=True,
        pos=[300, 200]
    ):
        dpg.add_spacer(height=20)

        # Title
        dpg.add_text(
            "Starting up, please wait...",
            color=ColorScheme.PRIMARY + (255,)
        )

        dpg.add_spacer(height=10)

        # Progress text
        progress_text = dpg.add_text("0%", tag="progress_text")

        dpg.add_spacer(height=20)

        # Progress bar with sheep animation
        progress_bar = CuteSheepProgressBar(
            parent="splash_window",
            width=400,
            height=60,
            tag="splash_progress"
        )

        dpg.add_spacer(height=20)

        # Status message
        status_text = dpg.add_text(
            "Loading modules...",
            tag="status_text",
            color=ColorScheme.TEXT_LIGHT + (255,)
        )

    # Start progress animation
    progress_bar.start()

    def animate_progress(progress=0):
        """Animate startup progress"""
        if progress <= 100:
            dpg.set_value("progress_text", f"{progress}%")

            # Update status message at milestones
            if progress == 20:
                dpg.set_value("status_text", "Loading modules...")
            elif progress == 40:
                dpg.set_value("status_text", "Setting up workspace...")
            elif progress == 60:
                dpg.set_value("status_text", "Almost there!")
            elif progress == 80:
                dpg.set_value("status_text", "Final touches...")
            elif progress == 100:
                dpg.set_value("status_text", "Ready to go!")

            # Schedule next update
            delay = 0.035 if progress < 90 else 0.025
            dpg.set_frame_callback(
                dpg.get_frame_count() + int(delay * 60),
                lambda: animate_progress(progress + 2)
            )
        else:
            # Finish startup
            progress_bar.stop()
            dpg.delete_item("splash_window")
            callback()

    # Start animation
    animate_progress(0)


def launch_main_app():
    """Launch the main application"""
    # Suppress all warnings
    import warnings
    warnings.filterwarnings('ignore')
    
    # Setup DPG context
    dpg.create_context()

    # Setup global theme first
    setup_dpg_theme()
    
    # Setup Arial font (suppresses errors)
    from dpg_components import setup_arial_font
    try:
        setup_arial_font(size=14)
    except:
        pass  # Silently continue if font fails

    # Create application
    app = XRDProcessingGUI()
    app.setup_ui()

    # Setup viewport
    dpg.create_viewport(
        title="XRD Data Post-Processing",
        width=1100,
        height=950,
        resizable=True
    )

    # Setup DPG
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("primary_window", True)

    # Start render loop
    dpg.start_dearpygui()
    dpg.destroy_context()


def main():
    """Main application entry point"""
    # Suppress all warnings
    import warnings
    warnings.filterwarnings('ignore')
    
    # Setup DPG context
    dpg.create_context()

    # Setup global theme first
    setup_dpg_theme()
    
    # Setup Arial font (suppresses errors)
    from dpg_components import setup_arial_font
    try:
        setup_arial_font(size=14)
    except:
        pass  # Silently continue if font fails

    # Setup viewport
    dpg.create_viewport(
        title="XRD Data Post-Processing - Loading...",
        width=480,
        height=280,
        resizable=False
    )

    # Show startup window first
    show_startup_window(lambda: main_app_callback())

    # Setup DPG
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # Start render loop
    dpg.start_dearpygui()
    dpg.destroy_context()


def main_app_callback():
    """Callback after startup completes"""
    # Resize viewport for main app
    dpg.configure_viewport("viewport", width=1100, height=950)
    dpg.set_viewport_title("XRD Data Post-Processing")

    # Create main application
    app = XRDProcessingGUI()
    app.setup_ui()
    dpg.set_primary_window("primary_window", True)


if __name__ == "__main__":
    main()