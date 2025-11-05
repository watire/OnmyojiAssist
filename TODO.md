# TODO 与改进建议

本文档列出 OnmyojiAssist 代码库中的已知问题、技术债与后续改进方向，包含优先级、预估体量与代码定位。

## 目录
- [高优先级 - 运行时兼容性](#高优先级---运行时兼容性)
- [中优先级 - 代码质量](#中优先级---代码质量)
- [中优先级 - 工程化](#中优先级---工程化)
- [低优先级 - 用户体验](#低优先级---用户体验)

---

## 高优先级 - 运行时兼容性

### 1. 替换废弃的 `time.clock()` API

**问题描述**：  
Python 3.8+ 已移除 `time.clock()`，当前代码在新版 Python 环境下无法运行。

**影响范围**：  
- **文件**：`OnmyojiThread.py`
- **受影响代码行**：
  - 第 158 行：`start_time = time.clock()`  
  - 第 170 行：`current_time = time.clock()`  
  - 第 384 行：`start_time = time.clock()`  
  - 第 388 行：`if time.clock() - start_time > max_time > 0:`  
  - 第 396 行：`start_time = time.clock()`  
  - 第 400 行：`if time.clock() - start_time > max_time > 0:`  
  - 第 409 行：`start_time = time.clock()`  
  - 第 413 行：`if time.clock() - start_time > max_time > 0:`  

**修复方案**：  
将所有 `time.clock()` 替换为 `time.perf_counter()`（用于性能测量）或 `time.monotonic()`（用于单调时间）。

**示例修改**：
```python
# 原代码
start_time = time.clock()
if time.clock() - start_time > 10:

# 替换为
start_time = time.perf_counter()
if time.perf_counter() - start_time > 10:
```

**工作量估计**：小（~30 分钟）

---

### 2. 修复窗口尺寸判断逻辑

**问题描述**：  
`OnmyojiAssist.py` 第 70 行判断窗口高度时使用了错误的坐标索引，可能导致窗口尺寸校验不正确。

**影响范围**：  
- **文件**：`OnmyojiAssist.py`
- **受影响代码行**：第 70 行

**当前代码**：
```python
if window_rect[2] - window_rect[0] != 1152 or window_rect[3] - window_rect[0] != 679:
```

**问题分析**：  
`window_rect = (left, top, right, bottom)`，高度应为 `bottom - top`，即 `window_rect[3] - window_rect[1]`。

**修复方案**：
```python
if window_rect[2] - window_rect[0] != 1152 or window_rect[3] - window_rect[1] != 679:
```

**工作量估计**：极小（~5 分钟）

---

## 中优先级 - 代码质量

### 3. 合并冗余的辅助模块

**问题描述**：  
`MyHelper.py` 与 `game_helper.py` 存在大量功能重复（日志配置、消息框、系统唤醒等），但 `MyHelper.py` 未被主流程引用，造成代码冗余与维护负担。

**影响范围**：  
- **文件**：`MyHelper.py`（可删除）、`game_helper.py`（保留并整合）

**对比分析**：
| 功能 | MyHelper.py | game_helper.py | 引用情况 |
| --- | --- | --- | --- |
| `init_logger()` | ✅ | ✅ | 主流程使用 `game_helper` |
| `keep_awake()` | ✅ | ✅ | 主流程使用 `game_helper` |
| `TimedMessageBox` | ✅ | ✅ | 主流程使用 `game_helper` |
| `XStream` | ✅ | ✅ | 主流程使用 `game_helper` |
| 坐标常量 | ✅（旧版） | ✅（新版） | 主流程使用 `game_helper` |

**修复方案**：  
1. 删除 `MyHelper.py`，确认无遗漏引用。
2. 将 `MyHelper.py` 中有价值的注释或历史坐标整合到 `game_helper.py` 的文档注释中（如需保留）。

**工作量估计**：小（~1 小时）

---

### 4. 抽离硬编码常量与配置

**问题描述**：  
坐标、匹配阈值、图片路径等硬编码在代码中，降低可维护性与扩展性。

**影响范围**：  
- **文件**：`OnmyojiThread.py`、`game_helper.py`

**示例问题**：
- 图片路径字符串散落在代码中（如 `'./img/ZHUN_BEI.bmp'`）。
- 匹配阈值固定为 0.9，用户无法调整。
- 坐标常量与业务逻辑混杂。

**修复方案**：  
1. 创建 `config.py` 或 `config.json`，集中管理图片路径映射、阈值、坐标区域等配置。
2. 支持用户自定义资源路径与识别参数。

**示例结构**：
```python
# config.py
class Config:
    MATCH_THRESHOLD = 0.9
    TEMPLATE_DIR = './img/'
    TEMPLATES = {
        'ZHUN_BEI': 'ZHUN_BEI.bmp',
        'ZI_DONG': 'ZI_DONG.bmp',
        # ...
    }
```

**工作量估计**：中（~3-4 小时）

---

### 5. 改进异常处理与日志

**问题描述**：  
当前异常处理依赖 `QuitThread` 自定义异常与日志记录，缺乏统一的错误兜底与恢复机制。

**影响范围**：  
- **文件**：`OnmyojiThread.py`、`game_window.py`

**示例问题**：
- `game_window.py` 第 107-111 行捕获模板匹配异常后仅返回默认值，可能导致静默失败。
- `OnmyojiThread.py` 中检测失败时直接调用 `__emit_stop_signal()` 退出，无重试机制。

**修复方案**：  
1. 为关键步骤（截图、匹配、点击）添加重试逻辑与超时保护。
2. 在 `game_helper.py` 中统一错误报告接口，记录堆栈跟踪并通知用户。
3. 在 GUI 中添加错误提示弹窗，避免静默退出。

**工作量估计**：中（~4-5 小时）

---

## 中优先级 - 工程化

### 6. 完善依赖清单与虚拟环境配置

**问题描述**：  
虽然仓库已新增 `requirements.txt` 与 `.gitignore`，但依赖版本仍较宽泛，缺乏面向 PyInstaller 打包与自动化测试的分层管理，也没有提供锁定文件或 `pyproject.toml` 描述。

**影响范围**：  
- **文件**：`requirements.txt`（需细化分层与注释）、`pyinstaller.py`
- **新增文件**：可选 `pyproject.toml` / `setup.cfg` / `requirements-dev.txt`

**修复方案**：  
1. 将运行时依赖与开发依赖拆分，例如新增 `requirements-dev.txt`（包含 `pytest`、`pyinstaller` 等开发工具）。
2. 在 `pyinstaller.py` 中引用依赖列表或文档化打包所需的额外包，确保发布过程可重现。
3. 评估引入 `pyproject.toml` 或 `pip-tools`（`requirements.in` → `requirements.txt`）以生成锁定版本，便于 CI 对齐。

**参考位置**：`requirements.txt`（[查看](./requirements.txt)）

**工作量估计**：小（~2 小时）

---

### 7. 引入单元测试与 CI/CD

**问题描述**：  
项目无任何自动化测试，代码变更后无法快速验证回归，质量保障依赖手工测试。

**影响范围**：  
- **新增目录**：`tests/`
- **新增文件**：`.github/workflows/ci.yml`（或 `.gitlab-ci.yml`）

**修复方案**：  
1. 使用 `unittest` 或 `pytest` 框架编写基础测试：
   - 模拟截图与窗口句柄，测试 `game_window.compare_image()` 逻辑。
   - 测试 `random_sleep()`、`click()` 等工具函数的参数边界。
2. 配置 GitHub Actions 或 GitLab CI，在 PR 时自动运行测试。
3. 引入代码覆盖率报告（`pytest-cov`）。

**示例测试**：
```python
# tests/test_game_window.py
import numpy as np
from game_window import compare_image

def test_compare_image_identical():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    max_val, max_loc = compare_image(img, img)
    assert max_val > 0.99  # 完全匹配
```

**工作量估计**：大（~8-10 小时）

---

### 8. 优化线程同步与资源管理

**问题描述**：  
当前使用 `threading.Lock` 保护截图与点击，但锁的作用域与释放时机不够清晰，容易在异常时造成死锁或资源泄漏。

**影响范围**：  
- **文件**：`OnmyojiThread.py`

**修复方案**：  
1. 将锁封装为上下文管理器或显式 `try-finally` 块，确保异常时释放锁。
2. 考虑使用 `concurrent.futures.ThreadPoolExecutor` 替代手动线程管理，简化生命周期控制。

**示例改进**：
```python
# 当前代码
with self._lock:
    max_val, pos = find_image(self._hwnd, './img/ZHUN_BEI.bmp')

# 改进为封装方法
def _safe_find_image(self, image_path, pos_lt=None, pos_rb=None):
    with self._lock:
        return find_image(self._hwnd, image_path, pos_lt, pos_rb)
```

**工作量估计**：中（~3-4 小时）

---

## 低优先级 - 用户体验

### 9. 支持多语言与本地化

**问题描述**：  
UI 与日志均为中文硬编码，无法为国际用户提供其他语言选项。

**影响范围**：  
- **文件**：`ui_onmyoji_assist.py`、所有日志输出

**修复方案**：  
1. 使用 Qt 的国际化框架（`QTranslator`）支持多语言切换。
2. 将日志字符串提取到资源文件（`.ts` / `.qm`）。

**工作量估计**：大（~10 小时）

---

### 10. 增强日志持久化与回放

**问题描述**：  
日志仅输出到 GUI 文本框与终端，关闭窗口后无法回溯历史执行记录。

**影响范围**：  
- **文件**：`game_helper.py`

**修复方案**：  
1. 在 `init_logger()` 中添加 `RotatingFileHandler`，将日志保存到 `logs/` 目录。
2. 支持按日期归档日志文件，方便问题排查。

**示例配置**：
```python
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler('logs/onmyoji_assist.log', maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
```

**工作量估计**：小（~1 小时）

---

### 11. 提供图形化配置界面

**问题描述**：  
当前需通过代码修改坐标、阈值等参数，对非技术用户不友好。

**影响范围**：  
- **新增功能**：设置面板或配置文件编辑器

**修复方案**：  
1. 在 UI 中添加"设置"按钮，弹出对话框允许用户调整识别阈值、资源路径等。
2. 配置保存到 JSON 文件，支持导入/导出。

**工作量估计**：中（~5-6 小时）

---

## 总结

| 优先级 | 任务 | 工作量 | 关键文件 |
| --- | --- | --- | --- |
| 高 | 替换 `time.clock()` | 小 | `OnmyojiThread.py` |
| 高 | 修复窗口尺寸判断 | 极小 | `OnmyojiAssist.py` L70 |
| 中 | 合并辅助模块 | 小 | `MyHelper.py`、`game_helper.py` |
| 中 | 抽离硬编码配置 | 中 | `OnmyojiThread.py`、新增 `config.py` |
| 中 | 改进异常处理 | 中 | `OnmyojiThread.py`、`game_window.py` |
| 中 | 完善依赖管理 | 小 | `requirements.txt`、`pyinstaller.py`、（可选）`pyproject.toml` |
| 中 | 引入单元测试与 CI | 大 | 新增 `tests/`、`.github/workflows/` |
| 中 | 优化线程同步 | 中 | `OnmyojiThread.py` |
| 低 | 多语言支持 | 大 | `ui_onmyoji_assist.py`、日志模块 |
| 低 | 日志持久化 | 小 | `game_helper.py` |
| 低 | 图形化配置界面 | 中 | 新增 UI 组件 |

---

## 如何贡献

如果你希望认领某个任务，请：
1. 在 Issue 中声明领取该任务编号（如 `TODO-1: 替换 time.clock()`）。
2. 在新分支上完成修改，提交 PR 时关联对应 Issue。
3. 确保代码风格一致，补充必要的注释与测试。

感谢你对 OnmyojiAssist 的贡献！
