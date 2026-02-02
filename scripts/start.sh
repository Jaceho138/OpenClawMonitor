#!/bin/bash
# 启动 OpenClawMonitor 脚本

# 获取脚本所在的目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 激活虚拟环境（如果存在）
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# 启动监控程序
cd "$PROJECT_ROOT"
python -m main "$@"
