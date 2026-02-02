"""
数据库管理模块 - SQLite 操作
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from utils.helpers import get_database_path


logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    SQLite 数据库管理器
    管理所有数据库操作
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径（可选，默认为项目根的 database/openclaw_monitor.db）
        """
        if db_path is None:
            self.db_path = get_database_path()
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"数据库路径: {self.db_path}")
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 创建活动记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT DEFAULT 'info',
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, timestamp, activity_type, description)
                )
            """)
            
            # 创建安全事件表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, timestamp, event_type, description)
                )
            """)
            
            # 创建日报告表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    generated_at TEXT NOT NULL,
                    security_score INTEGER,
                    total_events INTEGER,
                    process_count INTEGER,
                    command_count INTEGER,
                    file_access_count INTEGER,
                    security_event_count INTEGER,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建执行状态追踪表（支持增量更新）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id TEXT UNIQUE NOT NULL,
                    execution_time TEXT NOT NULL,
                    last_log_timestamp TEXT,
                    last_activity_timestamp TEXT,
                    execution_status TEXT DEFAULT 'success',
                    data_collected INTEGER DEFAULT 0,
                    email_sent INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引以加快查询
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activity_date ON activity_records(date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_security_date ON security_events(date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_report_date ON daily_reports(date)
            """)
            
            conn.commit()
            logger.info("数据库表初始化成功")
        
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
            raise
        
        finally:
            conn.close()
    
    def add_activity_record(
        self,
        date: str,
        timestamp: str,
        activity_type: str,
        description: str,
        severity: str = "info",
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        添加活动记录
        
        Args:
            date: 日期（YYYY-MM-DD）
            timestamp: 时间戳（ISO 格式）
            activity_type: 活动类型
            description: 描述
            severity: 严重级别
            details: 详细信息（字典）
        
        Returns:
            bool: 是否添加成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            details_json = json.dumps(details) if details else None
            
            cursor.execute("""
                INSERT INTO activity_records
                (date, timestamp, activity_type, description, severity, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date, timestamp, activity_type, description, severity, details_json))
            
            conn.commit()
            return True
        
        except sqlite3.IntegrityError:
            # 记录已存在，这是正常的
            return False
        
        except Exception as e:
            logger.error(f"添加活动记录失败: {e}")
            return False
        
        finally:
            conn.close()
    
    def add_security_event(
        self,
        date: str,
        timestamp: str,
        event_type: str,
        description: str,
        severity: str,
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        添加安全事件
        
        Args:
            date: 日期
            timestamp: 时间戳
            event_type: 事件类型
            description: 描述
            severity: 严重级别
            source: 事件来源
            details: 详细信息
        
        Returns:
            bool: 是否添加成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            details_json = json.dumps(details) if details else None
            
            cursor.execute("""
                INSERT INTO security_events
                (date, timestamp, event_type, description, severity, source, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date, timestamp, event_type, description, severity, source, details_json))
            
            conn.commit()
            return True
        
        except sqlite3.IntegrityError:
            return False
        
        except Exception as e:
            logger.error(f"添加安全事件失败: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_activities_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        获取指定日期的所有活动记录
        
        Args:
            date: 日期（YYYY-MM-DD）
        
        Returns:
            List[Dict[str, Any]]: 活动记录列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM activity_records
                WHERE date = ?
                ORDER BY timestamp
            """, (date,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        finally:
            conn.close()
    
    def get_security_events_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        获取指定日期的所有安全事件
        
        Args:
            date: 日期
        
        Returns:
            List[Dict[str, Any]]: 安全事件列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM security_events
                WHERE date = ?
                ORDER BY timestamp
            """, (date,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        finally:
            conn.close()
    
    def save_daily_report(
        self,
        date: str,
        security_score: int,
        total_events: int,
        process_count: int,
        command_count: int,
        file_access_count: int,
        security_event_count: int,
        summary: str,
    ) -> bool:
        """
        保存日报告
        
        Args:
            date: 日期
            security_score: 安全评分
            total_events: 总事件数
            process_count: 进程数
            command_count: 命令数
            file_access_count: 文件访问数
            security_event_count: 安全事件数
            summary: 摘要（HTML）
        
        Returns:
            bool: 是否保存成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            generated_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO daily_reports
                (date, generated_at, security_score, total_events,
                 process_count, command_count, file_access_count,
                 security_event_count, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date, generated_at, security_score, total_events,
                process_count, command_count, file_access_count,
                security_event_count, summary
            ))
            
            conn.commit()
            logger.info(f"已保存 {date} 的日报告")
            return True
        
        except Exception as e:
            logger.error(f"保存日报告失败: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_report_by_date(self, date: str) -> Optional[Dict[str, Any]]:
        """
        获取指定日期的报告
        
        Args:
            date: 日期
        
        Returns:
            Optional[Dict[str, Any]]: 报告信息或 None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM daily_reports WHERE date = ?", (date,))
            row = cursor.fetchone()
            return dict(row) if row else None
        
        finally:
            conn.close()
    def record_execution(
        self,
        execution_id: str,
        last_log_timestamp: Optional[str] = None,
        last_activity_timestamp: Optional[str] = None,
        status: str = "success",
        email_sent: int = 1,
    ) -> bool:
        """
        记录执行状态（用于增量更新）
        
        Args:
            execution_id: 执行 ID（通常是执行时间）
            last_log_timestamp: 最后一条日志的时间戳
            last_activity_timestamp: 最后一条活动记录的时间戳
            status: 执行状态
            email_sent: 是否发送邮件
        
        Returns:
            bool: 是否保存成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            execution_time = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO execution_tracking
                (execution_id, execution_time, last_log_timestamp,
                 last_activity_timestamp, execution_status, email_sent)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                execution_id, execution_time, last_log_timestamp,
                last_activity_timestamp, status, email_sent
            ))
            
            conn.commit()
            return True
        
        except Exception as e:
            logger.error(f"记录执行状态失败: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_last_execution(self) -> Optional[Dict[str, Any]]:
        """
        获取上一次执行的信息
        
        Returns:
            Optional[Dict[str, Any]]: 上次执行信息或 None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM execution_tracking
                ORDER BY execution_time DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else None
        
        finally:
            conn.close()