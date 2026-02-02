"""
OpenClaw 系统日志分析器 - 从系统日志提取监控数据
"""

import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OpenClawLogAnalyzer:
    """
    OpenClaw 系统日志分析器
    解析系统级别的网关、会话、运行日志，提取监控指标
    """
    
    def __init__(self):
        """初始化分析器"""
        self.events = []
        self.runs = {}
        self.sessions = {}
        self.errors = []
        self.api_methods = {}
        self.external_channels = {}
        self.statistics = {
            "total_lines": 0,
            "parsed_lines": 0,
            "runs": 0,
            "sessions": 0,
            "errors": 0,
            "file_accesses": 0,
            "api_calls": 0,
            "api_errors": 0,
            "external_conversations": 0,
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        分析日志文件
        
        Args:
            file_path: 日志文件路径
        
        Returns:
            Dict: 分析结果
        """
        logger.info(f"开始分析日志文件: {file_path}")
        self.events = []
        self.runs = {}
        self.sessions = {}
        self.errors = []
        self.api_methods = {}
        self.external_channels = {}
        self.statistics = {
            "total_lines": 0,
            "parsed_lines": 0,
            "runs": 0,
            "sessions": 0,
            "errors": 0,
            "file_accesses": 0,
            "api_calls": 0,
            "api_errors": 0,
            "external_conversations": 0,
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    self.statistics["total_lines"] += 1
                    
                    try:
                        data = json.loads(line)
                        self.statistics["parsed_lines"] += 1
                        
                        # 提取事件
                        event = self._extract_event(data, line_num)
                        if event:
                            self.events.append(event)
                            
                            # 分类处理不同类型的事件
                            self._process_event(event)
                    
                    except json.JSONDecodeError:
                        logger.debug(f"第 {line_num} 行: JSON 解析失败")
                        continue
            
            logger.info(f"分析完成: {self.statistics['parsed_lines']}/{self.statistics['total_lines']} 行")
            
            return self._generate_report()
        
        except Exception as e:
            logger.error(f"分析文件失败: {e}")
            return {"error": str(e)}
    
    def _extract_event(self, data: dict, line_num: int) -> Optional[Dict[str, Any]]:
        """
        从日志行提取事件
        
        Args:
            data: JSON 数据
            line_num: 行号
        
        Returns:
            Dict: 事件或 None
        """
        if not isinstance(data, dict):
            return None
        
        # 获取基础信息
        timestamp = data.get('_meta', {}).get('date') or data.get('time')
        subsystem = data.get('_meta', {}).get('name', '')
        log_level = data.get('_meta', {}).get('logLevelName', 'INFO')
        
        # 获取消息内容
        message_parts = []
        for i in range(10):
            key = str(i)
            if key in data:
                val = data[key]
                if isinstance(val, dict):
                    message_parts.append(json.dumps(val))
                else:
                    message_parts.append(str(val))
        
        message = " ".join(message_parts)
        clean_message = self._strip_ansi(message)
        
        event = {
            "timestamp": timestamp,
            "subsystem": subsystem,
            "log_level": log_level,
            "message": message,
            "clean_message": clean_message,
            "line_num": line_num,
            "type": self._classify_event(clean_message, subsystem),
        }
        
        return event
    
    def _classify_event(self, message: str, subsystem: str) -> str:
        """
        分类事件类型
        
        Args:
            message: 消息内容
            subsystem: 子系统
        
        Returns:
            str: 事件类型
        """
        message_lower = message.lower()
        
        # 运行相关
        if 'run' in message_lower and 'embedded' in message_lower:
            if 'start' in message_lower:
                return 'run_start'
            elif 'done' in message_lower or 'complete' in message_lower:
                return 'run_complete'
            else:
                return 'run_event'
        
        # 会话相关
        if 'session' in message_lower:
            if 'state' in message_lower:
                return 'session_state'
            else:
                return 'session_event'
        
        # 网关相关
        if 'gateway' in subsystem.lower():
            if 'listening' in message_lower:
                return 'gateway_listening'
            elif 'mounted' in message_lower:
                return 'gateway_mounted'
            else:
                return 'gateway_event'
        
        # 连接相关
        if 'connection' in message_lower or 'connect' in message_lower:
            if 'close' in message_lower or 'closed' in message_lower:
                return 'connection_closed'
            else:
                return 'connection_event'
        
        # 错误和警告
        if message_lower in ['ERROR', 'WARN', 'WARNING']:
            return 'error'
        
        # 文件访问
        if any(word in message_lower for word in ['file', 'path', '/users', '/tmp']):
            return 'file_access'
        
        return 'other'
    
    def _process_event(self, event: Dict[str, Any]):
        """
        处理事件，更新统计
        
        Args:
            event: 事件对象
        """
        event_type = event.get('type', 'other')
        clean_message = event.get('clean_message', event.get('message', ''))
        
        # 统计运行
        if 'run' in event_type:
            self.statistics["runs"] += 1
            
            # 尝试提取 runId
            run_id = self._extract_run_id(event['message'])
            if run_id:
                if run_id not in self.runs:
                    self.runs[run_id] = {
                        'start': None,
                        'complete': None,
                        'status': 'unknown',
                    }
                
                if event_type == 'run_start':
                    self.runs[run_id]['start'] = event['timestamp']
                    self.runs[run_id]['status'] = 'running'
                elif event_type == 'run_complete':
                    self.runs[run_id]['complete'] = event['timestamp']
                    self.runs[run_id]['status'] = 'complete'
        
        # 统计会话
        if 'session' in event_type:
            self.statistics["sessions"] += 1
            
            # 尝试提取 sessionId
            session_id = self._extract_session_id(event['message'])
            if session_id:
                if session_id not in self.sessions:
                    self.sessions[session_id] = {
                        'start': event['timestamp'],
                        'state': 'active',
                    }
                
                if event_type == 'session_state':
                    self.sessions[session_id]['state'] = self._extract_session_state(event['message'])
        
        # 统计错误
        if event.get('log_level') in ['ERROR', 'WARN']:
            self.statistics["errors"] += 1
            self.errors.append(event)
        
        # 统计文件访问
        if event_type == 'file_access':
            self.statistics["file_accesses"] += 1

        # 统计 API 使用情况
        api_method = self._extract_api_method(clean_message, event.get('subsystem', ''))
        if api_method:
            self.statistics["api_calls"] += 1
            self.api_methods[api_method] = self.api_methods.get(api_method, 0) + 1
            if event.get('log_level') in ['ERROR', 'WARN'] or 'failed' in clean_message.lower():
                self.statistics["api_errors"] += 1

        # 统计外部对话（频道）情况
        channel = self._detect_external_channel(clean_message, event.get('subsystem', ''))
        if channel:
            self.statistics["external_conversations"] += 1
            self.external_channels[channel] = self.external_channels.get(channel, 0) + 1

    @staticmethod
    def _strip_ansi(text: str) -> str:
        """
        去除 ANSI 颜色控制字符
        """
        return re.sub(r"\x1b\[[0-9;]*m", "", text or "")

    @staticmethod
    def _extract_api_method(message: str, subsystem: str) -> Optional[str]:
        """
        从消息中提取 API 方法名（如 chat.history / agent.turn）
        """
        if not message:
            return None

        subsystem_lower = (subsystem or "").lower()
        if "gateway/ws" not in subsystem_lower and "gateway" not in subsystem_lower and "agent" not in subsystem_lower:
            return None

        # 例: "res chat.history 61ms conn=..."
        method_match = re.search(r"\b(req|res)\b\s+([a-zA-Z][\w./:-]+)", message)
        if method_match:
            return method_match.group(2)

        # 兜底: method=xxx
        method_match = re.search(r"\bmethod=([a-zA-Z][\w./:-]+)", message)
        if method_match:
            return method_match.group(1)

        # 兜底: 已知常见方法
        message_lower = message.lower()
        common_methods = [
            "chat.history",
            "agent.turn",
            "agent.reply",
            "gateway.call",
            "models.status",
            "models.list",
        ]
        for method in common_methods:
            if method in message_lower:
                return method

        return None

    @staticmethod
    def _detect_external_channel(message: str, subsystem: str) -> Optional[str]:
        """
        检测外部对话渠道
        """
        channels = [
            "telegram", "whatsapp", "discord", "slack", "signal",
            "imessage", "nostr", "msteams", "mattermost", "matrix",
            "bluebubbles", "line", "zalo", "googlechat", "webchat",
            "wechat", "qq", "sms",
        ]

        subsystem_lower = (subsystem or "").lower()
        message_lower = (message or "").lower()

        if "gateway/channels/" in subsystem_lower:
            channel = subsystem_lower.split("/")[-1]
            return channel

        if "gateway/ws" in subsystem_lower:
            if "webchat" in message_lower or "control-ui" in message_lower:
                return "webchat"

        for channel in channels:
            if channel in message_lower:
                return channel

        return None
    
    def _extract_run_id(self, message: str) -> Optional[str]:
        """
        从消息中提取 runId
        
        Args:
            message: 消息内容
        
        Returns:
            str: runId 或 None
        """
        pattern = r'runId=([a-f0-9\-]+)'
        match = re.search(pattern, message)
        return match.group(1) if match else None
    
    def _extract_session_id(self, message: str) -> Optional[str]:
        """
        从消息中提取 sessionId
        
        Args:
            message: 消息内容
        
        Returns:
            str: sessionId 或 None
        """
        pattern = r'sessionId=([a-f0-9\-]+)'
        match = re.search(pattern, message)
        return match.group(1) if match else None
    
    def _extract_session_state(self, message: str) -> str:
        """
        从消息中提取会话状态
        
        Args:
            message: 消息内容
        
        Returns:
            str: 状态
        """
        if 'active' in message.lower():
            return 'active'
        elif 'inactive' in message.lower() or 'closed' in message.lower():
            return 'inactive'
        else:
            return 'unknown'
    
    def _generate_report(self) -> Dict[str, Any]:
        """
        生成分析报告
        
        Returns:
            Dict: 报告数据
        """
        # 计算时间范围
        timestamps = [e.get('timestamp') for e in self.events if e.get('timestamp')]
        timestamps = sorted([t for t in timestamps if t])
        
        time_range = {
            'start': timestamps[0] if timestamps else None,
            'end': timestamps[-1] if timestamps else None,
        }
        
        # 事件分类统计
        event_types = {}
        for event in self.events:
            event_type = event.get('type', 'other')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # 运行统计
        runs_stats = {
            'total': len(self.runs),
            'completed': sum(1 for r in self.runs.values() if r['status'] == 'complete'),
            'running': sum(1 for r in self.runs.values() if r['status'] == 'running'),
            'unknown': sum(1 for r in self.runs.values() if r['status'] == 'unknown'),
        }
        
        # 会话统计
        sessions_stats = {
            'total': len(self.sessions),
            'active': sum(1 for s in self.sessions.values() if s['state'] == 'active'),
            'inactive': sum(1 for s in self.sessions.values() if s['state'] == 'inactive'),
        }
        
        # 错误日志
        error_summary = {}
        for error in self.errors[:50]:  # 只保留前50个错误
            msg_preview = error['message'][:60]
            error_summary[msg_preview] = error_summary.get(msg_preview, 0) + 1
        
        report = {
            'analysis_time': datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
            'time_range': time_range,
            'statistics': self.statistics,
            'event_distribution': event_types,
            'runs': runs_stats,
            'sessions': sessions_stats,
            'api_usage': {
                'total_calls': self.statistics.get('api_calls', 0),
                'errors': self.statistics.get('api_errors', 0),
                'methods': self.api_methods,
            },
            'external_conversations': {
                'total': self.statistics.get('external_conversations', 0),
                'channels': self.external_channels,
            },
            'errors': {
                'total': len(self.errors),
                'top_errors': error_summary,
            },
            'details': {
                'runs': self.runs,
                'sessions': self.sessions,
                'recent_events': self.events[-100:],  # 最后100个事件
            }
        }
        
        return report
    
    def get_summary(self) -> str:
        """
        获取简洁的文本摘要
        
        Returns:
            str: 摘要文本
        """
        lines = [
            "=" * 60,
            "OpenClaw 系统日志分析摘要",
            "=" * 60,
            "",
            f"📊 日志处理: {self.statistics['parsed_lines']}/{self.statistics['total_lines']} 行成功解析",
            "",
            "📈 数据统计:",
            f"  • 运行事件: {self.statistics['runs']} 次",
            f"  • 会话: {len(self.sessions)} 个",
            f"  • 文件访问: {self.statistics['file_accesses']} 次",
            f"  • 错误/警告: {self.statistics['errors']} 条",
            f"  • API 调用: {self.statistics.get('api_calls', 0)} 次",
            f"  • 外部对话: {self.statistics.get('external_conversations', 0)} 次",
            "",
            "🚀 运行情况:",
            f"  • 总运行数: {len(self.runs)}",
            f"  • 已完成: {sum(1 for r in self.runs.values() if r['status'] == 'complete')}",
            f"  • 运行中: {sum(1 for r in self.runs.values() if r['status'] == 'running')}",
            "",
            "💬 会话情况:",
            f"  • 总会话数: {len(self.sessions)}",
            f"  • 活跃: {sum(1 for s in self.sessions.values() if s['state'] == 'active')}",
            f"  • 已关闭: {sum(1 for s in self.sessions.values() if s['state'] == 'inactive')}",
            "",
            "=" * 60,
        ]
        
        return "\n".join(lines)
