"""
基础监控类 - 抽象基类
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List


class BaseMonitor(ABC):
    """
    基础监控器抽象类
    所有具体的监控器都应继承此类
    """
    
    def __init__(self, name: str):
        """
        初始化监控器
        
        Args:
            name: 监控器名称
        """
        self.name = name
        self.data: List[Dict[str, Any]] = []
        self.start_time: datetime = None
        self.end_time: datetime = None
    
    @abstractmethod
    def collect(self, target_date: datetime = None) -> List[Dict[str, Any]]:
        """
        收集监控数据
        
        Args:
            target_date: 目标日期
        
        Returns:
            List[Dict[str, Any]]: 收集的数据列表
        """
        pass
    
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        分析收集的数据
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        pass
    
    def get_data(self) -> List[Dict[str, Any]]:
        """
        获取收集的原始数据
        
        Returns:
            List[Dict[str, Any]]: 数据列表
        """
        return self.data
    
    def clear_data(self):
        """清空数据"""
        self.data = []
