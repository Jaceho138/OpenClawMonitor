"""
配置模型定义（使用 Pydantic 进行数据验证）
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path


class EmailConfig(BaseModel):
    """邮件配置"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    sender_email: str
    sender_password: str = Field(..., description="使用环境变量或 keyring 存储")
    recipient_email: str
    use_encryption: bool = True


class LogPathsConfig(BaseModel):
    """日志路径配置"""
    paths: List[str] = [
        "/tmp/openclaw/",
        "/private/tmp/openclaw/",
        "/Users/jaceho/.openclaw/logs/",
        "/Users/jaceho/.openclaw/workspace/logs/",
        "~/Library/Logs/OpenClaw/",
    ]
    diagnostics_log: str = "~/Library/Logs/OpenClaw/diagnostics.jsonl"


class DatabaseConfig(BaseModel):
    """数据库配置"""
    db_path: str = "database/openclaw_monitor.db"
    enable_logging: bool = True


class OpenClawMonitorSettings(BaseModel):
    """主配置模型"""
    base_path: str = "/Users/jaceho/.openclaw"
    log_paths: LogPathsConfig = LogPathsConfig()
    database: DatabaseConfig = DatabaseConfig()
    email: EmailConfig
    debug_mode: bool = False
    
    class Config:
        """Pydantic 配置"""
        case_sensitive = False
