#!/bin/bash
# 快速验证脚本 - 检查项目结构和依赖

echo "================================"
echo "OpenClawMonitor 项目验证"
echo "================================"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 1. 检查 Python 版本
echo "✓ 检查 Python 版本..."
python3 --version

# 2. 检查项目结构
echo ""
echo "✓ 检查项目结构..."
required_dirs=(
    "src/openclawmonitor"
    "src/openclawmonitor/monitor"
    "src/openclawmonitor/db"
    "src/openclawmonitor/report"
    "src/openclawmonitor/utils"
    "config"
    "scripts"
    "tests"
    "database"
    "logs"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ✗ $dir (缺失)"
    fi
done

# 3. 检查关键文件
echo ""
echo "✓ 检查关键文件..."
required_files=(
    "src/openclawmonitor/main.py"
    "src/openclawmonitor/config.py"
    "config/config.yaml"
    "requirements.txt"
    "README.md"
    ".github/copilot-instructions.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (缺失)"
    fi
done

# 4. 检查虚拟环境
echo ""
echo "✓ 检查虚拟环境..."
if [ -d "venv" ]; then
    echo "  ✓ venv 已存在"
else
    echo "  ✗ venv 不存在，建议运行: python3 -m venv venv"
fi

# 5. 检查依赖安装
echo ""
echo "✓ 检查依赖安装..."
if [ -f "venv/bin/python" ]; then
    venv/bin/python -m pip list | grep -E "psutil|watchdog|pandas|matplotlib|schedule|pydantic" || echo "  ✗ 某些依赖未安装"
else
    echo "  ✗ 虚拟环境未激活"
fi

# 6. 测试导入
echo ""
echo "✓ 测试模块导入..."
python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from openclawmonitor.config import get_config
    print('  ✓ 配置模块导入成功')
    from openclawmonitor.monitor.base import BaseMonitor
    print('  ✓ 监控模块导入成功')
    from openclawmonitor.db.manager import DatabaseManager
    print('  ✓ 数据库模块导入成功')
except Exception as e:
    print(f'  ✗ 导入失败: {e}')
" 2>/dev/null || echo "  ✗ 导入测试失败"

# 7. 生成摘要
echo ""
echo "================================"
echo "✓ 项目验证完成"
echo "================================"
echo ""
echo "后续步骤:"
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 安装依赖: pip install -r requirements.txt"
echo "3. 配置邮箱: 编辑 config/config.yaml"
echo "4. 启用日志: bash scripts/enable_logs.sh"
echo "5. 测试运行: python -m main --run-once"
echo ""
