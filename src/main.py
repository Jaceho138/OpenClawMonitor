"""
主程序 - OpenClawMonitor 入口点和调度器
"""

import sys
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from config import get_config
from utils.logger import setup_logger
from monitor.process_monitor import ProcessMonitor
from monitor.log_parser import LogParser
from monitor.security_analyzer import SecurityAnalyzer
from monitor.openclaw_log_analyzer import OpenClawLogAnalyzer
from monitor.openclaw_report_generator import OpenClawReportGenerator
from db.manager import DatabaseManager
from report.generator import ReportGenerator
from report.notifier.email_sender import EmailNotifier
from scheduler import Scheduler


# 初始化日志
logger = setup_logger(
    "OpenClawMonitor",
    log_file=str(project_root / "logs" / "openclaw_monitor.log"),
)


class OpenClawMonitor:
    """
    主监控程序类
    """
    
    def __init__(self, config_path=None):
        """
        初始化监控程序
        
        Args:
            config_path: 配置文件路径
        """
        logger.info("正在初始化 OpenClawMonitor...")
        
        # 加载配置
        self.config = get_config(config_path)
        logger.info(f"配置已加载: {config_path or '使用默认配置'}")
        
        # 初始化各个组件
        self.db_manager = DatabaseManager()
        self.process_monitor = ProcessMonitor()
        self.log_parser = LogParser(self.config.log_paths.paths)
        self.security_analyzer = SecurityAnalyzer()
        self.report_generator = ReportGenerator()
        self.openclaw_log_analyzer = OpenClawLogAnalyzer()
        self.openclaw_report_generator = OpenClawReportGenerator()
        self.email_notifier = EmailNotifier(
            smtp_server=self.config.email.smtp_server,
            smtp_port=self.config.email.smtp_port,
            smtp_username=self.config.email.smtp_username,
            sender_email=self.config.email.sender_email,
            sender_password=self.config.email.sender_password,
            use_encryption=self.config.email.use_encryption,
        )
        
        # 初始化调度器
        self.scheduler = Scheduler()
        
        logger.info("OpenClawMonitor 初始化完成")
    
    def analyze_openclaw_logs(self, log_file_path: str = None):
        """
        分析 OpenClaw 系统日志并生成报告
        
        Args:
            log_file_path: 日志文件路径（默认为最新的 /private/tmp/openclaw 下的日志）
        
        Returns:
            str: 报告 HTML 内容
        """
        # 如果未指定文件，查找默认位置
        if log_file_path is None:
            from pathlib import Path
            import glob
            
            openclaw_dir = Path("/private/tmp/openclaw/")
            if openclaw_dir.exists():
                log_files = sorted(glob.glob(str(openclaw_dir / "*.log")), reverse=True)
                if log_files:
                    log_file_path = log_files[0]
                    logger.info(f"使用默认日志文件: {log_file_path}")
        
        if not log_file_path:
            logger.error("未找到 OpenClaw 日志文件")
            return None
        
        logger.info(f"开始分析 OpenClaw 日志: {log_file_path}")
        
        # 分析日志
        analysis_data = self.openclaw_log_analyzer.analyze_file(log_file_path)
        
        # 打印摘要
        summary = self.openclaw_log_analyzer.get_summary()
        logger.info(f"\n{summary}")
        
        # 生成 HTML 报告
        html_report = self.openclaw_report_generator.generate_html_report(analysis_data)
        
        # 保存报告到文件
        report_dir = Path(__file__).parent.parent / "reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"openclaw_analysis_{timestamp}.html"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        logger.info(f"报告已保存: {report_file}")
        
        return html_report

    @staticmethod
    def _extract_html_body(html_content: Optional[str]) -> str:
        """
        提取 HTML 的 body 内容（用于嵌入邮件）

        Args:
            html_content: 原始 HTML 内容

        Returns:
            str: body 内部内容
        """
        if not html_content:
            return ""
        match = re.search(r"<body[^>]*>(.*)</body>", html_content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return html_content

    def _inject_openclaw_analysis(self, base_html: str, openclaw_html: Optional[str]) -> str:
        """
        将 OpenClaw 系统日志分析嵌入到日报告 HTML 中

        Args:
            base_html: 日常监控报告 HTML
            openclaw_html: OpenClaw 系统日志分析 HTML

        Returns:
            str: 合并后的 HTML
        """
        openclaw_body = self._extract_html_body(openclaw_html)
        if not openclaw_body:
            return base_html

        injected_section = (
            "\n<hr style=\"margin:40px 0;border:0;border-top:2px solid #E0E0E0;\">\n"
            "<section id=\"openclaw-system-analysis\">\n"
            "  <h2>OpenClaw 系统日志分析</h2>\n"
            f"  {openclaw_body}\n"
            "</section>\n"
        )

        if "</body>" in base_html:
            return base_html.replace("</body>", injected_section + "</body>")

        return base_html + injected_section
    
    def collect_daily_data(self, target_date=None, since_timestamp: Optional[str] = None):
        """
        收集某一天的数据（支持增量更新）
        
        Args:
            target_date: 目标日期（默认为昨天）
            since_timestamp: 仅收集此时间戳之后的新数据（用于增量更新）
        
        Returns:
            dict: 收集的数据
        """
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        
        date_str = target_date.strftime("%Y-%m-%d")
        logger.info(f"开始收集 {date_str} 的数据...")
        if since_timestamp:
            logger.info(f"仅收集 {since_timestamp} 之后的新数据（增量更新）")
        
        # 1. 收集进程数据
        logger.debug("收集进程数据...")
        processes = self.process_monitor.collect(target_date)
        
        # 2. 解析日志（支持增量）
        logger.debug("解析日志文件...")
        log_data = self.log_parser.parse_all_logs(target_date, since_timestamp)
        
        # 3. 解析命令执行审批
        logger.debug("解析命令执行审批...")
        approvals = self.log_parser.parse_exec_approvals()
        
        # 4. 分析安全事件
        logger.debug("分析安全事件...")
        self.security_analyzer.collect(target_date, log_data)
        security_analysis = self.security_analyzer.analyze()
        
        # 合并数据
        collected_data = {
            "date": date_str,
            "processes": processes,
            "commands": log_data.get("commands", []) + approvals,
            "file_accesses": log_data.get("file_accesses", []),
            "events": security_analysis.get("events", []),
            "security_score": security_analysis.get("security_score", 0),
            "missing_logs": log_data.get("missing_logs", False),
        }
        
        logger.info(f"数据收集完成: {len(processes)} 个进程, "
                   f"{len(collected_data['commands'])} 条命令, "
                   f"{len(collected_data['events'])} 个事件")
        
        return collected_data
    
    def save_to_database(self, data):
        """
        将数据保存到数据库
        
        Args:
            data: 收集的数据
        """
        date_str = data["date"]
        logger.info(f"保存 {date_str} 的数据到数据库...")
        
        # 保存进程数据
        for proc in data.get("processes", []):
            self.db_manager.add_activity_record(
                date=date_str,
                timestamp=proc.get("timestamp"),
                activity_type="process",
                description=proc.get("name", "未知"),
                severity="info",
                details=proc,
            )
        
        # 保存命令数据
        for cmd in data.get("commands", []):
            self.db_manager.add_activity_record(
                date=date_str,
                timestamp=cmd.get("timestamp", datetime.now().isoformat()),
                activity_type="command",
                description=cmd.get("command", "未知命令")[:200],
                severity="info",
                details=cmd,
            )
        
        # 保存文件访问数据
        for access in data.get("file_accesses", []):
            self.db_manager.add_activity_record(
                date=date_str,
                timestamp=access.get("timestamp"),
                activity_type="file_access",
                description=access.get("path", "未知路径")[:200],
                severity="info",
                details=access,
            )
        
        # 保存安全事件
        for event in data.get("events", []):
            if event.get("type") == "security_event" or event.get("type") == "log_warning":
                self.db_manager.add_security_event(
                    date=date_str,
                    timestamp=event.get("timestamp"),
                    event_type=event.get("category", "general"),
                    description=event.get("message", "未知事件")[:200],
                    severity=event.get("severity", "info"),
                    details=event,
                )
        
        logger.info(f"数据保存完成")
    
    def generate_and_send_report(self, target_date=None, use_last_execution=True):
        """
        生成报告并发送邮件（支持增量更新）
        
        Args:
            target_date: 目标日期（默认为昨天）
            use_last_execution: 是否从上次执行的节点开始增量收集
        """
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        
        date_str = target_date.strftime("%Y-%m-%d")
        execution_id = datetime.now().isoformat()
        logger.info(f"生成 {date_str} 的报告...")
        
        # 获取上次执行信息（用于增量更新）
        since_timestamp = None
        if use_last_execution:
            last_exec = self.db_manager.get_last_execution()
            if last_exec:
                since_timestamp = last_exec.get("last_activity_timestamp")
                logger.info(f"从上次执行节点 {since_timestamp} 之后的数据开始收集")
        
        # 收集数据（增量）
        data = self.collect_daily_data(target_date, since_timestamp)
        
        # 保存到数据库
        self.save_to_database(data)
        
        # 获取最近24小时的所有数据用于报告
        now = datetime.now()
        time_window_start = now - timedelta(hours=24)
        
        # 从数据库查询最近24小时的数据
        activities = self.db_manager.get_activities_by_date(date_str)
        security_events = self.db_manager.get_security_events_by_date(date_str)
        
        # 过滤出最近24小时的数据
        recent_activities = [
            a for a in activities
            if a.get("timestamp") and datetime.fromisoformat(a.get("timestamp")) >= time_window_start
        ]
        recent_security_events = [
            e for e in security_events
            if e.get("timestamp") and datetime.fromisoformat(e.get("timestamp")) >= time_window_start
        ]
        
        # 生成 HTML 报告（24小时窗口）
        html_report = self.report_generator.generate_html_report(
            date_str,
            {
                "commands": [a for a in recent_activities if a.get("activity_type") == "command"],
                "file_accesses": [a for a in recent_activities if a.get("activity_type") == "file_access"],
                "events": recent_security_events,
            },
            missing_logs=data.get("missing_logs", False),
            security_score=data.get("security_score", 0),
            time_window_hours=24,
        )
        
        # 保存日报告
        self.db_manager.save_daily_report(
            date=date_str,
            security_score=data.get("security_score", 0),
            total_events=len(recent_activities),
            process_count=len([a for a in recent_activities if a.get("activity_type") == "process"]),
            command_count=len([a for a in recent_activities if a.get("activity_type") == "command"]),
            file_access_count=len([a for a in recent_activities if a.get("activity_type") == "file_access"]),
            security_event_count=len(recent_security_events),
            summary=html_report,
        )
        
        # 记录执行状态
        last_activity_ts = None
        if recent_activities:
            last_activity_ts = max(a.get("timestamp") for a in recent_activities if a.get("timestamp"))
        
        self.db_manager.record_execution(
            execution_id=execution_id,
            last_log_timestamp=since_timestamp,
            last_activity_timestamp=last_activity_ts,
            status="success",
            email_sent=1,
        )
        
        # 生成 OpenClaw 系统日志分析并嵌入邮件
        openclaw_html = self.analyze_openclaw_logs()
        email_content = self._inject_openclaw_analysis(html_report, openclaw_html)

        # 发送邮件
        logger.info(f"发送报告邮件给 {self.config.email.recipient_email}...")
        subject = f"OpenClaw 活动监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success = self.email_notifier.send(
            subject=subject,
            content=email_content,
            recipient_email=self.config.email.recipient_email,
        )
        
        if success:
            logger.info(f"报告邮件发送成功")
        else:
            logger.error(f"报告邮件发送失败")
    
    def start_scheduler(self):
        """
        启动定时任务调度器
        """
        # 安排每日 8:00 AM 生成报告并发送邮件
        self.scheduler.schedule_daily_task(
            "08:00",
            self.generate_and_send_report,
            "生成并发送日活动报告",
        )
        
        # 启动调度器
        self.scheduler.start()
        
        logger.info("调度器已启动，等待定时任务...")
    
    def run_once(self):
        """
        运行一次（用于测试）
        """
        logger.info("运行一次数据收集和报告生成...")
        self.generate_and_send_report()
        logger.info("完成")


def main():
    """
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw 活动监控工具")
    parser.add_argument(
        "--config",
        type=str,
        help="配置文件路径",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="运行一次并退出（用于测试）",
    )
    parser.add_argument(
        "--date",
        type=str,
        help="目标日期（格式：YYYY-MM-DD，默认为昨天）",
    )
    
    args = parser.parse_args()
    
    # 创建监控程序实例
    monitor = OpenClawMonitor(args.config)
    
    if args.run_once:
        # 测试模式：运行一次
        monitor.run_once()
    else:
        # 后台运行模式：启动调度器
        try:
            monitor.start_scheduler()
            
            # 保持程序运行
            while True:
                import time
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭...")
            monitor.scheduler.stop()
            logger.info("已关闭")
        
        except Exception as e:
            logger.error(f"程序错误: {e}", exc_info=True)
            monitor.scheduler.stop()


if __name__ == "__main__":
    main()
