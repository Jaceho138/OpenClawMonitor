"""
OpenClaw 系统日志监控报告生成器 - 邮件优化版本
支持 Gmail/Outlook 等邮件客户端，使用内联 CSS 和表格布局
"""

import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class OpenClawReportGenerator:
    """
    生成 OpenClaw 系统日志分析报告 - 邮件客户端优化版本
    """
    
    def __init__(self):
        """初始化报告生成器"""
        self.report_data = {}
    
    def generate_html_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        生成 HTML 报告
        
        Args:
            analysis_data: 分析数据
        
        Returns:
            str: HTML 字符串
        """
        self.report_data = analysis_data
        
        # 创建 HTML
        html = self._create_header()
        html += self._create_summary_section()
        html += self._create_api_usage_section()
        html += self._create_external_conversation_section()
        html += self._create_statistics_section()
        html += self._create_runs_section()
        html += self._create_sessions_section()
        html += self._create_errors_section()
        html += self._create_events_section()
        html += self._create_footer()
        
        return html
    
    def _create_header(self) -> str:
        """创建 HTML 头部 - 邮件客户端优化版本"""
        analysis_time = self._format_beijing_time(self.report_data.get('analysis_time', ''))
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="format-detection" content="telephone=no">
    <title>OpenClaw 系统日志监控报告</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:AllowPNG/>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style type="text/css">
        /* Reset styles */
        body {{
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        
        img {{
            border: 0;
            height: auto;
            line-height: 100%;
            outline: none;
            text-decoration: none;
            -ms-interpolation-mode: bicubic;
        }}
        
        table {{
            border-collapse: collapse !important;
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }}
        
        /* Mobile responsive */
        @media only screen and (max-width: 600px) {{
            .container {{
                width: 100% !important;
                padding: 10px !important;
            }}
            .stat-card {{
                margin-bottom: 15px !important;
            }}
            .header-title {{
                font-size: 24px !important;
            }}
            .chart-bar {{
                height: 20px !important;
            }}
        }}
    </style>
</head>
<body style="margin:0;padding:0;font-family:'Segoe UI','Microsoft YaHei',Arial,sans-serif;background-color:#f4f7fa;">
    
    <!-- Fallback text for non-HTML email clients -->
    <div style="display:none;font-size:1px;color:#fefefe;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
        OpenClaw 系统监控报告 - {analysis_time}
    </div>
    
    <!-- Main container -->
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f4f7fa;padding:20px 0;">
        <tr>
            <td align="center">
                <!-- Content wrapper -->
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" class="container" style="max-width:600px;background-color:#ffffff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);overflow:hidden;">
                    
                    <!-- Header with gradient -->
                    <tr>
                        <td style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);padding:40px 30px;text-align:center;">
                            <h1 class="header-title" style="margin:0;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;line-height:1.3;">
                                📊 OpenClaw 系统监控报告
                            </h1>
                            <p style="margin:15px 0 0 0;color:rgba(255,255,255,0.9);font-size:14px;line-height:1.5;">
                                🕐 分析时间: {analysis_time}
                            </p>
                        </td>
                    </tr>
"""

    def _create_summary_section(self) -> str:
        """创建摘要部分 - 使用表格布局的卡片样式"""
        stats = self.report_data.get('statistics', {})
        time_range = self.report_data.get('time_range', {})
        time_range_start = self._format_beijing_time(time_range.get('start'))
        time_range_end = self._format_beijing_time(time_range.get('end'))
        
        total_runs = len(self.report_data.get('details', {}).get('runs', {}))
        completed_runs = sum(1 for r in self.report_data.get('details', {}).get('runs', {}).values() 
                             if r.get('status') == 'complete')
        in_progress_runs = total_runs - completed_runs
        success_rate = f"{(completed_runs/total_runs*100):.1f}%" if total_runs > 0 else "0%"
        
        parsed_lines = stats.get('parsed_lines', 0)
        total_lines = stats.get('total_lines', 0)
        parse_rate = f"{(parsed_lines/total_lines*100):.1f}%" if total_lines > 0 else "0%"
        
        return f"""
                    <!-- Summary Stats Cards -->
                    <tr>
                        <td style="padding:30px 30px 10px 30px;">
                            <h2 style="margin:0 0 20px 0;color:#2c3e50;font-size:20px;font-weight:600;border-bottom:2px solid #e8edf2;padding-bottom:10px;">
                                📈 运行概览
                            </h2>
                        </td>
                    </tr>
                    
                    <!-- 3-column stats grid -->
                    <tr>
                        <td style="padding:0 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                <tr>
                                    <!-- Total Runs -->
                                    <td width="33%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:32px;font-weight:700;color:#ffffff;margin-bottom:5px;">{total_runs}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">总运行数</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    
                                    <!-- Completed -->
                                    <td width="33%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:32px;font-weight:700;color:#ffffff;margin-bottom:5px;">{completed_runs}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">已完成</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    
                                    <!-- In Progress -->
                                    <td width="33%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #fa709a 0%, #fee140 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:32px;font-weight:700;color:#ffffff;margin-bottom:5px;">{in_progress_runs}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">进行中</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Second row of stats -->
                    <tr>
                        <td style="padding:0 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                <tr>
                                    <!-- Sessions -->
                                    <td width="33%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #30cfd0 0%, #330867 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:32px;font-weight:700;color:#ffffff;margin-bottom:5px;">{stats.get('sessions', 0)}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">会话数</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    
                                    <!-- API Calls -->
                                    <td width="33%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:32px;font-weight:700;color:#2c3e50;margin-bottom:5px;">{stats.get('api_calls', 0)}</div>
                                                    <div style="font-size:13px;color:#555;">API 调用</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    
                                    <!-- Errors -->
                                    <td width="33%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #f093fb 0%, #f5576c 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:32px;font-weight:700;color:#ffffff;margin-bottom:5px;">{stats.get('errors', 0)}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">错误警告</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Info panel with time range and stats -->
                    <tr>
                        <td style="padding:20px 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f8f9fa;border-left:4px solid #667eea;border-radius:6px;padding:15px;">
                                <tr>
                                    <td>
                                        <p style="margin:0 0 8px 0;color:#2c3e50;font-size:14px;line-height:1.6;">
                                            <strong>📅 时间范围:</strong> {time_range_start} 至 {time_range_end}
                                        </p>
                                        <p style="margin:0 0 8px 0;color:#2c3e50;font-size:14px;line-height:1.6;">
                                            <strong>✅ 成功率:</strong> <span style="color:#4caf50;font-weight:600;">{success_rate}</span> ({completed_runs}/{total_runs} 运行完成)
                                        </p>
                                        <p style="margin:0;color:#2c3e50;font-size:14px;line-height:1.6;">
                                            <strong>📝 日志解析:</strong> <span style="color:#2196f3;font-weight:600;">{parse_rate}</span> ({parsed_lines:,}/{total_lines:,} 行)
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
"""

    def _create_api_usage_section(self) -> str:
        """创建 API 使用情况部分 - 邮件优化版本，带可视化图表"""
        api_usage = self.report_data.get('api_usage', {})
        total_calls = api_usage.get('total_calls', 0)
        api_errors = api_usage.get('errors', 0)
        methods = api_usage.get('methods', {})

        sorted_methods = sorted(methods.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 创建方法行和 CSS 条形图
        method_rows = ""
        max_calls = max([count for _, count in sorted_methods], default=1)
        
        for method, count in sorted_methods:
            bar_width = f"{(count/max_calls*100):.1f}%" if max_calls > 0 else "0%"
            method_rows += f"""
                                <tr>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;color:#2c3e50;font-size:13px;">
                                        {method}
                                    </td>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;width:60%;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                            <tr>
                                                <td style="background:#e8edf2;border-radius:4px;padding:0;height:24px;position:relative;">
                                                    <div style="background:linear-gradient(90deg, #667eea 0%, #764ba2 100%);height:24px;border-radius:4px;width:{bar_width};"></div>
                                                </td>
                                                <td style="padding-left:10px;white-space:nowrap;color:#2c3e50;font-weight:600;font-size:13px;">
                                                    {count}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>"""

        if not method_rows:
            method_rows = """
                                <tr>
                                    <td colspan="2" style="padding:20px;text-align:center;color:#95a5a6;font-size:14px;">
                                        未检测到 API 调用
                                    </td>
                                </tr>"""

        error_rate = f"{(api_errors/total_calls*100):.1f}%" if total_calls > 0 else "0%"

        return f"""
                    <!-- API Usage Section -->
                    <tr>
                        <td style="padding:30px 30px 10px 30px;">
                            <h2 style="margin:0 0 20px 0;color:#2c3e50;font-size:20px;font-weight:600;border-bottom:2px solid #e8edf2;padding-bottom:10px;">
                                🔌 API 使用情况
                            </h2>
                        </td>
                    </tr>
                    
                    <!-- API Stats Cards -->
                    <tr>
                        <td style="padding:0 30px 20px 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                <tr>
                                    <td width="50%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:36px;font-weight:700;color:#ffffff;margin-bottom:5px;">{total_calls}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">API 调用次数</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    <td width="50%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #f093fb 0%, #f5576c 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:36px;font-weight:700;color:#ffffff;margin-bottom:5px;">{api_errors}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">错误次数 ({error_rate})</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Top API Methods Chart -->
                    <tr>
                        <td style="padding:0 30px 20px 30px;">
                            <h3 style="margin:0 0 15px 0;color:#2c3e50;font-size:16px;font-weight:600;">
                                📊 热门 API 方法 (Top 10)
                            </h3>
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#ffffff;border:1px solid #e8edf2;border-radius:8px;overflow:hidden;">
                                {method_rows}
                            </table>
                        </td>
                    </tr>
"""

    def _create_external_conversation_section(self) -> str:
        """创建外部对话情况部分 - 邮件优化版本，带饼图模拟"""
        external = self.report_data.get('external_conversations', {})
        total = external.get('total', 0)
        channels = external.get('channels', {})

        sorted_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 生成渠道行和进度条
        channel_rows = ""
        max_count = max([count for _, count in sorted_channels], default=1)
        
        # 颜色列表
        colors = [
            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
            "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
            "linear-gradient(135deg, #30cfd0 0%, #330867 100%)",
            "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
            "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)",
            "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
            "linear-gradient(135deg, #ff6e7f 0%, #bfe9ff 100%)",
            "linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)",
            "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        ]
        
        for idx, (channel, count) in enumerate(sorted_channels):
            bar_width = f"{(count/max_count*100):.1f}%" if max_count > 0 else "0%"
            percentage = f"{(count/total*100):.1f}%" if total > 0 else "0%"
            color = colors[idx % len(colors)]
            
            channel_rows += f"""
                                <tr>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;">
                                        <span style="display:inline-block;width:12px;height:12px;background:{color};border-radius:3px;margin-right:8px;vertical-align:middle;"></span>
                                        <span style="color:#2c3e50;font-size:13px;vertical-align:middle;">{channel}</span>
                                    </td>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;width:55%;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                            <tr>
                                                <td style="background:#e8edf2;border-radius:4px;padding:0;height:24px;">
                                                    <div style="background:{color};height:24px;border-radius:4px;width:{bar_width};"></div>
                                                </td>
                                                <td style="padding-left:10px;white-space:nowrap;color:#2c3e50;font-weight:600;font-size:13px;">
                                                    {count} <span style="color:#95a5a6;font-weight:400;">({percentage})</span>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>"""

        if not channel_rows:
            channel_rows = """
                                <tr>
                                    <td colspan="2" style="padding:20px;text-align:center;color:#95a5a6;font-size:14px;">
                                        未检测到外部对话
                                    </td>
                                </tr>"""

        return f"""
                    <!-- External Conversations Section -->
                    <tr>
                        <td style="padding:30px 30px 10px 30px;">
                            <h2 style="margin:0 0 20px 0;color:#2c3e50;font-size:20px;font-weight:600;border-bottom:2px solid #e8edf2;padding-bottom:10px;">
                                💬 外部对话数据
                            </h2>
                        </td>
                    </tr>
                    
                    <!-- Total Conversations Card -->
                    <tr>
                        <td style="padding:0 30px 20px 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #fa709a 0%, #fee140 100%);border-radius:8px;padding:25px;text-align:center;">
                                <tr>
                                    <td>
                                        <div style="font-size:40px;font-weight:700;color:#ffffff;margin-bottom:5px;">{total}</div>
                                        <div style="font-size:14px;color:rgba(255,255,255,0.95);font-weight:500;">外部对话事件总数</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Channel Distribution Chart -->
                    <tr>
                        <td style="padding:0 30px 20px 30px;">
                            <h3 style="margin:0 0 15px 0;color:#2c3e50;font-size:16px;font-weight:600;">
                                📡 渠道分布 (Top 10)
                            </h3>
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#ffffff;border:1px solid #e8edf2;border-radius:8px;overflow:hidden;">
                                {channel_rows}
                            </table>
                        </td>
                    </tr>
"""

    def _create_statistics_section(self) -> str:
        """创建统计部分 - 邮件优化版本"""
        event_dist = self.report_data.get('event_distribution', {})
        
        # 排序事件类型
        sorted_events = sorted(event_dist.items(), key=lambda x: x[1], reverse=True)[:10]
        
        event_rows = ""
        max_count = max([count for _, count in sorted_events], default=1)
        
        for event_type, count in sorted_events:
            bar_width = f"{(count/max_count*100):.1f}%" if max_count > 0 else "0%"
            event_rows += f"""
                                <tr>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;color:#2c3e50;font-size:13px;">
                                        {event_type}
                                    </td>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;width:60%;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                            <tr>
                                                <td style="background:#e8edf2;border-radius:4px;padding:0;height:24px;">
                                                    <div style="background:linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);height:24px;border-radius:4px;width:{bar_width};"></div>
                                                </td>
                                                <td style="padding-left:10px;white-space:nowrap;color:#2c3e50;font-weight:600;font-size:13px;">
                                                    {count}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>"""
        
        if not event_rows:
            event_rows = """
                                <tr>
                                    <td colspan="2" style="padding:20px;text-align:center;color:#95a5a6;font-size:14px;">
                                        暂无事件数据
                                    </td>
                                </tr>"""
        
        return f"""
                    <!-- Statistics Section -->
                    <tr>
                        <td style="padding:30px 30px 10px 30px;">
                            <h2 style="margin:0 0 20px 0;color:#2c3e50;font-size:20px;font-weight:600;border-bottom:2px solid #e8edf2;padding-bottom:10px;">
                                📊 事件统计 (Top 10)
                            </h2>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding:0 30px 20px 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#ffffff;border:1px solid #e8edf2;border-radius:8px;overflow:hidden;">
                                {event_rows}
                            </table>
                        </td>
                    </tr>
"""

    def _create_runs_section(self) -> str:
        """创建运行部分 - 邮件优化版本"""
        runs_stats = self.report_data.get('runs', {})
        runs_detail = self.report_data.get('details', {}).get('runs', {})
        
        # 运行摘要
        html = f"""
                    <!-- Runs Section -->
                    <tr>
                        <td style="padding:30px 30px 10px 30px;">
                            <h2 style="margin:0 0 20px 0;color:#2c3e50;font-size:20px;font-weight:600;border-bottom:2px solid #e8edf2;padding-bottom:10px;">
                                🚀 运行详情
                            </h2>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding:0 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                <tr>
                                    <td width="50%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:36px;font-weight:700;color:#ffffff;margin-bottom:5px;">{runs_stats.get('complete', 0)}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">已完成</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    <td width="50%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #fa709a 0%, #fee140 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:36px;font-weight:700;color:#ffffff;margin-bottom:5px;">{runs_stats.get('running', 0)}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">运行中</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding:20px 30px 10px 30px;">
                            <h3 style="margin:0;color:#2c3e50;font-size:16px;font-weight:600;">最近运行 (最后 20 条)</h3>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding:0 30px 20px 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#ffffff;border:1px solid #e8edf2;border-radius:8px;overflow:hidden;">
                                <tr style="background:#f8f9fa;">
                                    <th style="padding:12px;text-align:left;color:#2c3e50;font-size:13px;font-weight:600;border-bottom:2px solid #e8edf2;">运行 ID</th>
                                    <th style="padding:12px;text-align:center;color:#2c3e50;font-size:13px;font-weight:600;border-bottom:2px solid #e8edf2;">状态</th>
                                    <th style="padding:12px;text-align:left;color:#2c3e50;font-size:13px;font-weight:600;border-bottom:2px solid #e8edf2;">开始时间</th>
                                    <th style="padding:12px;text-align:left;color:#2c3e50;font-size:13px;font-weight:600;border-bottom:2px solid #e8edf2;">完成时间</th>
                                </tr>
"""
        
        # 显示最后20个运行
        for run_id, run_info in list(runs_detail.items())[-20:]:
            status = run_info.get('status', 'unknown')
            status_text = status.upper()
            
            # 状态徽章样式
            if status == 'complete':
                badge_style = "background:#d4edda;color:#155724;padding:4px 10px;border-radius:4px;font-size:11px;font-weight:600;"
            elif status == 'running':
                badge_style = "background:#cce5ff;color:#004085;padding:4px 10px;border-radius:4px;font-size:11px;font-weight:600;"
            else:
                badge_style = "background:#f8d7da;color:#721c24;padding:4px 10px;border-radius:4px;font-size:11px;font-weight:600;"
            
            start = self._format_beijing_time(run_info.get('start'))
            complete = self._format_beijing_time(run_info.get('complete'))
            
            html += f"""
                                <tr>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;font-family:monospace;font-size:12px;color:#495057;">{run_id[:24]}...</td>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;text-align:center;"><span style="{badge_style}">{status_text}</span></td>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;color:#6c757d;font-size:12px;">{start}</td>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;color:#6c757d;font-size:12px;">{complete}</td>
                                </tr>
"""
        
        if not runs_detail:
            html += """
                                <tr>
                                    <td colspan="4" style="padding:20px;text-align:center;color:#95a5a6;font-size:14px;">
                                        暂无运行数据
                                    </td>
                                </tr>"""
        
        html += """
                            </table>
                        </td>
                    </tr>
"""
        return html

    def _create_sessions_section(self) -> str:
        """创建会话部分 - 邮件优化版本"""
        sessions_stats = self.report_data.get('sessions', {})
        sessions_detail = self.report_data.get('details', {}).get('sessions', {})
        
        html = f"""
                    <!-- Sessions Section -->
                    <tr>
                        <td style="padding:30px 30px 10px 30px;">
                            <h2 style="margin:0 0 20px 0;color:#2c3e50;font-size:20px;font-weight:600;border-bottom:2px solid #e8edf2;padding-bottom:10px;">
                                💬 会话情况
                            </h2>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding:0 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                <tr>
                                    <td width="33%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:36px;font-weight:700;color:#ffffff;margin-bottom:5px;">{sessions_stats.get('total', 0)}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">总会话数</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    <td width="33%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:36px;font-weight:700;color:#ffffff;margin-bottom:5px;">{sessions_stats.get('active', 0)}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">活跃会话</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    <td width="33%" style="padding:10px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:linear-gradient(135deg, #fa709a 0%, #fee140 100%);border-radius:8px;padding:20px;text-align:center;">
                                            <tr>
                                                <td>
                                                    <div style="font-size:36px;font-weight:700;color:#ffffff;margin-bottom:5px;">{sessions_stats.get('inactive', 0)}</div>
                                                    <div style="font-size:13px;color:rgba(255,255,255,0.9);">已关闭</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding:20px 30px 10px 30px;">
                            <h3 style="margin:0;color:#2c3e50;font-size:16px;font-weight:600;">最近会话 (最后 20 条)</h3>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding:0 30px 20px 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#ffffff;border:1px solid #e8edf2;border-radius:8px;overflow:hidden;">
                                <tr style="background:#f8f9fa;">
                                    <th style="padding:12px;text-align:left;color:#2c3e50;font-size:13px;font-weight:600;border-bottom:2px solid #e8edf2;">会话 ID</th>
                                    <th style="padding:12px;text-align:center;color:#2c3e50;font-size:13px;font-weight:600;border-bottom:2px solid #e8edf2;">状态</th>
                                    <th style="padding:12px;text-align:left;color:#2c3e50;font-size:13px;font-weight:600;border-bottom:2px solid #e8edf2;">开始时间</th>
                                </tr>
"""
        
        # 显示最后20个会话
        for session_id, session_info in list(sessions_detail.items())[-20:]:
            state = session_info.get('state', 'unknown')
            state_text = state.upper()
            
            # 状态徽章样式
            if state == 'active':
                badge_style = "background:#d4edda;color:#155724;padding:4px 10px;border-radius:4px;font-size:11px;font-weight:600;"
            elif state == 'inactive':
                badge_style = "background:#fff3cd;color:#856404;padding:4px 10px;border-radius:4px;font-size:11px;font-weight:600;"
            else:
                badge_style = "background:#e2e3e5;color:#383d41;padding:4px 10px;border-radius:4px;font-size:11px;font-weight:600;"
            
            start = self._format_beijing_time(session_info.get('start'))
            
            html += f"""
                                <tr>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;font-family:monospace;font-size:12px;color:#495057;">{session_id[:24]}...</td>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;text-align:center;"><span style="{badge_style}">{state_text}</span></td>
                                    <td style="padding:10px;border-bottom:1px solid #e8edf2;color:#6c757d;font-size:12px;">{start}</td>
                                </tr>
"""
        
        if not sessions_detail:
            html += """
                                <tr>
                                    <td colspan="3" style="padding:20px;text-align:center;color:#95a5a6;font-size:14px;">
                                        暂无会话数据
                                    </td>
                                </tr>"""
        
        html += """
                            </table>
                        </td>
                    </tr>
"""
        return html

    def _create_errors_section(self) -> str:
        """创建错误部分 - 邮件优化版本"""
        errors = self.report_data.get('errors', {})
        total_errors = errors.get('total', 0)
        top_errors = errors.get('top_errors', {})
        
        html = f"""
                    <!-- Errors Section -->
                    <tr>
                        <td style="padding:30px 30px 10px 30px;">
                            <h2 style="margin:0 0 20px 0;color:#2c3e50;font-size:20px;font-weight:600;border-bottom:2px solid #e8edf2;padding-bottom:10px;">
                                ⚠️ 错误警告
                            </h2>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding:0 30px 20px 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#fff3cd;border-left:4px solid #ffc107;border-radius:6px;padding:15px;">
                                <tr>
                                    <td>
                                        <p style="margin:0;color:#856404;font-size:14px;">
                                            <strong>总错误数:</strong> {total_errors}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding:0 30px 20px 30px;">
                            <h3 style="margin:0 0 15px 0;color:#2c3e50;font-size:16px;font-weight:600;">常见错误 (Top 10)</h3>
"""
        
        if top_errors:
            for error_msg, count in sorted(top_errors.items(), key=lambda x: x[1], reverse=True)[:10]:
                html += f"""
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#fff9c4;border-left:4px solid #fbc02d;border-radius:6px;padding:12px;margin-bottom:10px;">
                                <tr>
                                    <td>
                                        <div style="color:#f57f17;font-weight:600;font-size:13px;margin-bottom:3px;">
                                            🔴 出现 {count} 次
                                        </div>
                                        <div style="color:#333;font-size:13px;line-height:1.5;">
                                            {error_msg[:150]}{'...' if len(error_msg) > 150 else ''}
                                        </div>
                                    </td>
                                </tr>
                            </table>
"""
        else:
            html += """
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#e8f5e9;border-left:4px solid #4caf50;border-radius:6px;padding:15px;">
                                <tr>
                                    <td style="text-align:center;color:#2e7d32;font-size:14px;">
                                        ✅ 未发现错误或警告
                                    </td>
                                </tr>
                            </table>
"""
        
        html += """
                        </td>
                    </tr>
"""
        return html

    def _create_events_section(self) -> str:
        """创建事件部分 - 邮件优化版本"""
        recent_events = self.report_data.get('details', {}).get('recent_events', [])
        
        html = """
                    <!-- Events Section -->
                    <tr>
                        <td style="padding:30px 30px 10px 30px;">
                            <h2 style="margin:0 0 20px 0;color:#2c3e50;font-size:20px;font-weight:600;border-bottom:2px solid #e8edf2;padding-bottom:10px;">
                                📋 最近事件 (最后 20 条)
                            </h2>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding:0 30px 20px 30px;">
"""
        
        for event in recent_events[-20:]:
            timestamp = self._format_beijing_time(event.get('timestamp'))
            event_type = event.get('type', 'unknown')
            message = event.get('message', '')[:100]
            subsystem = event.get('subsystem', '')
            
            html += f"""
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f8f9fa;border-left:4px solid #2196f3;border-radius:6px;padding:12px;margin-bottom:10px;">
                                <tr>
                                    <td>
                                        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                            <tr>
                                                <td style="color:#6c757d;font-size:12px;">{timestamp}</td>
                                                <td align="right">
                                                    <span style="background:#e0e0e0;padding:2px 8px;border-radius:3px;font-size:11px;color:#2c3e50;">{event_type}</span>
                                                </td>
                                            </tr>
                                        </table>
                                        <div style="margin-top:8px;color:#333;font-size:13px;line-height:1.5;">
                                            <strong>{subsystem}:</strong> {message}{'...' if len(event.get('message', '')) > 100 else ''}
                                        </div>
                                    </td>
                                </tr>
                            </table>
"""
        
        if not recent_events:
            html += """
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f8f9fa;border-radius:6px;padding:20px;">
                                <tr>
                                    <td style="text-align:center;color:#95a5a6;font-size:14px;">
                                        暂无事件记录
                                    </td>
                                </tr>
                            </table>
"""
        
        html += """
                        </td>
                    </tr>
"""
        return html

    def _create_footer(self) -> str:
        """创建页脚 - 邮件优化版本"""
        current_year = datetime.now(ZoneInfo("Asia/Shanghai")).year
        
        return f"""
                    <!-- Footer -->
                    <tr>
                        <td style="padding:30px;background:#f8f9fa;border-top:1px solid #e8edf2;text-align:center;">
                            <p style="margin:0 0 5px 0;color:#6c757d;font-size:13px;">
                                本报告由 <strong style="color:#667eea;">OpenClawMonitor</strong> 自动生成
                            </p>
                            <p style="margin:0;color:#95a5a6;font-size:12px;">
                                © {current_year} OpenClaw 系统监控
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
    
</body>
</html>
"""

    def _format_beijing_time(self, value: Any) -> str:
        """将时间统一转换为北京时间显示。"""
        if not value:
            return "N/A"

        def _coerce_to_datetime(text: str) -> datetime:
            normalized = text.strip()
            if normalized.endswith("Z"):
                normalized = normalized[:-1] + "+00:00"

            if normalized.endswith(" UTC"):
                normalized = normalized[:-4]
                dt = datetime.fromisoformat(normalized)
                return dt.replace(tzinfo=ZoneInfo("UTC"))

            if re.search(r"[+-]\d{4}$", normalized):
                normalized = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", normalized)

            try:
                return datetime.fromisoformat(normalized)
            except ValueError:
                pass

            patterns = [
                "%Y-%m-%d %H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S %z",
                "%Y-%m-%d %H:%M:%S.%f%z",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
            ]
            for pattern in patterns:
                try:
                    return datetime.strptime(normalized, pattern)
                except ValueError:
                    continue

            raise ValueError("Unsupported datetime format")

        try:
            if isinstance(value, datetime):
                dt = value
            else:
                text = str(value).strip()
                if not text:
                    return "N/A"
                dt = _coerce_to_datetime(text)

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))

            return dt.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(value)
