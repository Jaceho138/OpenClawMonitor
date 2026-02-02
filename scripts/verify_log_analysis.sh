#!/bin/bash
#
# OpenClaw 日志分析功能验证脚本
# 用于验证所有组件是否正确安装和配置
#

echo "=================================================="
echo "OpenClaw 日志分析功能验证"
echo "=================================================="
echo ""

# 检查项目目录
echo "1. 检查项目目录..."
if [ -d "/Users/jaceho/Python/Project/OpenClawMonitor" ]; then
    echo "   ✅ 项目目录存在"
else
    echo "   ❌ 项目目录不存在"
    exit 1
fi

cd /Users/jaceho/Python/Project/OpenClawMonitor

# 检查核心文件
echo ""
echo "2. 检查核心文件..."

files=(
    "src/openclawmonitor/monitor/openclaw_log_analyzer.py"
    "src/openclawmonitor/monitor/openclaw_report_generator.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo "   ✅ $file ($lines 行)"
    else
        echo "   ❌ $file 不存在"
    fi
done

# 检查文档
echo ""
echo "3. 检查文档文件..."

docs=(
    "docs/OPENCLAW_LOG_ANALYSIS.md"
    "docs/QUICKSTART_LOG_ANALYSIS.md"
    "docs/OPENCLAW_ANALYSIS_SUMMARY.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        size=$(du -h "$doc" | cut -f1)
        echo "   ✅ $doc ($size)"
    else
        echo "   ❌ $doc 不存在"
    fi
done

# 检查日志目录
echo ""
echo "4. 检查 OpenClaw 日志目录..."
if [ -d "/private/tmp/openclaw" ]; then
    log_count=$(ls -1 /private/tmp/openclaw/*.log 2>/dev/null | wc -l)
    if [ $log_count -gt 0 ]; then
        echo "   ✅ 日志目录存在，找到 $log_count 个日志文件"
        latest=$(ls -t /private/tmp/openclaw/*.log 2>/dev/null | head -1)
        size=$(du -h "$latest" | cut -f1)
        echo "      最新日志: $(basename "$latest") ($size)"
    else
        echo "   ⚠️  日志目录存在但没有日志文件"
    fi
else
    echo "   ⚠️  日志目录不存在: /private/tmp/openclaw"
fi

# 检查 Python 环境
echo ""
echo "5. 检查 Python 环境..."
if [ -d "venv" ]; then
    echo "   ✅ 虚拟环境存在"
    source venv/bin/activate
    
    # 设置 PYTHONPATH
    export PYTHONPATH=src
    
    # 检查依赖
    if python -c "from openclawmonitor.monitor.openclaw_log_analyzer import OpenClawLogAnalyzer" 2>/dev/null; then
        echo "   ✅ OpenClawLogAnalyzer 可导入"
    else
        echo "   ❌ OpenClawLogAnalyzer 导入失败"
    fi
    
    if python -c "from openclawmonitor.monitor.openclaw_report_generator import OpenClawReportGenerator" 2>/dev/null; then
        echo "   ✅ OpenClawReportGenerator 可导入"
    else
        echo "   ❌ OpenClawReportGenerator 导入失败"
    fi
else
    echo "   ⚠️  虚拟环境不存在"
fi

# 检查报告目录
echo ""
echo "6. 检查报告输出..."
if [ -d "reports" ]; then
    report_count=$(ls -1 reports/openclaw_analysis_*.html 2>/dev/null | wc -l)
    if [ $report_count -gt 0 ]; then
        echo "   ✅ 找到 $report_count 个分析报告"
        latest_report=$(ls -t reports/openclaw_analysis_*.html 2>/dev/null | head -1)
        size=$(du -h "$latest_report" | cut -f1)
        echo "      最新报告: $(basename "$latest_report") ($size)"
    else
        echo "   ℹ️  尚未生成分析报告"
    fi
else
    echo "   ⚠️  报告目录不存在"
fi

# 测试运行（可选）
echo ""
echo "7. 测试运行（可选）..."
echo "   运行以下命令进行完整测试："
echo ""
echo "   cd /Users/jaceho/Python/Project/OpenClawMonitor"
echo "   source venv/bin/activate"
echo "   PYTHONPATH=src python -m main --run-once"
echo ""

# 总结
echo ""
echo "=================================================="
echo "验证完成！"
echo "=================================================="
echo ""
echo "📚 查看文档："
echo "   - 完整功能文档: docs/OPENCLAW_LOG_ANALYSIS.md"
echo "   - 快速开始:     docs/QUICKSTART_LOG_ANALYSIS.md"
echo "   - 实现总结:     docs/OPENCLAW_ANALYSIS_SUMMARY.md"
echo ""
echo "🚀 快速运行："
echo "   bash scripts/test_log_analysis.sh"
echo ""
