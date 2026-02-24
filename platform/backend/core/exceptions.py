#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层 - 异常定义
统一异常体系
"""

class DataGenProError(Exception):
    """DataGen Pro 基础异常"""
    pass

class ValidationError(DataGenProError):
    """数据验证异常"""
    pass

class QualityError(DataGenProError):
    """质量控制异常"""
    pass

class ConfigurationError(DataGenProError):
    """配置异常"""
    pass

class StorageError(DataGenProError):
    """存储异常"""
    pass

class AuthenticationError(DataGenProError):
    """认证异常"""
    pass

class AuthorizationError(DataGenProError):
    """授权异常"""
    pass

class RateLimitError(DataGenProError):
    """速率限制异常"""
    pass

class TaskError(DataGenProError):
    """任务异常"""
    pass

class GenerationError(DataGenProError):
    """生成异常"""
    pass

class TemplateError(DataGenProError):
    """模板异常"""
    pass

class DomainError(DataGenProError):
    """领域异常"""
    pass

__all__ = [
    'DataGenProError',
    'ValidationError',
    'QualityError',
    'ConfigurationError',
    'StorageError',
    'AuthenticationError',
    'AuthorizationError',
    'RateLimitError',
    'TaskError',
    'GenerationError',
    'TemplateError',
    'DomainError',
]
