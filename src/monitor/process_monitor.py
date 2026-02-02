"""
进程监控模块 - 使用 psutil 监控 OpenClaw 进程
"""

import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from monitor.base import BaseMonitor


logger = logging.getLogger(__name__)


class ProcessMonitor(BaseMonitor):
    """
    进程监控器
    监控 OpenClaw 相关的进程（如 bot.molt）
    """
    
    def __init__(self, target_process_names: List[str] = None):
        """
        初始化进程监控器
        
        Args:
            target_process_names: 目标进程名称列表（默认为 ['bot.molt', 'python']）
        """
        super().__init__("ProcessMonitor")
        self.target_process_names = target_process_names or ["bot.molt", "python"]
        self.process_history = {}
    
    def collect(self, target_date: datetime = None) -> List[Dict[str, Any]]:
        """
        收集进程监控数据
        
        Args:
            target_date: 目标日期（此模块中主要获取当前进程信息）
        
        Returns:
            List[Dict[str, Any]]: 进程信息列表
        """
        self.data = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                # 检查是否是目标进程
                if any(target in proc.info['name'] for target in self.target_process_names):
                    process_info = {
                        "timestamp": datetime.now().isoformat(),
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "memory_mb": proc.info['memory_info'].rss / 1024 / 1024,
                        "cpu_percent": proc.cpu_percent(interval=0.1),
                    }
                    
                    # 尝试获取进程启动时间
                    try:
                        create_time = datetime.fromtimestamp(proc.create_time())
                        duration = datetime.now() - create_time
                        process_info["create_time"] = create_time.isoformat()
                        process_info["duration_seconds"] = int(duration.total_seconds())
                    except (psutil.NoSuchProcess, OSError):
                        pass
                    
                    self.data.append(process_info)
                    logger.debug(f"捕获进程: {proc.info['name']} (PID: {proc.info['pid']})")
            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return self.data
    
    def analyze(self) -> Dict[str, Any]:
        """
        分析进程数据
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        if not self.data:
            return {
                "total_processes": 0,
                "total_memory_mb": 0,
                "average_cpu_percent": 0,
            }
        
        total_memory = sum(p.get("memory_mb", 0) for p in self.data)
        avg_cpu = sum(p.get("cpu_percent", 0) for p in self.data) / len(self.data)
        
        return {
            "total_processes": len(self.data),
            "total_memory_mb": round(total_memory, 2),
            "average_cpu_percent": round(avg_cpu, 2),
            "process_details": self.data,
        }
