#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataGen Pro - 结构化日志系统
支持文件日志、控制台日志、JSON格式

合并自：
- 结构化日志.py（完整功能）
- datagenpro/utils/logger.py（success方法）
"""

import json
import logging
import os
import sys
from datetime import datetime
from functools import wraps
import threading

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器 - JSON格式"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'extra_data') and record.extra_data:
            log_data["data"] = record.extra_data
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """彩色控制台格式化器"""
    
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'SUCCESS': '\033[32;1m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        formatted = f"{color}[{timestamp}] [{record.levelname:8}]{self.RESET} {record.name}: {record.getMessage()}"
        
        if hasattr(record, 'extra_data') and record.extra_data:
            formatted += f" | {json.dumps(record.extra_data, ensure_ascii=False)}"
        
        return formatted

class StructuredLogger:
    """结构化日志器 - 完整版"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, name="DataGenPro"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, name="DataGenPro"):
        if self._initialized:
            return
        
        self._initialized = True
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        self.logger.handlers.clear()
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        file_handler = logging.FileHandler(
            os.path.join(LOG_DIR, f'{name.lower()}.log'),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        error_handler = logging.FileHandler(
            os.path.join(LOG_DIR, 'error.log'),
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
        
        logging.addLevelName(25, 'SUCCESS')
    
    def _log(self, level, message, **kwargs):
        extra = {'extra_data': kwargs} if kwargs else {}
        if level == 'success':
            self.logger.log(25, message, extra=extra)
        else:
            getattr(self.logger, level)(message, extra=extra)
    
    def debug(self, message, **kwargs):
        self._log('debug', message, **kwargs)
    
    def info(self, message, **kwargs):
        self._log('info', message, **kwargs)
    
    def warning(self, message, **kwargs):
        self._log('warning', message, **kwargs)
    
    def error(self, message, **kwargs):
        self._log('error', message, **kwargs)
    
    def critical(self, message, **kwargs):
        self._log('critical', message, **kwargs)
    
    def success(self, message, **kwargs):
        self._log('success', message, **kwargs)
    
    def task_start(self, task_id, domain, count):
        self.info("任务开始", task_id=task_id, domain=domain, count=count, event="task_start")
    
    def task_complete(self, task_id, count, elapsed):
        self.info("任务完成", task_id=task_id, count=count, elapsed_seconds=elapsed, event="task_complete")
    
    def task_error(self, task_id, error):
        self.error("任务失败", task_id=task_id, error=str(error), event="task_error")
    
    def api_request(self, method, path, ip, user=None):
        self.debug("API请求", method=method, path=path, client_ip=ip, user=user, event="api_request")
    
    def api_response(self, method, path, status_code, elapsed_ms):
        self.debug("API响应", method=method, path=path, status_code=status_code, elapsed_ms=elapsed_ms, event="api_response")
    
    def user_action(self, username, action, details=None):
        self.info("用户操作", username=username, action=action, details=details, event="user_action")
    
    def security_event(self, event_type, details):
        self.warning("安全事件", event_type=event_type, details=details, event="security")
    
    def performance(self, operation, elapsed_ms, details=None):
        if elapsed_ms > 1000:
            self.warning("性能警告", operation=operation, elapsed_ms=elapsed_ms, details=details, event="performance")
        else:
            self.debug("性能指标", operation=operation, elapsed_ms=elapsed_ms, details=details, event="performance")

def log_execution(logger_instance=None):
    """执行日志装饰器"""
    if logger_instance is None:
        logger_instance = StructuredLogger()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            func_name = func.__name__
            
            try:
                result = func(*args, **kwargs)
                elapsed = (datetime.now() - start_time).total_seconds() * 1000
                logger_instance.performance(func_name, elapsed)
                return result
            except Exception as e:
                elapsed = (datetime.now() - start_time).total_seconds() * 1000
                logger_instance.error(f"函数执行失败: {func_name}", error=str(e), elapsed_ms=elapsed)
                raise
        
        return wrapper
    return decorator

def get_logger(name="DataGenPro"):
    """获取日志器实例"""
    return StructuredLogger(name)

logger = StructuredLogger()

__all__ = ["StructuredLogger", "logger", "get_logger", "log_execution"]
