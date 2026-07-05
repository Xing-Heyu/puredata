#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层 - 请求处理辅助模块
提供统一的请求解析、上下文构建等功能

使用方式：
    from core.request_handler import (
        parse_body, build_context, init_context, response
    )
"""

import json
from typing import Any, Dict

from core.logger_impl import get_logger

logger = get_logger('RequestHandler')


def parse_body(handler) -> Dict[str, Any]:
    """
    统一解析请求体
    
    Args:
        handler: HTTP请求处理器实例
    
    Returns:
        解析后的字典，失败返回空字典
    """
    try:
        length = int(handler.headers.get('Content-Length', 0))
        if length > 0:
            body = handler.rfile.read(length).decode('utf-8')
            return json.loads(body)
        return {}
    except Exception as e:
        logger.warning(f"解析请求体失败: {e}")
        return {}


class RequestContext:
    """请求上下文构建器"""
    
    _base_context: Dict[str, Any] = {}
    
    @classmethod
    def init_base_context(cls, **kwargs):
        """初始化基础上下文（启动时调用一次）"""
        cls._base_context = kwargs.copy()
    
    @classmethod
    def build(cls, **extra) -> Dict[str, Any]:
        """
        构建请求上下文
        
        Args:
            **extra: 额外的上下文项
        
        Returns:
            完整的上下文字典
        """
        context = cls._base_context.copy()
        context.update(extra)
        return context
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """获取上下文项"""
        return cls._base_context.get(key, default)


def build_context(**extra) -> Dict[str, Any]:
    """
    构建请求上下文的便捷函数
    
    Args:
        **extra: 额外的上下文项
    
    Returns:
        完整的上下文字典
    """
    return RequestContext.build(**extra)


def init_context(**kwargs):
    """
    初始化基础上下文
    
    在服务器启动时调用一次，设置全局共享的上下文项
    
    Example:
        init_context(
            tasks=tasks,
            ...
        )
    """
    RequestContext.init_base_context(**kwargs)


class ResponseHelper:
    """响应辅助类"""
    
    @staticmethod
    def success(handler, data: Any = None, message: str = "操作成功"):
        """发送成功响应"""
        response = {"success": True, "message": message}
        if data is not None:
            response["data"] = data
        handler._send_json(200, response)
    
    @staticmethod
    def error(handler, error: str, code: int = 400, **extra):
        """发送错误响应"""
        response = {"success": False, "error": error}
        response.update(extra)
        handler._send_json(code, response)
    
    @staticmethod
    def not_found(handler, message: str = "资源不存在"):
        """发送未找到响应"""
        handler._send_json(404, {"success": False, "error": message})
    
    @staticmethod
    def server_error(handler, message: str = "服务器内部错误"):
        """发送服务器错误响应"""
        handler._send_json(500, {"success": False, "error": message})


response = ResponseHelper()


__all__ = [
    'parse_body',
    'RequestContext',
    'build_context',
    'init_context',
    'ResponseHelper',
    'response',
]
