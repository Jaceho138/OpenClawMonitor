# OpenClaw 系统日志分析功能

## 概述

OpenClawMonitor 现已支持对 OpenClaw 系统日志的深度分析，能够从系统日志中提取运行事件、会话状态、错误统计等关键信息，并生成可视化的 HTML 报告。

## 功能特性

### 1. 日志解析 (`OpenClawLogAnalyzer`)

**支持的数据提取：**
- **运行事件 (Runs)**: 追踪每次运行的 ID、状态（运行中/已完成）、时间戳
- **会话 (Sessions)**: 监控会话的创建、状态变化（活跃/非活跃）
- **错误分析**: 统计错误和警告消息，按出现频率排序
- **文件访问**: 记录文件操作事件（如果日志中包含）
- **事件分类**: 将日志条目分为 11 种类型
  - run_start（运行开始）
  - run_complete（运行完成）
  - session_state（会话状态变化）
  - gateway_*（网关事件）
  - connection_*（连接事件）
  - error（错误）
  - file_access（文件访问）
  - other（其他）

**关键方法：**
```python
analyzer = OpenClawLogAnalyzer()
analysis_data = analyzer.analyze_file('/path/to/openclaw.log')

# 获取文本摘要
summary = analyzer.get_summary()
print(summary)
```

### 2. HTML 报告生成 (`OpenClawReportGenerator`)

**报告章节：**
1. **概览统计**
   - 渐变色卡片展示关键指标
   - 包含：日志行数、运行次数、会话数、错误数

2. **事件分布统计**
   - 表格形式展示各类事件的数量和占比

3. **运行情况分析**
   - 运行状态分布（已完成/运行中/未知）
   - 最近运行记录表格（最多显示 20 条）

4. **会话追踪**
   - 会话状态分布（活跃/已关闭）
   - 最近会话列表（最多显示 20 条）

5. **错误分析**
   - Top 错误消息列表（最多显示 50 条）
   - 错误出现次数统计

6. **事件流**
   - 最近 20 条事件详情
   - 包含时间戳、类型、子系统、消息内容

**报告样式特性：**
- 响应式网格布局
- 渐变色统计卡片
- 悬停交互效果
- 颜色编码状态徽章
- 现代化 CSS 设计

### 3. 自动化集成

**程序执行流程：**
```
运行 main.py --run-once
  ↓
生成日常监控报告（进程、命令、日志事件）
  ↓
发送邮件
  ↓
分析 OpenClaw 系统日志
  ↓
生成 HTML 报告并保存
  ↓
完成
```

**自动日志发现：**
- 默认扫描 `/private/tmp/openclaw/` 目录
- 自动选择最新的 `.log` 文件
- 无需手动指定日志路径

## 使用方法

### 命令行执行

```bash
# 运行一次（包含日志分析）
cd /Users/jaceho/Python/Project/OpenClawMonitor
source venv/bin/activate
PYTHONPATH=src python -m main --run-once
```

**输出示例：**
```
2026-02-02 16:51:32 - OpenClawMonitor - INFO - 分析 OpenClaw 系统日志...
2026-02-02 16:51:32 - OpenClawMonitor - INFO - 使用默认日志文件: /private/tmp/openclaw/openclaw-2026-02-02.log

============================================================
OpenClaw 系统日志分析摘要
============================================================

📊 日志处理: 1159/1159 行成功解析

📈 数据统计:
  • 运行事件: 363 次
  • 会话: 1 个
  • 文件访问: 26 次
  • 错误/警告: 122 条

🚀 运行情况:
  • 总运行数: 46
  • 已完成: 46
  • 运行中: 0

💬 会话情况:
  • 总会话数: 1
  • 活跃: 0
  • 已关闭: 0

============================================================
2026-02-02 16:51:32 - OpenClawMonitor - INFO - 报告已保存: /Users/jaceho/Python/Project/OpenClawMonitor/reports/openclaw_analysis_20260202_165132.html
```

### Python API 调用

```python
from main import OpenClawMonitor

# 创建监控实例
monitor = OpenClawMonitor()

# 方法 1: 使用默认路径（自动发现最新日志）
monitor.analyze_openclaw_logs()

# 方法 2: 指定日志文件
monitor.analyze_openclaw_logs('/path/to/specific.log')
```

### 直接使用分析器

```python
from openclawmonitor.monitor.openclaw_log_analyzer import OpenClawLogAnalyzer
from openclawmonitor.monitor.openclaw_report_generator import OpenClawReportGenerator

# 分析日志
analyzer = OpenClawLogAnalyzer()
analysis_data = analyzer.analyze_file('/private/tmp/openclaw/openclaw-2026-02-02.log')

# 生成报告
generator = OpenClawReportGenerator()
html_report = generator.generate_html_report(analysis_data)

# 保存报告
with open('report.html', 'w', encoding='utf-8') as f:
    f.write(html_report)
```

## 报告位置

所有分析报告保存在项目根目录的 `reports/` 文件夹中，文件名格式为：

```
openclaw_analysis_<YYYYMMDD>_<HHMMSS>.html
```

示例：`openclaw_analysis_20260202_165132.html`

## 配置说明

### 日志路径配置

在 `config/config.yaml` 中添加：

```yaml
log_paths:
  paths:
    - /private/tmp/openclaw/
```

或在 `src/settings.py` 中修改默认路径。

### 日志格式要求

支持的日志格式为 **JSON Lines (JSONL)**，每行一个 JSON 对象：

```json
{"0":"[2026-02-02 09:10:15]","1":"Gateway started","_meta":{"subsystem":"gateway","level":"info",...}}
```

**必需字段：**
- `_meta.subsystem`: 日志来源子系统
- `_meta.timestamp`: 时间戳
- 消息内容（数字键 "0", "1", "2" 等）

## 数据来源

该功能分析的是 OpenClaw 的**系统运行日志**，包含：
- 网关启动/停止事件
- 运行任务的生命周期
- 会话管理
- 连接状态
- 系统错误和警告

**注意：** 这些日志不包含详细的文件访问记录。如需监控文件操作，请参考主监控功能（使用 watchdog）。

## 性能优化

### 大日志文件处理

对于大型日志文件（>10MB）：
- 使用流式读取，内存占用低
- JSON 解析错误自动跳过，不中断处理
- 报告表格限制行数（最多 20 行），避免 HTML 过大

### 执行效率

- **小文件（<1MB）**: <1 秒
- **中等文件（1-5MB）**: 1-3 秒
- **大文件（>5MB）**: 3-10 秒

示例：分析 2.1MB 日志（1159 行）耗时约 1 秒。

## 故障排查

### 问题：未生成报告

**检查：**
1. 日志目录是否存在：`ls -la /private/tmp/openclaw/`
2. 是否有 `.log` 文件
3. 检查日志：`tail -50 logs/openclaw_monitor.log`

### 问题：解析失败

**可能原因：**
- 日志格式不是 JSON Lines
- JSON 格式错误（不影响整体解析，会跳过错误行）
- 文件权限问题

**调试方法：**
```python
from openclawmonitor.monitor.openclaw_log_analyzer import OpenClawLogAnalyzer

analyzer = OpenClawLogAnalyzer()
data = analyzer.analyze_file('/path/to/log')
print(data['parse_errors'])  # 查看解析错误
```

### 问题：数据为 0

这是正常的，说明该日志中没有对应类型的事件。OpenClaw 系统日志可能不包含所有事件类型（如文件访问需要单独启用）。

## 扩展开发

### 添加新的事件类型

编辑 `src/monitor/openclaw_log_analyzer.py`：

```python
def _classify_event(self, message: str, subsystem: str) -> str:
    # 添加新的分类逻辑
    if "your_pattern" in message.lower():
        return "your_event_type"
    # ...
```

### 自定义报告章节

编辑 `src/monitor/openclaw_report_generator.py`：

```python
def generate_html_report(self, analysis_data: Dict[str, Any]) -> str:
    sections = [
        self._create_header(analysis_data),
        self._create_summary_section(analysis_data),
        # 添加你的自定义章节
        self._create_your_section(analysis_data),
        self._create_footer(),
    ]
    return "\n".join(sections)
```

## 未来计划

- [ ] 将分析报告集成到邮件通知中
- [ ] 支持定时自动分析（每日、每周）
- [ ] 添加图表可视化（matplotlib 集成）
- [ ] 支持导出 PDF 格式
- [ ] 支持多日志文件聚合分析
- [ ] 添加异常检测和告警阈值

## 相关文件

| 文件 | 作用 |
|------|------|
| `src/monitor/openclaw_log_analyzer.py` | 日志解析器 |
| `src/monitor/openclaw_report_generator.py` | HTML 报告生成器 |
| `src/main.py` | 集成点（`analyze_openclaw_logs()` 方法）|
| `reports/` | 报告输出目录 |

## 参考

- 主文档：[README.md](../README.md)
- 配置指南：[config/config.yaml](../config/config.yaml)
- 增量更新机制：[INCREMENTAL_UPDATE.md](INCREMENTAL_UPDATE.md)
- 数据为 0 问题：[LOG_DATA_ZERO.md](LOG_DATA_ZERO.md)
