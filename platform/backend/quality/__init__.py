#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量层 - 懒加载入口（更新版）
质量控制：流水线、门控、验证器、去重、审计等

常驻模块（立即加载）：
- QualityGateController - 质量门控
- DiversityEnhancer - 多样性增强
- DataRecoveryEngine - 失败数据回收

懒加载模块：
- DataQualityPipeline - 完整流水线
- LLMDataAuditor - 数据审计
- 其他高级功能

使用方式：
    from quality import QualityGateController, DiversityEnhancer, DataRecoveryEngine
    from quality import DataQualityPipeline  # 懒加载
"""

# ============ 常驻模块 - 立即加载 ============
from .gate import QualityGateController, QualityLevel, BatchQualityManager
from .diversity_enhancer import DiversityEnhancer, GECELongTailDetector
from .data_recovery import DataRecoveryEngine, SubTaskDecomposer

# ============ 懒加载模块 ============
__all__ = [
    # 常驻模块
    'QualityGateController', 'QualityLevel', 'BatchQualityManager',
    'DiversityEnhancer', 'GECELongTailDetector',
    'DataRecoveryEngine', 'SubTaskDecomposer',
    # 懒加载模块
    'DataQualityPipeline', 'PipelineConfig',
    'DeduplicationSystem', 'MinHashDeduplicator',
    'AnomalyDetector', 'AutoAnomalyFixer',
    'ProfessionalValidator', 'ProfessionalEnhancer',
    'DataLineage', 'LineageAwareGenerator',
    'CalibratedMixupEnhancer', 'MMDCalibrator',
    'T2Generator', 'QualityControlPipeline',
    'LLMDataAuditor', 'QualityMetrics', 'TrustworthinessMetrics',
]

_lazy_modules = {
    'DataQualityPipeline': ('.pipeline', 'DataQualityPipeline'),
    'PipelineConfig': ('.pipeline', 'PipelineConfig'),
    'DeduplicationSystem': ('.deduplication', 'DeduplicationSystem'),
    'MinHashDeduplicator': ('.deduplication', 'MinHashDeduplicator'),
    'AnomalyDetector': ('.anomaly_detector', 'AnomalyDetector'),
    'AutoAnomalyFixer': ('.anomaly_detector', 'AutoAnomalyFixer'),
    'ProfessionalValidator': ('.professional_validator', 'ProfessionalValidator'),
    'ProfessionalEnhancer': ('.professional_validator', 'ProfessionalEnhancer'),
    'DataLineage': ('.data_lineage', 'DataLineage'),
    'LineageAwareGenerator': ('.data_lineage', 'LineageAwareGenerator'),
    'CalibratedMixupEnhancer': ('.calibrated_enhancer', 'CalibratedMixupEnhancer'),
    'MMDCalibrator': ('.calibrated_enhancer', 'MMDCalibrator'),
    'T2Generator': ('.t2_control', 'T2Generator'),
    'QualityControlPipeline': ('.t2_control', 'QualityControlPipeline'),
    'LLMDataAuditor': ('.auditor', 'LLMDataAuditor'),
    'QualityMetrics': ('.auditor', 'QualityMetrics'),
    'TrustworthinessMetrics': ('.auditor', 'TrustworthinessMetrics'),
}

def __getattr__(name):
    """懒加载质量模块"""
    if name in _lazy_modules:
        module_path, class_name = _lazy_modules[name]
        import importlib
        module = importlib.import_module(module_path, package='quality')
        return getattr(module, class_name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
