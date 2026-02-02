"""
通知基类 - 支持多种通知方式
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging


logger = logging.getLogger(__name__)


class BaseNotifier(ABC):
    """
    基础通知器抽象类
    支持扩展不同的通知方式（邮件、Slack、WeChat 等）
    """
    
    def __init__(self, name: str):
        """
        初始化通知器
        
        Args:
            name: 通知器名称
        """
        self.name = name
    
    @abstractmethod
    def send(self, subject: str, content: str, **kwargs) -> bool:
        """
        发送通知
        
        Args:
            subject: 主题
            content: 内容
            **kwargs: 其他参数
        
        Returns:
            bool: 是否发送成功
        """
        pass
    
    def log_status(self, success: bool, message: str = ""):
        """
        记录发送状态
        
        Args:
            success: 是否成功
            message: 消息
        """
        status = "成功" if success else "失败"
        logger.info(f"通知发送 [{self.name}] {status}: {message}")
