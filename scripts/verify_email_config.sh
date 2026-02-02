#!/bin/bash
# 邮箱配置验证脚本
# 用于快速检查 SMTP 配置是否正确

set -e

echo "🔍 OpenClawMonitor 邮箱配置检查工具"
echo "======================================"
echo ""

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "❌ 错误: 未找到 .env 文件"
    echo "请先运行: cp .env.example .env"
    exit 1
fi

echo "✅ 检查 .env 文件..."

# 加载环境变量
source .env

# 检查必要的环境变量
check_env_var() {
    local var_name=$1
    local var_value=${!var_name}
    
    if [ -z "$var_value" ]; then
        echo "❌ 缺少环境变量: $var_name"
        return 1
    else
        echo "✅ $var_name = ${var_value:0:20}..."
        return 0
    fi
}

echo ""
echo "📝 检查环境变量..."
all_ok=true

check_env_var "OPENCLAW_SMTP_SERVER" || all_ok=false
check_env_var "OPENCLAW_SMTP_PORT" || all_ok=false
if [ -z "$OPENCLAW_SMTP_USERNAME" ]; then
    echo "⚠️  OPENCLAW_SMTP_USERNAME 未设置（将默认使用发送者邮箱）"
else
    echo "✅ OPENCLAW_SMTP_USERNAME = ${OPENCLAW_SMTP_USERNAME:0:20}..."
fi
check_env_var "OPENCLAW_SENDER_EMAIL" || all_ok=false
check_env_var "OPENCLAW_SENDER_PASSWORD" || all_ok=false
check_env_var "OPENCLAW_RECIPIENT_EMAIL" || all_ok=false

if [ "$all_ok" = false ]; then
    echo ""
    echo "❌ 某些环境变量缺失，请更新 .env 文件"
    exit 1
fi

echo ""
echo "🌐 检查网络连接..."

# 测试到 SMTP 服务器的连接
if nc -zv "$OPENCLAW_SMTP_SERVER" "$OPENCLAW_SMTP_PORT" 2>&1 | grep -q succeeded; then
    echo "✅ 可以连接到 $OPENCLAW_SMTP_SERVER:$OPENCLAW_SMTP_PORT"
else
    echo "⚠️  无法连接到 $OPENCLAW_SMTP_SERVER:$OPENCLAW_SMTP_PORT"
    echo "   可能的原因:"
    echo "   1. SMTP 服务器地址不正确"
    echo "   2. SMTP 端口不正确"
    echo "   3. 防火墙阻止了连接"
fi

echo ""
echo "🐍 激活 Python 虚拟环境..."

if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate

echo "✅ 虚拟环境激活成功"

echo ""
echo "📧 测试邮箱配置..."

PYTHONPATH=src python3 << 'EOF'
import sys
import os
sys.path.insert(0, 'src')

from openclawmonitor.config import get_config
from openclawmonitor.report.notifier.email_sender import EmailNotifier

try:
    config = get_config()
    print(f"✅ 配置加载成功")
    print(f"   SMTP 服务器: {config.email.smtp_server}")
    print(f"   SMTP 端口: {config.email.smtp_port}")
    print(f"   发送者邮箱: {config.email.sender_email}")
    print(f"   接收者邮箱: {config.email.recipient_email}")
    print()
    
    # 尝试创建邮件通知程序
    notifier = EmailNotifier(
        smtp_server=config.email.smtp_server,
        smtp_port=config.email.smtp_port,
        sender_email=config.email.sender_email,
        sender_password=config.email.sender_password,
    )
    print("✅ 邮件通知程序初始化成功")
    print()
    
    # 发送测试邮件
    print("📤 发送测试邮件...")
    test_html = """
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>✅ OpenClawMonitor 邮箱配置测试</h2>
            <p>如果您收到这封邮件，说明 SMTP 配置正确！</p>
            <p><strong>测试时间:</strong> """ + str(__import__('datetime').datetime.now()) + """</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                这是一条自动测试邮件，无需回复。
            </p>
        </body>
    </html>
    """
    
    result = notifier.send(
        subject="[测试] OpenClawMonitor 邮箱配置验证",
        content=test_html,
        recipient_email=config.email.recipient_email,
    )
    
    if result:
        print("✅ 测试邮件发送成功！")
        print("   请检查 " + config.email.recipient_email + " 的收件箱")
    else:
        print("❌ 测试邮件发送失败")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 所有检查完成！邮箱配置正确。"
else
    echo ""
    echo "❌ 邮箱配置检查失败，请查看上面的错误信息"
    exit 1
fi
