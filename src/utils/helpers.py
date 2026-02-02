"""
辅助函数
"""

import os
from pathlib import Path
from typing import Union


def expand_path(path: Union[str, Path]) -> Path:
    """
    扩展路径，处理 ~ 和环境变量
    
    Args:
        path: 路径字符串或 Path 对象
    
    Returns:
        Path: 扩展后的 Path 对象
    """
    return Path(os.path.expanduser(os.path.expandvars(str(path))))


def get_project_root() -> Path:
    """
    获取项目根目录
    
    Returns:
        Path: 项目根目录路径
    """
    # 获取当前文件的父目录链
    current_file = Path(__file__)
    # src/utils/helpers.py -> 项目根目录（往上 2 层）
    return current_file.parent.parent.parent


def get_database_path(relative_path: str = "database/openclaw_monitor.db") -> Path:
    """
    获取数据库文件的绝对路径
    
    Args:
        relative_path: 相对于项目根的路径
    
    Returns:
        Path: 数据库文件的绝对路径
    """
    project_root = get_project_root()
    db_path = project_root / relative_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path
