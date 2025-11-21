#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
示例：如何使用增强版批量积分脚本

本示例展示了不同的格式选择方案和使用场景
"""

from batch_integration import run_batch_integration

# ========================================
# 示例 1: 推荐配置（基本格式 + 堆叠图）
# ========================================
def example_recommended():
    """推荐配置：输出XY和DAT格式，生成堆叠图"""
    print("示例 1: 推荐配置 - 基本格式 + 堆叠图")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_recommended',
        formats=['xy', 'dat'],  # 基本格式
        create_stacked_plot=True,
        stacked_plot_offset='auto'
    )


# ========================================
# 示例 2: 完整功能（所有格式）
# ========================================
def example_all_formats():
    """输出所有可用格式（占用空间较大）"""
    print("示例 2: 输出所有格式")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_all',
        formats=['xy', 'dat', 'chi', 'fxye', 'svg', 'png'],  # 所有格式
        create_stacked_plot=True,
        stacked_plot_offset='auto'
    )


# ========================================
# 示例 3: 仅XY格式（最常用，最节省空间）
# ========================================
def example_xy_only():
    """仅输出XY格式，最常用的数据格式"""
    print("示例 3: 仅输出XY格式")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_xy',
        formats=['xy'],  # 仅XY格式
        create_stacked_plot=True
    )


# ========================================
# 示例 4: 仅图形输出（用于可视化）
# ========================================
def example_plots_only():
    """仅生成图形文件，适合快速预览和报告"""
    print("示例 4: 仅生成图形文件")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_plots',
        formats=['svg', 'png'],  # 仅图形格式
        create_stacked_plot=True
    )


# ========================================
# 示例 5: GSAS精修格式
# ========================================
def example_gsas_format():
    """输出GSAS-II和GSAS兼容格式，用于Rietveld精修"""
    print("示例 5: 生成GSAS精修格式")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_gsas',
        formats=['chi', 'fxye'],  # CHI (GSAS-II) 和 FXYE (GSAS) 格式
        create_stacked_plot=True
    )


# ========================================
# 示例 6: 数据分析组合（XY + 图形）
# ========================================
def example_analysis_combo():
    """数据分析常用组合：XY数据 + PNG图形"""
    print("示例 6: 数据分析组合")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_analysis',
        formats=['xy', 'png'],  # 数据 + 图形
        create_stacked_plot=True
    )


# ========================================
# 示例 7: 发表级图形（高质量矢量图）
# ========================================
def example_publication():
    """用于论文发表的高质量图形"""
    print("示例 7: 发表级图形输出")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_publication',
        formats=['xy', 'svg'],  # XY数据 + 矢量图
        create_stacked_plot=True
    )


# ========================================
# 示例 8: 自定义偏移量的堆叠图
# ========================================
def example_custom_offset():
    """手动设置堆叠图的偏移量"""
    print("示例 8: 自定义堆叠图偏移")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_custom',
        formats=['xy'],
        create_stacked_plot=True,
        stacked_plot_offset=5000  # 手动设置偏移为5000
    )


if __name__ == "__main__":
    print("=" * 80)
    print("HDF5 批量积分 - 使用示例")
    print("=" * 80)
    print("\n可用示例函数：")
    print("  1. example_recommended()   - 推荐配置（xy + dat）")
    print("  2. example_all_formats()   - 输出所有格式")
    print("  3. example_xy_only()       - 仅XY格式（最节省）")
    print("  4. example_plots_only()    - 仅图形文件")
    print("  5. example_gsas_format()   - GSAS精修格式")
    print("  6. example_analysis_combo()- 数据+图形组合")
    print("  7. example_publication()   - 发表级输出")
    print("  8. example_custom_offset() - 自定义堆叠偏移")
    print("\n请取消注释下方要运行的示例函数：\n")

    # 取消注释要运行的示例
    # example_recommended()
    # example_all_formats()
    # example_xy_only()
    # example_plots_only()
    # example_gsas_format()
    # example_analysis_combo()
    # example_publication()
    # example_custom_offset()

    print("提示：请编辑本文件，取消注释要运行的示例函数")
