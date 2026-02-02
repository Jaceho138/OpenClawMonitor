# OpenClaw 日志分析 - 快速开始

## 一键运行

```bash
cd /Users/jaceho/Python/Project/OpenClawMonitor
source venv/bin/activate
PYTHONPATH=src python -m main --run-once
```

## 查看结果

**1. 查看控制台输出**

程序会在控制台显示分析摘要：

```
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
```

**2. 打开 HTML 报告**

```bash
# 找到最新的报告文件
ls -lt reports/ | head -5

# 在浏览器中打开
open reports/openclaw_analysis_<timestamp>.html
```

## 报告内容

HTML 报告包含以下章节：

### 📊 概览统计
- 日志处理行数
- 运行事件总数
- 会话数量
- 错误/警告数量

### 📈 事件分布统计
11 种事件类型的数量和占比分析

### 🚀 运行情况分析
- 运行状态分布（已完成/运行中/未知）
- 最近 20 次运行详情表格

### 💬 会话追踪
- 会话状态分布（活跃/已关闭）
- 最近 20 个会话详情

### ⚠️ 错误分析
- Top 50 错误消息列表
- 每个错误的出现次数

### 📝 事件流
最近 20 条事件的详细记录（时间、类型、消息）

## 分析数据来源

**默认日志路径**: `/private/tmp/openclaw/`

程序会自动选择最新的 `.log` 文件进行分析。

## 只运行日志分析

```python
from main import OpenClawMonitor

monitor = OpenClawMonitor()
monitor.analyze_openclaw_logs()  # 分析最新日志
# 或
monitor.analyze_openclaw_logs('/path/to/specific.log')  # 分析指定日志
```

## 示例数据

**测试执行结果**（2026-02-02）：
- 日志文件：2.1MB，1159 行
- 解析成功率：100%
- 发现运行：46 次（全部完成）
- 发现会话：1 个
- 发现错误：122 条
- 文件访问：26 次
- 执行时间：<1 秒

## 报告保存位置

```
/Users/jaceho/Python/Project/OpenClawMonitor/reports/
  ├── openclaw_analysis_20260202_165132.html  (26KB)
  └── ...
```

文件名格式：`openclaw_analysis_<YYYYMMDD>_<HHMMSS>.html`

## 查看日志

```bash
# 程序运行日志
tail -f logs/openclaw_monitor.log

# OpenClaw 系统日志
tail -f /private/tmp/openclaw/openclaw-2026-02-02.log
```

## 常见问题

**Q: 报告中数据为 0？**  
A: OpenClaw 系统日志不包含所有类型的事件。这是正常的，取决于 OpenClaw 的运行活动。

**Q: 如何定时分析日志？**  
A: 目前每次运行 `--run-once` 都会自动分析。未来会支持独立的定时分析任务。

**Q: 能否导出 PDF？**  
A: 当前只支持 HTML 格式。PDF 导出功能在未来计划中。

## 详细文档

参见：[OPENCLAW_LOG_ANALYSIS.md](OPENCLAW_LOG_ANALYSIS.md)

## 联系支持

如有问题，请查看：
- 主文档：[README.md](../README.md)
- 日志文件：`logs/openclaw_monitor.log`
- GitHub Issues（如果配置了 git 仓库）
