#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API层 - LLM服务懒加载入口
千问API、智能调用器等

使用方式：
    from api.llm import QwenAPI, SmartAPICaller
    from api.llm import get_llm_client, call_with_fallback
"""

__all__ = [
    'QwenAPI', 'CostController', 'CostConfig', 'HybridDataGenerator',
    'SmartAPICaller',
    'get_llm_client', 'call_with_fallback',
]

_lazy_modules = {
    'QwenAPI': ('.qwen', 'QwenAPI'),
    'CostController': ('.qwen', 'CostController'),
    'CostConfig': ('.qwen', 'CostConfig'),
    'HybridDataGenerator': ('.qwen', 'HybridDataGenerator'),
    'SmartAPICaller': ('.smart_caller', 'SmartAPICaller'),
}

_llm_client = None

def __getattr__(name):
    """懒加载LLM模块"""
    if name in _lazy_modules:
        module_path, class_name = _lazy_modules[name]
        import importlib
        module = importlib.import_module(module_path, package='api.llm')
        return getattr(module, class_name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def get_llm_client():
    """获取LLM客户端（单例懒加载）"""
    global _llm_client
    if _llm_client is None:
        from .qwen import QwenAPI
        _llm_client = QwenAPI()
    return _llm_client

def call_with_fallback(prompt, **kwargs):
    """带降级的API调用"""
    client = get_llm_client()
    return client.generate(prompt, **kwargs)
