#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - 懒加载入口
数据生成核心：生成器、变化引擎、真实感增强等

使用方式：
    from generation import DataGenerator, TopologyGenerator
    from generation import VariationEngine, RealismEnhancer
"""

__all__ = [
    'DataGenerator', 'TopologyGenerator', 'CopulaGenerator',
    'VariationEngine', 'RealismEnhancer', 'NoiseGenerator',
    'HighQualityGenerator', 'InfiniteDataGenerator', 'HumanLikeGenerator',
    'SequenceGenerator', 'TemplateGenerator',
]

_lazy_modules = {
    'DataGenerator': ('.data_generator', 'DataGenerator'),
    'TopologyGenerator': ('.topology_generator', 'TopologyGenerator'),
    'CopulaGenerator': ('.copula_generator', 'CopulaGenerator'),
    'VariationEngine': ('.variation_engine', 'VariationEngine'),
    'RealismEnhancer': ('.realism_enhancer', 'RealismEnhancer'),
    'NoiseGenerator': ('.noise_generator', 'NoiseGenerator'),
    'HighQualityGenerator': ('.high_quality', 'HighQualityGenerator'),
    'InfiniteDataGenerator': ('.infinite', 'InfiniteDataGenerator'),
    'HumanLikeGenerator': ('.human_like', 'HumanLikeGenerator'),
    'SequenceGenerator': ('.sequence', 'SequenceGenerator'),
    'TemplateGenerator': ('.template_gen', 'TemplateGenerator'),
}

def __getattr__(name):
    """懒加载生成模块"""
    if name in _lazy_modules:
        module_path, class_name = _lazy_modules[name]
        import importlib
        module = importlib.import_module(module_path, package='generation')
        return getattr(module, class_name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
