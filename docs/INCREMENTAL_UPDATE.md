# 增量更新功能文档

## 概述

OpenClawMonitor 支持**每次执行都发送邮件报告**，并通过**增量更新机制**避免重复数据：

- ✅ 每次执行命令都收集最新数据并实时写入数据库
- ✅ 每次执行都发送最近 24 小时的综合报告邮件
- ✅ 支持从上次执行节点开始增量抓取新数据
- ✅ 数据库自动去重（唯一约束 + UNIQUE 键）

## 核心特性

### 1. 实时数据写入

- 每次执行时，新收集的数据**立即写入**数据库
- 数据库中的活动记录表使用 UNIQUE 约束防止重复
- 安全事件表同样使用 UNIQUE 约束自动去重

```
执行流程：
收集数据 → 检查增量 → 保存到数据库 → 查询24小时数据 → 生成报告 → 发送邮件 → 记录执行
```

### 2. 增量日志解析

修改后的日志解析器支持从上次记录的时间戳开始解析新日志：

```python
# 获取上次执行的最后时间戳
last_execution = db_manager.get_last_execution()
since_timestamp = last_execution.get("last_activity_timestamp")

# 从该时间戳之后开始解析新日志
log_data = log_parser.parse_all_logs(target_date, since_timestamp)
```

**好处**：
- 避免重复处理已解析的日志
- 减少 CPU 和 I/O 消耗
- 加快执行速度

### 3. 24 小时滑动窗口报告

每次发送的邮件报告包含**最近 24 小时**的综合数据：

```python
# 计算时间窗口
now = datetime.now()
time_window_start = now - timedelta(hours=24)

# 查询数据库，过滤出24小时内的数据
recent_activities = [
    a for a in all_activities
    if datetime.fromisoformat(a.get("timestamp")) >= time_window_start
]
```

**优势**：
- 用户每次看到的是完整的最近 24 小时趋势
- 即使每小时执行一次也能获得完整上下文
- 避免碎片化的报告

### 4. 执行状态追踪

新增 `execution_tracking` 表记录每次执行的信息：

| 字段 | 说明 | 示例 |
|------|------|------|
| `execution_id` | 执行 ID（通常是执行时间） | `2026-02-02T16:15:29.007851` |
| `execution_time` | 实际执行完成时间 | `2026-02-02T16:15:29.095765` |
| `last_log_timestamp` | 上次处理的最后日志时间戳 | `2026-01-31T10:30:45.123456` |
| `last_activity_timestamp` | 上次处理的最后活动时间戳 | `2026-02-01T09:15:30.654321` |
| `execution_status` | 执行状态 | `success` / `failed` |
| `email_sent` | 是否发送邮件 | `0` / `1` |
| `created_at` | 创建时间 | `2026-02-02 16:15:29` |

查询上次执行：

```sql
SELECT * FROM execution_tracking
ORDER BY execution_time DESC
LIMIT 1;
```

## 使用方式

### 每次执行都发送报告

基础命令（每次执行都发送邮件）：

```bash
PYTHONPATH=src python -m main --run-once
```

### 从指定时间开始增量更新

如需从某个时间点之后的数据开始收集，可修改代码：

```python
# 在 main.py 中
monitor = OpenClawMonitor()

# 手动指定上次执行的时间戳
monitor.db_manager.record_execution(
    execution_id="manual_reset_point",
    last_activity_timestamp="2026-02-01T12:00:00.000000"
)

# 后续执行会从这个时间点开始增量
monitor.run_once()
```

### 后台定时执行

每小时执行一次，可在 `launchd` 配置中设置：

```xml
<!-- 在 ~/Library/LaunchAgents/com.openclaw.monitor.plist 中 -->
<key>StartInterval</key>
<integer>3600</integer>  <!-- 3600 秒 = 1 小时 -->
```

或每 30 分钟执行一次：

```xml
<integer>1800</integer>  <!-- 1800 秒 = 30 分钟 -->
```

## 数据库表结构

### 活动记录表（activity_records）

```sql
CREATE TABLE activity_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT DEFAULT 'info',
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, timestamp, activity_type, description)  -- 自动去重
);
```

### 安全事件表（security_events）

```sql
CREATE TABLE security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,
    source TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, timestamp, event_type, description)  -- 自动去重
);
```

### 执行追踪表（execution_tracking）

```sql
CREATE TABLE execution_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT UNIQUE NOT NULL,
    execution_time TEXT NOT NULL,
    last_log_timestamp TEXT,
    last_activity_timestamp TEXT,
    execution_status TEXT DEFAULT 'success',
    data_collected INTEGER DEFAULT 0,
    email_sent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 工作流示例

### 场景：每小时执行一次

```
09:00 - 第一次执行
  ├─ 收集全部数据（没有上次执行记录）
  ├─ 保存到数据库
  ├─ 查询最近24小时数据（08:00-09:00）
  ├─ 生成报告并发送邮件
  └─ 记录执行：last_activity_timestamp = 09:00

10:00 - 第二次执行
  ├─ 从 09:00 之后开始增量收集（更快）
  ├─ 保存新数据到数据库
  ├─ 查询最近24小时数据（09:00-10:00）
  ├─ 生成报告并发送邮件（包含09:00和10:00的综合视图）
  └─ 记录执行：last_activity_timestamp = 10:00

11:00 - 第三次执行
  ├─ 从 10:00 之后开始增量收集
  ├─ 保存新数据到数据库
  ├─ 查询最近24小时数据（10:00-11:00）
  ├─ 生成报告并发送邮件
  └─ 记录执行：last_activity_timestamp = 11:00
```

### 数据库变化

```
第一次执行后：
- activity_records: 10 条记录
- daily_reports: 生成一份报告

第二次执行后：
- activity_records: 15 条记录（新增5条）
- daily_reports: 更新（覆盖）现有报告

第三次执行后：
- activity_records: 22 条记录（新增7条）
- daily_reports: 再次更新
```

## 性能优化

### 1. 增量解析节省时间

```
全量解析：扫描所有 1000 行日志  (~100ms)
增量解析：仅处理最后 50 行新日志  (~5ms)  ✅ 快 20 倍
```

### 2. UNIQUE 约束自动去重

```sql
-- 重复尝试插入时
INSERT INTO activity_records (date, timestamp, activity_type, description, ...)
VALUES ('2026-02-01', '09:00:00', 'command', 'echo hello', ...);

-- 触发 UNIQUE 约束，被忽略（返回 False）
-- 不会创建重复记录
```

### 3. 数据库索引加快查询

```sql
CREATE INDEX idx_activity_date ON activity_records(date);
CREATE INDEX idx_security_date ON security_events(date);
CREATE INDEX idx_report_date ON daily_reports(date);
```

## 常见问题

### Q: 如果同一时间戳的事件发生了多次，会被去重吗？

A: 会。UNIQUE 约束基于 `(date, timestamp, activity_type, description)` 的组合。
- 相同时间戳、相同类型、相同描述的事件只会保存一条
- 如果你需要追踪多次相同事件，建议在 `description` 中加入计数或其他唯一标识

### Q: 增量更新失败了怎么办？

A: 即使增量收集失败，系统仍会：
1. 尝试收集所有数据（作为降级方案）
2. 记录执行状态为 `failed`
3. 发送包含错误信息的邮件

### Q: 如何清除执行记录重新开始增量？

A: 删除最后一条执行记录：

```sql
DELETE FROM execution_tracking
ORDER BY execution_time DESC
LIMIT 1;
```

下次执行会从头开始（无增量）。

### Q: 报告中为什么有旧数据？

A: 这是正常的！报告显示最近 24 小时的所有数据，包括：
- 本次执行新收集的数据
- 之前执行保存的数据

这样可以提供完整的时间窗口视图。

### Q: 能否改为只显示本次新增的数据？

A: 可以，修改 `report/generator.py` 的数据过滤逻辑，但不推荐，因为：
- 24 小时窗口能更好地反映趋势
- 多次执行能汇总完整上下文
- 只看增量数据容易遗漏信息

## 相关代码位置

| 功能 | 文件 | 方法 |
|------|------|------|
| 增量日志解析 | `monitor/log_parser.py` | `parse_all_logs(since_timestamp)` |
| 执行追踪 | `db/manager.py` | `record_execution()`, `get_last_execution()` |
| 24小时报告 | `report/generator.py` | `generate_html_report(time_window_hours=24)` |
| 主流程 | `main.py` | `generate_and_send_report(use_last_execution=True)` |

## 总结

✅ **每次执行都发送最新报告**
✅ **支持增量更新避免重复**
✅ **数据库自动去重**
✅ **24小时滑动窗口**
✅ **执行历史可追踪**
✅ **性能优化明显**

现在可以配置为每小时执行一次，持续监控 OpenClaw 活动！
