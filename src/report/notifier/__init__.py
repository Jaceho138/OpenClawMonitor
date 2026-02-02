"""
通知模块初始化
"""

from .base_notifier import BaseNotifier
from .email_sender import EmailNotifier

__all__ = ["BaseNotifier", "EmailNotifier"]
