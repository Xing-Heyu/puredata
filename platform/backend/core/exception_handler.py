#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层 - 统一异常处理
提供装饰器和工具函数，减少 try-except 嵌套

使用方式：
    from core.exception_handler import safe_execute, SafeContext
    
    # 装饰器方式
    @safe_execute(default_return=None, log_error=True)
    def my_function():
        ...
    
    # 上下文管理器方式
    with SafeContext("操作名称", default_return={}):
        ...
"""

import functools
import traceback
from typing import Any, Callable, Optional, Type, Tuple
from contextlib import contextmanager

from core.logger_impl import get_logger

logger = get_logger('ExceptionHandler')


def safe_execute(
    default_return: Any = None,
    log_error: bool = True,
    reraise: bool = False,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    统一异常处理装饰器
    
    Args:
        default_return: 发生异常时的默认返回值
        log_error: 是否记录错误日志
        reraise: 是否重新抛出异常
        exceptions: 要捕获的异常类型元组
    
    Returns:
        装饰器函数
    
    Example:
        @safe_execute(default_return=[], log_error=True)
        def get_items():
            return risky_operation()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log_error:
                    logger.error(
                        f"函数执行失败: {func.__name__}",
                        error=str(e),
                        error_type=type(e).__name__
                    )
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def safe_execute_async(
    default_return: Any = None,
    log_error: bool = True,
    reraise: bool = False,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    异步版本的统一异常处理装饰器
    
    Args:
        default_return: 发生异常时的默认返回值
        log_error: 是否记录错误日志
        reraise: 是否重新抛出异常
        exceptions: 要捕获的异常类型元组
    
    Returns:
        异步装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                if log_error:
                    logger.error(
                        f"异步函数执行失败: {func.__name__}",
                        error=str(e),
                        error_type=type(e).__name__
                    )
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


class SafeContext:
    """
    安全上下文管理器
    
    Example:
        with SafeContext("数据库操作", default_return={}):
            result = db.query()
    """
    
    def __init__(
        self,
        operation: str,
        default_return: Any = None,
        log_error: bool = True,
        reraise: bool = False
    ):
        self.operation = operation
        self.default_return = default_return
        self.log_error = log_error
        self.reraise = reraise
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            if self.log_error:
                logger.error(
                    f"操作失败: {self.operation}",
                    error=str(exc_val),
                    error_type=exc_type.__name__
                )
            if self.reraise:
                return False
            return True
        return False


@contextmanager
def safe_context(
    operation: str,
    default_return: Any = None,
    log_error: bool = True,
    reraise: bool = False
):
    """
    安全上下文管理器函数形式
    
    Example:
        with safe_context("文件操作"):
            with open(file) as f:
                content = f.read()
    """
    ctx = SafeContext(operation, default_return, log_error, reraise)
    try:
        yield ctx
    except Exception as e:
        if log_error:
            logger.error(
                f"操作失败: {operation}",
                error=str(e),
                error_type=type(e).__name__
            )
        if reraise:
            raise
        ctx.error = e


def ignore_errors(*exceptions: Type[Exception]):
    """
    忽略指定异常的装饰器
    
    Example:
        @ignore_errors(KeyError, IndexError)
        def get_value(data, key):
            return data[key]
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions:
                return None
        return wrapper
    return decorator


def retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟时间增长因子
        exceptions: 要重试的异常类型
    
    Example:
        @retry(max_retries=3, delay=1.0)
        def unstable_operation():
            ...
    """
    import time
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"操作失败，准备重试: {func.__name__}",
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            delay=current_delay,
                            error=str(e)
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            logger.error(
                f"操作最终失败: {func.__name__}",
                attempts=max_retries + 1,
                error=str(last_exception)
            )
            raise last_exception
        return wrapper
    return decorator


class ModuleLoader:
    """
    模块加载器 - 统一处理模块导入的 try-except
    
    Example:
        loader = ModuleLoader()
        bcrypt = loader.load('bcrypt')
        if bcrypt:
            password = bcrypt.hashpw(password, bcrypt.gensalt())
    """
    
    def __init__(self):
        self._loaded = {}
        self._available = {}
    
    def load(self, module_name: str, items: list = None) -> Any:
        """
        加载模块，失败返回 None
        
        Args:
            module_name: 模块名称
            items: 要导入的子项列表
        
        Returns:
            模块对象或 None
        """
        if module_name in self._loaded:
            return self._loaded[module_name]
        
        try:
            module = __import__(module_name, fromlist=items or [])
            self._loaded[module_name] = module
            self._available[module_name] = True
            logger.debug(f"模块加载成功: {module_name}")
            return module
        except ImportError as e:
            self._loaded[module_name] = None
            self._available[module_name] = False
            logger.debug(f"模块不可用: {module_name} - {e}")
            return None
    
    def is_available(self, module_name: str) -> bool:
        """检查模块是否可用"""
        if module_name not in self._available:
            self.load(module_name)
        return self._available.get(module_name, False)
    
    def get_attr(self, module_name: str, attr_name: str, default: Any = None) -> Any:
        """获取模块属性，失败返回默认值"""
        module = self.load(module_name)
        if module and hasattr(module, attr_name):
            return getattr(module, attr_name)
        return default


module_loader = ModuleLoader()


__all__ = [
    "safe_execute",
    "safe_execute_async",
    "SafeContext",
    "safe_context",
    "ignore_errors",
    "retry",
    "ModuleLoader",
    "module_loader"
]
