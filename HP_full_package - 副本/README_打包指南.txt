==============================================================================
                    XRD数据后处理应用程序 - 打包指南
==============================================================================

📦 快速开始 - 三种打包方式
==============================================================================

方式一：【最简单】一键打包脚本
------------------------------------------------------------------------------
Windows系统：
  双击运行 → 快速打包.bat

Linux/Mac系统：
  终端执行 → ./快速打包.sh

方式二：【自动化】标准打包脚本
------------------------------------------------------------------------------
Windows系统：
  双击运行 → build.bat

Linux/Mac系统：
  终端执行 → ./build.sh

方式三：【手动】命令行打包
------------------------------------------------------------------------------
1. 安装依赖：
   pip install -r requirements_gui.txt

2. 执行打包：
   pyinstaller --clean xrd_app.spec

3. 查看结果：
   Windows: dist\XRD_PostProcessing\XRD_PostProcessing.exe
   Linux/Mac: dist/XRD_PostProcessing/XRD_PostProcessing

==============================================================================

📋 所有文件清单
==============================================================================

【核心程序文件】
  main.py                      - 主程序入口
  theme_module.py              - UI主题和组件
  gui_base.py                  - GUI基础类

【功能模块】
  powder_module.py             - 粉末XRD处理
  radial_module.py             - 径向积分处理
  single_crystal_module.py     - 单晶XRD处理
  batch_integration.py         - 批量HDF5积分
  batch_cal_volume.py          - 体积计算分析
  peak_fitting.py              - 峰拟合
  half_auto_fitting.py         - 半自动拟合
  birch_murnaghan_batch.py     - BM方程拟合
  batch_appearance.py          - 批处理UI

【打包配置文件】✨
  xrd_app.spec                 - PyInstaller配置（核心）
  pyi_rth_pyFAI.py            - pyFAI运行时钩子
  requirements_gui.txt         - Python依赖列表

【打包脚本】✨
  快速打包.bat                 - Windows快速打包（推荐）
  快速打包.sh                  - Linux/Mac快速打包（推荐）
  build.bat                    - Windows标准打包
  build.sh                     - Linux/Mac标准打包

【资源文件】
  ChatGPT Image.ico            - 应用图标
  ChatGPT Image.png            - 应用图片

【文档】
  生成EXE说明.md               - 详细打包文档
  README_打包指南.txt          - 本文件（快速指南）

==============================================================================

🔧 打包前准备
==============================================================================

1. 确保Python版本 >= 3.8
   检查命令：python --version  或  python3 --version

2. 确保pip已安装
   检查命令：pip --version  或  pip3 --version

3. 【可选】配置国内镜像源（加速安装）
   pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

==============================================================================

💡 常见问题快速解决
==============================================================================

问题1：打包失败，提示找不到某个模块
解决：pip install 模块名

问题2：pyFAI安装失败
解决：pip install pyFAI --no-binary pyFAI

问题3：打包后运行报错缺少DLL（Windows）
解决：安装 Visual C++ Redistributable
      https://aka.ms/vs/17/release/vc_redist.x64.exe

问题4：Linux下缺少tkinter
解决（Ubuntu）：sudo apt-get install python3-tk
解决（CentOS）：sudo yum install python3-tkinter

问题5：打包文件太大（超过500MB）
解决：编辑 xrd_app.spec，在excludes部分添加不需要的模块

问题6：Mac系统权限问题
解决：chmod +x 快速打包.sh
      chmod +x dist/XRD_PostProcessing/XRD_PostProcessing

==============================================================================

📊 打包后文件结构
==============================================================================

dist/
└── XRD_PostProcessing/              ← 这就是可分发的完整应用
    ├── XRD_PostProcessing.exe       ← 可执行文件（Windows）
    ├── XRD_PostProcessing           ← 可执行文件（Linux/Mac）
    ├── _internal/                   ← 依赖库（不要删除）
    │   ├── numpy/
    │   ├── scipy/
    │   ├── matplotlib/
    │   └── ... (其他依赖)
    ├── ChatGPT Image.ico
    └── ChatGPT Image.png

使用方法：
  - 将整个 XRD_PostProcessing 文件夹复制到任何电脑
  - 双击可执行文件即可运行（无需安装Python）

==============================================================================

🎯 验证打包是否成功
==============================================================================

Windows：
  1. 进入 dist\XRD_PostProcessing 文件夹
  2. 双击 XRD_PostProcessing.exe
  3. 如果GUI正常启动，说明打包成功 ✓

Linux/Mac：
  1. 打开终端
  2. cd dist/XRD_PostProcessing
  3. ./XRD_PostProcessing
  4. 如果GUI正常启动，说明打包成功 ✓

==============================================================================

📧 技术支持
==============================================================================

如遇到无法解决的问题，请联系：
  - lixd@ihep.ac.cn
  - fzhang@ihep.ac.cn
  - yswang@ihep.ac.cn
  - candicewang928@gmail.com

或查看详细文档：生成EXE说明.md

==============================================================================

✨ 提示：推荐使用"快速打包.bat"或"快速打包.sh"，它会自动处理所有依赖！

==============================================================================
