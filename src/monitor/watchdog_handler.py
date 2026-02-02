"""
文件系统监控模块 - 使用 watchdog 监控日志文件变更
"""

import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from typing import Callable, List
import logging


logger = logging.getLogger(__name__)


class LogFileHandler(FileSystemEventHandler):
    """
    日志文件变更处理器
    """
    
    def __init__(self, callback: Callable = None, watched_extensions: List[str] = None):
        """
        初始化处理器
        
        Args:
            callback: 文件变更时的回调函数
            watched_extensions: 监控的文件扩展名列表
        """
        super().__init__()
        self.callback = callback
        self.watched_extensions = watched_extensions or ['.log', '.jsonl']
    
    def on_modified(self, event: FileModifiedEvent):
        """
        处理文件修改事件
        
        Args:
            event: 文件事件
        """
        if not event.is_directory:
            # 检查文件扩展名
            if any(event.src_path.endswith(ext) for ext in self.watched_extensions):
                logger.debug(f"日志文件已修改: {event.src_path}")
                
                if self.callback:
                    try:
                        self.callback(event.src_path)
                    except Exception as e:
                        logger.error(f"处理文件变更回调时出错: {e}")
    
    def on_created(self, event: FileModifiedEvent):
        """
        处理文件创建事件
        
        Args:
            event: 文件事件
        """
        if not event.is_directory:
            if any(event.src_path.endswith(ext) for ext in self.watched_extensions):
                logger.debug(f"新日志文件已创建: {event.src_path}")
                
                if self.callback:
                    try:
                        self.callback(event.src_path)
                    except Exception as e:
                        logger.error(f"处理文件创建回调时出错: {e}")


class LogFileMonitor:
    """
    日志文件监控器
    """
    
    def __init__(self, paths: List[str], callback: Callable = None):
        """
        初始化监控器
        
        Args:
            paths: 监控的路径列表
            callback: 文件变更时的回调函数
        """
        self.paths = paths
        self.callback = callback
        self.observer = None
        self.event_handler = LogFileHandler(callback)
    
    def start(self):
        """
        开始监控
        """
        if self.observer is None:
            self.observer = Observer()
            
            for path in self.paths:
                expanded_path = os.path.expanduser(os.path.expandvars(path))
                
                if os.path.exists(expanded_path):
                    self.observer.schedule(self.event_handler, expanded_path, recursive=True)
                    logger.info(f"已开始监控路径: {expanded_path}")
                else:
                    logger.warning(f"监控路径不存在: {expanded_path}")
            
            self.observer.start()
            logger.info("文件监控器已启动")
    
    def stop(self):
        """
        停止监控
        """
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            logger.info("文件监控器已停止")
