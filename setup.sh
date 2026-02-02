#!/bin/bash
# 快速启动指南 - 一键配置

echo "🚀 OpenClawMonitor 快速启动"
echo "================================"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 1. 创建虚拟环境
echo "📦 步骤 1: 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ 虚拟环境已创建"
else
    echo "✓ 虚拟环境已存在"
fi

# 2. 激活虚拟环境
echo ""
echo "📦 步骤 2: 激活虚拟环境..."
source venv/bin/activate
echo "✓ 虚拟环境已激活"

# 3. 安装依赖
echo ""
echo "📦 步骤 3: 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ 依赖已安装"

# 4. 创建必要的目录和文件
echo ""
echo "📦 步骤 4: 创建必要的目录..."
mkdir -p database logs
echo "✓ 目录已创建"

# 5. 提示用户配置
echo ""
echo "================================"
echo "✓ 初始化完成！"
echo "================================"
echo ""
echo "📝 后续配置步骤:"
echo ""
echo "1️⃣  编辑邮箱配置"
echo "   编辑 config/config.yaml，填入您的 Gmail 设置:"
echo "   - sender_email: 您的 Gmail 邮箱"
echo "   - sender_password: Gmail 应用专用密码"
echo "   - recipient_email: 接收者邮箱"
echo ""
echo "2️⃣  启用 OpenClaw 日志"
echo "   bash scripts/enable_logs.sh"
echo "   按照提示在 OpenClaw 中启用日志"
echo ""
echo "3️⃣  测试运行"
echo "   python -m main --run-once --date 2024-01-15"
echo ""
echo "4️⃣  后台运行"
echo "   bash scripts/install_launchd.sh"
echo ""
echo "📚 更多信息，请查看 README.md"
echo ""
