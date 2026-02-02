"""
日志解析模块 - 解析 JSONL 格式的日志文件
"""

import json
import glob
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from utils.path_resolver import PathResolver


logger = logging.getLogger(__name__)


class LogParser:
    """
    日志解析器
    支持多路径、多格式的日志解析
    """
    
    def __init__(self, log_paths: List[str]):
        """
        初始化日志解析器
        
        Args:
            log_paths: 日志路径列表
        """
        self.log_paths = log_paths
        self.path_resolver = PathResolver(log_paths)
        self.parsed_logs = []
    
    def parse_all_logs(self, target_date: datetime = None, since_timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        解析所有配置路径中的日志文件
        
        Args:
            target_date: 目标日期（默认为昨天）
            since_timestamp: 仅解析此时间戳之后的日志（用于增量更新）
        
        Returns:
            Dict[str, Any]: {
                'commands': [...],
                'file_accesses': [...],
                'events': [...],
                'missing_logs': bool
            }
        """
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        
        # 解析所有路径中的日志
        found_logs = self.path_resolver.resolve_all_logs(target_date)
        
        commands = []
        file_accesses = []
        events = []
        
        for path_pattern, files in found_logs.items():
            for file_path in files:
                try:
                    logger.info(f"解析日志文件: {file_path}")
                    
                    # 如果是 JSONL 格式
                    if file_path.endswith('.jsonl') or file_path.endswith('.log'):
                        parsed = self._parse_jsonl_file(file_path, since_timestamp)
                        commands.extend(parsed.get("commands", []))
                        file_accesses.extend(parsed.get("file_accesses", []))
                        events.extend(parsed.get("events", []))
                    
                except Exception as e:
                    logger.error(f"解析日志文件失败 {file_path}: {e}")
        
        # 检查是否找到日志
        missing_logs = len(found_logs) == 0
        
        if missing_logs:
            logger.warning(
                f"未找到 {target_date.strftime('%Y-%m-%d')} 的日志文件。"
                "请检查 ~/.openclaw/openclaw.json 的 logging.file 和 level 配置"
            )
        
        return {
            "target_date": target_date.isoformat(),
            "commands": commands,
            "file_accesses": file_accesses,
            "events": events,
            "missing_logs": missing_logs,
            "found_logs_count": len([f for files in found_logs.values() for f in files]),
        }
    
    @staticmethod
    def _parse_jsonl_file(file_path: str, since_timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        解析单个 JSONL 文件
        
        Args:
            file_path: 文件路径
            since_timestamp: 仅解析此时间戳之后的日志
        
        Returns:
            Dict[str, Any]: 解析的数据
        """
        commands = []
        file_accesses = []
        events = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        # 如果指定了 since_timestamp，跳过之前的日志
                        if since_timestamp and data.get("timestamp"):
                            if data.get("timestamp") <= since_timestamp:
                                continue
                        
                        # 提取命令信息
                        if any(key in data for key in ['exec', 'command', 'cmd']):
                            cmd_entry = {
                                "line": line_num,
                                "timestamp": data.get("timestamp"),
                                "command": data.get("exec") or data.get("command") or data.get("cmd"),
                                "type": "exec",
                            }
                            commands.append(cmd_entry)
                        
                        # 提取文件访问信息
                        if any(key in data for key in ['path', 'file', 'read', 'write']):
                            access_entry = {
                                "line": line_num,
                                "timestamp": data.get("timestamp"),
                                "path": data.get("path") or data.get("file"),
                                "type": data.get("type", "access"),
                                "read": data.get("read", False),
                                "write": data.get("write", False),
                            }
                            file_accesses.append(access_entry)
                        
                        # 提取安全事件
                        if any(key in data for key in ['error', 'permission', 'security']):
                            event_entry = {
                                "line": line_num,
                                "timestamp": data.get("timestamp"),
                                "level": data.get("level", "info"),
                                "message": data.get("message") or data.get("error"),
                                "type": "security" if "permission" in data else "event",
                            }
                            events.append(event_entry)
                    
                    except json.JSONDecodeError as e:
                        logger.debug(f"JSON 解析错误 {file_path}:{line_num} - {e}")
        
        except FileNotFoundError:
            logger.warning(f"日志文件不存在: {file_path}")
        
        return {
            "commands": commands,
            "file_accesses": file_accesses,
            "events": events,
        }
    
    def parse_exec_approvals(self, approvals_file: str = None) -> List[Dict[str, Any]]:
        """
        解析命令执行审批文件
        
        Args:
            approvals_file: 审批文件路径（默认为 ~/.openclaw/exec-approvals.json）
        
        Returns:
            List[Dict[str, Any]]: 执行的命令列表
        """
        if approvals_file is None:
            approvals_file = os.path.expanduser("~/.openclaw/exec-approvals.json")
        
        approvals = []
        
        try:
            if os.path.exists(approvals_file):
                with open(approvals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 提取已批准的命令
                    if isinstance(data, list):
                        approvals = data
                    elif isinstance(data, dict):
                        approvals = data.get("approvals", [])
                
                logger.info(f"从 {approvals_file} 加载了 {len(approvals)} 条命令记录")
            else:
                logger.info(f"审批文件不存在: {approvals_file}")
        
        except Exception as e:
            logger.error(f"解析审批文件失败 {approvals_file}: {e}")
        
        return approvals
