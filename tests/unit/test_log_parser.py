"""
单元测试 - 日志解析模块测试
"""

import pytest
import json
import tempfile
from pathlib import Path
from openclawmonitor.monitor.log_parser import LogParser


def test_parse_jsonl_file():
    """测试 JSONL 文件解析"""
    # 创建临时 JSONL 文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # 写入测试数据
        test_data = [
            {"timestamp": "2024-01-15T10:00:00", "exec": "ls -la"},
            {"timestamp": "2024-01-15T10:01:00", "path": "/tmp/test.txt", "type": "access"},
            {"timestamp": "2024-01-15T10:02:00", "message": "permission denied", "level": "error"},
        ]
        
        for data in test_data:
            f.write(json.dumps(data) + "\n")
        
        f.flush()
        
        # 解析文件
        result = LogParser._parse_jsonl_file(f.name)
        
        # 验证结果
        assert len(result["commands"]) == 1
        assert len(result["file_accesses"]) == 1
        assert len(result["events"]) == 1
        assert result["commands"][0]["command"] == "ls -la"
        
        # 清理
        Path(f.name).unlink()


def test_path_resolver():
    """测试路径解析器"""
    from openclawmonitor.utils.path_resolver import PathResolver
    
    resolver = PathResolver(["/tmp/openclaw/", "~/.openclaw/logs/"])
    
    # 测试 glob 模式生成
    pattern = PathResolver.get_daily_log_pattern("/tmp/openclaw/")
    assert "/tmp/openclaw/" in pattern
    assert "*" in pattern
