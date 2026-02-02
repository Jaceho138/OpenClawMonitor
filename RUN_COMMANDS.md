# OpenClawMonitor - 运行命令快速参考

## 🚀 基础准备

### 1. 进入项目目录
```bash
cd /Users/jaceho/Python/Project/OpenClawMonitor
```

### 2. 激活虚拟环境
```bash
source venv/bin/activate
```

### 3. 验证环境（可选）
```bash
python --version
pip list | grep -E "psutil|watchdog|pandas|schedule"
```

---

## 📋 主要运行命令

### 🔄 **一次性运行（采集数据 + 生成报告 + 分析日志）**

最常用的命令，执行一次完整的监控流程：

```bash
# 基础运行（默认分析前一天的数据）
python -m main --run-once

# 指定特定日期
python -m main --run-once --date 2024-01-15

# 使用自定义配置文件
python -m main --run-once --config /path/to/config.yaml
```

**执行内容：**
- ✅ 采集进程监控数据
- ✅ 解析执行命令
- ✅ 监控文件变更
- ✅ 分析安全事件
- ✅ 🆕 分析 OpenClaw 系统日志
- ✅ 生成 HTML 报告（多个格式）
- ✅ 发送邮件通知

---

### 🔁 **后台持续运行（监控模式）**

前台运行，持续监控每日 08:00 自动生成报告：

```bash
# 方式 1: 直接运行
python -m main

# 方式 2: 使用启动脚本
bash scripts/start.sh

# 方式 3: 使用 Python 路径
PYTHONPATH=src python -m main
```

**特点：**
- 🔄 持续后台监控
- ⏰ 每天早上 08:00 自动执行
- 📧 自动生成并发送邮件报告
- 🆕 自动分析最新的日志文件

---

### 🖥️ **macOS launchd 后台服务（推荐用于部署）**

#### 安装为系统服务

```bash
# 一次性安装（自动创建 launchd 配置）
bash scripts/install_launchd.sh
```

**安装后自动特性：**
- 📅 每天 08:00 AM 自动执行
- 🔄 系统启动后自动启动
- 📝 日志输出到 `logs/launchd.out.log`

#### 管理 launchd 服务

```bash
# 查看服务状态
launchctl list | grep com.openclaw.monitor

# 启动服务
launchctl load ~/Library/LaunchAgents/com.openclaw.monitor.plist

# 停止服务
launchctl unload ~/Library/LaunchAgents/com.openclaw.monitor.plist

# 重启服务
launchctl unload ~/Library/LaunchAgents/com.openclaw.monitor.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.monitor.plist

# 查看 launchd 日志
tail -f logs/launchd.out.log

# 清除日志并重新启动
rm logs/launchd.out.log
launchctl unload ~/Library/LaunchAgents/com.openclaw.monitor.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.monitor.plist
```

---

## 🆕 **日志分析相关命令**

### 查看最新分析报告

```bash
# 列出最新的分析报告
ls -lt reports/openclaw_analysis_*.html | head -5

# 打开最新报告（自动在浏览器打开）
open "$(ls -t reports/openclaw_analysis_*.html | head -1)"

# 找到特定日期的报告
ls reports/openclaw_analysis_*20260202*.html
```

### 调试日志分析

```bash
# 启用调试模式运行
OPENCLAW_DEBUG=true python -m main --run-once

# 查看实时程序日志
tail -f logs/openclaw_monitor.log

# 查看特定日期的日志
grep "2026-02-02" logs/openclaw_monitor.log
```

---

## 📧 **邮件相关命令**

### 验证邮件配置

```bash
# 使用脚本验证
bash scripts/verify_email_config.sh

# 或手动测试
python -c "
from src.report.notifier.email_sender import EmailNotifier
from src.config import get_config
config = get_config()
notifier = EmailNotifier(config)
notifier.send('Test', '<h1>测试邮件</h1>')
"
```

### 查看邮件配置

```bash
# 从 .env 文件读取
cat .env | grep OPENCLAW

# 从配置文件读取
grep -A 5 "email:" config/config.yaml
```

---

## 💾 **数据库操作命令**

### 查看数据库内容

```bash
# 使用 sqlite3 查询数据库
sqlite3 database/openclaw_monitor.db

# 进入数据库后可执行的命令：
# 查看所有表
.tables

# 查看特定日期的活动记录
SELECT * FROM activity_records WHERE date = '2024-01-15' LIMIT 10;

# 查看最近的 20 条记录
SELECT * FROM activity_records ORDER BY date DESC LIMIT 20;

# 统计活动数量
SELECT COUNT(*) FROM activity_records;

# 退出
.quit
```

### 数据库备份

```bash
# 备份数据库
cp database/openclaw_monitor.db database/openclaw_monitor_backup_$(date +%Y%m%d_%H%M%S).db

# 列出所有备份
ls -lt database/openclaw_monitor_backup_*.db

# 恢复备份
cp database/openclaw_monitor_backup_20260202_120000.db database/openclaw_monitor.db
```

---

## 🔍 **故障排查命令**

### 检查环境

```bash
# 验证 Python 版本
python --version    # 需要 3.8+

# 检查虚拟环境激活状态
which python

# 验证依赖安装
pip list | grep -E "psutil|watchdog|pandas|matplotlib|schedule|pydantic"

# 检查项目结构
find . -name "*.py" -path "*/src/*" | head -20
```

### 检查日志和报告

```bash
# 查看程序日志
cat logs/openclaw_monitor.log

# 查看最近 50 行日志
tail -n 50 logs/openclaw_monitor.log

# 搜索错误日志
grep ERROR logs/openclaw_monitor.log

# 查看生成的报告数量
ls -l reports/ | wc -l

# 找出最大的报告（可能有性能问题）
ls -lhS reports/*.html | head -5
```

### 检查日志文件

```bash
# 查看 OpenClaw 日志文件路径
find /private/tmp/openclaw -name "*.jsonl" -o -name "*.log"

# 检查最近修改的日志
find /private/tmp/openclaw -type f -mmin -60

# 查看日志文件大小
du -h /private/tmp/openclaw/

# 查看日志内容样本
head -20 /private/tmp/openclaw/openclaw.jsonl
```

---

## ⚙️ **配置相关命令**

### 创建环境文件

```bash
# 创建 .env 文件模板
cat > .env << 'EOF'
# SMTP 配置
OPENCLAW_SMTP_SERVER=smtp.gmail.com
OPENCLAW_SMTP_PORT=587
OPENCLAW_SMTP_USERNAME=your_email@gmail.com

# 邮件账户
OPENCLAW_SENDER_EMAIL=your_email@gmail.com
OPENCLAW_SENDER_PASSWORD=your_app_password
OPENCLAW_RECIPIENT_EMAIL=recipient@example.com

# 调试模式
OPENCLAW_DEBUG=false
EOF

# 编辑配置文件
nano .env
```

### 查看和编辑配置

```bash
# 查看主配置文件
cat config/config.yaml

# 编辑配置
nano config/config.yaml

# 查看日志配置
cat config/logging.yaml

# 验证 YAML 语法（需要 Python）
python -c "import yaml; print(yaml.safe_load(open('config/config.yaml')))"
```

---

## 📊 **报告相关命令**

### 查看和处理报告

```bash
# 列出所有报告
ls -lh reports/

# 查看最近的 5 个报告
ls -lt reports/*.html | head -5

# 打开最新报告
open "$(ls -t reports/*.html | head -1)"

# 转发报告给某人
# 注：手动打开浏览器复制链接或附件

# 统计报告数量
echo "Total reports: $(ls reports/*.html | wc -l)"

# 查看报告文件大小统计
du -sh reports/
```

### 生成特定类型的报告

```bash
# 生成标准报告（包含日志分析）
python -m main --run-once

# 分别生成各类报告
# 1. 常规监控报告
python -c "from src.report.generator import ReportGenerator; ..."

# 2. 日志分析报告
python -c "from src.monitor.openclaw_report_generator import OpenClawReportGenerator; ..."
```

---

## 🧪 **测试命令**

### 运行单元测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/unit/test_config.py -v

# 运行集成测试
pytest tests/integration/

# 生成测试覆盖率报告
pytest --cov=src tests/
```

### 单独测试各个模块

```bash
# 测试日志解析
python -c "
from src.monitor.log_parser import LogParser
parser = LogParser()
logs = parser.parse_all_logs()
print(f'Found {len(logs)} log entries')
"

# 测试数据库操作
python -c "
from src.db.manager import DatabaseManager
db = DatabaseManager()
records = db.get_records('2024-01-15')
print(f'Found {len(records)} records')
"

# 测试报告生成
python -c "
from src.report.generator import ReportGenerator
gen = ReportGenerator()
html = gen.generate_html_report({})
print(f'Generated {len(html)} bytes of HTML')
"
```

---

## 📌 **常用工作流**

### 日常使用流程

```bash
# 1. 启动项目
cd /Users/jaceho/Python/Project/OpenClawMonitor
source venv/bin/activate

# 2. 运行一次采集（测试）
python -m main --run-once

# 3. 查看生成的报告
open "$(ls -t reports/*.html | head -1)"

# 4. 检查数据库
sqlite3 database/openclaw_monitor.db "SELECT COUNT(*) FROM activity_records;"

# 5. 查看日志
tail -f logs/openclaw_monitor.log
```

### 部署到后台

```bash
# 1. 安装 launchd 服务
bash scripts/install_launchd.sh

# 2. 验证安装
launchctl list | grep com.openclaw.monitor

# 3. 监控日志
tail -f logs/launchd.out.log

# 4. 需要时卸载
launchctl unload ~/Library/LaunchAgents/com.openclaw.monitor.plist
```

---

## 🆘 **快速故障排查**

| 问题 | 命令 |
|------|------|
| 程序无输出 | `PYTHONPATH=src python -m main --run-once 2>&1` |
| 找不到模块 | `pip install -r requirements.txt` |
| 邮件配置错误 | `bash scripts/verify_email_config.sh` |
| 数据库损坏 | `rm database/openclaw_monitor.db && python -m main --run-once` |
| launchd 问题 | `launchctl unload ... && launchctl load ...` |
| 日志文件问题 | `head -20 /private/tmp/openclaw/openclaw.jsonl` |

---

## 📚 **更多信息**

- 详细配置: [config/config.yaml](config/config.yaml)
- 邮件设置: [docs/EMAIL_CONFIG.md](docs/EMAIL_CONFIG.md)
- 日志分析: [docs/OPENCLAW_LOG_ANALYSIS.md](docs/OPENCLAW_LOG_ANALYSIS.md)
- 快速开始: [docs/QUICKSTART_LOG_ANALYSIS.md](docs/QUICKSTART_LOG_ANALYSIS.md)

---

**创建时间**: 2026-02-02  
**版本**: 2.0  
**状态**: ✅ 完整测试
