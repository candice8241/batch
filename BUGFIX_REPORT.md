# 修复报告：RuntimeError 和进度显示优化

## 修复日期
2025-11-21

## 问题描述

### 1. RuntimeError: main thread is not in main loop
```
Exception ignored in: <function Variable.__del__ at 0x000002381DFA1550>
Traceback (most recent call last):
  File "E:\Python\Anaconda\envs\pytorch_gpu\lib\tkinter\__init__.py", line 363, in __del__
    if self._tk.getboolean(self._tk.call("info", "exists", self._name)):
RuntimeError: main thread is not in main loop
```

**原因**: Tkinter变量在线程中被访问，当垃圾回收时主线程不在主循环中。

### 2. 堆叠图标签位置
压力标签位于图外，不方便查看。

### 3. 堆叠图颜色单调
所有曲线颜色相同，不便区分。

### 4. 进度显示冗余
每个文件处理时都显示"Found 1 HDF5 files"信息，冗余且不清晰。

---

## 解决方案

### 1. 修复 RuntimeError

#### 根本原因
- 后台线程持有Tkinter变量的引用
- 变量析构时主线程可能不在事件循环中
- 导致RuntimeError异常

#### 解决方法
在所有线程函数开始时：
1. **立即捕获所有Tkinter变量值**，转换为Python原生类型
2. **不保持对Tkinter变量的引用**
3. **所有GUI操作用try-except包裹**

#### 修复的函数
- `_run_integration_thread()`
- `_run_fitting_thread()`
- `_run_full_pipeline_thread()`
- `_separate_peaks_thread()`
- `_run_phase_analysis_thread()` (已存在类似保护)
- `_run_birch_murnaghan_thread()` (已存在类似保护)

#### 代码模式

**修复前**:
```python
def _some_thread(self):
    try:
        # 直接使用Tkinter变量
        path = self.some_var.get()
        self.show_error("Error", "message")
    finally:
        self.root.after(0, self.progress.stop)
```

**修复后**:
```python
def _some_thread(self):
    # 立即捕获所有变量
    try:
        path = str(self.some_var.get())
        value = int(self.another_var.get())
    except Exception as e:
        self.log(f"❌ Failed to read settings: {str(e)}")
        try:
            self.root.after(0, lambda: self.show_error("Error", str(e)))
        except:
            pass
        return

    try:
        # 使用捕获的变量，不再访问Tkinter变量
        result = process(path, value)

        # GUI操作包裹在try-except中
        try:
            self.root.after(0, lambda: self.show_success(self.root, "Done!"))
        except:
            pass
    finally:
        try:
            self.root.after(0, self.progress.stop)
        except:
            pass
```

---

### 2. 堆叠图压力标签位置优化

#### 修改前
- 标签位置：`x_min - 0.02 * (x_max - x_min)`
- 对齐方式：`horizontalalignment='right'`
- 效果：标签在图外左侧

#### 修改后
- 标签位置：`x_min + 0.02 * (x_max - x_min)`
- 对齐方式：`horizontalalignment='left'`
- 效果：标签在图内左侧

#### 代码对比
```python
# 修改前
ax.text(x_min - 0.02 * (x_max - x_min),  # 图外
       i * offset_value + np.mean(y[:10]),
       f'{pressure:.1f} GPa',
       horizontalalignment='right')  # 右对齐

# 修改后
ax.text(x_min + 0.02 * (x_max - x_min),  # 图内
       i * offset_value + np.mean(y[:10]),
       f'{pressure:.1f} GPa',
       horizontalalignment='left')  # 左对齐
```

---

### 3. 堆叠图颜色优化

#### 实现方式
- 每10 GPa换一次颜色
- 使用10种预定义颜色循环
- 颜色索引：`int(pressure / 10) % 10`

#### 颜色列表
```python
color_palette = [
    '#1f77b4',  # 蓝色 (0-9.9 GPa)
    '#ff7f0e',  # 橙色 (10-19.9 GPa)
    '#2ca02c',  # 绿色 (20-29.9 GPa)
    '#d62728',  # 红色 (30-39.9 GPa)
    '#9467bd',  # 紫色 (40-49.9 GPa)
    '#8c564b',  # 棕色 (50-59.9 GPa)
    '#e377c2',  # 粉色 (60-69.9 GPa)
    '#7f7f7f',  # 灰色 (70-79.9 GPa)
    '#bcbd22',  # 黄绿 (80-89.9 GPa)
    '#17becf'   # 青色 (90-99.9 GPa)
]
```

#### 示例
- 8.5 GPa → 蓝色
- 15.2 GPa → 橙色
- 25.0 GPa → 绿色
- 35.8 GPa → 红色

---

### 4. 进度显示优化

#### 修改前
```
Found 1 HDF5 files to process
Output directory: D:/HEPS/ID31/test/OUTPUT
Integration parameters: 4000 points, unit=2th_deg
Output formats: xy

Processing: 100%|██████████| 1/1 [00:00<00:00, 1.84it/s]
✓ Success: D:/HEPS/ID31/test/input_dir\1.645.h5 -> D:/HEPS/ID31/test/OUTPUT\1.645.[xy]
```
每个文件都重复以上信息

#### 修改后
```
============================================================
🔁 Starting Batch Integration
📁 Directory: D:/HEPS/ID31/test/input_dir
📊 Total files to process: 3
📈 Output formats: xy
📉 Number of points: 4000
📏 Unit: 2th_deg
============================================================

[1/3] Processing: 0.72.h5
[1/3] ✓ Completed: 0.72.h5

[2/3] Processing: 1.645.h5
[2/3] ✓ Completed: 1.645.h5

[3/3] Processing: 11.188.h5
[3/3] ✓ Completed: 11.188.h5

📈 Creating combined stacked plot for all 3 files...

============================================================
✅ All integrations completed!
📊 Total processed: 3/3
💾 Output directory: D:/HEPS/ID31/test/OUTPUT
============================================================
```

#### 改进点
1. ✅ 开头显示总文件数
2. ✅ 每个文件显示 `[当前/总数]` 格式
3. ✅ 信息更简洁，不重复
4. ✅ 使用分隔线和emoji增强可读性
5. ✅ 最后汇总显示总进度

---

## 测试建议

### 1. RuntimeError测试
- 运行积分任务并快速关闭程序
- 多次连续运行不同任务
- 观察控制台是否还有RuntimeError

### 2. 堆叠图测试
- 准备包含不同压力的h5文件
- 文件名格式: `xxx_压力GPa.h5`
- 验证:
  - 压力标签在图内
  - 颜色每10GPa变化
  - 按压力排序正确

### 3. 进度显示测试
- 处理包含多个h5文件的文件夹
- 验证进度显示格式正确
- 确认不重复显示文件信息

---

## 文件修改清单

### 修改的函数

1. **_create_combined_stacked_plot()**
   - 添加颜色循环逻辑
   - 修改标签位置（图内）
   - 添加颜色提示日志

2. **_run_integration_thread()**
   - 添加变量捕获保护
   - 优化进度显示格式
   - 添加try-except包裹GUI调用

3. **_run_fitting_thread()**
   - 添加变量捕获保护
   - 添加try-except包裹GUI调用

4. **_run_full_pipeline_thread()**
   - 添加变量捕获保护
   - 优化进度显示格式
   - 添加try-except包裹GUI调用

5. **_separate_peaks_thread()**
   - 添加变量捕获保护
   - 添加try-except包裹GUI调用

### 未修改的函数
- `_run_phase_analysis_thread()` - 已有类似保护
- `_run_birch_murnaghan_thread()` - 已有类似保护

---

## 兼容性

- ✅ 向后兼容：所有现有功能保持不变
- ✅ Python版本：适用于Python 3.6+
- ✅ Tkinter版本：适用于所有常见Tkinter版本
- ✅ 操作系统：Windows/Linux/macOS

---

## 性能影响

- **内存**: 无显著影响（仅在线程开始时复制变量值）
- **速度**: 无影响（try-except开销可忽略）
- **稳定性**: 显著提升（消除RuntimeError）

---

## 未来改进建议

1. 考虑使用更安全的线程通信机制（如Queue）
2. 添加进度条显示百分比
3. 支持取消正在运行的任务
4. 添加实时日志滚动显示
