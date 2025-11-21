# HDF5 批量积分脚本使用说明（增强版）

## 新增功能

### 1. 灵活的多格式输出支持

脚本支持6种输出格式，**可根据需求自由选择**任意组合：

| 格式 | 类型 | 用途 | 文件大小 |
|------|------|------|---------|
| **`.xy`** | 数据文件 | 最常用的两列数据格式 | 小 |
| **`.dat`** | 数据文件 | 与XY格式相同 | 小 |
| **`.chi`** | 数据文件 | GSAS-II精修软件兼容 | 小 |
| **`.fxye`** | 数据文件 | GSAS精修软件兼容（含误差） | 中 |
| **`.svg`** | 矢量图 | 可无限缩放的图形 | 中 |
| **`.png`** | 位图 | 高分辨率图片（300 DPI） | 大 |

**注意**：可以只选择需要的格式，不必全部输出，节省磁盘空间和处理时间

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

# 根据需求选择输出格式
run_batch_integration(
    poni_file='path/to/calibration.poni',
    mask_file='path/to/mask.edf',
    input_pattern='path/to/data/*.h5',
    output_dir='path/to/output',
    formats=['xy', 'dat'],  # 选择需要的格式
    create_stacked_plot=True,  # 生成堆叠图
    stacked_plot_offset='auto'  # 自动计算偏移
)
```

### 格式选择快速指南

**如何选择合适的输出格式？**

```
┌─ 需要什么？
│
├─ 只需要原始数据 → formats = ['xy']  ⭐ 推荐
│  最常用，文件小，处理快
│
├─ 需要用GSAS软件精修 → formats = ['chi', 'fxye']
│  GSAS-II用chi，GSAS用fxye
│
├─ 需要图形展示 → formats = ['xy', 'png']
│  数据+图片，适合报告
│
├─ 需要发表论文 → formats = ['xy', 'svg']
│  数据+矢量图，可编辑
│
├─ 需要完整备份 → formats = ['xy', 'dat', 'chi', 'fxye']
│  所有数据格式
│
└─ 需要全部功能 → formats = ['xy', 'dat', 'chi', 'fxye', 'svg', 'png']
   完整输出，占用空间大
```

### 常用配置方案

```python
# 方案1: 基础分析（⭐ 推荐）
formats = ['xy', 'dat']

# 方案2: 最精简（最节省空间）
formats = ['xy']

# 方案3: 数据+预览
formats = ['xy', 'png']

# 方案4: GSAS精修
formats = ['chi', 'fxye']

# 方案5: 发表论文
formats = ['xy', 'svg']

# 方案6: 完整输出（占用空间大）
formats = ['xy', 'dat', 'chi', 'fxye', 'svg', 'png']
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

### 1. 选择特定格式组合

```python
# 示例：仅输出XY和PNG（数据+图片）
run_batch_integration(
    poni_file='...',
    mask_file='...',
    input_pattern='...',
    output_dir='...',
    formats=['xy', 'png'],  # 自由选择需要的格式
    create_stacked_plot=True
)
```

### 2. 手动设置堆叠图偏移量

```python
# 示例：固定偏移值
run_batch_integration(
    ...,
    formats=['xy'],
    create_stacked_plot=True,
    stacked_plot_offset=5000  # 手动设置固定偏移为5000
)
```

### 3. 禁用堆叠图生成

```python
# 示例：仅积分，不生成堆叠图
run_batch_integration(
    ...,
    formats=['xy', 'dat'],
    create_stacked_plot=False  # 禁用堆叠图
)
```

### 4. 单一格式输出

```python
# 示例：只输出XY格式（最节省）
run_batch_integration(
    ...,
    formats=['xy'],  # 仅一种格式
    create_stacked_plot=True
)
```

## 注意事项

### 1. 依赖包
确保安装了 `matplotlib`：
```bash
pip install matplotlib
```

### 2. 格式选择建议
- **日常使用**：推荐 `formats = ['xy']` 或 `['xy', 'dat']`
- **磁盘空间有限**：仅使用 `formats = ['xy']`
- **大批量处理**：避免使用 PNG/SVG 格式（文件大）
- **精修分析**：使用 `formats = ['chi', 'fxye']`

### 3. 文件大小参考
以100个文件为例（每个2000点积分）：
- XY格式：约50 KB/文件 → 总计 5 MB
- PNG格式：约200 KB/文件 → 总计 20 MB
- 所有格式：约500 KB/文件 → 总计 50 MB

### 4. 压力识别
如果文件名不包含压力信息，所有文件压力值将为0，但仍会生成堆叠图

### 5. 内存使用
堆叠图生成需要加载所有数据到内存，超大数据集（>1000文件）可能需要调整

## 常见问题

### Q1: 如何选择合适的输出格式？
**A**:
- 仅需数据分析 → `formats = ['xy']`
- 需要精修软件 → `formats = ['chi', 'fxye']`
- 需要图形展示 → `formats = ['xy', 'png']`
- 发表论文使用 → `formats = ['xy', 'svg']`

### Q2: 可以只输出一种格式吗？
**A**: 可以！只需设置 `formats = ['xy']` 或任意单一格式

### Q3: 输出所有格式会很慢吗？
**A**: 会稍慢，且占用磁盘空间大。建议根据实际需求选择格式

### Q4: XY和DAT格式有什么区别？
**A**: 完全相同，只是扩展名不同。某些软件习惯用.dat扩展名

### Q5: 堆叠图颜色不明显？
**A**: 可以修改 `create_stacked_plot` 方法中的 `alpha` 参数来调整透明度

### Q6: 压力标签位置不合适？
**A**: 可以调整 `x_pos` 和 `y_pos` 的计算公式

### Q7: 需要更多颜色？
**A**: 可以使用其他colormap，如 `plt.cm.tab20` (20种颜色)

## 技术支持

如有问题，请检查：
1. pyFAI版本是否兼容
2. 文件路径是否正确
3. HDF5文件格式是否符合要求
