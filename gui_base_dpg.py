# -*- coding: utf-8 -*-
"""
DPG Base GUI Components and Styles
Contains shared UI elements, color schemes, and utility methods

This is the DPG (Dear PyGui) version of gui_base.py
"""

import dearpygui.dearpygui as dpg
from dpg_components import ColorScheme, FilePicker, ModernButton, CardFrame
from typing import Callable, Optional, Any


class GUIBase:
    """Base class for GUI components with shared styles and utilities"""

    def __init__(self):
        """Initialize color scheme and styles"""
        self.colors = {
            'bg': ColorScheme.BG,
            'card_bg': ColorScheme.CARD_BG,
            'primary': ColorScheme.PRIMARY,
            'primary_hover': ColorScheme.PRIMARY_HOVER,
            'secondary': ColorScheme.SECONDARY,
            'accent': ColorScheme.ACCENT,
            'text_dark': ColorScheme.TEXT_DARK,
            'text_light': ColorScheme.TEXT_LIGHT,
            'border': ColorScheme.BORDER,
            'success': ColorScheme.SUCCESS,
            'error': ColorScheme.ERROR,
            'light_purple': ColorScheme.LIGHT_PURPLE,
            'active_module': ColorScheme.ACTIVE_MODULE
        }

    def create_card_frame(self, parent: str, label: str = "", **kwargs) -> str:
        """
        Create a styled card frame

        Args:
            parent: Parent container tag
            label: Optional card label
            **kwargs: Additional arguments

        Returns:
            Card tag
        """
        tag = kwargs.get('tag', f"card_{id(self)}")
        card = CardFrame(parent, label=label, tag=tag)
        return card.tag

    def create_file_picker(self, parent: str, label: str, variable_tag: str,
                          filetypes: str, pattern: bool = False):
        """
        Create a file picker widget with browse button

        Args:
            parent: Parent container tag
            label: Label text
            variable_tag: Tag for the input field that will store the file path
            filetypes: File type filter (e.g., ".poni,.edf")
            pattern: If True, creates pattern from selected file
        """
        with dpg.group(parent=parent, horizontal=False):
            dpg.add_text(label, color=self.colors['text_dark'] + (255,))

            with dpg.group(horizontal=True):
                # Input field
                input_tag = variable_tag
                dpg.add_input_text(
                    tag=input_tag,
                    width=-100,
                    readonly=False
                )

                # Browse button
                if pattern:
                    callback = lambda: self._browse_pattern(input_tag, filetypes)
                else:
                    callback = lambda: self._browse_file(input_tag, filetypes)

                ModernButton(
                    parent=dpg.last_container(),
                    text="Browse",
                    callback=callback,
                    bg_color=self.colors['secondary'],
                    hover_color=self.colors['primary'],
                    width=75,
                    height=28
                )

    def create_folder_picker(self, parent: str, label: str, variable_tag: str):
        """
        Create a folder picker widget with browse button

        Args:
            parent: Parent container tag
            label: Label text
            variable_tag: Tag for the input field that will store the folder path
        """
        with dpg.group(parent=parent, horizontal=False):
            dpg.add_text(label, color=self.colors['text_dark'] + (255,))

            with dpg.group(horizontal=True):
                # Input field
                input_tag = variable_tag
                dpg.add_input_text(
                    tag=input_tag,
                    width=-100,
                    readonly=False
                )

                # Browse button
                ModernButton(
                    parent=dpg.last_container(),
                    text="Browse",
                    callback=lambda: self._browse_folder(input_tag),
                    bg_color=self.colors['secondary'],
                    hover_color=self.colors['primary'],
                    width=75,
                    height=28
                )

    def create_entry(self, parent: str, label: str, variable_tag: str,
                    default_value: str = ""):
        """
        Create a text entry widget

        Args:
            parent: Parent container tag
            label: Label text
            variable_tag: Tag for the input field
            default_value: Default value
        """
        with dpg.group(parent=parent, horizontal=False):
            dpg.add_text(label, color=self.colors['text_dark'] + (255,))
            dpg.add_input_text(
                tag=variable_tag,
                default_value=default_value,
                width=-1
            )

    def _browse_file(self, variable_tag: str, filetypes: str):
        """
        Open file browser dialog

        Args:
            variable_tag: Tag of input field to update
            filetypes: File type filter
        """
        def callback(file_path):
            dpg.set_value(variable_tag, file_path)

        FilePicker.open_file(callback, filetypes)

    def _browse_pattern(self, variable_tag: str, filetypes: str):
        """
        Open file browser and create pattern from selected file

        Args:
            variable_tag: Tag of input field to update
            filetypes: File type filter
        """
        import os

        def callback(file_path):
            folder = os.path.dirname(file_path)
            ext = os.path.splitext(file_path)[1]
            pattern = os.path.join(folder, f"*{ext}")
            dpg.set_value(variable_tag, pattern)

        FilePicker.open_file(callback, filetypes)

    def _browse_folder(self, variable_tag: str):
        """
        Open folder browser dialog

        Args:
            variable_tag: Tag of input field to update
        """
        def callback(folder_path):
            dpg.set_value(variable_tag, folder_path)

        FilePicker.open_folder(callback)

    def show_success(self, message: str, details: str = ""):
        """
        Show success dialog

        Args:
            message: Success message
            details: Additional details
        """
        from dpg_components import MessageDialog
        MessageDialog.show_success("Success", message, details)

    def show_error(self, message: str):
        """
        Show error dialog

        Args:
            message: Error message
        """
        from dpg_components import MessageDialog
        MessageDialog.show_error("Error", message)

    def show_warning(self, message: str):
        """
        Show warning dialog

        Args:
            message: Warning message
        """
        from dpg_components import MessageDialog
        MessageDialog.show_warning("Warning", message)

    def show_info(self, message: str):
        """
        Show info dialog

        Args:
            message: Info message
        """
        from dpg_components import MessageDialog
        MessageDialog.show_info("Information", message)