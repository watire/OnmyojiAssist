# OnmyojiAssist 代码库概要

## 目录
- [1. 项目概览](#1-项目概览)
- [2. 目录结构与模块职责](#2-目录结构与模块职责)
  - [2.1 顶层目录树](#21-顶层目录树)
  - [2.2 关键模块说明](#22-关键模块说明)
- [3. 运行与构建方式](#3-运行与构建方式)
- [4. 技术栈与第三方依赖](#4-技术栈与第三方依赖)
- [5. 数据流与系统边界](#5-数据流与系统边界)
- [6. 质量保障与工程实践](#6-质量保障与工程实践)
- [7. 文档与可维护性评估](#7-文档与可维护性评估)
- [8. 后续开发建议](#8-后续开发建议)

## 1. 项目概览
OnmyojiAssist 是一个在 Windows 平台运行的桌面自动化工具，通过 PyQt5 提供图形界面，结合 OpenCV 图像识别与 Win32 API 控制，实现《阴阳师》游戏的御魂周回与结界卡合成功能。应用支持多实例并发，使用多线程驱动多个游戏窗口，提供任务计数、完成后退出游戏/关机等附加操作。

## 2. 目录结构与模块职责

### 2.1 顶层目录树
```text
.
├── main.py                  # Qt 应用入口，加载窗口并启动事件循环
├── OnmyojiAssist.py         # 主界面逻辑，负责线程管理与 UI 交互
├── OnmyojiThread.py         # 业务线程，封装御魂与结界卡自动化流程
├── game_window.py           # Win32 截图与模板匹配工具函数
├── game_control.py          # Win32 输入控制封装（点击行为）
├── game_helper.py           # 常量、日志、保持唤醒、消息框等辅助方法
├── MyHelper.py              # 早期版本的辅助工具（基本已被 game_helper 取代）
├── ui_onmyoji_assist.py     # 由 Qt Designer 生成的 UI Python 文件
├── ui_onmyoji_assist.ui     # Qt Designer 源文件
├── pyinstaller.py           # 打包脚本，使用 PyInstaller 生成可执行文件
├── img/                     # 模板图片资源，用于界面元素识别
├── yys.ico                  # 应用图标
└── docs/
    └── CODEBASE_SUMMARY.md  # 本文档
```

### 2.2 关键模块说明
- **`main.py`**
  - 调用 `init_logger()` 配置日志输出到终端与 UI。
  - 创建 `QApplication` 与主窗口 `OnmyojiAssist`，设置图标并进入 Qt 事件循环。
  - 是整个应用的唯一入口，被 PyInstaller 用于打包。

- **`OnmyojiAssist.OnmyojiAssist`（QWidget 子类）**
  - 负责加载 `ui_onmyoji_assist` 生成的界面组件，绑定按钮、复选框与单选框事件。
  - `detect_onmyoji_windows()` 枚举游戏窗口，调整分辨率，实例化 `OnmyojiThread` 并保持引用。
  - 提供开始、停止、通关后停止等控件逻辑；在所有线程完成后重置 UI 状态，必要时触发倒计时消息框（关机/退出游戏）。
  - 通过 `stop_signal`（`pyqtSignal(int)`）跨线程通知停止某个子线程。

- **`OnmyojiThread.OnmyojiThread`（`threading.Thread` 子类）**
  - 定义 `WorkType`、`Role` 枚举区分任务类型（御魂/结界卡）与角色（司机/队员）。
  - 根据工作类型执行主循环：
    - 御魂：角色识别 → 进场 → 战斗等待 → 结算处理 → 重新组队。
    - 结界卡：合成流程 → 结果判定 → 物料补充。
  - 大量使用 `game_window.find_image()`、`game_control.click()` 与 `random_sleep()` 完成图像识别与自动点击。
  - 借助线程锁在同一时刻序列化截图与点击，避免多个线程操作同一窗口导致冲突。
  - 当计数达到目标或检测到异常时通过 `QuitThread` 异常退出并发出 `stop_signal`。

- **`game_window.py`**
  - 基于 `pywin32` 对窗口句柄进行枚举、截图与移动。
  - 使用 OpenCV (`cv2.matchTemplate`) 做模板匹配，返回匹配度及坐标，用于后续点击。
  - 封装 `screen_shot` 支持局部截图，可保存文件或返回 Numpy 数组。

- **`game_control.py`**
  - 使用 `win32api.SendMessage` 与 `WM_LBUTTONDOWN/UP` 模拟窗口点击。
  - 随机化点击位置与延迟，降低被检测概率。

- **`game_helper.py`**
  - 定义 UI 元素坐标常量、匹配区域、日志配置、保持系统唤醒、倒计时消息框、`XStream`（将 stdout/stderr 重定向到 Qt 文本框）。
  - 是多个模块共享的工具集合。

- **`ui_onmyoji_assist.py` / `ui_onmyoji_assist.ui`**
  - Qt Designer 导出的界面定义，包含所有控件与布局。Python 文件由 `pyuic5` 生成，不建议直接修改。

- **`pyinstaller.py`**
  - 使用 `PyInstaller.__main__.run` 以单文件、无控制台窗口模式打包，输出名为“阴阳师自动”的可执行文件。

- **`MyHelper.py`**
  - 旧版工具集合，与 `game_helper.py` 大量重复；当前主流程未引用，可视为技术债。

- **`img/` 模板库**
  - 存放各类 UI 元素截图（如准备按钮、胜利/失败、悬赏提醒等），被 `OnmyojiThread` 通过相对路径加载。

## 3. 运行与构建方式
- **系统要求**：
  - Windows 10/11，需安装《阴阳师》客户端，并允许窗口化运行。
  - 由于 `time.clock()` 已在 Python 3.8 废弃，建议使用 Python 3.7.x 环境，或在后续重构中替换该 API。
- **依赖安装**：项目提供 `requirements.txt` 列出核心依赖，可按如下步骤安装环境：
  ```bash
  python -m venv .venv
  .\.venv\Scripts\activate  # Windows PowerShell/cmd
  pip install --upgrade pip
  pip install -r requirements.txt
  ```
  - 其中 PyInstaller 仅在打包阶段需要，普通运行可选安装。
- **运行步骤**：
  1. 启动并登录游戏客户端，将目标窗口切换为“阴阳师-网易游戏”，保持前台或后台均可。
  2. 在虚拟环境中执行 `python main.py`。
  3. 在 GUI 中选择模式（御魂/结界卡）、配置计数与结束行为，点击“开始”。
- **打包方式**：
  - 执行 `python pyinstaller.py`，生成单文件可执行程序，包含自定义图标（`yys.ico`）。
  - 请在打包前确保依赖与资源文件 `img/` 同目录分发。

## 4. 技术栈与第三方依赖
| 组件 | 版本建议 | 用途 | 兼容性/风险 |
| --- | --- | --- | --- |
| Python | 3.7.x | 运行时环境 | 代码使用 `time.clock()`，与 3.8+ 不兼容 |
| PyQt5 | ≥5.15 | GUI 构建、事件循环、信号槽 | 需与 Qt Designer 版本匹配 |
| pywin32 (`win32gui`, `win32api`, `win32con`, `win32ui`) | 223+ | 窗口枚举、截图、输入模拟 | Windows 平台限定，需管理员权限执行部分操作 |
| opencv-python | ≥4.5 | 模板匹配、图像处理 | 体积较大，需与 numpy 版本兼容 |
| numpy | ≥1.19 | OpenCV 数据结构依赖 | 与 opencv-python 耦合 |
| PyInstaller | ≥5.0 | 打包发布 | 默认打包为单文件，注意资源路径 |

## 5. 数据流与系统边界
1. **入口与初始化**：`main.py` → 初始化日志 → 创建 `OnmyojiAssist` GUI。
2. **用户交互**：用户在 GUI 中设置模式、计数与结束策略，点击“开始”。
3. **窗口检测**：`OnmyojiAssist.detect_onmyoji_windows()` 枚举匹配标题的游戏窗口，为每个窗口创建线程并共享锁。
4. **任务执行**：`OnmyojiThread.run()` 根据 `WorkType` 进入不同循环：
   - 屏幕截图 → 模板匹配 → 计算点击区域。
   - 通过 `game_control.click()` 发送鼠标消息。
   - `random_sleep()` 注入随机等待，降低模式化行为。
5. **日志输出**：日志通过 `logging` 模块同时写入终端与 GUI 文本框（`XStream`）。
6. **停止逻辑**：达到计数/检测异常时调用 `stop_signal` 通知主线程更新 UI，并选择性执行关机/退出游戏（调用 `os.system` 与 `ctypes`）。
7. **外部边界**：
   - 与《阴阳师》客户端交互完全通过 Windows 消息与截图实现，无直接 API。
   - `os.system('shutdown /s /t 5')` 与 `taskkill /f /im onmyoji.exe` 存在副作用，需谨慎启用。

## 6. 质量保障与工程实践
- **测试**：未提供任何自动化测试、模拟或集成验证。
- **静态检查**：无 lint/format 配置；存在 PEP 8 风格与命名不统一等问题。
- **CI/CD**：仓库中未发现持续集成配置（如 GitHub Actions、GitLab CI）。
- **错误处理**：主要通过日志记录与线程退出完成，缺乏统一的异常兜底机制。

## 7. 文档与可维护性评估
- **README**：原有内容极少，缺乏安装、运行、开发指引（已在本次任务中补充）。
- **注释**：核心逻辑拥有适量中文注释/日志，但函数 docstring 较少，且存在部分硬编码常量。
- **技术债**：
  - `time.clock()` 已废弃，影响 Python 3.8+ 兼容。
  - `MyHelper.py` 与 `game_helper.py` 功能重复，需要合并或删除。
  - `detect_onmyoji_windows()` 中窗口高度判断写法疑似错误（`window_rect[3] - window_rect[0]` 应为 `window_rect[3] - window_rect[1]`）。
  - 缺少依赖清单与配置化路径，部署成本高。

## 8. 后续开发建议
| 建议 | 优先级 | 预估体量 | 影响范围 | 说明 |
| --- | --- | --- | --- | --- |
| 替换废弃 API 并适配 Python 3.8+ | 高 | 中 | 全局运行时 | 将 `time.clock()` 替换为 `time.perf_counter()`/`time.monotonic()`，并在新版 Python 环境下补充兼容性测试。 |
| 梳理辅助模块与配置管理 | 中 | 中 | 工程结构 | 合并 `MyHelper.py` 与 `game_helper.py`，抽离常量到独立配置/JSON，并支持自定义资源路径。 |
| 引入自动化测试与 CI | 中 | 大 | 质量保障 | 使用 mock 截图与虚拟窗口搭建最小单元测试，配置 GitHub Actions/pytest，提高回归效率。 |
| 优化线程同步与异常处理 | 中 | 中 | 稳定性 | 将线程锁与资源访问封装为上下文管理器，确保异常时释放资源并避免 GUI 阻塞。 |
| 编写使用文档与操作指南 | 低 | 小 | 用户支持 | 为不同模式补充图文教程与常见问题，减少使用门槛。 |
