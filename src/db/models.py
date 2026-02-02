"""
数据库模型定义（使用 Pydantic）
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ActivityRecord(BaseModel):
    """活动记录"""
    
    id: Optional[int] = None
    date: str  # YYYY-MM-DD
    timestamp: str  # ISO 格式时间
    activity_type: str  # 'process', 'command', 'file_access', 'security_event'
    description: str
    severity: str = "info"  # 'critical', 'high', 'medium', 'low', 'info'
    details: Optional[str] = None  # JSON 字符串
    
    class Config:
        """Pydantic 配置"""
        pass


class SecurityEvent(BaseModel):
    """安全事件"""
    
    id: Optional[int] = None
    date: str  # YYYY-MM-DD
    timestamp: str  # ISO 格式时间
    event_type: str  # 'permission_denied', 'unauthorized_access', 等
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    source: Optional[str] = None  # 事件来源
    details: Optional[str] = None  # 详细信息（JSON 字符串）
    
    class Config:
        """Pydantic 配置"""
        pass


class DailyReport(BaseModel):
    """日报告"""
    
    id: Optional[int] = None
    date: str  # YYYY-MM-DD
    generated_at: str  # 生成时间
    security_score: int  # 0-100
    total_events: int
    process_count: int
    command_count: int
    file_access_count: int
    security_event_count: int
    summary: str  # HTML 摘要
    
    class Config:
        """Pydantic 配置"""
        pass
