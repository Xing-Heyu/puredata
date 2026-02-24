#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
过滤器模块 - 导出

整合所有学术前沿模块：
- 去重系统 (MinHash LSH)
- 异常检测 (国家标准)
- 质量门控 (四级分类)
- 多样性增强 (GECE长尾检测)
- 专业验证 (解决"逻辑通但专业错")
- 数据血缘 (追溯)
- 校准增强 (Calibrated Mixup)
"""

from .deduplication_system import DeduplicationSystem, SimpleDeduplicator, deduplication_system, simple_deduplicator
from .calibrated_enhancer import (
    CalibratedMixupEnhancer, QualityBinner, MMDCalibrator, SNNRegularizer,
    calibrated_enhancer
)
from .anomaly_detector import (
    AnomalyDetector, AnomalyRuleLibrary, AnomalyRule, AnomalyResult,
    AutoAnomalyFixer, anomaly_detector, auto_fixer
)
from .data_lineage import (
    DataLineage, LineageAwareGenerator, LineageRecord,
    data_lineage, lineage_aware_generator
)
from .quality_gate import (
    QualityLevel, QualityGate, QualityGateController, BatchQualityManager,
    QUALITY_GATES, quality_gate_controller, batch_quality_manager
)
from .diversity_enhancer import (
    DiversityEnhancer, DiversityMetrics, GECELongTailDetector,
    DistributionAugmenter, AdversarialDiversityGenerator, diversity_enhancer
)
from .professional_validator import (
    ProfessionalValidator, ProfessionalEnhancer, ValidationError, ValidationResult,
    DomainKnowledgeBase, professional_validator, professional_enhancer
)

__all__ = [
    "DeduplicationSystem",
    "SimpleDeduplicator",
    "deduplication_system",
    "simple_deduplicator",
    "CalibratedMixupEnhancer",
    "QualityBinner",
    "MMDCalibrator",
    "SNNRegularizer",
    "calibrated_enhancer",
    "AnomalyDetector",
    "AnomalyRuleLibrary",
    "AnomalyRule",
    "AnomalyResult",
    "AutoAnomalyFixer",
    "anomaly_detector",
    "auto_fixer",
    "DataLineage",
    "LineageAwareGenerator",
    "LineageRecord",
    "data_lineage",
    "lineage_aware_generator",
    "QualityLevel",
    "QualityGate",
    "QualityGateController",
    "BatchQualityManager",
    "QUALITY_GATES",
    "quality_gate_controller",
    "batch_quality_manager",
    "DiversityEnhancer",
    "DiversityMetrics",
    "GECELongTailDetector",
    "DistributionAugmenter",
    "AdversarialDiversityGenerator",
    "diversity_enhancer",
    "ProfessionalValidator",
    "ProfessionalEnhancer",
    "ValidationError",
    "ValidationResult",
    "DomainKnowledgeBase",
    "professional_validator",
    "professional_enhancer",
]
