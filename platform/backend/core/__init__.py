#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层模块 - 懒加载入口
提供基础设施：配置、日志、缓存、异常、常量、路径

使用方式：
    from core import config, logger, cache
    from core import DataGenProError, ValidationError
    from core import BACKEND_DIR, OUTPUT_DIR, FRONTEND_DIR
"""

__all__ = [
    'config', 'logger', 'cache',
    'Config', 'StructuredLogger', 'CacheManager',
    'DataGenProError', 'ValidationError', 'QualityError',
    'DOMAINS', 'QUALITY_LEVELS', 'SUPPORTED_FORMATS',
    'invalidate_cache',
    'BACKEND_DIR', 'PLATFORM_DIR', 'PROJECT_ROOT',
    'FRONTEND_DIR', 'DOCS_DIR',
    'OUTPUT_DIR', 'CACHE_DIR', 'LOGS_DIR', 'DATA_DIR', 'BACKUPS_DIR',
    'KEYWORDS_DIR', 'DOMAIN_CONFIGS_DIR', 'DOMAIN_TEMPLATES_DIR', 'CONFIG_DIR',
    'STATIC_DIR', 'IMAGES_DIR',
    'USER_DB_FILE', 'SESSION_FILE', 'USER_JSON_FILE', 'DATAGENPRO_DB_FILE',
    'safe_path_join', 'ensure_dirs',
    'safe_execute', 'SafeContext', 'safe_context', 'retry', 'module_loader',
    'get_logger', 'setup_logging',
    'parse_body', 'get_token', 'require_auth',
    'RequestContext', 'build_context', 'init_context', 'response',
    'module_registry', 'ModuleRegistry',
]

_core_modules = {
    'config': ('.config_impl', 'config'),
    'Config': ('.config_impl', 'Config'),
    'logger': ('.logger_impl', 'logger'),
    'StructuredLogger': ('.logger_impl', 'StructuredLogger'),
    'cache': ('.cache_impl', 'cache_manager'),
    'CacheManager': ('.cache_impl', 'CacheManager'),
    'invalidate_cache': ('.cache_impl', 'invalidate_cache'),
}

_path_attrs = {
    'BACKEND_DIR', 'PLATFORM_DIR', 'PROJECT_ROOT',
    'FRONTEND_DIR', 'DOCS_DIR',
    'OUTPUT_DIR', 'CACHE_DIR', 'LOGS_DIR', 'DATA_DIR', 'BACKUPS_DIR',
    'KEYWORDS_DIR', 'DOMAIN_CONFIGS_DIR', 'DOMAIN_TEMPLATES_DIR', 'CONFIG_DIR',
    'STATIC_DIR', 'IMAGES_DIR',
    'USER_DB_FILE', 'SESSION_FILE', 'USER_JSON_FILE', 'DATAGENPRO_DB_FILE',
    'safe_path_join', 'ensure_dirs',
}

def __getattr__(name):
    if name in _core_modules:
        module_path, attr_name = _core_modules[name]
        import importlib
        module = importlib.import_module(module_path, package='core')
        return getattr(module, attr_name)
    
    if name in _path_attrs:
        from . import paths
        return getattr(paths, name)
    
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
    
    if name == 'safe_execute':
        from .exception_handler import safe_execute
        return safe_execute
    if name == 'SafeContext':
        from .exception_handler import SafeContext
        return SafeContext
    if name == 'safe_context':
        from .exception_handler import safe_context
        return safe_context
    if name == 'retry':
        from .exception_handler import retry
        return retry
    if name == 'module_loader':
        from .exception_handler import module_loader
        return module_loader
    if name == 'get_logger':
        from .logger_impl import get_logger
        return get_logger
    if name == 'setup_logging':
        from .logger_impl import setup_logging
        return setup_logging
    
    if name == 'parse_body':
        from .request_handler import parse_body
        return parse_body
    if name == 'get_token':
        from .request_handler import get_token
        return get_token
    if name == 'require_auth':
        from .request_handler import require_auth
        return require_auth
    if name == 'RequestContext':
        from .request_handler import RequestContext
        return RequestContext
    if name == 'build_context':
        from .request_handler import build_context
        return build_context
    if name == 'init_context':
        from .request_handler import init_context
        return init_context
    if name == 'response':
        from .request_handler import response
        return response
    if name == 'module_registry':
        from .module_registry import module_registry
        return module_registry
    if name == 'ModuleRegistry':
        from .module_registry import ModuleRegistry
        return ModuleRegistry
    
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
