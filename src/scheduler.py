"""
调度模块 - 使用 schedule 库进行定时任务
"""

import schedule
import time
import logging
from datetime import datetime
from typing import Callable
from threading import Thread


logger = logging.getLogger(__name__)


class Scheduler:
    """
    任务调度器
    管理定时任务（如每日 8:00 AM 生成报告和发送邮件）
    """
    
    def __init__(self):
        """初始化调度器"""
        self.tasks = []
        self.running = False
        self.scheduler_thread = None
    
    def schedule_daily_task(
        self,
        time_str: str,
        task_func: Callable,
        task_name: str = "定时任务",
    ):
        """
        安排每日定时任务
        
        Args:
            time_str: 执行时间（格式：'HH:MM'，例如 '08:00'）
            task_func: 要执行的函数
            task_name: 任务名称
        """
        def wrapper():
            logger.info(f"执行任务: {task_name}")
            try:
                task_func()
                logger.info(f"任务完成: {task_name}")
            except Exception as e:
                logger.error(f"任务执行失败: {task_name} - {e}")
        
        schedule.every().day.at(time_str).do(wrapper)
        self.tasks.append({
            "name": task_name,
            "time": time_str,
            "function": task_func,
        })
        logger.info(f"已安排任务: {task_name} 在 {time_str}")
    
    def schedule_interval_task(
        self,
        interval: int,
        unit: str,
        task_func: Callable,
        task_name: str = "定时任务",
    ):
        """
        安排间隔定时任务
        
        Args:
            interval: 间隔数
            unit: 单位（'seconds', 'minutes', 'hours', 'days'）
            task_func: 要执行的函数
            task_name: 任务名称
        """
        def wrapper():
            logger.info(f"执行任务: {task_name}")
            try:
                task_func()
                logger.info(f"任务完成: {task_name}")
            except Exception as e:
                logger.error(f"任务执行失败: {task_name} - {e}")
        
        if unit == "seconds":
            schedule.every(interval).seconds.do(wrapper)
        elif unit == "minutes":
            schedule.every(interval).minutes.do(wrapper)
        elif unit == "hours":
            schedule.every(interval).hours.do(wrapper)
        elif unit == "days":
            schedule.every(interval).days.do(wrapper)
        else:
            raise ValueError(f"不支持的时间单位: {unit}")
        
        self.tasks.append({
            "name": task_name,
            "interval": interval,
            "unit": unit,
            "function": task_func,
        })
        logger.info(f"已安排任务: {task_name} 每 {interval} 个 {unit}")
    
    def start(self):
        """
        启动调度器（后台线程）
        """
        if self.running:
            logger.warning("调度器已在运行")
            return
        
        self.running = True
        self.scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("调度器已启动")
    
    def _run_scheduler(self):
        """
        运行调度器主循环
        """
        logger.info("调度器主循环已启动")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"调度器错误: {e}")
                time.sleep(5)  # 错误后暂停 5 秒
    
    def stop(self):
        """
        停止调度器
        """
        if not self.running:
            logger.warning("调度器未运行")
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        logger.info("调度器已停止")
    
    def get_tasks(self):
        """
        获取所有已安排的任务
        
        Returns:
            list: 任务列表
        """
        return self.tasks
