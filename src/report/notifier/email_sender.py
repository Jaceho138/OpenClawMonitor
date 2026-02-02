"""
邮件通知模块 - 支持 Gmail SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
import keyring

from report.notifier.base_notifier import BaseNotifier


logger = logging.getLogger(__name__)


class EmailNotifier(BaseNotifier):
    """
    邮件通知器
    使用 Gmail SMTP 或其他邮件服务发送邮件
    """
    
    def __init__(
        self,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_username: Optional[str] = None,
        sender_email: str = None,
        sender_password: str = None,
        use_encryption: bool = True,
        use_keyring: bool = True,
    ):
        """
        初始化邮件通知器
        
        Args:
            smtp_server: SMTP 服务器地址
            smtp_port: SMTP 端口
            smtp_username: SMTP 登录用户名（可选，默认使用 sender_email）
            sender_email: 发送者邮箱
            sender_password: 发送者密码
            use_encryption: 是否使用加密连接
            use_keyring: 是否从 keyring 获取密码
        """
        super().__init__("EmailNotifier")
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_encryption = use_encryption
        
        # 从 keyring 获取密码
        if use_keyring and self.sender_email:
            try:
                stored_password = keyring.get_password("openclaw_monitor", self.sender_email)
                if stored_password:
                    self.sender_password = stored_password
                    logger.debug(f"从 keyring 获取密码成功")
            except Exception as e:
                logger.warning(f"从 keyring 获取密码失败: {e}")
    
    def send(self, subject: str, content: str, recipient_email: str = None, **kwargs) -> bool:
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            content: 邮件内容（HTML 格式）
            recipient_email: 收件人邮箱
            **kwargs: 其他参数
        
        Returns:
            bool: 是否发送成功
        """
        if not self.sender_email or not self.sender_password:
            logger.error("缺少邮箱配置信息")
            return False
        
        if not recipient_email:
            recipient_email = kwargs.get("recipient_email")
            if not recipient_email:
                logger.error("未指定收件人邮箱")
                return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            
            # 添加 HTML 内容
            html_part = MIMEText(content, "html", "utf-8")
            msg.attach(html_part)
            
            # 连接到 SMTP 服务器并发送
            if self.use_encryption and self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_encryption:
                    server.starttls()

            login_username = self.smtp_username or self.sender_email
            server.login(login_username, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            self.log_status(True, f"发送给 {recipient_email}")
            return True
        
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            self.log_status(False, str(e))
            return False
    
    @staticmethod
    def save_password_to_keyring(email: str, password: str) -> bool:
        """
        将密码保存到 keyring
        
        Args:
            email: 邮箱地址
            password: 密码
        
        Returns:
            bool: 是否保存成功
        """
        try:
            keyring.set_password("openclaw_monitor", email, password)
            logger.info(f"密码已保存到 keyring")
            return True
        except Exception as e:
            logger.error(f"保存密码到 keyring 失败: {e}")
            return False
