#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术模块层 - 懒加载入口
高级生成算法：CADS、DASGen、FAC、知识图谱等

使用方式：
    from academic import CADSPipeline, FACSynthesisPipeline
    from academic import get_knowledge_graph
"""

__all__ = [
    'CADSPipeline',
    'DistributionAlignedGenerator',
    'FACSynthesisPipeline',
    'LocalKnowledgeGraph',
    'SeedDataManager',
    'EnhancedDataGenerator',
    'DataRecoveryEngine',
    'AcademicDataGenerator',
    'get_cads_pipeline',
    'get_fac_pipeline',
    'get_knowledge_graph',
]

_lazy_modules = {
    'CADSPipeline': ('.cads', 'CADSPipeline'),
    'DistributionAlignedGenerator': ('.dasgen', 'DistributionAlignedGenerator'),
    'FACSynthesisPipeline': ('.fac', 'FACSynthesisPipeline'),
    'LocalKnowledgeGraph': ('.knowledge_graph', 'LocalKnowledgeGraph'),
    'SeedDataManager': ('.seed_data', 'SeedDataManager'),
    'EnhancedDataGenerator': ('.enhanced_generator', 'EnhancedDataGenerator'),
    'DataRecoveryEngine': ('.failure_recovery', 'DataRecoveryEngine'),
    'AcademicDataGenerator': ('.academic_system', 'AcademicDataGenerator'),
}

def __getattr__(name):
    """懒加载学术模块"""
    if name in _lazy_modules:
        module_path, class_name = _lazy_modules[name]
        import importlib
        module = importlib.import_module(module_path, package='academic')
        return getattr(module, class_name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def get_cads_pipeline():
    """获取CADS对抗合成流水线"""
    from .cads import CADSPipeline
    return CADSPipeline()

def get_fac_pipeline():
    """获取FAC特征覆盖合成流水线"""
    from .fac import FACSynthesisPipeline
    return FACSynthesisPipeline()

def get_knowledge_graph():
    """获取本地知识图谱"""
    from .knowledge_graph import LocalKnowledgeGraph
    return LocalKnowledgeGraph()
