"""
多路径日志解析模块
用于解析配置中的多个日志路径，支持 glob 模式
"""

import glob
import os
from pathlib import Path
from typing import List
from datetime import datetime, timedelta


class PathResolver:
    """日志路径解析器"""
    
    def __init__(self, log_paths: List[str]):
        """
        初始化路径解析器
        
        Args:
            log_paths: 日志路径列表（支持 ~ 和 glob 模式）
        """
        self.log_paths = log_paths
        self.logger = None  # 在需要时注入
    
    def resolve_all_logs(self, target_date: datetime = None) -> dict:
        """
        解析所有配置的日志路径，返回找到的日志文件
        
        Args:
            target_date: 目标日期（默认为昨天）
        
        Returns:
            dict: {路径: [文件列表]}
        """
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        
        found_logs = {}
        
        for path_pattern in self.log_paths:
            # 展开 ~ 和环境变量
            expanded_path = os.path.expanduser(os.path.expandvars(path_pattern))
            
            # 使用 glob 查找匹配的文件
            matching_files = self._find_logs_by_pattern(expanded_path, target_date)
            
            if matching_files:
                found_logs[path_pattern] = matching_files
                if self.logger:
                    self.logger.info(f"在 {path_pattern} 中找到 {len(matching_files)} 个日志文件")
        
        if not found_logs and self.logger:
            self.logger.warning(
                f"未在任何配置的路径中找到 {target_date.strftime('%Y-%m-%d')} 的日志文件"
            )
        
        return found_logs
    
    @staticmethod
    def _find_logs_by_pattern(path_pattern: str, target_date: datetime) -> List[str]:
        """
        根据模式查找日志文件
        
        Args:
            path_pattern: 路径模式（可能包含 glob）
            target_date: 目标日期
        
        Returns:
            List[str]: 找到的文件路径列表
        """
        date_str = target_date.strftime("%Y-%m-%d")
        matching_files = []
        
        try:
            # 支持多种日志名称格式
            patterns = [
                f"{path_pattern}/openclaw-{date_str}.log",
                f"{path_pattern}/openclaw-{date_str}.jsonl",
                f"{path_pattern}/*{date_str}*.log",
                f"{path_pattern}/*{date_str}*.jsonl",
                f"{path_pattern}/openclaw*.log",
                f"{path_pattern}/openclaw*.jsonl",
            ]
            
            for pattern in patterns:
                files = glob.glob(pattern)
                for file in files:
                    if os.path.isfile(file) and file not in matching_files:
                        matching_files.append(file)
        except Exception:
            pass  # 忽略 glob 错误
        
        return matching_files
    
    @staticmethod
    def get_daily_log_pattern(base_path: str, target_date: datetime = None) -> str:
        """
        生成每日日志的 glob 模式
        
        Args:
            base_path: 基础路径
            target_date: 目标日期（默认为昨天）
        
        Returns:
            str: glob 模式字符串
        """
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        
        date_str = target_date.strftime("%Y-%m-%d")
        return f"{base_path}/*{date_str}*.log"
