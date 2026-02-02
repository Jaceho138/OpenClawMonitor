#!/bin/bash
# 启用 OpenClaw 日志脚本

echo "此脚本帮助您启用 OpenClaw 的日志功能"
echo ""
echo "步骤 1: 打开 OpenClaw 应用"
echo "步骤 2: 打开菜单 -> 调试 (Debug)"
echo "步骤 3: 找到 'Logs' 部分"
echo "步骤 4: 启用 'App logging' -> 'Write rolling diagnostics log (JSONL)'"
echo "步骤 5: 重启 OpenClaw"
echo ""
echo "日志将保存到:"
echo "  ~/Library/Logs/OpenClaw/diagnostics.jsonl"
echo ""
echo "或者检查配置文件:"
cat "$HOME/.openclaw/openclaw.json" | grep -i "logging" || echo "未找到日志配置"
