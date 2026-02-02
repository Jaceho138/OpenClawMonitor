"""
单元测试 - 配置模块测试
"""

import pytest
import tempfile
from pathlib import Path
from openclawmonitor.config import ConfigLoader, get_config
from openclawmonitor.settings import OpenClawMonitorSettings


def test_config_loader_with_existing_file():
    """测试从现有文件加载配置"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
base_path: /test/path
debug_mode: true
email:
  sender_email: test@example.com
  sender_password: test_password
  recipient_email: recipient@example.com
""")
        f.flush()
        
        loader = ConfigLoader(f.name)
        config = loader.load()
        
        assert config.base_path == "/test/path"
        assert config.debug_mode is True
        assert config.email.sender_email == "test@example.com"
        
        # 清理
        Path(f.name).unlink()


def test_config_singleton():
    """测试配置单例模式"""
    config1 = get_config()
    config2 = get_config()
    
    assert config1 is config2


def test_settings_validation():
    """测试设置验证"""
    settings = OpenClawMonitorSettings(
        email={
            "sender_email": "test@example.com",
            "sender_password": "password",
            "recipient_email": "recipient@example.com",
        }
    )
    
    assert settings.email.sender_email == "test@example.com"
    assert settings.database.db_path == "database/openclaw_monitor.db"
