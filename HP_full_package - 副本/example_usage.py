#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
示例：如何使用增强版批量积分脚本

本示例展示了不同的使用场景和配置选项
"""

from batch_integration import run_batch_integration

# ========================================
# 示例 1: 完整功能（所有格式 + 堆叠图）
# ========================================
def example_full_features():
    """使用所有功能的完整示例"""
    print("示例 1: 生成所有格式并创建堆叠图")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_full',
        dataset_path=None,  # 自动检测
        npt=2000,
        unit='2th_deg',
        formats=['xy', 'dat', 'chi', 'svg', 'png', 'fxye'],  # 所有格式
        create_stacked_plot=True,  # 生成堆叠图
        stacked_plot_offset='auto'  # 自动计算偏移
    )


# ========================================
# 示例 2: 仅基本格式（节省空间）
# ========================================
def example_basic_formats():
    """仅输出XY和DAT格式，适合快速处理"""
    print("示例 2: 仅输出XY和DAT格式")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_basic',
        formats=['xy', 'dat'],  # 仅基本格式
        create_stacked_plot=True
    )


# ========================================
# 示例 3: 手动设置堆叠图偏移
# ========================================
def example_custom_offset():
    """自定义堆叠图的偏移量"""
    print("示例 3: 手动设置堆叠图偏移量")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_custom',
        formats=['xy', 'dat'],
        create_stacked_plot=True,
        stacked_plot_offset=3000  # 手动设置偏移为3000
    )


# ========================================
# 示例 4: 仅图形输出（用于可视化）
# ========================================
def example_plots_only():
    """仅生成图形文件，适合快速预览"""
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
# 示例 5: GSAS格式（用于Rietveld精修）
# ========================================
def example_gsas_format():
    """输出GSAS兼容格式，用于结构精修"""
    print("示例 5: 生成GSAS格式文件")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_gsas',
        formats=['chi', 'fxye'],  # GSAS格式
        create_stacked_plot=True
    )


# ========================================
# 示例 6: 无掩膜处理
# ========================================
def example_no_mask():
    """不使用掩膜文件的示例"""
    print("示例 6: 不使用掩膜")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=None,  # 不使用掩膜
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_nomask',
        formats=['xy', 'dat', 'png'],
        create_stacked_plot=True
    )


# ========================================
# 示例 7: Q空间积分
# ========================================
def example_q_space():
    """在Q空间进行积分（而非2theta）"""
    print("示例 7: Q空间积分")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_qspace',
        unit='q_A^-1',  # Q空间单位
        formats=['xy', 'dat', 'png'],
        create_stacked_plot=True
    )


# ========================================
# 示例 8: 高分辨率积分
# ========================================
def example_high_resolution():
    """使用更多积分点获得更高分辨率"""
    print("示例 8: 高分辨率积分")

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\output_hires',
        npt=5000,  # 更多积分点
        formats=['xy', 'dat'],
        create_stacked_plot=True
    )


if __name__ == "__main__":
    # 运行示例（取消注释你想运行的示例）

    # example_full_features()      # 完整功能
    # example_basic_formats()      # 基本格式
    # example_custom_offset()      # 自定义偏移
    # example_plots_only()         # 仅图形
    # example_gsas_format()        # GSAS格式
    # example_no_mask()            # 无掩膜
    # example_q_space()            # Q空间
    # example_high_resolution()    # 高分辨率

    print("\n请取消注释要运行的示例函数")
