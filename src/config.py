"""
配置加载模块 - 支持 YAML 文件、.env 文件和环境变量
"""

import os
import yaml
from pathlib import Path
from typing import Optional
from settings import OpenClawMonitorSettings

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: Optional[str] = None, env_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径（可选，默认为 config/config.yaml）
            env_path: .env 文件路径（可选，默认为项目根的 .env）
        """
        # 获取项目根目录（src 的上级目录）
        project_root = Path(__file__).parent.parent
        
        if config_path is None:
            config_path = project_root / "config" / "config.yaml"
        
        if env_path is None:
            env_path = project_root / ".env"
        
        self.config_path = Path(config_path)
        self.env_path = Path(env_path)
        
        # 加载 .env 文件
        if self.env_path.exists() and DOTENV_AVAILABLE:
            load_dotenv(self.env_path)
        elif self.env_path.exists() and not DOTENV_AVAILABLE:
            # 手动加载 .env 文件（如果 python-dotenv 不可用）
            self._manual_load_env()
    
    def load(self) -> OpenClawMonitorSettings:
        """
        加载配置
        
        Returns:
            OpenClawMonitorSettings: 配置对象
        """
        config_dict = {}
        
        # 1. 从 YAML 文件加载
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_dict = yaml.safe_load(f) or {}
        else:
            print(f"警告：配置文件不存在 {self.config_path}，使用默认配置")
        
        # 2. 环境变量覆盖
        if email_config := self._load_email_from_env():
            if "email" not in config_dict:
                config_dict["email"] = {}
            config_dict["email"].update(email_config)
        
        # 3. 验证并返回
        settings = OpenClawMonitorSettings(**config_dict)
        return settings
    
    @staticmethod
    def _manual_load_env():
        """
        手动加载 .env 文件（当 python-dotenv 不可用时）
        解析 .env 文件并设置环境变量
        """
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # 跳过空行和注释
                        if not line or line.startswith("#"):
                            continue
                        # 解析 KEY=VALUE 格式
                        if "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key.strip()] = value.strip()
            except Exception:
                pass  # 忽略解析错误
    
    @staticmethod
    def _load_email_from_env() -> dict:
        """
        从环境变量加载邮件配置
        
        Returns:
            dict: 邮件配置字典
        """
        email_config = {}
        
        # SMTP 服务器配置
        if smtp_server := os.getenv("OPENCLAW_SMTP_SERVER"):
            email_config["smtp_server"] = smtp_server
        
        if smtp_port := os.getenv("OPENCLAW_SMTP_PORT"):
            try:
                email_config["smtp_port"] = int(smtp_port)
            except ValueError:
                pass

        if smtp_username := os.getenv("OPENCLAW_SMTP_USERNAME"):
            email_config["smtp_username"] = smtp_username
        
        # 邮件内容配置
        if sender_email := os.getenv("OPENCLAW_SENDER_EMAIL"):
            email_config["sender_email"] = sender_email
        
        if sender_password := os.getenv("OPENCLAW_SENDER_PASSWORD"):
            email_config["sender_password"] = sender_password
        
        if recipient_email := os.getenv("OPENCLAW_RECIPIENT_EMAIL"):
            email_config["recipient_email"] = recipient_email
        
        return email_config


# 单例配置实例
_config_instance: Optional[OpenClawMonitorSettings] = None


def get_config(config_path: Optional[str] = None) -> OpenClawMonitorSettings:
    """
    获取全局配置实例（单例模式）
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        OpenClawMonitorSettings: 配置对象
    """
    global _config_instance
    
    if _config_instance is None:
        loader = ConfigLoader(config_path)
        _config_instance = loader.load()
    
    return _config_instance
