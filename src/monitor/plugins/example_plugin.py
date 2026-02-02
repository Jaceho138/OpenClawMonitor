"""
示例插件 - 演示如何创建自定义监控插件
"""

from datetime import datetime
from typing import Dict, Any, List
from ..base import BaseMonitor


class ExamplePlugin(BaseMonitor):
    """
    示例插件
    
    使用说明：
    1. 继承 BaseMonitor
    2. 实现 collect() 和 analyze() 方法
    3. 在主程序中注册和使用
    """
    
    def __init__(self):
        """初始化示例插件"""
        super().__init__("ExamplePlugin")
    
    def collect(self, target_date: datetime = None) -> List[Dict[str, Any]]:
        """
        收集数据
        
        Args:
            target_date: 目标日期
        
        Returns:
            List[Dict[str, Any]]: 收集的数据
        """
        self.data = [
            {
                "timestamp": datetime.now().isoformat(),
                "event": "example_event",
                "value": 42,
            }
        ]
        return self.data
    
    def analyze(self) -> Dict[str, Any]:
        """
        分析数据
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        return {
            "plugin_name": self.name,
            "data_count": len(self.data),
            "details": self.data,
        }
