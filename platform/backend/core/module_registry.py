#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层 - 模块注册表
统一管理所有懒加载模块，替代多个 get_xxx() 函数

使用方式：
    from core.module_registry import module_registry
    
    # 获取模块实例
    task_queue = module_registry.get('task_queue')
    
    # 检查模块是否可用
    if module_registry.is_available('data_cache'):
        dc = module_registry.get('data_cache')
"""

import threading
from typing import Any, Callable, Dict, Optional, Tuple

_module_cache: Dict[str, Any] = {}
_module_available: Dict[str, bool] = {}
_module_lock = threading.Lock()

_module_registry: Dict[str, Tuple[str, str]] = {
    'task_queue': ('task_queue', 'task_queue'),
    'data_cache': ('data_cache', 'data_cache'),
    'academic_validation': ('academic_validation', 'get_academic_validation'),
    'data_expansion': ('data_expansion', 'data_expansion_engine'),
    'variation_engine': ('variation_engine', 'variation_engine'),
    'qwen_api': ('千问API集成', 'QwenAPI'),
    'scoring_configurator': ('scoring_configurator', 'get_scoring_configurator'),
    'domain_config_loader': ('domain_config_loader', 'get_domain_config_loader'),
    'implicit_noise_detector': ('implicit_noise_detector', 'get_implicit_noise_detector'),
    'professional_error_generator': ('professional_error_generator', 'get_professional_error_generator'),
    't2_quality': ('t2_quality_control', None),
    'sdgt_generator': ('sdgt_generator', None),
    'data_sanitizer': ('data_sanitizer', 'sanitizer'),
    'human_like_generator': ('human_like_generator', 'human_like_generator'),
    'noise_generator': ('noise_generator', 'noise_generator'),
    'quality_analyzer': ('quality_analyzer', 'quality_analyzer'),
    'advanced_sampler': ('advanced_sampler', 'advanced_sampler'),
}


def _load_module(module_name: str) -> Optional[Any]:
    """加载模块"""
    with _module_lock:
        if module_name in _module_cache:
            return _module_cache[module_name]
        
        try:
            module = __import__(module_name, fromlist=[])
            _module_cache[module_name] = module
            _module_available[module_name] = True
            return module
        except ImportError:
            _module_cache[module_name] = None
            _module_available[module_name] = False
            return None


class ModuleRegistry:
    """模块注册表 - 统一管理懒加载模块"""
    
    def __init__(self):
        self._instance_cache: Dict[str, Any] = {}
    
    def get(self, name: str) -> Optional[Any]:
        """
        获取模块实例
        
        Args:
            name: 模块注册名称
        
        Returns:
            模块实例或 None
        """
        if name in self._instance_cache:
            return self._instance_cache[name]
        
        if name not in _module_registry:
            return None
        
        module_name, attr_name = _module_registry[name]
        module = _load_module(module_name)
        
        if module is None:
            return None
        
        if attr_name is None:
            self._instance_cache[name] = module
            return module
        
        if attr_name.startswith('get_'):
            getter = getattr(module, attr_name, None)
            if callable(getter):
                instance = getter()
                self._instance_cache[name] = instance
                return instance
        else:
            instance = getattr(module, attr_name, None)
            self._instance_cache[name] = instance
            return instance
        
        return None
    
    def is_available(self, name: str) -> bool:
        """
        检查模块是否可用
        
        Args:
            name: 模块注册名称
        
        Returns:
            是否可用
        """
        if name not in _module_registry:
            return False
        
        module_name = _module_registry[name][0]
        if module_name not in _module_available:
            _load_module(module_name)
        
        return _module_available.get(module_name, False)
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """
        直接获取模块对象
        
        Args:
            module_name: 模块文件名
        
        Returns:
            模块对象或 None
        """
        return _load_module(module_name)
    
    def register(self, name: str, module_name: str, attr_name: str = None):
        """
        注册新模块
        
        Args:
            name: 注册名称
            module_name: 模块文件名
            attr_name: 属性名（可选）
        """
        _module_registry[name] = (module_name, attr_name)
    
    def list_available(self) -> Dict[str, bool]:
        """列出所有模块的可用状态"""
        result = {}
        for name in _module_registry:
            result[name] = self.is_available(name)
        return result


module_registry = ModuleRegistry()


def get_task_queue():
    return module_registry.get('task_queue')

def get_data_cache():
    return module_registry.get('data_cache')

def get_academic_validation():
    return module_registry.get('academic_validation')

def get_data_expansion():
    return module_registry.get('data_expansion')

def get_variation_engine():
    return module_registry.get('variation_engine')

def get_qwen_api():
    return module_registry.get('qwen_api')

def get_scoring_configurator():
    return module_registry.get('scoring_configurator')

def get_domain_config_loader():
    return module_registry.get('domain_config_loader')

def get_implicit_noise_detector():
    return module_registry.get('implicit_noise_detector')

def get_professional_error_generator():
    return module_registry.get('professional_error_generator')

def get_t2_quality():
    return module_registry.get('t2_quality')

def get_sdgt_generator():
    return module_registry.get('sdgt_generator')

def get_data_sanitizer():
    return module_registry.get('data_sanitizer')

def get_human_like_generator():
    return module_registry.get('human_like_generator')

def get_noise_generator():
    return module_registry.get('noise_generator')

def get_quality_analyzer():
    return module_registry.get('quality_analyzer')

def get_advanced_sampler():
    return module_registry.get('advanced_sampler')


__all__ = [
    'module_registry',
    'ModuleRegistry',
    'get_task_queue',
    'get_data_cache',
    'get_academic_validation',
    'get_data_expansion',
    'get_variation_engine',
    'get_qwen_api',
    'get_scoring_configurator',
    'get_domain_config_loader',
    'get_implicit_noise_detector',
    'get_professional_error_generator',
    'get_t2_quality',
    'get_sdgt_generator',
    'get_data_sanitizer',
    'get_human_like_generator',
    'get_noise_generator',
    'get_quality_analyzer',
    'get_advanced_sampler',
]
