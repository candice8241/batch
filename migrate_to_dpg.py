#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tkinter to DPG Migration Script
自动备份Tkinter文件并替换为DPG版本

This script:
1. Backs up all Tkinter files with _tk suffix
2. Renames DPG files to replace the originals
3. Creates a rollback script in case you need to revert

Usage:
    python migrate_to_dpg.py [--dry-run]
"""

import os
import shutil
import argparse
from pathlib import Path


# Tkinter文件列表 (需要备份和替换的文件)
TKINTER_FILES = [
    "powder_module.py",
    "batch_appearance.py",
    "gui_base.py",
    "main.py",
    "radial_module.py",
    "single_crystal_module.py",
    "theme_module.py",
    "interactive_eos_gui.py",
]

# DPG文件映射 (DPG文件 -> 目标文件名)
DPG_FILE_MAPPING = {
    "dpg_components.py": "dpg_components.py",  # 保持不变
    "gui_base_dpg.py": "gui_base.py",          # 替换gui_base.py
    "main_dpg.py": "main.py",                  # 替换main.py
}


def backup_tkinter_files(dry_run=False):
    """
    备份所有Tkinter文件为 *_tk.py

    Args:
        dry_run: 如果True，只打印操作不实际执行
    """
    print("=" * 60)
    print("步骤 1: 备份Tkinter文件")
    print("=" * 60)

    for file in TKINTER_FILES:
        if not os.path.exists(file):
            print(f"⚠️  文件不存在，跳过: {file}")
            continue

        # 生成备份文件名
        backup_name = file.replace(".py", "_tk.py")

        if dry_run:
            print(f"[DRY RUN] 将备份: {file} -> {backup_name}")
        else:
            try:
                shutil.copy2(file, backup_name)
                print(f"✓ 已备份: {file} -> {backup_name}")
            except Exception as e:
                print(f"❌ 备份失败 {file}: {e}")

    print()


def replace_with_dpg_files(dry_run=False):
    """
    用DPG版本替换原文件

    Args:
        dry_run: 如果True，只打印操作不实际执行
    """
    print("=" * 60)
    print("步骤 2: 替换为DPG版本")
    print("=" * 60)

    for dpg_file, target_file in DPG_FILE_MAPPING.items():
        if not os.path.exists(dpg_file):
            print(f"⚠️  DPG文件不存在，跳过: {dpg_file}")
            continue

        if dpg_file == target_file:
            # 文件名相同，不需要替换
            print(f"ℹ️  保持不变: {dpg_file}")
            continue

        if dry_run:
            print(f"[DRY RUN] 将替换: {target_file} <- {dpg_file}")
        else:
            try:
                # 如果目标文件存在，先删除（因为已经备份了）
                if os.path.exists(target_file):
                    os.remove(target_file)

                # 复制DPG文件到目标位置
                shutil.copy2(dpg_file, target_file)
                print(f"✓ 已替换: {target_file} <- {dpg_file}")
            except Exception as e:
                print(f"❌ 替换失败 {dpg_file} -> {target_file}: {e}")

    print()


def create_rollback_script(dry_run=False):
    """
    创建回滚脚本，以便需要时恢复Tkinter版本

    Args:
        dry_run: 如果True，只打印操作不实际执行
    """
    print("=" * 60)
    print("步骤 3: 创建回滚脚本")
    print("=" * 60)

    rollback_script = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
DPG to Tkinter Rollback Script
恢复Tkinter版本

This script restores all Tkinter files from *_tk.py backups.

Usage:
    python rollback_to_tkinter.py
\"\"\"

import os
import shutil

BACKUP_FILES = [
"""

    for file in TKINTER_FILES:
        backup_name = file.replace(".py", "_tk.py")
        rollback_script += f'    ("{backup_name}", "{file}"),\n'

    rollback_script += """]

def rollback():
    print("=" * 60)
    print("恢复Tkinter版本")
    print("=" * 60)

    for backup_file, original_file in BACKUP_FILES:
        if not os.path.exists(backup_file):
            print(f"⚠️  备份文件不存在，跳过: {backup_file}")
            continue

        try:
            shutil.copy2(backup_file, original_file)
            print(f"✓ 已恢复: {original_file} <- {backup_file}")
        except Exception as e:
            print(f"❌ 恢复失败 {backup_file} -> {original_file}: {e}")

    print()
    print("✅ 回滚完成！")
    print("现在可以运行Tkinter版本: python main.py")

if __name__ == "__main__":
    rollback()
"""

    if dry_run:
        print("[DRY RUN] 将创建回滚脚本: rollback_to_tkinter.py")
    else:
        try:
            with open("rollback_to_tkinter.py", "w", encoding="utf-8") as f:
                f.write(rollback_script)

            # 在Unix系统上设置执行权限
            try:
                os.chmod("rollback_to_tkinter.py", 0o755)
            except:
                pass

            print("✓ 已创建回滚脚本: rollback_to_tkinter.py")
        except Exception as e:
            print(f"❌ 创建回滚脚本失败: {e}")

    print()


def verify_dpg_installation():
    """验证DPG是否已安装"""
    print("=" * 60)
    print("步骤 0: 验证DPG安装")
    print("=" * 60)

    try:
        import dearpygui.dearpygui as dpg
        print("✓ Dear PyGui 已安装")
        print(f"  版本: {dpg.get_dearpygui_version()}")
    except ImportError:
        print("❌ Dear PyGui 未安装!")
        print("   请运行: pip install dearpygui")
        return False

    print()
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Tkinter到DPG迁移脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示将要执行的操作，不实际执行"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  Tkinter -> DPG 迁移脚本")
    print("=" * 60)
    print()

    if args.dry_run:
        print("⚠️  DRY RUN 模式 - 不会执行实际操作\n")

    # 验证DPG是否安装
    if not verify_dpg_installation():
        return

    # 1. 备份Tkinter文件
    backup_tkinter_files(args.dry_run)

    # 2. 替换为DPG版本
    replace_with_dpg_files(args.dry_run)

    # 3. 创建回滚脚本
    create_rollback_script(args.dry_run)

    # 完成
    print("=" * 60)
    if args.dry_run:
        print("✅ DRY RUN 完成！")
        print()
        print("如果确认无误，请运行:")
        print("    python migrate_to_dpg.py")
    else:
        print("✅ 迁移完成！")
        print()
        print("下一步:")
        print("  1. 运行DPG版本: python main.py")
        print("  2. 如需回滚: python rollback_to_tkinter.py")
        print()
        print("注意: Tkinter备份文件保存为 *_tk.py")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()