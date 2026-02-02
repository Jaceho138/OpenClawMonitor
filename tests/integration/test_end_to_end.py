"""
集成测试 - 端到端工作流测试
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta


def test_end_to_end_data_collection():
    """测试端到端数据收集工作流"""
    # 这是一个占位符测试
    # 实际测试需要 mock OpenClaw 日志文件
    
    from openclawmonitor.main import OpenClawMonitor
    
    # 创建临时配置
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text("""
base_path: /tmp/test_openclaw
debug_mode: true
email:
  sender_email: test@example.com
  sender_password: test_password
  recipient_email: recipient@example.com
""")
        
        # 初始化监控程序
        monitor = OpenClawMonitor(str(config_path))
        
        # 验证组件已初始化
        assert monitor.db_manager is not None
        assert monitor.process_monitor is not None
        assert monitor.log_parser is not None
        assert monitor.security_analyzer is not None
