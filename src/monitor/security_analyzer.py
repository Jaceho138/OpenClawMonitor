"""
安全分析模块 - 分析安全事件并计算安全评分
"""

from datetime import datetime
from typing import Dict, Any, List
import logging
from monitor.base import BaseMonitor


logger = logging.getLogger(__name__)


class SecurityAnalyzer(BaseMonitor):
    """
    安全分析器
    分析日志中的安全事件、权限请求和错误
    """
    
    # 文件分类标签
    SENSITIVE_PATHS = [
        "/Users",
        "/etc",
        "/private",
        "/System",
        "/Library",
        "/.aws",
        "/.ssh",
        "/.gnupg",
    ]
    
    SYSTEM_PATHS = [
        "/System",
        "/Library",
        "/usr",
        "/var",
        "/bin",
        "/sbin",
        "/opt",
    ]
    
    def __init__(self):
        """初始化安全分析器"""
        super().__init__("SecurityAnalyzer")
        self.security_score = 100  # 初始评分为 100
        self.events = []
    
    def collect(self, target_date: datetime = None, log_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        收集安全事件
        
        Args:
            target_date: 目标日期
            log_data: 日志解析结果
        
        Returns:
            List[Dict[str, Any]]: 安全事件列表
        """
        if log_data is None:
            log_data = {
                "commands": [],
                "file_accesses": [],
                "events": [],
                "missing_logs": False,
            }
        
        self.data = []
        self.events = []
        
        # 分析命令执行
        for cmd in log_data.get("commands", []):
            self.data.append({
                "type": "command",
                "timestamp": cmd.get("timestamp"),
                "command": cmd.get("command"),
                "severity": "info",
            })
        
        # 分析文件访问
        for access in log_data.get("file_accesses", []):
            classified = self._classify_file_access(access)
            self.data.append(classified)
        
        # 分析日志中的安全事件
        for event in log_data.get("events", []):
            self.data.append({
                "type": "security_event",
                "timestamp": event.get("timestamp"),
                "message": event.get("message"),
                "severity": self._determine_severity(event),
                "category": self._categorize_event(event),
            })
        
        # 如果日志缺失，添加警告事件
        if log_data.get("missing_logs", False):
            self.data.append({
                "type": "log_warning",
                "timestamp": (target_date or datetime.now()).isoformat(),
                "message": "日志文件缺失或未找到，安全分析可能不完整",
                "severity": "warning",
                "category": "log_management",
            })
            self.security_score -= 10
        
        return self.data
    
    def analyze(self) -> Dict[str, Any]:
        """
        分析安全数据，计算安全评分
        
        Returns:
            Dict[str, Any]: 安全分析结果
        """
        # 计算各类型事件的数量
        event_counts = {}
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        
        for event in self.data:
            event_type = event.get("type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            severity = event.get("severity", "info")
            severity_counts[severity] += 1
        
        # 根据严重事件调整安全评分
        self.security_score -= severity_counts["critical"] * 10
        self.security_score -= severity_counts["high"] * 5
        self.security_score -= severity_counts["medium"] * 2
        
        # 确保评分在 0-100 之间
        self.security_score = max(0, min(100, self.security_score))
        
        return {
            "security_score": self.security_score,
            "event_counts": event_counts,
            "severity_counts": severity_counts,
            "total_events": len(self.data),
            "events": self.data,
        }
    
    @staticmethod
    def _classify_file_access(access: Dict[str, Any]) -> Dict[str, Any]:
        """
        分类文件访问
        
        Args:
            access: 文件访问记录
        
        Returns:
            Dict[str, Any]: 分类后的访问记录
        """
        path = access.get("path", "")
        
        # 确定文件类型
        if any(path.startswith(sp) for sp in SecurityAnalyzer.SENSITIVE_PATHS):
            file_type = "sensitive"
            severity = "medium"
        elif any(path.startswith(sp) for sp in SecurityAnalyzer.SYSTEM_PATHS):
            file_type = "system"
            severity = "low"
        else:
            file_type = "user"
            severity = "low"
        
        return {
            "type": "file_access",
            "timestamp": access.get("timestamp"),
            "path": path,
            "file_type": file_type,
            "read": access.get("read", False),
            "write": access.get("write", False),
            "severity": severity,
        }
    
    @staticmethod
    def _determine_severity(event: Dict[str, Any]) -> str:
        """
        确定事件的严重级别
        
        Args:
            event: 事件记录
        
        Returns:
            str: 严重级别 (critical, high, medium, low, info)
        """
        message = (event.get("message") or "").lower()
        level = (event.get("level") or "info").lower()
        
        # 根据关键字确定严重级别
        if any(keyword in message for keyword in ["permission denied", "access denied", "unauthorized"]):
            return "high"
        elif any(keyword in message for keyword in ["error", "failed", "exception"]):
            return "medium"
        elif level == "warn":
            return "medium"
        else:
            return "info"
    
    @staticmethod
    def _categorize_event(event: Dict[str, Any]) -> str:
        """
        分类事件
        
        Args:
            event: 事件记录
        
        Returns:
            str: 事件类别
        """
        event_type = event.get("type", "").lower()
        
        if "permission" in event_type:
            return "permission"
        elif "security" in event_type:
            return "security"
        else:
            return "general"
