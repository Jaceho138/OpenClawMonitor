# 邮箱配置指南

本指南说明如何配置各种邮箱服务与 OpenClawMonitor 一起使用。

## 目录

1. [Gmail（推荐）](#gmail推荐)
2. [企业邮箱（阿里云）](#企业邮箱阿里云)
3. [其他 SMTP 邮箱](#其他-smtp-邮箱)
4. [故障排除](#故障排除)

---

## Gmail（推荐）

### 步骤 1: 启用 2FA（双因素认证）

1. 访问 https://myaccount.google.com
2. 左侧菜单选择 **安全**
3. 启用**两步验证**

### 步骤 2: 生成应用专用密码

1. 访问 https://myaccount.google.com/apppasswords
2. 选择应用：**邮件**
3. 选择设备：**Mac**
4. Google 会生成 16 位密码，如：`abcd efgh ijkl mnop`

### 步骤 3: 配置 .env 文件

编辑 `.env` 文件，填入以下内容：

```bash
# SMTP 邮件服务器配置
OPENCLAW_SMTP_SERVER=smtp.gmail.com
OPENCLAW_SMTP_PORT=587
OPENCLAW_SMTP_USERNAME=your_email@gmail.com

# 邮件账户配置
OPENCLAW_SENDER_EMAIL=your_email@gmail.com
OPENCLAW_SENDER_PASSWORD=abcdefghijklmnop          # 16 位应用专用密码（去空格）
OPENCLAW_RECIPIENT_EMAIL=recipient@gmail.com

# 其他配置
OPENCLAW_DEBUG=false
```

### 步骤 4: 测试配置

运行以下命令测试：

```bash
source venv/bin/activate
PYTHONPATH=src python -m main --run-once --date 2024-01-15
```

检查输出中是否有 "邮件发送成功" 信息。

---

## 企业邮箱（阿里云）

### 前置条件

- 已开通阿里云企业邮箱
- 已获取 SMTP 服务器地址

### 步骤 1: 确认 SMTP 设置

登录阿里云邮箱控制台，查看邮箱设置：
- 点击 **设置** → **账户**
- 查看 **SMTP/POP3 设置** 部分
- 确认：
  - SMTP 服务器：通常为 `smtp.qiye.aliyun.com` 或 `smtp.mxhichina.com`
  - SMTP 端口：通常为 **465**（SSL）或 **25**（无加密）

### 步骤 2: 配置 .env 文件

编辑 `.env` 文件，填入以下内容：

```bash
# SMTP 邮件服务器配置
OPENCLAW_SMTP_SERVER=smtp.qiye.aliyun.com
OPENCLAW_SMTP_PORT=465
OPENCLAW_SMTP_USERNAME=your_email@company.com

# 邮件账户配置
OPENCLAW_SENDER_EMAIL=your_email@company.com
OPENCLAW_SENDER_PASSWORD=your_actual_password      # 邮箱密码
OPENCLAW_RECIPIENT_EMAIL=recipient@company.com

# 其他配置
OPENCLAW_DEBUG=false
```

### 步骤 3: 测试配置

```bash
source venv/bin/activate
PYTHONPATH=src python -m main --run-once --date 2024-01-15
```

---

## 其他 SMTP 邮箱

### 常见邮箱服务配置参考

| 邮箱服务 | SMTP 服务器 | 端口 | 加密方式 |
|---------|-----------|------|--------|
| **Outlook/Microsoft** | smtp-mail.outlook.com | 587 | TLS |
| **QQ 邮箱** | smtp.qq.com | 587 | TLS |
| **网易邮箱** | smtp.163.com | 587 | TLS |
| **新浪邮箱** | smtp.sina.cn | 587 | TLS |
| **腾讯企业邮** | smtp.exmail.qq.com | 587 | TLS |
| **SendGrid** | smtp.sendgrid.net | 587 | TLS |

### 通用配置模板

```bash
# 根据上表选择相应的 SMTP 服务器
OPENCLAW_SMTP_SERVER=smtp-mail.outlook.com
OPENCLAW_SMTP_PORT=587
OPENCLAW_SMTP_USERNAME=your_email@example.com

# 填入您的邮箱凭证
OPENCLAW_SENDER_EMAIL=your_email@example.com
OPENCLAW_SENDER_PASSWORD=your_password_or_app_token
OPENCLAW_RECIPIENT_EMAIL=recipient@example.com

# 调试模式
OPENCLAW_DEBUG=true                 # 设为 true 可查看详细日志
```

---

## 故障排除

### 问题 1: 邮件发送失败 - "Connection unexpectedly closed"

**原因**: SMTP 服务器连接被拒绝

**解决方案**:
1. 确认 SMTP 服务器地址是否正确
2. 确认端口号是否正确（587 TLS 或 465 SSL）
3. 尝试切换为其他端口：`25`, `465`, `587`, `2525`
4. 检查防火墙是否阻止了 SMTP 连接

```bash
# macOS 测试网络连接
nc -zv smtp.gmail.com 587
# 如果成功，应输出：Connection to smtp.gmail.com port 587 [tcp/submission] succeeded!
```

### 问题 2: 邮件发送失败 - "Invalid username or password"

**原因**: 邮箱凭证不正确

**解决方案**:
1. **Gmail 用户**: 确认使用的是 16 位应用专用密码，而非常规密码
2. **其他邮箱**: 确认密码是否包含特殊字符（如需转义）
3. 有些邮箱需要启用 "SMTP 认证"，请检查邮箱设置

```bash
# 输出详细日志来调试
OPENCLAW_DEBUG=true python -m main --run-once --date 2024-01-15
```

### 问题 3: 邮件发送失败 - "STARTTLS failed"

**原因**: TLS 握手失败，通常是 SSL/TLS 版本不匹配

**解决方案**:
1. 尝试使用 SSL 端口 `465` 而非 TLS 端口 `587`
2. 查看 `logs/openclaw_monitor.log` 中的详细错误信息

### 问题 4: 邮件发送成功但没有收到

**可能的原因**:
1. 检查收件箱的垃圾/推广文件夹
2. 确认接收者邮箱地址 `OPENCLAW_RECIPIENT_EMAIL` 是否正确
3. 某些企业邮箱可能有内容过滤，检查邮件服务器的审查规则

### 问题 5: 每日邮件没有发送

**可能的原因**:
1. 确认程序是否在运行（检查 launchd）
2. 查看 `logs/openclaw_monitor.log` 中是否有错误
3. 检查系统时间是否正确（邮件应在每天 08:00 AM 发送）

```bash
# 查看最近的日志
tail -f logs/openclaw_monitor.log

# 查看 launchd 状态
launchctl list | grep com.openclaw

# 查看 launchd 错误日志
tail -f logs/launchd.out.log
```

---

## 安全最佳实践

### 1. 不要提交 .env 文件到版本控制

确保 `.gitignore` 中包含 `.env`:

```bash
cat .gitignore | grep "\.env"
```

### 2. 使用应用专用密码（适用 Gmail）

永远不要在 `.env` 中存储 Gmail 主账户密码。使用 Google 应用专用密码。

### 3. 定期轮换凭证

对于企业邮箱，定期更改密码或重新生成应用令牌。

### 4. 使用系统 keyring（可选但推荐）

对于生产环境，可以将密码存储在 macOS Keyring 中：

```python
from openclawmonitor.report.notifier.email_sender import EmailNotifier

# 存储密码到 Keyring
EmailNotifier.save_password_to_keyring('your_email@gmail.com', 'abcdefghijklmnop')
```

然后在代码中使用：

```python
# 配置会自动从 Keyring 读取密码
```

### 5. 监控邮件发送日志

检查 `logs/openclaw_monitor.log` 中的邮件发送记录：

```bash
grep -i "邮件" logs/openclaw_monitor.log | tail -20
```

---

## 常见问题（FAQ）

**Q: 可以使用多个接收者吗？**
A: 当前版本只支持单个接收者。如需支持多个接收者，可修改 `report/notifier/email_sender.py` 中的逻辑。

**Q: 能否更改每日发送邮件的时间？**
A: 可以。修改 `main.py` 中 `schedule.every().day.at("08:00").do()` 为您需要的时间。

**Q: 如何测试邮件配置而不运行完整的监控？**
A: 运行以下命令：
```bash
source venv/bin/activate
PYTHONPATH=src python -c "
from openclawmonitor.report.notifier.email_sender import EmailNotifier
from openclawmonitor.config import get_config
config = get_config()
notifier = EmailNotifier(config)
notifier.send('测试', '<h1>这是一条测试邮件</h1>')
"
```

**Q: 企业邮箱支持哪些加密方式？**
A: 大多数现代 SMTP 服务器支持：
- **TLS**（587 端口，推荐）
- **SSL**（465 端口）
- **无加密**（25 端口，不安全，不推荐）

---

## 获取帮助

如有问题，请：
1. 查看 `logs/openclaw_monitor.log` 中的错误信息
2. 设置 `OPENCLAW_DEBUG=true` 获取详细日志
3. 参考本文档的故障排除部分
4. 检查对应邮箱服务的官方文档
