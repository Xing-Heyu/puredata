#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一异常处理 - 装饰器和错误处理
支持: 自动重试、错误日志、用户友好消息
"""

import functools
import traceback
import logging
from datetime import datetime
from typing import Callable, Any, Optional, Dict, List
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DataGenPro')

class ErrorCode(Enum):
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    VALIDATION_ERROR = 1001
    AUTHENTICATION_ERROR = 1002
    AUTHORIZATION_ERROR = 1003
    NOT_FOUND_ERROR = 1004
    RATE_LIMIT_ERROR = 1005
    QUOTA_EXCEEDED_ERROR = 1006
    GENERATION_ERROR = 1007
    FILE_ERROR = 1008
    DATABASE_ERROR = 1009
    NETWORK_ERROR = 1010
    TIMEOUT_ERROR = 1011

ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "操作成功",
    ErrorCode.UNKNOWN_ERROR: "未知错误，请稍后重试",
    ErrorCode.VALIDATION_ERROR: "参数验证失败",
    ErrorCode.AUTHENTICATION_ERROR: "认证失败，请重新登录",
    ErrorCode.AUTHORIZATION_ERROR: "权限不足",
    ErrorCode.NOT_FOUND_ERROR: "资源不存在",
    ErrorCode.RATE_LIMIT_ERROR: "请求过于频繁，请稍后重试",
    ErrorCode.QUOTA_EXCEEDED_ERROR: "配额已用尽",
    ErrorCode.GENERATION_ERROR: "数据生成失败",
    ErrorCode.FILE_ERROR: "文件操作失败",
    ErrorCode.DATABASE_ERROR: "数据库操作失败",
    ErrorCode.NETWORK_ERROR: "网络连接失败",
    ErrorCode.TIMEOUT_ERROR: "操作超时",
}

class AppException(Exception):
    """应用异常基类"""
    
    def __init__(self, code: ErrorCode, message: str = None, details: Any = None):
        self.code = code
        self.message = message or ERROR_MESSAGES.get(code, "未知错误")
        self.details = details
        self.timestamp = datetime.now().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict:
        return {
            "success": False,
            "error": {
                "code": self.code.value,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp
            }
        }

class ValidationError(AppException):
    def __init__(self, message: str = "参数验证失败", details: Any = None):
        super().__init__(ErrorCode.VALIDATION_ERROR, message, details)

class AuthenticationError(AppException):
    def __init__(self, message: str = "认证失败", details: Any = None):
        super().__init__(ErrorCode.AUTHENTICATION_ERROR, message, details)

class AuthorizationError(AppException):
    def __init__(self, message: str = "权限不足", details: Any = None):
        super().__init__(ErrorCode.AUTHORIZATION_ERROR, message, details)

class NotFoundError(AppException):
    def __init__(self, message: str = "资源不存在", details: Any = None):
        super().__init__(ErrorCode.NOT_FOUND_ERROR, message, details)

class RateLimitError(AppException):
    def __init__(self, message: str = "请求过于频繁", details: Any = None):
        super().__init__(ErrorCode.RATE_LIMIT_ERROR, message, details)

class QuotaExceededError(AppException):
    def __init__(self, message: str = "配额已用尽", details: Any = None):
        super().__init__(ErrorCode.QUOTA_EXCEEDED_ERROR, message, details)

class GenerationError(AppException):
    def __init__(self, message: str = "数据生成失败", details: Any = None):
        super().__init__(ErrorCode.GENERATION_ERROR, message, details)

class FileError(AppException):
    def __init__(self, message: str = "文件操作失败", details: Any = None):
        super().__init__(ErrorCode.FILE_ERROR, message, details)

class DatabaseError(AppException):
    def __init__(self, message: str = "数据库操作失败", details: Any = None):
        super().__init__(ErrorCode.DATABASE_ERROR, message, details)

def handle_errors(
    default_return: Any = None,
    log_errors: bool = True,
    reraise: bool = False,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    retry_exceptions: tuple = (Exception,)
):
    """
    统一异常处理装饰器
    
    Args:
        default_return: 异常时的默认返回值
        log_errors: 是否记录错误日志
        reraise: 是否重新抛出异常
        retry_count: 重试次数
        retry_delay: 重试间隔(秒)
        retry_exceptions: 需要重试的异常类型
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(retry_count + 1):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    last_exception = e
                    
                    if attempt < retry_count:
                        import time
                        time.sleep(retry_delay)
                        if log_errors:
                            logger.warning(
                                f"[重试] {func.__name__} 第{attempt + 1}次失败: {str(e)}, "
                                f"{retry_delay}秒后重试..."
                            )
                        continue
                    
                    if log_errors:
                        logger.error(
                            f"[错误] {func.__name__} 执行失败: {str(e)}\n"
                            f"{''.join(traceback.format_tb(e.__traceback__))}"
                        )
                    
                    if reraise:
                        raise
                    
                    if isinstance(e, AppException):
                        return e.to_dict()
                    
                    return {
                        "success": False,
                        "error": str(e),
                        "function": func.__name__,
                        "timestamp": datetime.now().isoformat()
                    }
                except AppException as e:
                    if log_errors:
                        logger.error(f"[业务错误] {func.__name__}: {e.message}")
                    if reraise:
                        raise
                    return e.to_dict()
                except Exception as e:
                    if log_errors:
                        logger.error(
                            f"[未知错误] {func.__name__}: {str(e)}\n"
                            f"{''.join(traceback.format_tb(e.__traceback__))}"
                        )
                    if reraise:
                        raise
                    return {
                        "success": False,
                        "error": str(e),
                        "function": func.__name__,
                        "timestamp": datetime.now().isoformat()
                    }
            
            return default_return
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, default=None, **kwargs) -> Any:
    """安全执行函数，捕获所有异常"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"安全执行失败: {func.__name__} - {str(e)}")
        return default

def assert_condition(condition: bool, error_message: str, error_class: type = ValidationError):
    """断言条件，失败时抛出指定异常"""
    if not condition:
        raise error_class(error_message)

def validate_required(data: Dict, required_fields: List[str]):
    """验证必填字段"""
    missing = [f for f in required_fields if f not in data or not data[f]]
    if missing:
        raise ValidationError(f"缺少必填字段: {', '.join(missing)}")

def validate_type(value: Any, expected_type: type, field_name: str):
    """验证字段类型"""
    if not isinstance(value, expected_type):
        raise ValidationError(f"字段 {field_name} 类型错误，期望 {expected_type.__name__}")

def validate_range(value: (int, float), min_val: (int, float), max_val: (int, float), field_name: str):
    """验证数值范围"""
    if not min_val <= value <= max_val:
        raise ValidationError(f"字段 {field_name} 值 {value} 超出范围 [{min_val}, {max_val}]")

def validate_length(value: str, min_len: int, max_len: int, field_name: str):
    """验证字符串长度"""
    length = len(value)
    if not min_len <= length <= max_len:
        raise ValidationError(f"字段 {field_name} 长度 {length} 超出范围 [{min_len}, {max_len}]")

class ErrorContext:
    """错误上下文管理器"""
    
    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            logger.error(
                f"[{self.operation}] 执行失败 (耗时: {elapsed:.2f}s)\n"
                f"上下文: {self.context}\n"
                f"错误: {exc_val}"
            )
        return False

def error_response(error: Exception) -> Dict:
    """生成标准错误响应"""
    if isinstance(error, AppException):
        return error.to_dict()
    
    return {
        "success": False,
        "error": {
            "code": ErrorCode.UNKNOWN_ERROR.value,
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        }
    }

def success_response(data: Any = None, message: str = "操作成功") -> Dict:
    """生成标准成功响应"""
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return response


if __name__ == "__main__":
    print("\n" + "="*60)
    print("统一异常处理测试")
    print("="*60)
    
    @handle_errors(default_return={"success": False}, retry_count=2, retry_delay=0.1)
    def risky_operation(should_fail: bool = True):
        if should_fail:
            raise ValueError("模拟错误")
        return {"success": True, "data": "操作成功"}
    
    print("\n[1] 测试重试机制...")
    result = risky_operation(should_fail=True)
    print(f"  结果: {result}")
    
    print("\n[2] 测试成功执行...")
    result = risky_operation(should_fail=False)
    print(f"  结果: {result}")
    
    print("\n[3] 测试业务异常...")
    @handle_errors()
    def business_operation():
        raise ValidationError("用户名不能为空", details={"field": "username"})
    
    result = business_operation()
    print(f"  结果: {result}")
    
    print("\n[4] 测试验证工具...")
    try:
        validate_required({"username": "test"}, ["username", "email"])
    except ValidationError as e:
        print(f"  验证失败: {e.message}")
    
    print("\n[5] 测试错误上下文...")
    with ErrorContext("测试操作", user_id="test_user"):
        raise ValueError("测试错误")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
