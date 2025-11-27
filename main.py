# -*- coding: utf-8 -*-
"""
Main GUI Application - Safe DPG Version
更新的 DPG 入口，提供依赖检查、加载动画和模块切换
"""

import importlib.util
import sys
import traceback

print("正在启动 XRD 数据处理程序...")
print("=" * 70)


def _ensure_module(name: str, display_name: str, required: bool = True) -> bool:
    """检查模块是否可用"""
    available = importlib.util.find_spec(name) is not None
    prefix = "✓" if available else ("✗" if required else "⚠")
    status = "可用" if available else "不可用"
    print(f"      {prefix} {display_name} {status}")

    if required and not available:
        print(f"缺少必要依赖: {display_name}. 请安装后重试。")
        input("按回车键退出...")
        sys.exit(1)

    return available


print("[1/6] 检查 dearpygui...")
_ensure_module("dearpygui.dearpygui", "dearpygui")
import dearpygui.dearpygui as dpg

print("[2/6] 检查 dpg_components...")
_ensure_module("dpg_components", "dpg_components")
from dpg_components import (
    ColorScheme,
    ModernTab,
    CuteSheepProgressBar,
    setup_dpg_theme,
)

print("[3/6] 检查 gui_base_dpg...")
_ensure_module("gui_base_dpg", "gui_base_dpg")
from gui_base_dpg import GUIBase

print("[4/6] 检查 powder_module_dpg (可选)...")
POWDER_MODULE_AVAILABLE = _ensure_module(
    "powder_module_dpg", "powder_module_dpg", required=False
)
if POWDER_MODULE_AVAILABLE:
    from powder_module_dpg import PowderXRDModule

print("[5/6] 检查 radial_module_dpg (可选)...")
RADIAL_MODULE_AVAILABLE = _ensure_module(
    "radial_module_dpg", "radial_module_dpg", required=False
)

print("[6/6] 检查 single_crystal_module_dpg (占位)...")
print("      ⚠ single_crystal_module_dpg 不可用: 占位实现")
print("=" * 70)


class XRDProcessingGUI(GUIBase):
    """Main GUI application for XRD data processing - DPG Version"""

    def __init__(self):
        super().__init__()
        self.powder_module = None
        self.radial_module = None
        self.single_crystal_module = None
        self.current_tab = "powder"
        self.tabs = {}

    def setup_ui(self):
        """Setup main user interface"""
        with dpg.window(
            tag="primary_window",
            label="XRD Data Post-Processing",
            width=1100,
            height=950,
            no_close=False,
            no_collapse=True,
        ):
            with dpg.group(horizontal=False):
                with dpg.group(horizontal=True):
                    dpg.add_text("🧪", color=ColorScheme.PRIMARY + (255,))
                    dpg.add_text(
                        "XRD Data Post-Processing",
                        color=ColorScheme.TEXT_DARK + (255,),
                    )
                dpg.add_separator()

            with dpg.group(horizontal=True, tag="tab_bar"):
                self.tabs["powder"] = ModernTab(
                    parent="tab_bar",
                    text="Powder XRD",
                    callback=lambda: self.switch_tab("powder"),
                    is_active=True,
                    tag="tab_powder",
                )
                self.tabs["single"] = ModernTab(
                    parent="tab_bar",
                    text="Single Crystal XRD",
                    callback=lambda: self.switch_tab("single"),
                    is_active=False,
                    tag="tab_single",
                )
                self.tabs["radial"] = ModernTab(
                    parent="tab_bar",
                    text="Radial XRD",
                    callback=lambda: self.switch_tab("radial"),
                    is_active=False,
                    tag="tab_radial",
                )

            dpg.add_separator()

            with dpg.child_window(
                tag="content_area", border=False, autosize_x=True, autosize_y=True
            ):
                pass

        self.switch_tab("powder")

    def switch_tab(self, tab_name: str):
        """Switch between main tabs"""
        for name, tab in self.tabs.items():
            tab.set_active(name == tab_name)

        self.current_tab = tab_name
        dpg.delete_item("content_area", children_only=True)

        if tab_name == "powder":
            self._load_powder_module()
        elif tab_name == "radial":
            self._load_radial_module()
        elif tab_name == "single":
            self._load_single_crystal_module()

    def _load_powder_module(self):
        """Load powder XRD module"""
        if POWDER_MODULE_AVAILABLE:
            if self.powder_module is None:
                self.powder_module = PowderXRDModule("content_area")
            self.powder_module.setup_ui()
        else:
            self._show_module_placeholder(
                "Powder XRD Module",
                "powder_module_dpg.py",
                ["1D Integration", "Peak Fitting", "Phase Analysis"],
            )

    def _load_radial_module(self):
        """Load radial XRD module"""
        if not RADIAL_MODULE_AVAILABLE:
            self._show_module_placeholder(
                "Radial XRD Module",
                "radial_module_dpg.py",
                ["Radial Integration", "Texture Analysis"],
            )
            return

        from radial_module_dpg import RadialIntegrationModule

        if self.radial_module is None:
            self.radial_module = RadialIntegrationModule("content_area")
        self.radial_module.setup_ui()

    def _load_single_crystal_module(self):
        """Load single crystal module (placeholder)"""
        self._show_module_placeholder(
            "Single Crystal XRD",
            "single_crystal_module_dpg.py",
            ["Coming soon..."],
        )

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
                    color=ColorScheme.TEXT_DARK + (255,),
                )
                for feature in features:
                    dpg.add_text(f"  • {feature}", color=ColorScheme.TEXT_DARK + (255,))

                dpg.add_spacer(height=20)
                dpg.add_text(
                    f"Note: Full module implementation available in {filename}",
                    color=ColorScheme.TEXT_LIGHT + (255,),
                )

    def _show_module_error(self, title: str, error: str):
        """Show error message for module that failed to load"""
        with dpg.child_window(parent="content_area", border=True, menubar=False):
            dpg.add_text(title, color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_text(
                f"Error loading module: {error}",
                color=ColorScheme.ERROR + (255,),
            )
            dpg.add_spacer(height=20)
            dpg.add_text(
                "Please check that all dependencies are installed.",
                color=ColorScheme.TEXT_LIGHT + (255,),
            )


def _show_startup_window(callback):
    """Show startup splash screen with progress animation"""
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
        pos=[300, 200],
    ):
        dpg.add_spacer(height=20)
        dpg.add_text("Starting up, please wait...", color=ColorScheme.PRIMARY + (255,))
        dpg.add_spacer(height=10)
        progress_text = dpg.add_text("0%", tag="progress_text")
        dpg.add_spacer(height=20)
        progress_bar = CuteSheepProgressBar(
            parent="splash_window", width=400, height=60, tag="splash_progress"
        )
        dpg.add_spacer(height=20)
        dpg.add_text(
            "Loading modules...",
            tag="status_text",
            color=ColorScheme.TEXT_LIGHT + (255,),
        )

    progress_bar.start()

    def animate_progress(progress: int = 0):
        if progress <= 100:
            dpg.set_value("progress_text", f"{progress}%")
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

            delay = 0.035 if progress < 90 else 0.025
            dpg.set_frame_callback(
                dpg.get_frame_count() + int(delay * 60),
                lambda: animate_progress(progress + 2),
            )
        else:
            progress_bar.stop()
            dpg.delete_item("splash_window")
            callback()

    animate_progress(0)


def _launch_main_app():
    """Create the main application and start the render loop"""
    dpg.create_context()
    setup_dpg_theme()

    from dpg_components import setup_arial_font

    try:
        setup_arial_font(size=14)
    except Exception:
        pass

    app = XRDProcessingGUI()
    app.setup_ui()

    dpg.create_viewport(
        title="XRD Data Post-Processing",
        width=1100,
        height=950,
        resizable=True,
    )

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("primary_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


def main():
    """Main application entry point"""
    print("应用正在启动...")
    try:
        import warnings

        warnings.filterwarnings("ignore")
        dpg.create_context()
        setup_dpg_theme()

        from dpg_components import setup_arial_font

        try:
            setup_arial_font(size=14)
        except Exception:
            pass

        dpg.create_viewport(
            title="XRD Data Post-Processing - Loading...",
            width=480,
            height=280,
            resizable=False,
        )

        # Dear PyGui requires the context to be fully setup before frame callbacks
        # (used by the splash animation) can be registered. Move the splash
        # creation after setup/show to avoid initialization errors on startup.
        dpg.setup_dearpygui()
        dpg.show_viewport()

        _show_startup_window(lambda: _main_app_callback())
        dpg.start_dearpygui()
        dpg.destroy_context()
    except Exception:
        print()
        print("=" * 70)
        print("✗ 启动失败！")
        print("=" * 70)
        print("详细错误追踪:")
        print("-" * 70)
        traceback.print_exc()
        print("-" * 70)
        print()
        input("按回车键退出...")
        sys.exit(1)


def _main_app_callback():
    """Callback after splash screen completes"""
    dpg.configure_viewport("viewport", width=1100, height=950)
    dpg.set_viewport_title("XRD Data Post-Processing")

    app = XRDProcessingGUI()
    app.setup_ui()
    dpg.set_primary_window("primary_window", True)


if __name__ == "__main__":
    main()
