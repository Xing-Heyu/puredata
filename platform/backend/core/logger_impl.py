#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层 - 日志系统实现
统一日志配置入口，支持日志轮转、结构化日志、向后兼容

使用方式：
    from core.logger_impl import setup_logging, get_logger
    
    # 在程序入口处调用一次
    logger = setup_logging()
    
    # 在其他模块中获取logger
    logger = get_logger('ModuleName')
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from functools import wraps
from typing import Optional, Dict, Any
import threading

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

_initialized = False
_init_lock = threading.Lock()
_main_logger: Optional['StructuredLogger'] = None


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
    
    _instances: Dict[str, 'StructuredLogger'] = {}
    _lock = threading.Lock()
    
    def __new__(cls, name: str = "DataGenPro"):
        if name not in cls._instances:
            with cls._lock:
                if name not in cls._instances:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instances[name] = instance
        return cls._instances[name]
    
    def __init__(self, name: str = "DataGenPro"):
        if self._initialized:
            return
        
        self._initialized = True
        self.name = name
        self.logger = logging.getLogger(name)
        
        if not self.logger.handlers:
            self.logger.setLevel(logging.DEBUG)
            self._setup_handlers()
        
        logging.addLevelName(25, 'SUCCESS')
    
    def _setup_handlers(self):
        """设置日志处理器"""
        self.logger.handlers.clear()
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(LOG_DIR, f'{self.name.lower()}.log'),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(LOG_DIR, 'error.log'),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
    
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


def setup_logging(
    name: str = "DataGenPro",
    log_file: Optional[str] = None,
    level: int = logging.DEBUG,
    console_level: int = logging.INFO,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_error_file: bool = True,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> StructuredLogger:
    """
    统一的日志配置入口
    
    在程序入口处调用一次，返回主日志器实例。
    后续可通过 get_logger() 获取其他模块的日志器。
    
    Args:
        name: 日志器名称
        log_file: 自定义日志文件路径（None则使用默认路径）
        level: 日志级别
        console_level: 控制台日志级别
        enable_console: 是否输出到控制台
        enable_file: 是否输出到文件
        enable_error_file: 是否单独记录错误日志
        max_bytes: 单个日志文件最大大小（字节）
        backup_count: 保留的日志文件数量
    
    Returns:
        StructuredLogger 实例
    """
    global _initialized, _main_logger
    
    with _init_lock:
        if _initialized and _main_logger:
            return _main_logger
        
        logger_instance = StructuredLogger(name)
        
        if log_file or max_bytes != 10 * 1024 * 1024 or backup_count != 5:
            logger_instance.logger.handlers.clear()
            
            if enable_console:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(console_level)
                console_handler.setFormatter(ColoredFormatter())
                logger_instance.logger.addHandler(console_handler)
            
            if enable_file:
                file_path = log_file or os.path.join(LOG_DIR, f'{name.lower()}.log')
                file_handler = logging.handlers.RotatingFileHandler(
                    file_path,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(level)
                file_handler.setFormatter(StructuredFormatter())
                logger_instance.logger.addHandler(file_handler)
            
            if enable_error_file:
                error_handler = logging.handlers.RotatingFileHandler(
                    os.path.join(LOG_DIR, 'error.log'),
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                error_handler.setLevel(logging.ERROR)
                error_handler.setFormatter(StructuredFormatter())
                logger_instance.logger.addHandler(error_handler)
        
        _initialized = True
        _main_logger = logger_instance
        
        return logger_instance


def get_logger(name: str = "DataGenPro") -> StructuredLogger:
    """
    获取日志器实例
    
    如果尚未初始化，会自动使用默认配置初始化。
    
    Args:
        name: 日志器名称
    
    Returns:
        StructuredLogger 实例
    """
    global _initialized
    
    if not _initialized:
        return setup_logging(name)
    
    return StructuredLogger(name)


def log_execution(logger_instance: Optional[StructuredLogger] = None):
    """执行日志装饰器"""
    if logger_instance is None:
        logger_instance = get_logger()
    
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


logger = StructuredLogger()

__all__ = [
    "StructuredLogger",
    "StructuredFormatter", 
    "ColoredFormatter",
    "logger",
    "get_logger",
    "setup_logging",
    "log_execution",
    "LOG_DIR"
]
