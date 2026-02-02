"""
报告生成模块 - HTML 报告和图表生成
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.rcParams import rcParams
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("pandas 或 matplotlib 未安装")


logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    报告生成器
    生成 HTML 格式的日活动报告，包括表格和图表
    """
    
    def __init__(self, base_title: str = "OpenClaw 日活动报告"):
        """
        初始化报告生成器
        
        Args:
            base_title: 报告标题
        """
        self.base_title = base_title
        self.report_data = {}
    
    def generate_html_report(
        self,
        date: str,
        data: Dict[str, Any],
        missing_logs: bool = False,
        security_score: int = 0,
        time_window_hours: int = 24,
    ) -> str:
        """
        生成 HTML 报告
        
        Args:
            date: 日期（仅用于显示）
            data: 报告数据
            missing_logs: 是否缺失日志
            security_score: 安全评分
            time_window_hours: 时间窗口（小时，用于标题显示）
        
        Returns:
            str: HTML 字符串
        """
        self.report_data = data
        
        # 创建 HTML 结构
        html = self._create_html_header(date, time_window_hours)
        
        # 添加安全评分卡片
        html += self._create_security_score_card(security_score, missing_logs)
        
        # 添加统计信息
        html += self._create_statistics_section(data)
        
        # 添加详细表格
        html += self._create_details_tables(data)
        
        # 添加图表
        if PANDAS_AVAILABLE:
            html += self._create_charts_section(data)
        
        # 添加警告信息
        if missing_logs:
            html += self._create_missing_logs_warning()
        
        # 关闭 HTML
        html += self._create_html_footer()
        
        return html
    
    @staticmethod
    def _create_html_header(date: str, time_window_hours: int = 24) -> str:
        """创建 HTML 头部"""
        title_suffix = f"（最近{time_window_hours}小时）" if time_window_hours != 24 else ""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw 日活动报告 - {date}{title_suffix}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1000px;
            margin: 20px auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        header {{
            border-bottom: 3px solid #2196F3;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2196F3;
            font-size: 28px;
            margin-bottom: 5px;
        }}
        .report-meta {{
            font-size: 12px;
            color: #999;
        }}
        .score-card {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
            min-width: 250px;
        }}
        .score-card .label {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .score-card .score {{
            font-size: 48px;
            font-weight: bold;
        }}
        .score-card.critical {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .score-card.warning {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        .score-card.success {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        
        .section {{
            margin: 30px 0;
        }}
        h2 {{
            color: #333;
            font-size: 20px;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        
        .statistics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-box .number {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-box .label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th {{
            background-color: #f0f0f0;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #2196F3;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        
        .warning-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .warning-box h3 {{
            color: #856404;
            margin-bottom: 10px;
        }}
        .warning-box p {{
            color: #856404;
            font-size: 13px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #999;
        }}
        
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>OpenClaw 日活动报告</h1>
            <div class="report-meta">
                <strong>日期:</strong> {date}<br>
                <strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </header>
"""
    
    @staticmethod
    def _create_security_score_card(security_score: int, missing_logs: bool) -> str:
        """创建安全评分卡片"""
        if missing_logs:
            score_class = "critical"
            message = "日志缺失"
        elif security_score >= 80:
            score_class = "success"
        elif security_score >= 50:
            score_class = "warning"
        else:
            score_class = "critical"
        
        return f"""        <div class="section">
            <div class="score-card {score_class}">
                <div class="label">安全评分</div>
                <div class="score">{security_score}</div>
            </div>
        </div>
"""
    
    @staticmethod
    def _create_statistics_section(data: Dict[str, Any]) -> str:
        """创建统计信息部分"""
        commands = data.get("commands", [])
        file_accesses = data.get("file_accesses", [])
        events = data.get("events", [])
        
        html = """        <div class="section">
            <h2>📊 日活动统计</h2>
            <div class="statistics">
                <div class="stat-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <div class="number">""" + str(len(commands)) + """</div>
                    <div class="label">执行的命令</div>
                </div>
                <div class="stat-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <div class="number">""" + str(len(file_accesses)) + """</div>
                    <div class="label">文件访问事件</div>
                </div>
                <div class="stat-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <div class="number">""" + str(len(events)) + """</div>
                    <div class="label">安全事件</div>
                </div>
            </div>
        </div>
"""
        return html
    
    @staticmethod
    def _create_details_tables(data: Dict[str, Any]) -> str:
        """创建详细信息表格"""
        html = """        <div class="section">
            <h2>📋 详细信息</h2>
"""
        
        # 命令表格
        commands = data.get("commands", [])
        if commands:
            html += """            <h3>执行的命令</h3>
            <table>
                <tr>
                    <th>时间</th>
                    <th>命令</th>
                </tr>
"""
            for cmd in commands[:20]:  # 仅显示前 20 条
                timestamp = cmd.get("timestamp", "未知")
                command = cmd.get("command", "未知")[:80]  # 截断长命令
                html += f"                <tr><td>{timestamp}</td><td>{command}</td></tr>\n"
            
            if len(commands) > 20:
                html += f"                <tr><td colspan='2'>... 还有 {len(commands) - 20} 条</td></tr>\n"
            
            html += "            </table>\n"
        
        # 文件访问表格
        file_accesses = data.get("file_accesses", [])
        if file_accesses:
            html += """            <h3>文件访问</h3>
            <table>
                <tr>
                    <th>时间</th>
                    <th>路径</th>
                    <th>类型</th>
                </tr>
"""
            for access in file_accesses[:20]:
                timestamp = access.get("timestamp", "未知")
                path = access.get("path", "未知")[:60]
                access_type = access.get("type", "unknown")
                html += f"                <tr><td>{timestamp}</td><td>{path}</td><td>{access_type}</td></tr>\n"
            
            if len(file_accesses) > 20:
                html += f"                <tr><td colspan='3'>... 还有 {len(file_accesses) - 20} 条</td></tr>\n"
            
            html += "            </table>\n"
        
        # 安全事件表格
        events = data.get("events", [])
        if events:
            html += """            <h3>安全事件</h3>
            <table>
                <tr>
                    <th>时间</th>
                    <th>事件</th>
                    <th>严重级别</th>
                </tr>
"""
            for event in events[:20]:
                timestamp = event.get("timestamp", "未知")
                message = event.get("message", "未知")[:60]
                severity = event.get("severity", "info")
                html += f"                <tr><td>{timestamp}</td><td>{message}</td><td>{severity}</td></tr>\n"
            
            if len(events) > 20:
                html += f"                <tr><td colspan='3'>... 还有 {len(events) - 20} 条</td></tr>\n"
            
            html += "            </table>\n"
        
        html += """        </div>
"""
        return html
    
    @staticmethod
    def _create_charts_section(data: Dict[str, Any]) -> str:
        """创建图表部分（如果 pandas 可用）"""
        if not PANDAS_AVAILABLE:
            return ""
        
        try:
            # 创建事件类型频率图
            events = data.get("events", [])
            if events:
                event_types = {}
                for event in events:
                    event_type = event.get("type", "unknown")
                    event_types[event_type] = event_types.get(event_type, 0) + 1
                
                # 使用 matplotlib 创建图表
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.bar(event_types.keys(), event_types.values(), color="#2196F3")
                ax.set_title("事件类型频率", fontsize=14, fontweight="bold")
                ax.set_xlabel("事件类型")
                ax.set_ylabel("频率")
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # 保存为 data URL（可选）
                import io
                import base64
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                image_base64 = base64.b64encode(buf.read()).decode()
                plt.close()
                
                return f"""        <div class="section">
            <h2>📈 事件频率分布</h2>
            <div class="chart-container">
                <img src="data:image/png;base64,{image_base64}" alt="事件频率图表">
            </div>
        </div>
"""
        except Exception as e:
            logger.warning(f"生成图表失败: {e}")
        
        return ""
    
    @staticmethod
    def _create_missing_logs_warning() -> str:
        """创建缺失日志警告"""
        return """        <div class="section">
            <div class="warning-box">
                <h3>⚠️ 日志文件缺失</h3>
                <p>
                    未在配置的路径中找到日志文件。请检查以下内容：
                </p>
                <ul style="margin-left: 20px; margin-top: 10px;">
                    <li>确认 <code>~/.openclaw/openclaw.json</code> 中的 <code>logging.file</code> 和 <code>level</code> 配置正确</li>
                    <li>在 OpenClaw 的调试窗格中，启用 "Logs" → "App logging" → "Write rolling diagnostics log (JSONL)"</li>
                    <li>重启 OpenClaw 以启用日志功能</li>
                </ul>
            </div>
        </div>
"""
    
    @staticmethod
    def _create_html_footer() -> str:
        """创建 HTML 页脚"""
        return """        <div class="footer">
            <p>此报告由 OpenClaw Monitor 自动生成</p>
        </div>
    </div>
</body>
</html>
"""
