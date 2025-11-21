# HDF5 批量积分脚本使用说明（增强版）

## 新增功能

### 1. 多格式输出支持

现在脚本支持同时输出多种格式的积分数据文件：

- **`.xy`** - 标准XY格式（两列数据）
- **`.dat`** - DAT格式（与XY格式相同）
- **`.chi`** - GSAS-II兼容格式
- **`.fxye`** - GSAS兼容格式（包含误差估计）
- **`.svg`** - 矢量图格式（可缩放）
- **`.png`** - 位图格式（高分辨率 300 DPI）

### 2. 堆叠图自动生成

脚本会自动生成压力堆叠图，具有以下特点：

- **按压力排序**：从低压到高压自动排列
- **自动偏移**：根据数据强度自动计算合适的间距
- **压力标签**：每条曲线旁边显示对应的压力值
- **颜色编码**：每10 GPa更换一种颜色
- **双格式输出**：同时生成PNG和SVG格式

## 使用方法

### 基本用法

```python
from batch_integration import run_batch_integration

run_batch_integration(
    poni_file='path/to/calibration.poni',
    mask_file='path/to/mask.edf',
    input_pattern='path/to/data/*.h5',
    output_dir='path/to/output',
    formats=['xy', 'dat', 'chi', 'svg', 'png', 'fxye'],  # 所有格式
    create_stacked_plot=True,  # 生成堆叠图
    stacked_plot_offset='auto'  # 自动计算偏移
)
```

### 参数说明

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `poni_file` | str | 校准文件路径 (.poni) | 必需 |
| `mask_file` | str | 掩膜文件路径 | None |
| `input_pattern` | str | 输入HDF5文件匹配模式 | 必需 |
| `output_dir` | str | 输出目录 | 必需 |
| `dataset_path` | str | HDF5数据集路径 | None (自动检测) |
| `npt` | int | 积分点数 | 2000 |
| `unit` | str | 输出单位 | '2th_deg' |
| `formats` | list | 输出格式列表 | ['xy', 'dat', ...] |
| `create_stacked_plot` | bool | 是否生成堆叠图 | True |
| `stacked_plot_offset` | str/float | 堆叠图偏移量 | 'auto' |

## 文件命名规范（用于压力提取）

为了让脚本正确识别压力值并生成堆叠图，建议文件名包含压力信息：

### 支持的命名格式：

- `10GPa.h5` 或 `10.5GPa.h5`
- `10_GPa.h5` 或 `sample_10_GPa.h5`
- `P10.h5` 或 `p10.5.h5`
- `pressure_10.h5`
- `10.h5`（纯数字开头）

### 示例：

```
1.5GPa.h5   → 压力: 1.5 GPa
5GPa.h5     → 压力: 5.0 GPa
10_GPa.h5   → 压力: 10.0 GPa
P15.h5      → 压力: 15.0 GPa
20.5GPa.h5  → 压力: 20.5 GPa
```

## 输出结果

### 文件结构示例：

```
output_dir/
├── 1.5GPa.xy
├── 1.5GPa.dat
├── 1.5GPa.chi
├── 1.5GPa.fxye
├── 1.5GPa.svg
├── 1.5GPa.png
├── 5GPa.xy
├── 5GPa.dat
├── ...
├── stacked_plot.png      # 堆叠图（PNG）
└── stacked_plot.svg      # 堆叠图（SVG）
```

### 堆叠图特点：

1. **Y轴偏移**：每条曲线自动偏移，避免重叠
2. **压力标签**：左侧显示压力值（带颜色背景框）
3. **颜色变化**：
   - 0-10 GPa: 第一种颜色
   - 10-20 GPa: 第二种颜色
   - 20-30 GPa: 第三种颜色
   - ... 以此类推（共10种颜色循环）

## 自定义选项

### 仅输出特定格式

```python
run_batch_integration(
    ...,
    formats=['xy', 'dat'],  # 仅输出XY和DAT格式
    create_stacked_plot=True
)
```

### 手动设置堆叠图偏移量

```python
run_batch_integration(
    ...,
    create_stacked_plot=True,
    stacked_plot_offset=5000  # 固定偏移5000
)
```

### 不生成堆叠图

```python
run_batch_integration(
    ...,
    create_stacked_plot=False  # 禁用堆叠图
)
```

## 注意事项

1. **依赖包**：确保安装了 `matplotlib`
   ```bash
   pip install matplotlib
   ```

2. **压力识别**：如果文件名不包含压力信息，所有文件压力值将为0，但仍会生成堆叠图

3. **大数据集**：处理大量文件时，建议减少输出格式以节省磁盘空间

4. **内存使用**：堆叠图生成需要加载所有数据到内存，超大数据集可能需要调整

## 常见问题

### Q: 堆叠图颜色不明显？
A: 可以修改 `create_stacked_plot` 方法中的 `alpha` 参数来调整颜色透明度

### Q: 压力标签位置不合适？
A: 可以调整 `x_pos` 和 `y_pos` 的计算公式

### Q: 需要更多颜色？
A: 可以使用其他colormap，如 `plt.cm.tab20` (20种颜色)

## 技术支持

如有问题，请检查：
1. pyFAI版本是否兼容
2. 文件路径是否正确
3. HDF5文件格式是否符合要求
