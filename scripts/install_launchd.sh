#!/bin/bash
# 安装 launchd 服务脚本

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"
LAUNCH_AGENT_FILE="$LAUNCH_AGENT_DIR/com.openclaw.monitor.plist"

# 创建 LaunchAgent 目录
mkdir -p "$LAUNCH_AGENT_DIR"

# 创建 plist 文件
cat > "$LAUNCH_AGENT_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.monitor</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$PROJECT_ROOT/scripts/start.sh</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>WorkingDirectory</key>
    <string>$PROJECT_ROOT</string>
    
    <key>StandardOutPath</key>
    <string>$PROJECT_ROOT/logs/launchd.out.log</string>
    
    <key>StandardErrorPath</key>
    <string>$PROJECT_ROOT/logs/launchd.err.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

echo "LaunchAgent 已创建: $LAUNCH_AGENT_FILE"

# 加载 LaunchAgent
launchctl load "$LAUNCH_AGENT_FILE"
echo "LaunchAgent 已加载"

# 显示状态
launchctl list | grep com.openclaw.monitor
