# -*- coding: utf-8 -*-
"""
DPG Core Components Module
Contains Dear PyGui version of all UI components, replacing Tkinter

Dear PyGui is a fast and powerful Python GUI framework that uses GPU rendering.
This module provides DPG equivalents for all Tkinter components used in the application.

Features:
- Light purple/lavender theme with NO black backgrounds or borders
- Arial font support with system font fallback
- Modern UI components with rounded corners and smooth transitions
- Comprehensive theme coverage to eliminate all default black elements

Created as a replacement for theme_module.py and batch_appearance.py
"""

import dearpygui.dearpygui as dpg
import math
import time
from pathlib import Path
from typing import Callable, Optional, Tuple, Any


# ==============================================================================
# Color Scheme
# ==============================================================================

class ColorScheme:
    """Color scheme matching the original Tkinter theme"""

    # Main colors
    BG = (248, 247, 255)  # #F8F7FF
    CARD_BG = (255, 255, 255)  # #FFFFFF
    PRIMARY = (183, 148, 246)  # #B794F6
    PRIMARY_HOVER = (212, 187, 255)  # #D4BBFF
    SECONDARY = (224, 170, 255)  # #E0AAFF
    ACCENT = (255, 107, 157)  # #FF6B9D
    TEXT_DARK = (43, 45, 66)  # #2B2D42
    TEXT_LIGHT = (120, 100, 150)  # Light purple instead of gray
    BORDER = (232, 228, 243)  # #E8E4F3
    SUCCESS = (6, 214, 160)  # #06D6A0
    ERROR = (239, 71, 111)  # #EF476F
    LIGHT_PURPLE = (230, 217, 245)  # #E6D9F5
    ACTIVE_MODULE = (200, 179, 230)  # #C8B3E6

    @staticmethod
    def to_normalized(color: Tuple[int, int, int], alpha: int = 255) -> Tuple[float, float, float, float]:
        """Convert RGB color to normalized RGBA for DPG"""
        return (color[0]/255, color[1]/255, color[2]/255, alpha/255)

    @staticmethod
    def to_int(color: Tuple[int, int, int], alpha: int = 255) -> int:
        """Convert RGB color to 32-bit integer for DPG"""
        r, g, b = color
        return (alpha << 24) | (b << 16) | (g << 8) | r


# ==============================================================================
# Modern Button Component
# ==============================================================================

class ModernButton:
    """
    Modern button component with rounded corners and hover effects
    DPG version of Tkinter ModernButton (Canvas-based)
    """

    def __init__(self, parent: str, text: str, callback: Callable,
                 icon: str = "",
                 bg_color: Tuple[int, int, int] = ColorScheme.PRIMARY,
                 hover_color: Tuple[int, int, int] = ColorScheme.PRIMARY_HOVER,
                 text_color: Tuple[int, int, int] = (255, 255, 255),
                 width: int = 200, height: int = 40,
                 tag: Optional[str] = None):
        """
        Create a modern button with rounded corners

        Args:
            parent: Parent container tag
            text: Button text
            callback: Function to call on click
            icon: Optional emoji icon
            bg_color: Background color (RGB tuple)
            hover_color: Hover state color (RGB tuple)
            text_color: Text color (RGB tuple)
            width: Button width in pixels
            height: Button height in pixels
            tag: Optional tag for the button
        """
        self.text = text
        self.callback = callback
        self.icon = icon
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self.is_hovered = False

        display_text = f"{icon}  {text}" if icon else text

        if tag is None:
            tag = f"button_{id(self)}"
        self.tag = tag

        with dpg.group(parent=parent, horizontal=False):
            self.button = dpg.add_button(
                label=display_text,
                callback=callback,
                width=width,
                height=height,
                tag=tag
            )

            # Set button colors using theme
            with dpg.theme() as button_theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, bg_color + (255,))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, hover_color + (255,))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, hover_color + (255,))
                    dpg.add_theme_color(dpg.mvThemeCol_Text, text_color + (255,))
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 15, 10)

            dpg.bind_item_theme(self.button, button_theme)


# ==============================================================================
# Modern Tab Component
# ==============================================================================

class ModernTab:
    """
    Modern tab component with active/inactive states
    DPG version of Tkinter ModernTab
    """

    def __init__(self, parent: str, text: str, callback: Callable,
                 is_active: bool = False,
                 tag: Optional[str] = None):
        """
        Create a modern tab component

        Args:
            parent: Parent container tag
            text: Tab text
            callback: Function to call on click
            is_active: Whether this tab is initially active
            tag: Optional tag for the tab
        """
        self.text = text
        self.callback = callback
        self.is_active = is_active

        if tag is None:
            tag = f"tab_{id(self)}"
        self.tag = tag

        self.active_color = ColorScheme.PRIMARY
        self.inactive_color = ColorScheme.TEXT_LIGHT
        self.hover_color = ColorScheme.PRIMARY_HOVER

        with dpg.group(parent=parent, horizontal=True):
            self.tab_button = dpg.add_button(
                label=text,
                callback=self._on_click,
                tag=tag
            )

            self._update_theme()

    def _on_click(self):
        """Handle tab click"""
        if self.callback:
            self.callback()

    def set_active(self, active: bool):
        """Set the active state of the tab"""
        self.is_active = active
        self._update_theme()

    def _update_theme(self):
        """Update tab appearance based on active state"""
        color = self.active_color if self.is_active else self.inactive_color

        with dpg.theme() as tab_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, color + (255,))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, self.hover_color + (255,))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, color + (255,))
                dpg.add_theme_color(dpg.mvThemeCol_Text, ColorScheme.TEXT_DARK + (255,))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 20, 10)

        dpg.bind_item_theme(self.tab_button, tab_theme)


# ==============================================================================
# Progress Bar with Animation
# ==============================================================================

class CuteSheepProgressBar:
    """
    Cute sheep progress bar animation
    DPG version of Tkinter CuteSheepProgressBar
    """

    def __init__(self, parent: str, width: int = 700, height: int = 80,
                 tag: Optional[str] = None):
        """
        Create an animated sheep progress bar

        Args:
            parent: Parent container tag
            width: Canvas width
            height: Canvas height
            tag: Optional tag for the canvas
        """
        self.width = width
        self.height = height
        self.is_animating = False
        self.sheep = []
        self.frame_count = 0

        if tag is None:
            tag = f"progress_{id(self)}"
        self.tag = tag

        with dpg.drawlist(width=width, height=height, parent=parent, tag=tag):
            pass

    def start(self):
        """Start the animation"""
        self.is_animating = True
        self.frame_count = 0
        self.sheep = []
        self._animate()

    def stop(self):
        """Stop the animation"""
        self.is_animating = False
        dpg.delete_item(self.tag, children_only=True)
        self.sheep = []
        self.frame_count = 0

    def _animate(self):
        """Animation loop"""
        if not self.is_animating:
            return

        # Clear canvas
        dpg.delete_item(self.tag, children_only=True)

        # Spawn new sheep periodically
        if self.frame_count % 35 == 0:
            self.sheep.append({'x': -40, 'phase': 0})

        # Update and draw all sheep
        new_sheep = []
        for sheep_data in self.sheep:
            sheep_data['x'] += 3.5
            sheep_data['phase'] += 0.25

            if sheep_data['x'] < self.width + 50:
                self._draw_sheep(sheep_data['x'], self.height // 2, sheep_data['phase'])
                new_sheep.append(sheep_data)

        self.sheep = new_sheep
        self.frame_count += 1

        # Schedule next frame (approximately 35ms)
        if self.is_animating:
            dpg.set_frame_callback(dpg.get_frame_count() + 1, self._animate)

    def _draw_sheep(self, x: float, y: float, jump_phase: float):
        """Draw a cute sheep with bounce animation"""
        jump = -abs(math.sin(jump_phase) * 15)
        y_pos = y + jump

        # Draw sheep emoji using text
        dpg.draw_text((x, y_pos), "🐿️", parent=self.tag, size=48,
                     color=ColorScheme.TEXT_DARK + (255,))


# ==============================================================================
# Card Frame Component
# ==============================================================================

class CardFrame:
    """
    Styled card frame with border
    DPG version of card frames used throughout the application
    """

    def __init__(self, parent: str, label: str = "",
                 bg_color: Tuple[int, int, int] = ColorScheme.CARD_BG,
                 border_color: Tuple[int, int, int] = ColorScheme.BORDER,
                 tag: Optional[str] = None):
        """
        Create a card frame

        Args:
            parent: Parent container tag
            label: Optional card label
            bg_color: Background color
            border_color: Border color
            tag: Optional tag for the card
        """
        if tag is None:
            tag = f"card_{id(self)}"
        self.tag = tag

        with dpg.child_window(parent=parent, border=True, tag=tag):
            if label:
                dpg.add_text(label, color=ColorScheme.PRIMARY + (255,))
                dpg.add_separator()

        # Apply card theme
        with dpg.theme() as card_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, bg_color + (255,))
                dpg.add_theme_color(dpg.mvThemeCol_Border, border_color + (255,))
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 20, 12)

        dpg.bind_item_theme(tag, card_theme)


# ==============================================================================
# File and Folder Pickers
# ==============================================================================

class FilePicker:
    """File picker dialog wrapper for DPG"""

    @staticmethod
    def open_file(callback: Callable, filetypes: str = ".*",
                  tag: Optional[str] = None):
        """
        Open a file selection dialog

        Args:
            callback: Function to call with selected file path
            filetypes: File type filter (e.g., ".poni,.edf")
            tag: Optional tag for the dialog
        """
        if tag is None:
            tag = f"file_dialog_{id(callback)}"

        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=lambda sender, app_data: callback(app_data['file_path_name']),
            tag=tag,
            width=700,
            height=400
        ):
            dpg.add_file_extension(filetypes, color=ColorScheme.PRIMARY + (255,))

    @staticmethod
    def open_folder(callback: Callable, tag: Optional[str] = None):
        """
        Open a folder selection dialog

        Args:
            callback: Function to call with selected folder path
            tag: Optional tag for the dialog
        """
        if tag is None:
            tag = f"folder_dialog_{id(callback)}"

        with dpg.file_dialog(
            directory_selector=True,
            show=True,
            callback=lambda sender, app_data: callback(app_data['file_path_name']),
            tag=tag,
            width=700,
            height=400
        ):
            pass


# ==============================================================================
# Input Components
# ==============================================================================

class SpinboxStyleButton:
    """
    Spinbox-style button widget
    DPG version of custom Tkinter SpinboxStyleButton
    """

    def __init__(self, parent: str, text: str, callback: Callable,
                 width: int = 80, font_size: int = 9,
                 tag: Optional[str] = None):
        """Create a spinbox-style button"""
        if tag is None:
            tag = f"spinbox_btn_{id(self)}"
        self.tag = tag

        self.button = dpg.add_button(
            label=text,
            callback=callback,
            width=width,
            parent=parent,
            tag=tag
        )

        # Apply spinbox button theme
        with dpg.theme() as btn_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (232, 213, 240, 255))  # #E8D5F0
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (213, 192, 224, 255))  # #D5C0E0
                dpg.add_theme_color(dpg.mvThemeCol_Text, (107, 76, 122, 255))  # #6B4C7A
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)

        dpg.bind_item_theme(self.button, btn_theme)


class CustomSpinbox:
    """
    Custom spinbox with left/right arrow buttons
    DPG version of custom Tkinter CustomSpinbox
    """

    def __init__(self, parent: str, min_val: float = 0, max_val: float = 100,
                 default_val: float = 0, increment: float = 1,
                 is_float: bool = False, width: int = 80,
                 callback: Optional[Callable] = None,
                 tag: Optional[str] = None):
        """Create a custom spinbox with +/- buttons"""
        if tag is None:
            tag = f"spinbox_{id(self)}"
        self.tag = tag

        self.min_val = min_val
        self.max_val = max_val
        self.increment = increment
        self.is_float = is_float
        self.callback = callback

        with dpg.group(parent=parent, horizontal=True, tag=tag):
            # Decrease button
            dpg.add_button(label="<", callback=self._decrease, width=30)

            # Value input
            if is_float:
                self.input = dpg.add_input_float(
                    default_value=default_val,
                    width=width,
                    step=0,
                    min_value=min_val,
                    max_value=max_val,
                    min_clamped=True,
                    max_clamped=True,
                    on_enter=True,
                    callback=self._on_value_change
                )
            else:
                self.input = dpg.add_input_int(
                    default_value=int(default_val),
                    width=width,
                    step=0,
                    min_value=int(min_val),
                    max_value=int(max_val),
                    min_clamped=True,
                    max_clamped=True,
                    on_enter=True,
                    callback=self._on_value_change
                )

            # Increase button
            dpg.add_button(label=">", callback=self._increase, width=30)

    def _increase(self):
        """Increase value"""
        current = dpg.get_value(self.input)
        new_val = min(self.max_val, current + self.increment)
        dpg.set_value(self.input, new_val)
        if self.callback:
            self.callback()

    def _decrease(self):
        """Decrease value"""
        current = dpg.get_value(self.input)
        new_val = max(self.min_val, current - self.increment)
        dpg.set_value(self.input, new_val)
        if self.callback:
            self.callback()

    def _on_value_change(self):
        """Handle value change"""
        if self.callback:
            self.callback()

    def get_value(self):
        """Get current value"""
        return dpg.get_value(self.input)

    def set_value(self, value):
        """Set value"""
        dpg.set_value(self.input, value)


# ==============================================================================
# Message Dialogs
# ==============================================================================

class MessageDialog:
    """Message dialog wrappers for DPG"""
    
    # Message type constants for backward compatibility
    INFO = "info"
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"

    @staticmethod
    def show(title: str, message: str, msg_type: str = INFO, callback: Optional[Callable] = None):
        """
        Generic show method for backward compatibility
        
        Args:
            title: Dialog title
            message: Message to display
            msg_type: Type of message (INFO, ERROR, SUCCESS, WARNING)
            callback: Optional callback function
        """
        if msg_type == MessageDialog.ERROR:
            MessageDialog.show_error(title, message, callback)
        elif msg_type == MessageDialog.SUCCESS:
            MessageDialog.show_success(title, message, "", callback)
        elif msg_type == MessageDialog.WARNING:
            MessageDialog.show_warning(title, message, callback)
        else:
            MessageDialog.show_info(title, message, callback)

    @staticmethod
    def show_info(title: str, message: str, callback: Optional[Callable] = None):
        """Show info message"""
        dialog_tag = f"info_{time.time()}"
        
        with dpg.window(label=title, modal=True, show=True, tag=dialog_tag,
                       no_title_bar=False, popup=True, width=400, height=200):
            dpg.add_text("[i]", color=ColorScheme.PRIMARY + (255,))
            dpg.add_spacer(height=5)
            dpg.add_text(message, wrap=350)
            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_button(
                label="OK",
                width=100,
                callback=lambda: (dpg.delete_item(dialog_tag),
                                callback() if callback else None)
            )

    @staticmethod
    def show_error(title: str, message: str, callback: Optional[Callable] = None):
        """Show error message"""
        dialog_tag = f"error_{time.time()}"
        
        with dpg.window(label=title, modal=True, show=True, tag=dialog_tag,
                       no_title_bar=False, popup=True, width=450, height=250):
            dpg.add_text("[!]", color=ColorScheme.ERROR + (255,))
            dpg.add_spacer(height=5)
            dpg.add_text(message, wrap=400, color=ColorScheme.ERROR + (255,))
            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_button(
                label="OK",
                width=100,
                callback=lambda: (dpg.delete_item(dialog_tag),
                                callback() if callback else None)
            )

    @staticmethod
    def show_success(title: str, message: str, details: str = "",
                    callback: Optional[Callable] = None):
        """Show success dialog with enhanced styling"""
        dialog_tag = f"success_{time.time()}"
        
        with dpg.window(label=title, modal=True, show=True, tag=dialog_tag,
                       no_title_bar=False, popup=True, width=450, height=280):
            dpg.add_text("[OK]", color=ColorScheme.SUCCESS + (255,))
            dpg.add_spacer(height=5)
            dpg.add_text(message, wrap=400, color=ColorScheme.PRIMARY + (255,))
            if details:
                dpg.add_spacer(height=5)
                dpg.add_separator()
                dpg.add_spacer(height=5)
                dpg.add_text(details, wrap=400, color=ColorScheme.TEXT_LIGHT + (255,))
            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_button(
                label="OK",
                width=150,
                callback=lambda: (dpg.delete_item(dialog_tag),
                                callback() if callback else None)
            )

    @staticmethod
    def show_warning(title: str, message: str, callback: Optional[Callable] = None):
        """Show warning message"""
        dialog_tag = f"warning_{time.time()}"
        
        with dpg.window(label=title, modal=True, show=True, tag=dialog_tag,
                       no_title_bar=False, popup=True, width=400, height=220):
            dpg.add_text("[Warning]", color=(255, 165, 0, 255))
            dpg.add_spacer(height=5)
            dpg.add_text(message, wrap=350, color=(255, 165, 0, 255))
            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_button(
                label="OK",
                width=100,
                callback=lambda: (dpg.delete_item(dialog_tag),
                                callback() if callback else None)
            )


# ==============================================================================
# Scrolled Text Widget
# ==============================================================================

class ScrolledText:
    """
    Scrolled text widget for logs
    DPG version of Tkinter scrolledtext
    """

    def __init__(self, parent: str, width: int = -1, height: int = 200,
                 readonly: bool = True, tag: Optional[str] = None):
        """Create a scrolled text widget"""
        if tag is None:
            tag = f"scrolltext_{id(self)}"
        self.tag = tag
        self.readonly = readonly

        self.text_widget = dpg.add_input_text(
            parent=parent,
            multiline=True,
            readonly=readonly,
            width=width,
            height=height,
            tag=tag,
            default_value=""
        )

    def insert(self, text: str):
        """Insert text at the end"""
        current = dpg.get_value(self.text_widget)
        dpg.set_value(self.text_widget, current + text)

    def clear(self):
        """Clear all text"""
        dpg.set_value(self.text_widget, "")

    def get(self):
        """Get all text"""
        return dpg.get_value(self.text_widget)


# ==============================================================================
# Utility Functions
# ==============================================================================

def setup_dpg_theme():
    """Setup global DPG theme with light purple color scheme and no black elements"""
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            # Window and background colors - light purple theme
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, ColorScheme.BG + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, ColorScheme.CARD_BG + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, ColorScheme.CARD_BG + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_Border, ColorScheme.BORDER + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0))  # Transparent shadow
            
            # Text colors - no gray!
            dpg.add_theme_color(dpg.mvThemeCol_Text, ColorScheme.TEXT_DARK + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, ColorScheme.PRIMARY + (180,))  # Purple instead of gray
            
            # Button colors
            dpg.add_theme_color(dpg.mvThemeCol_Button, ColorScheme.PRIMARY + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ColorScheme.PRIMARY_HOVER + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ColorScheme.PRIMARY + (255,))

            # Input field colors - light purple/lavender theme (no gray)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (248, 246, 255, 255))  # Very light purple
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (240, 238, 255, 255))  # Lighter purple
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (235, 230, 255, 255))  # Light purple
            
            # Header colors (for collapsing headers, tables, etc.)
            dpg.add_theme_color(dpg.mvThemeCol_Header, ColorScheme.LIGHT_PURPLE + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, ColorScheme.PRIMARY + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, ColorScheme.PRIMARY_HOVER + (255,))
            
            # Tab colors
            dpg.add_theme_color(dpg.mvThemeCol_Tab, ColorScheme.LIGHT_PURPLE + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, ColorScheme.PRIMARY_HOVER + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, ColorScheme.PRIMARY + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, ColorScheme.BORDER + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, ColorScheme.LIGHT_PURPLE + (255,))
            
            # Scrollbar colors - light purple theme
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (248, 246, 255, 255))  # Very light purple
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, ColorScheme.PRIMARY + (200,))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, ColorScheme.PRIMARY + (230,))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, ColorScheme.PRIMARY + (255,))
            
            # Slider colors
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, ColorScheme.PRIMARY + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, ColorScheme.PRIMARY_HOVER + (255,))
            
            # Checkbox and radio button colors
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, ColorScheme.PRIMARY + (255,))
            
            # Separator color
            dpg.add_theme_color(dpg.mvThemeCol_Separator, ColorScheme.BORDER + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, ColorScheme.PRIMARY + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, ColorScheme.PRIMARY_HOVER + (255,))
            
            # Title colors
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, ColorScheme.LIGHT_PURPLE + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, ColorScheme.PRIMARY + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, ColorScheme.BORDER + (255,))
            
            # Menu bar colors
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, ColorScheme.LIGHT_PURPLE + (255,))
            
            # Table colors
            dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, ColorScheme.LIGHT_PURPLE + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, ColorScheme.BORDER + (255,))
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, ColorScheme.BORDER + (180,))
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, ColorScheme.CARD_BG + (255,))  # White background
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (240, 238, 255, 255))  # Very light purple

            # Styles
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 15, 15)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 5)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 8, 6)
            dpg.add_theme_style(dpg.mvStyleVar_IndentSpacing, 20)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 14)
            dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 12)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_PopupBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_TabBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 9)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 5)

    dpg.bind_theme(global_theme)


def setup_arial_font(size: int = 16):
    """
    Setup Arial font for the entire application
    Suppresses all errors and warnings
    
    Args:
        size: Font size in pixels
        
    Returns:
        Font registry tag or None
    """
    import warnings
    import sys
    import io
    
    # Suppress all warnings
    warnings.filterwarnings('ignore')
    
    try:
        # Redirect stderr temporarily to suppress DPG warnings
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        
        with dpg.font_registry():
            # Try to find Arial font in common system locations
            arial_paths = [
                "C:/Windows/Fonts/arial.ttf",  # Windows
                "C:/Windows/Fonts/Arial.ttf",  # Windows (case sensitive)
                "/usr/share/fonts/truetype/msttcorefonts/arial.ttf",  # Linux
                "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS
                "/Library/Fonts/Arial.ttf",  # macOS alternate
            ]
            
            # Try each path
            for font_path in arial_paths:
                try:
                    if Path(font_path).exists():
                        default_font = dpg.add_font(font_path, size)
                        dpg.bind_font(default_font)
                        sys.stderr = old_stderr  # Restore stderr
                        return default_font
                except:
                    continue
            
            # If Arial not found, use default font silently
            try:
                default_font = dpg.add_font("", size)
                dpg.bind_font(default_font)
                sys.stderr = old_stderr  # Restore stderr
                return default_font
            except:
                sys.stderr = old_stderr  # Restore stderr
                return None
                
    except Exception as e:
        # Restore stderr in case of error
        try:
            sys.stderr = old_stderr
        except:
            pass
        return None


def create_font(font_file: str = None, size: int = 16) -> int:
    """
    Create and register a custom font
    
    Args:
        font_file: Path to TTF font file
        size: Font size
        
    Returns:
        Font tag
    """
    with dpg.font_registry():
        if font_file and Path(font_file).exists():
            return dpg.add_font(font_file, size)
        else:
            # Use default font
            return dpg.add_font("", size)