# OpenClawMonitor - OpenClaw 活动监控工具

一个强大的 macOS 应用程序，用于监控 OpenClaw 的日常活动，包括进程、命令执行、文件访问和安全事件。支持 SQLite 数据库存储、HTML 报告生成和每日邮件通知。

## 功能特性

✨ **核心功能**

- 🔍 **进程监控**: 使用 `psutil` 监控 OpenClaw 相关的进程（如 `bot.molt`）
- 💻 **命令追踪**: 从 `exec-approvals.json` 和日志文件中解析执行的命令
- 📁 **文件监控**: 使用 `watchdog` 监控日志文件变更，解析文件读写操作
- 🔐 **安全分析**: 分析权限请求、错误事件，计算每日安全评分
- 📊 **报告生成**: 生成美观的 HTML 报告，包含表格和图表
- 📧 **邮件通知**: 每日 8:00 AM 自动生成报告并通过 Gmail SMTP 发送
- 🗄️ **数据持久化**: 使用 SQLite 数据库存储所有监控数据
- 🚀 **后台运行**: 支持 macOS launchd 后台运行

🆕 **新功能 - OpenClaw 系统日志分析**

- 📝 **深度日志解析**: 自动分析 OpenClaw 系统日志（JSON Lines 格式）
- 🚀 **运行追踪**: 监控所有运行事件，追踪运行 ID、状态和时间戳
- 💬 **会话管理**: 追踪会话创建、状态变化（活跃/非活跃）
- ⚠️ **错误统计**: 统计和排序错误/警告消息，显示 Top 50
- 📈 **事件分类**: 将日志条目分为 11 种事件类型（运行、会话、网关、连接、错误等）
- 🎨 **可视化报告**: 生成带渐变色卡片、交互表格的现代化 HTML 报告
- 🤖 **自动发现**: 自动选择最新日志文件进行分析，无需手动配置

> 详见：[OpenClaw 日志分析文档](docs/OPENCLAW_LOG_ANALYSIS.md) | [快速开始](docs/QUICKSTART_LOG_ANALYSIS.md)

## 项目结构

```
OpenClawMonitor/
├── src/openclawmonitor/          # 主代码
│   ├── __init__.py
│   ├── main.py                   # 程序入口 + 调度器
│   ├── config.py                 # 配置加载
│   ├── settings.py               # 配置模型（Pydantic）
│   │
│   ├── monitor/                  # 核心监控模块
│   │   ├── base.py               # BaseMonitor 抽象基类
│   │   ├── process_monitor.py    # 进程监控
│   │   ├── log_parser.py         # 多路径日志解析
│   │   ├── watchdog_handler.py   # 文件系统监控
│   │   ├── security_analyzer.py  # 安全分析
│   │   ├── openclaw_log_analyzer.py        # 🆕 OpenClaw 日志分析器
│   │   ├── openclaw_report_generator.py    # 🆕 分析报告生成器
│   │   └── plugins/              # 插件系统
│   │
│   ├── db/                       # 数据库层
│   │   ├── manager.py            # SQLite 操作
│   │   └── models.py             # 数据模型
│   │
│   ├── report/                   # 报告生成
│   │   ├── generator.py          # HTML + 图表
│   │   └── notifier/
│   │       ├── email_sender.py   # 邮件发送
│   │       └── base_notifier.py  # 通知基类
│   │
│   ├── utils/                    # 工具函数
│   │   ├── logger.py
│   │   ├── helpers.py
│   │   └── path_resolver.py
│   │
│   └── scheduler.py              # 定时任务
│
├── config/
│   ├── config.yaml               # 主配置文件
│   └── logging.yaml              # 日志配置
│
├── scripts/
│   ├── start.sh                  # 启动脚本
│   ├── install_launchd.sh        # 安装 launchd 服务
│   └── enable_logs.sh            # 启用日志指南
│
├── database/                     # SQLite 数据库（自动创建）
├── logs/                         # 日志文件
├── requirements.txt              # 项目依赖
├── pyproject.toml               # 项目元数据
├── README.md                    # 本文件
└── .gitignore
```

## 快速开始

### 前置需求

- Python 3.8+
- macOS 10.14+
- pip 或 conda

### 安装步骤

#### 1. 克隆或下载项目

```bash
cd /Users/jaceho/Python/Project/OpenClawMonitor
```

#### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

**主要依赖:**
- `psutil` - 进程监控
- `watchdog` - 文件系统监控
- `pandas` - 数据处理
- `matplotlib` - 图表生成
- `schedule` - 定时任务
- `pydantic` - 配置验证
- `PyYAML` - YAML 配置解析
- `keyring` - 密码加密存储

#### 4. 配置邮件设置

编辑 `config/config.yaml` 或设置环境变量:

```bash
# 方式 1: 编辑配置文件
cp .env.example .env
# 编辑 .env 文件，添加邮箱配置

# 方式 2: 使用环境变量
export OPENCLAW_SENDER_EMAIL="your_email@gmail.com"
export OPENCLAW_SENDER_PASSWORD="your_app_password"
export OPENCLAW_RECIPIENT_EMAIL="recipient@example.com"
```

**Gmail 设置说明:**
1. 启用 [Google 应用专用密码](https://myaccount.google.com/apppasswords)
2. 使用应用密码而非常规密码
3. 密码将安全地存储在 macOS Keyring 中

#### 5. 启用 OpenClaw 日志

在 OpenClaw 中启用日志功能是必须的，否则监控程序将无法收集数据。

**步骤:**
1. 打开 OpenClaw 应用
2. 菜单 → 调试 (Debug)
3. 找到 "Logs" 部分
4. 启用 "App logging" → "Write rolling diagnostics log (JSONL)"
5. 重启 OpenClaw

**查看状态:**
```bash
bash scripts/enable_logs.sh
```

## 使用方式

### 测试模式（运行一次）

```bash
# 运行一次数据收集和报告生成（包含日志分析）
python -m main --run-once

# 指定特定日期
python -m main --run-once --date 2024-01-15

# 使用自定义配置文件
python -m main --run-once --config /path/to/config.yaml
```

**新功能：** 每次运行都会自动：
1. 收集常规监控数据（进程、命令、文件）
2. 生成并发送每日报告邮件
3. 🆕 分析 OpenClaw 系统日志（`/private/tmp/openclaw/`）
4. 🆕 生成日志分析 HTML 报告（保存至 `reports/` 目录）

**查看日志分析报告：**
```bash
# 找到最新的分析报告
ls -lt reports/openclaw_analysis_*.html | head -1

# 在浏览器中打开
open reports/openclaw_analysis_<timestamp>.html
```

### 后台运行模式（持续监控）

```bash
# 启动监控程序（前台）
python -m main

# 或使用启动脚本
bash scripts/start.sh
```

### 配置 launchd 后台服务

**一次性安装:**
```bash
bash scripts/install_launchd.sh
```

**后续管理:**
```bash
# 卸载服务
launchctl unload ~/Library/LaunchAgents/com.openclaw.monitor.plist

# 查看服务状态
launchctl list | grep com.openclaw.monitor

# 查看日志
tail -f logs/launchd.out.log
```

## 配置说明

### config.yaml 主要配置项

```yaml
# 基础设置
base_path: /Users/jaceho/.openclaw
debug_mode: false

# 日志路径（多路径支持）
log_paths:
  paths:
    - /tmp/openclaw/
    - /Users/jaceho/.openclaw/logs/
    - /Users/jaceho/.openclaw/workspace/logs/
    - ~/Library/Logs/OpenClaw/

# 数据库设置
database:
  db_path: database/openclaw_monitor.db

# 邮件设置
email:
  smtp_server: smtp.gmail.com
  smtp_port: 587
  sender_email: your_email@gmail.com
  sender_password: your_app_password  # 或使用环境变量
  recipient_email: recipient@example.com
  use_encryption: true
```

### 环境变量

创建 `.env` 文件或设置系统环境变量。配置优先级：系统环境变量 > .env 文件 > YAML 配置 > 默认值。

**基础配置（邮件）：**

```bash
# SMTP 邮件服务器配置
OPENCLAW_SMTP_SERVER=smtp.gmail.com          # 默认值：smtp.gmail.com
OPENCLAW_SMTP_PORT=587                       # 默认值：587（TLS）或 465（SSL）
OPENCLAW_SMTP_USERNAME=your_email@gmail.com  # 可选，默认使用发送者邮箱

# 邮件内容配置
OPENCLAW_SENDER_EMAIL=your_email@gmail.com
OPENCLAW_SENDER_PASSWORD=your_app_password
OPENCLAW_RECIPIENT_EMAIL=recipient@example.com

# 其他配置
OPENCLAW_DEBUG=false
```

**Google Gmail 配置示例：**

```bash
OPENCLAW_SMTP_SERVER=smtp.gmail.com
OPENCLAW_SMTP_PORT=587
OPENCLAW_SMTP_USERNAME=your_email@gmail.com
OPENCLAW_SENDER_EMAIL=your_email@gmail.com
OPENCLAW_SENDER_PASSWORD=your_app_password    # 16 位应用专用密码
OPENCLAW_RECIPIENT_EMAIL=recipient@example.com
```

**企业邮箱（如阿里云邮箱）配置示例：**

```bash
OPENCLAW_SMTP_SERVER=smtp.qiye.aliyun.com
OPENCLAW_SMTP_PORT=465                        # SSL 端口
OPENCLAW_SMTP_USERNAME=your_email@company.com
OPENCLAW_SENDER_EMAIL=your_email@company.com
OPENCLAW_SENDER_PASSWORD=your_password
OPENCLAW_RECIPIENT_EMAIL=recipient@company.com
```

**获取 Gmail 应用专用密码：**
1. 访问 https://myaccount.google.com/apppasswords
2. 选择应用：Mail，选择设备：Mac
3. 复制生成的 16 位密码
4. 放入 `.env` 文件的 `OPENCLAW_SENDER_PASSWORD` 字段

## 核心模块说明

### 监控模块 (`monitor/`)

**BaseMonitor**
- 抽象基类，所有监控器的父类
- 定义 `collect()` 和 `analyze()` 接口

**ProcessMonitor**
- 监控特定进程（如 `bot.molt`）
- 收集进程信息：PID、内存使用、CPU 使用率、运行时长

**LogParser**
- 支持多路径和多格式的日志解析
- 自动查找 `/tmp/openclaw/openclaw-YYYY-MM-DD.log` 等日志文件
- 支持 JSONL 格式日志解析
- 从 `exec-approvals.json` 提取命令执行记录

**SecurityAnalyzer**
- 分析日志中的安全事件
- 分类文件访问（敏感/系统/用户）
- 计算每日安全评分（0-100）
- 识别权限问题和错误

**WatchdogHandler**
- 监控日志文件变更
- 实时捕获新生成的日志

### 数据库模块 (`db/`)

**DatabaseManager**
- SQLite 数据库操作
- 表结构：`activity_records`、`security_events`、`daily_reports`
- 支持数据去重（UNIQUE 约束）
- 自动索引优化查询

**Models**
- Pydantic 数据模型：`ActivityRecord`、`SecurityEvent`、`DailyReport`
- 数据验证和类型检查

### 报告模块 (`report/`)

**ReportGenerator**
- 生成美观的 HTML 报告
- 支持 Pandas + Matplotlib 图表
- 包含事件统计、表格和趋势图
- 缺失日志自动提示

**EmailNotifier**
- Gmail SMTP 发送邮件
- 密码安全存储（使用 keyring）
- 支持 STARTTLS 加密连接
- HTML 邮件格式

### 调度模块 (`scheduler.py`)

**Scheduler**
- 基于 `schedule` 库的任务调度
- 支持每日固定时间任务（例如 08:00 AM）
- 支持间隔任务（例如每 30 分钟）
- 后台线程运行

## 开发指南

### 添加自定义监控器

创建新的监控器类（继承 `BaseMonitor`）:

```python
from openclawmonitor.monitor.base import BaseMonitor
from datetime import datetime
from typing import Dict, Any, List

class CustomMonitor(BaseMonitor):
    def __init__(self):
        super().__init__("CustomMonitor")
    
    def collect(self, target_date: datetime = None) -> List[Dict[str, Any]]:
        # 实现数据收集逻辑
        self.data = [{"event": "example"}]
        return self.data
    
    def analyze(self) -> Dict[str, Any]:
        # 实现数据分析逻辑
        return {"summary": "analysis results"}
```

### 扩展通知方式

创建新的通知器类（继承 `BaseNotifier`）:

```python
from openclawmonitor.report.notifier.base_notifier import BaseNotifier

class SlackNotifier(BaseNotifier):
    def __init__(self, webhook_url: str):
        super().__init__("SlackNotifier")
        self.webhook_url = webhook_url
    
    def send(self, subject: str, content: str, **kwargs) -> bool:
        # 实现 Slack 通知逻辑
        pass
```

## 故障排查

### 日志文件未找到

```
警告：未在任何配置的路径中找到日志文件
```

**解决方案:**
1. 检查 `config.yaml` 中的 `log_paths`
2. 确认 OpenClaw 已启用日志记录（见上面的"启用 OpenClaw 日志"）
3. 查看 `~/.openclaw/openclaw.json` 中的 `logging.file` 配置

### 邮件发送失败

```
邮件发送失败: [SSL: WRONG_VERSION_NUMBER]
```

**解决方案:**
1. 确认使用了 Gmail 应用专用密码（不是常规密码）
2. 检查 SMTP 服务器和端口配置
3. 确认网络连接正常
4. 查看详细日志：`tail -f logs/openclaw_monitor.log`

### 内存使用过高

**优化方案:**
1. 减少日志解析的历史记录数
2. 启用数据库自动清理（需要自定义实现）
3. 调整监控间隔

### 权限问题

```
PermissionError: [Errno 13] Permission denied
```

**解决方案:**
1. 确保对 `database/` 目录有写权限
2. 检查日志文件的读权限
3. 运行 `chmod 755 scripts/*.sh`

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关文档

**主要文档：**
- 🆕 [OpenClaw 日志分析功能](docs/OPENCLAW_LOG_ANALYSIS.md) - 系统日志深度分析完整文档
- 🆕 [日志分析快速开始](docs/QUICKSTART_LOG_ANALYSIS.md) - 一键运行和查看报告
- [增量更新机制](docs/INCREMENTAL_UPDATE.md) - 24 小时滑动窗口报告
- [数据为 0 问题诊断](docs/LOG_DATA_ZERO.md) - 常见数据收集问题

**技术参考：**
- [Python psutil 文档](https://psutil.readthedocs.io/)
- [watchdog 文档](https://watchdog.readthedocs.io/)
- [Pydantic 文档](https://pydantic-docs.helpmanual.io/)
- [schedule 库文档](https://schedule.readthedocs.io/)
- [macOS launchd 指南](https://launchd.info/)

## 常见问题

**Q: 为什么需要启用 OpenClaw 日志？**
A: 日志是监控程序的数据源。没有日志，无法收集任何活动信息。

**Q: 可以监控多个用户或多台机器吗？**
A: 目前设计用于单机单用户。多用户/多机器支持需要额外开发。

**Q: 报告会保存多久？**
A: 报告永久保存在 SQLite 数据库中。可手动删除或设置清理策略。

**Q: 如何禁用特定类型的通知？**
A: 在 `config.yaml` 中禁用相应的通知器，或在代码中注释掉对应行。

---

**最后更新:** 2024年
