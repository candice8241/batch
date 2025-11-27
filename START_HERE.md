# 🚀 XRD GUI - 快速启动指南

## ⚠️ 当前问题诊断

您遇到的 **"打不开UI界面"** 问题是因为：

### 🔍 问题原因
1. **缺少图形界面支持** - 当前是远程无头(headless)环境
2. **缺少部分依赖包** - 需要安装 numpy 等科学计算库

---

## ✅ 解决方案（按推荐顺序）

### 方案 1：在本地计算机运行 ⭐ 推荐

**这是最简单的方法！**

1. **下载所有文件到本地**
   - 将整个 `/workspace` 目录复制到您的本地计算机

2. **安装依赖**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python3 main_dpg.py
   ```

---

### 方案 2：使用 X11 转发（远程服务器）

如果您必须在远程服务器上运行：

#### 在 Linux/Mac 客户端：
```bash
# 1. 使用 X11 转发连接
ssh -X username@server

# 2. 检查显示是否正常
echo $DISPLAY  # 应该显示类似 "localhost:10.0"

# 3. 安装依赖
pip3 install -r requirements.txt

# 4. 运行程序
python3 main_dpg.py
```

#### 在 Windows 客户端：
```bash
# 1. 安装 X Server
下载并安装 VcXsrv: https://sourceforge.net/projects/vcxsrv/

# 2. 启动 VcXsrv (使用默认设置)

# 3. 使用 PuTTY 连接，启用 X11 转发：
#    Connection -> SSH -> X11 -> Enable X11 forwarding ✓

# 4. 在服务器上安装依赖并运行
pip3 install -r requirements.txt
python3 main_dpg.py
```

---

### 方案 3：Windows WSL 用户

如果您使用 Windows WSL：

```bash
# 1. 在 Windows 上安装 VcXsrv
# 下载: https://sourceforge.net/projects/vcxsrv/

# 2. 启动 VcXsrv，配置：
#    - Multiple windows
#    - Display number: 0  
#    - ✓ Disable access control

# 3. 在 WSL 终端设置显示
export DISPLAY=:0

# 4. 安装依赖
pip3 install -r requirements.txt

# 5. 运行程序
python3 main_dpg.py
```

---

## 🛠️ 安装所有依赖

在任何环境中，首先运行：

```bash
pip3 install -r requirements.txt
```

这会安装：
- ✅ dearpygui (GUI框架)
- ✅ numpy, pandas, scipy (科学计算)
- ✅ pyFAI, h5py (XRD数据处理)
- ✅ matplotlib (绘图)

---

## 🔍 环境检查工具

我已创建了自动诊断工具：

```bash
python3 check_environment.py
```

这个工具会：
- ✓ 检查 Python 版本
- ✓ 检查图形界面支持
- ✓ 检查所有依赖包
- ✓ 提供具体解决方案

---

## 📝 验证安装

安装完成后测试：

```bash
# 1. 检查环境
python3 check_environment.py

# 2. 如果所有检查通过，运行主程序
python3 main_dpg.py

# 3. 或使用启动脚本（Linux/Mac）
./run_gui.sh
```

---

## 🎯 应该看到什么

程序成功运行时，您会看到：

1. **启动画面** (2-3秒)
   - 加载进度条
   - "Starting up, please wait..."

2. **主界面** 
   - 标题：XRD Data Post-Processing
   - 三个标签页：
     - Powder XRD (粉末衍射)
     - Single Crystal XRD (单晶衍射)
     - Radial XRD (径向积分)

---

## ❌ 常见错误及解决

### 错误 1: "No module named 'dearpygui'"
```bash
pip3 install dearpygui
```

### 错误 2: "cannot connect to X server"
您在无头环境中。参考上面的"方案2"或"方案3"

### 错误 3: "No module named 'numpy'"
```bash
pip3 install -r requirements.txt
```

### 错误 4: 程序启动但窗口是黑色的
检查 X11 转发是否正确：
```bash
echo $DISPLAY  # 必须有输出
xclock         # 测试 X11（应显示时钟）
```

---

## 📂 创建的辅助文件

我已经创建了以下文件帮助您：

| 文件 | 用途 |
|------|------|
| `requirements.txt` | 所有依赖包列表 |
| `check_environment.py` | 自动诊断工具 |
| `run_gui.sh` | 启动脚本（Linux/Mac） |
| `INSTALLATION_GUIDE.md` | 详细安装指南（英文） |
| `START_HERE.md` | 本文件（中文快速指南） |

---

## 💡 推荐流程

```
1. 运行诊断工具
   → python3 check_environment.py

2. 根据诊断结果：
   
   ├─ 本地机器
   │  └─ pip3 install -r requirements.txt
   │     └─ python3 main_dpg.py ✓
   │
   ├─ 远程服务器  
   │  └─ ssh -X user@server
   │     └─ pip3 install -r requirements.txt
   │        └─ python3 main_dpg.py ✓
   │
   └─ WSL
      └─ 安装 VcXsrv
         └─ export DISPLAY=:0
            └─ pip3 install -r requirements.txt
               └─ python3 main_dpg.py ✓
```

---

## 🆘 仍然有问题？

如果按照上述步骤仍无法运行：

1. **重新运行诊断**
   ```bash
   python3 check_environment.py
   ```

2. **检查基本信息**
   ```bash
   python3 --version    # 应该是 3.7+
   echo $DISPLAY        # 应该有输出
   pip3 list | grep dear  # 应该看到 dearpygui
   ```

3. **查看详细文档**
   ```bash
   cat INSTALLATION_GUIDE.md  # 英文详细指南
   ```

4. **测试单个模块**
   ```bash
   # 测试是否能导入
   python3 -c "import dearpygui; print('OK')"
   ```

---

## 🎉 成功标志

程序成功运行的标志：
- ✅ 看到启动画面
- ✅ 进度条从 0% 到 100%
- ✅ 主窗口打开，显示三个标签页
- ✅ 可以点击不同标签页切换
- ✅ 每个模块显示完整界面

---

**祝您使用愉快！如有问题，请先运行 `check_environment.py` 查看具体原因。** 🚀
