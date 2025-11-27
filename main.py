# -*- coding: utf-8 -*-
"""
Main GUI Application - Safe Version
带完整错误处理的安全版本
"""

import sys
import traceback

print("正在启动 XRD 数据处理程序...")
print("="*70)

# Step 1: Check dearpygui
print("[1/6] 检查 dearpygui...")
try:
    import dearpygui.dearpygui as dpg
    print("      ✓ dearpygui 可用")
except ImportError as e:
    print("      ✗ 缺少 dearpygui")
    print("      解决: pip install dearpygui")
    input("按回车键退出...")
    sys.exit(1)

# Step 2: Check dpg_components
print("[2/6] 检查 dpg_components...")
try:
    from dpg_components import (
        ColorScheme, ModernButton, ModernTab, CuteSheepProgressBar,
        setup_dpg_theme, MessageDialog
    )
    print("      ✓ dpg_components 可用")
except Exception as e:
    print(f"      ✗ dpg_components 错误: {e}")
    traceback.print_exc()
    input("按回车键退出...")
    sys.exit(1)

# Step 3: Check gui_base_dpg
print("[3/6] 检查 gui_base_dpg...")
try:
    from gui_base_dpg import GUIBase
    print("      ✓ gui_base_dpg 可用")
except Exception as e:
    print(f"      ✗ gui_base_dpg 错误: {e}")
    input("按回车键退出...")
    sys.exit(1)

# Step 4: Try to import powder module (optional)
print("[4/6] 检查 powder_module_dpg (可选)...")
try:
    from powder_module_dpg import PowderXRDModule
    POWDER_MODULE_AVAILABLE = True
    print("      ✓ powder_module_dpg 可用")
except Exception as e:
    POWDER_MODULE_AVAILABLE = False
    print(f"      ⚠ powder_module_dpg 不可用: {e}")
    print("      (这是可选模块，程序会继续运行)")

# Step 5: Create GUI class
print("[5/6] 创建 GUI 类...")
try:
    class XRDProcessingGUI(GUIBase):
        """Main GUI application"""

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
                no_collapse=True
            ):
                # Header
                with dpg.group(horizontal=False):
                    with dpg.group(horizontal=True):
                        dpg.add_text("XRD Data Post-Processing",
                                   color=ColorScheme.TEXT_DARK + (255,))
                    dpg.add_separator()

                # Tab bar
                with dpg.group(horizontal=True, tag="tab_bar"):
                    self.tabs['powder'] = ModernTab(
                        parent="tab_bar",
                        text="Powder XRD",
                        callback=lambda: self.switch_tab("powder"),
                        is_active=True,
                        tag="tab_powder"
                    )
                    self.tabs['single'] = ModernTab(
                        parent="tab_bar",
                        text="Single Crystal XRD",
                        callback=lambda: self.switch_tab("single"),
                        is_active=False,
                        tag="tab_single"
                    )
                    self.tabs['radial'] = ModernTab(
                        parent="tab_bar",
                        text="Radial XRD",
                        callback=lambda: self.switch_tab("radial"),
                        is_active=False,
                        tag="tab_radial"
                    )

                dpg.add_separator()

                # Content area
                with dpg.child_window(
                    tag="content_area",
                    border=False,
                    autosize_x=True,
                    autosize_y=True
                ):
                    pass

            self.switch_tab("powder")

        def switch_tab(self, tab_name: str):
            """Switch between tabs"""
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
            """Load powder module"""
            if POWDER_MODULE_AVAILABLE:
                try:
                    if self.powder_module is None:
                        self.powder_module = PowderXRDModule("content_area")
                    self.powder_module.setup_ui()
                except Exception as e:
                    self._show_error("Powder XRD Module", str(e))
            else:
                self._show_placeholder("Powder XRD Module", 
                    ["1D Integration", "Peak Fitting", "Phase Analysis"])

        def _load_radial_module(self):
            """Load radial module"""
            try:
                from radial_module_dpg import RadialIntegrationModule
                if self.radial_module is None:
                    self.radial_module = RadialIntegrationModule("content_area")
                self.radial_module.setup_ui()
            except Exception as e:
                self._show_error("Radial XRD Module", str(e))

        def _load_single_crystal_module(self):
            """Load single crystal module"""
            self._show_placeholder("Single Crystal XRD", ["Coming soon..."])

        def _show_placeholder(self, title: str, features: list):
            """Show placeholder"""
            with dpg.child_window(parent="content_area", border=True, menubar=False):
                dpg.add_text(title, color=ColorScheme.PRIMARY + (255,))
                dpg.add_separator()
                dpg.add_spacer(height=10)
                if features[0] == "Coming soon...":
                    dpg.add_text("Coming soon...", color=ColorScheme.TEXT_LIGHT + (255,))
                else:
                    dpg.add_text("功能列表:", color=ColorScheme.TEXT_DARK + (255,))
                    for feature in features:
                        dpg.add_text(f"  • {feature}", color=ColorScheme.TEXT_DARK + (255,))

        def _show_error(self, title: str, error: str):
            """Show error"""
            with dpg.child_window(parent="content_area", border=True, menubar=False):
                dpg.add_text(title, color=ColorScheme.PRIMARY + (255,))
                dpg.add_separator()
                dpg.add_spacer(height=10)
                dpg.add_text(f"错误: {error}", color=ColorScheme.ERROR + (255,))
                dpg.add_spacer(height=10)
                dpg.add_text("请检查依赖是否安装完整", color=ColorScheme.TEXT_LIGHT + (255,))
    
    print("      ✓ GUI 类创建成功")
except Exception as e:
    print(f"      ✗ GUI 类创建失败: {e}")
    traceback.print_exc()
    input("按回车键退出...")
    sys.exit(1)

# Step 6: Run the application
print("[6/6] 启动应用...")
print("="*70)
print()

try:
    # Suppress warnings
    import warnings
    warnings.filterwarnings('ignore')
    
    # Create context
    dpg.create_context()
    
    # Setup theme
    setup_dpg_theme()
    
    # Setup font (suppress errors)
    try:
        from dpg_components import setup_arial_font
        setup_arial_font(size=14)
    except:
        pass
    
    # Create and setup GUI
    app = XRDProcessingGUI()
    app.setup_ui()
    
    # Create viewport
    dpg.create_viewport(
        title="XRD Data Post-Processing",
        width=1150,
        height=1000
    )
    
    # Setup and show
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("primary_window", True)
    
    print("✓ 应用启动成功！")
    print("如果窗口打开，说明程序正常运行。")
    print()
    
    # Start main loop
    dpg.start_dearpygui()
    dpg.destroy_context()
    
    print()
    print("应用已正常关闭。")

except Exception as e:
    print()
    print("="*70)
    print("✗ 启动失败！")
    print("="*70)
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print()
    print("详细错误追踪:")
    print("-"*70)
    traceback.print_exc()
    print("-"*70)
    print()
    input("按回车键退出...")
    sys.exit(1)