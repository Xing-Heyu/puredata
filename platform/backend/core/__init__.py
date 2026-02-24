#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层模块 - 懒加载入口
提供基础设施：配置、日志、缓存、存储、异常、常量

使用方式：
    from core import config, logger, cache, storage
    from core import DataGenProError, ValidationError
"""

__all__ = [
    'config', 'logger', 'cache', 'storage',
    'Config', 'StructuredLogger', 'CacheManager', 'StorageManager',
    'DataGenProError', 'ValidationError', 'QualityError',
    'DOMAINS', 'QUALITY_LEVELS', 'SUPPORTED_FORMATS',
    'invalidate_cache',
]

_core_modules = {
    'config': ('.config_impl', 'config'),
    'Config': ('.config_impl', 'Config'),
    'logger': ('.logger_impl', 'logger'),
    'StructuredLogger': ('.logger_impl', 'StructuredLogger'),
    'cache': ('.cache_impl', 'cache_manager'),
    'CacheManager': ('.cache_impl', 'CacheManager'),
    'storage': ('.storage_impl', 'storage_manager'),
    'StorageManager': ('.storage_impl', 'StorageManager'),
    'invalidate_cache': ('.cache_impl', 'invalidate_cache'),
}

def __getattr__(name):
    if name in _core_modules:
        module_path, attr_name = _core_modules[name]
        import importlib
        module = importlib.import_module(module_path, package='core')
        return getattr(module, attr_name)
    
    if name == 'DataGenProError':
        from .exceptions import DataGenProError
        return DataGenProError
    if name == 'ValidationError':
        from .exceptions import ValidationError
        return ValidationError
    if name == 'QualityError':
        from .exceptions import QualityError
        return QualityError
    if name == 'DOMAINS':
        from .constants import DOMAINS
        return DOMAINS
    if name == 'QUALITY_LEVELS':
        from .constants import QUALITY_LEVELS
        return QUALITY_LEVELS
    if name == 'SUPPORTED_FORMATS':
        from .constants import SUPPORTED_FORMATS
        return SUPPORTED_FORMATS
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def get_config(key: str = None, default=None):
    """获取配置"""
    from .config_impl import get_config as _get_config
    return _get_config(key, default)

def get_logger(name: str = "DataGenPro"):
    """获取日志器"""
    from .logger_impl import get_logger as _get_logger
    return _get_logger(name)

def get_cache(name: str = "default"):
    """获取缓存"""
    from .cache_impl import CacheManager
    return CacheManager().get_cache(name)
