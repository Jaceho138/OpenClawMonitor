"""
报告模块初始化
"""

from .generator import ReportGenerator
from .notifier import EmailNotifier

__all__ = ["ReportGenerator", "EmailNotifier"]
