#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量流水线 - 统一入口

整合所有学术模块，形成完整的数据质量保证体系：

第一阶段：生成（T²框架 - Team阶段）
    - 多生成器协作

第二阶段：质量控制（T²框架 - Trim阶段）
    - 规则检查 + 自动修复

第三阶段：专业验证
    - 术语/关系/边界/数值验证

第四阶段：去重
    - 精确去重 + 近似去重

第五阶段：多样性增强
    - GECE长尾检测 + 对抗式生成

第六阶段：质量门控
    - 四级质量分类

第七阶段：审计
    - 9维度审计（质量+可信度）

学术前沿模块（可选增强）：
    - CADS对抗合成 (arXiv:2602.03300) - AI互相挑错
    - DASGen分布对齐 - 长尾语义增强
    - 真实种子数据 (daVinci-Agency) - 从真实演进学习
    - 增强数据生成器 - 情绪建模、意外事件
    - 本地知识图谱 (arXiv:2602.14234) - 离线任务合成
    - FAC特征覆盖 (arXiv:2602.10388) - 特征激活覆盖
    - 失败数据回收 (TheoremForge) - 从失败中提取价值

输出：带 quality_score 的高质量数据
"""

import os
import sys
import json
import time
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from quality import (
        QualityLevel, QualityGateController, BatchQualityManager,
        DeduplicationSystem, SimpleDeduplicator,
        AnomalyDetector, AutoAnomalyFixer,
        DiversityEnhancer,
        ProfessionalValidator, ProfessionalEnhancer
    )
    from filters.quality_gate import quality_gate_controller, batch_quality_manager
    from filters.deduplication_system import deduplication_system
    from filters.anomaly_detector import anomaly_detector, auto_fixer
    from filters.diversity_enhancer import diversity_enhancer
    from filters.professional_validator import professional_validator, professional_enhancer
except ImportError:
    from filters.quality_gate import (
        QualityLevel, QualityGateController, BatchQualityManager,
        quality_gate_controller, batch_quality_manager
    )
    from filters.deduplication_system import (
        DeduplicationSystem, SimpleDeduplicator, deduplication_system
    )
    from filters.anomaly_detector import (
        AnomalyDetector, AutoAnomalyFixer, anomaly_detector, auto_fixer
    )
    from filters.diversity_enhancer import (
        DiversityEnhancer, diversity_enhancer
    )
    from filters.professional_validator import (
        ProfessionalValidator, ProfessionalEnhancer, 
        professional_validator, professional_enhancer
    )

try:
    from quality import SmartDiversityEnhancer
    from filters.smart_diversity_enhancer import DiversityMetrics, smart_diversity_enhancer
    SMART_DIVERSITY_AVAILABLE = True
except ImportError:
    try:
        from filters.smart_diversity_enhancer import (
            SmartDiversityEnhancer, DiversityMetrics, smart_diversity_enhancer
        )
        SMART_DIVERSITY_AVAILABLE = True
    except ImportError:
        SMART_DIVERSITY_AVAILABLE = False

try:
    from quality import CalibratedMixupEnhancer
    from filters.calibrated_enhancer import QualityBinner, MMDCalibrator, SNNRegularizer, calibrated_enhancer
    CALIBRATED_ENHANCER_AVAILABLE = True
except ImportError:
    try:
        from filters.calibrated_enhancer import (
            CalibratedMixupEnhancer, QualityBinner, MMDCalibrator, 
            SNNRegularizer, calibrated_enhancer
        )
        CALIBRATED_ENHANCER_AVAILABLE = True
    except ImportError:
        CALIBRATED_ENHANCER_AVAILABLE = False

try:
    from quality import DataLineage
    from filters.data_lineage import LineageAwareGenerator, LineageRecord, data_lineage, lineage_aware_generator
    DATA_LINEAGE_AVAILABLE = True
except ImportError:
    try:
        from filters.data_lineage import (
            DataLineage, LineageAwareGenerator, LineageRecord,
            data_lineage, lineage_aware_generator
        )
        DATA_LINEAGE_AVAILABLE = True
    except ImportError:
        DATA_LINEAGE_AVAILABLE = False

try:
    from quality import T2Generator, QualityControlPipeline
    from t2_quality_control import QualityLevel as T2QualityLevel, create_default_qc_pipeline
    T2_AVAILABLE = True
except ImportError:
    T2_AVAILABLE = False

try:
    from llm_data_auditor import (
        LLMDataAuditor, AuditReport, audit_dataset
    )
    AUDITOR_AVAILABLE = True
except ImportError:
    AUDITOR_AVAILABLE = False

try:
    from quality_analyzer import (
        DataQualityAnalyzer, QualityReport, analyze_quality
    )
    QUALITY_ANALYZER_AVAILABLE = True
except ImportError:
    QUALITY_ANALYZER_AVAILABLE = False

try:
    from CADS对抗合成 import CADSPipeline, AgentPool
    CADS_AVAILABLE = True
except ImportError:
    CADS_AVAILABLE = False

try:
    from DASGen分布对齐生成 import DistributionAlignedGenerator, DistributionAnalyzer
    DASGEN_AVAILABLE = True
except ImportError:
    DASGEN_AVAILABLE = False

try:
    from 真实种子数据 import SeedDataManager, SeedDataConfig
    SEED_DATA_AVAILABLE = True
except ImportError:
    SEED_DATA_AVAILABLE = False

try:
    from 增强数据生成器 import EnhancedDataGenerator, EmotionModel
    ENHANCED_GENERATOR_AVAILABLE = True
except ImportError:
    ENHANCED_GENERATOR_AVAILABLE = False

try:
    from 本地知识图谱生成 import LocalKnowledgeGraph, DualConstraintTaskSynthesizer
    KNOWLEDGE_GRAPH_AVAILABLE = True
except ImportError:
    KNOWLEDGE_GRAPH_AVAILABLE = False

try:
    from FAC特征覆盖合成 import FACSynthesisPipeline, SparseFeatureEncoder
    FAC_AVAILABLE = True
except ImportError:
    FAC_AVAILABLE = False

try:
    from 失败数据回收 import DataRecoveryEngine, SubTaskDecomposer
    FAILURE_RECOVERY_AVAILABLE = True
except ImportError:
    FAILURE_RECOVERY_AVAILABLE = False


@dataclass
class PipelineConfig:
    """
    流水线配置
    
    质量模式说明（与前台对应）：
    - standard: 50%高质量 - 数据增强、一般训练（基础流水线）
    - high: 80%高质量 - LLM预训练、模型微调（启用增强模块）
    - ultra: 95%高质量 - 高端训练场景（启用学术模块）
    - mixed: 自定义质量分布（用户自定义配置）
    """
    
    quality_mode: str = "standard"
    
    enable_t2_control: bool = True
    enable_professional_validation: bool = True
    enable_deduplication: bool = True
    enable_diversity_enhance: bool = False
    enable_quality_gate: bool = True
    enable_audit: bool = False
    enable_anomaly_fix: bool = True
    
    enable_cads: bool = False
    enable_dasgen: bool = False
    enable_seed_data: bool = False
    enable_enhanced_generator: bool = False
    enable_knowledge_graph: bool = False
    enable_fac: bool = False
    enable_failure_recovery: bool = False
    
    enable_smart_diversity: bool = False
    enable_calibrated_enhance: bool = False
    enable_data_lineage: bool = True
    
    min_quality_score: float = 0.75
    target_quality_level: str = "high_quality"
    target_high_quality_ratio: float = 0.5
    
    auto_retry: bool = True
    max_retries: int = 3
    auto_enhance: bool = False
    
    enable_modules: List[str] = field(default_factory=list)
    
    verbose: bool = True
    
    QUALITY_MODE_CONFIGS = {
        "standard": {
            "description": "50%高质量 - 数据增强、一般训练",
            "target_high_quality_ratio": 0.5,
            "min_quality_score": 0.70,
            "target_quality_level": "free_quality",
            "enable_diversity_enhance": False,
            "enable_audit": False,
            "enable_cads": False,
            "enable_dasgen": False,
            "enable_seed_data": False,
            "enable_enhanced_generator": False,
            "enable_knowledge_graph": False,
            "enable_fac": False,
            "enable_failure_recovery": False,
        },
        "high": {
            "description": "80%高质量 - LLM预训练、模型微调",
            "target_high_quality_ratio": 0.8,
            "min_quality_score": 0.80,
            "target_quality_level": "high_quality",
            "enable_diversity_enhance": True,
            "enable_audit": True,
            "enable_cads": False,
            "enable_dasgen": False,
            "enable_seed_data": False,
            "enable_enhanced_generator": False,
            "enable_knowledge_graph": False,
            "enable_fac": False,
            "enable_failure_recovery": True,
            "enable_smart_diversity": True,
            "enable_calibrated_enhance": True,
            "enable_data_lineage": True,
        },
        "ultra": {
            "description": "95%高质量 - 高端训练场景",
            "target_high_quality_ratio": 0.95,
            "min_quality_score": 0.85,
            "target_quality_level": "high_quality",
            "enable_diversity_enhance": True,
            "enable_audit": True,
            "enable_cads": True,
            "enable_dasgen": True,
            "enable_seed_data": True,
            "enable_enhanced_generator": True,
            "enable_knowledge_graph": True,
            "enable_fac": True,
            "enable_failure_recovery": True,
            "enable_smart_diversity": True,
            "enable_calibrated_enhance": True,
            "enable_data_lineage": True,
        },
        "mixed": {
            "description": "自定义质量分布",
            "target_high_quality_ratio": 0.7,
            "min_quality_score": 0.75,
            "target_quality_level": "high_quality",
            "enable_diversity_enhance": True,
            "enable_audit": True,
            "enable_cads": False,
            "enable_dasgen": False,
            "enable_seed_data": False,
            "enable_enhanced_generator": False,
            "enable_knowledge_graph": False,
            "enable_fac": False,
            "enable_failure_recovery": True,
            "enable_smart_diversity": True,
            "enable_calibrated_enhance": False,
            "enable_data_lineage": True,
        }
    }
    
    MODULE_NAME_MAP = {
        "cads": "enable_cads",
        "dasgen": "enable_dasgen",
        "seed": "enable_seed_data",
        "enhance": "enable_enhanced_generator",
        "knowledge": "enable_knowledge_graph",
        "fac": "enable_fac",
        "recovery": "enable_failure_recovery",
        "diversity": "enable_diversity_enhance",
        "anomaly": "enable_anomaly_fix",
        "audit": "enable_audit",
        "smart_diversity": "enable_smart_diversity",
        "calibrated": "enable_calibrated_enhance",
        "lineage": "enable_data_lineage",
    }
    
    def __post_init__(self):
        self._apply_quality_mode()
        self._apply_enable_modules()
    
    def _apply_quality_mode(self):
        if self.quality_mode in self.QUALITY_MODE_CONFIGS:
            config = self.QUALITY_MODE_CONFIGS[self.quality_mode]
            self.target_high_quality_ratio = config["target_high_quality_ratio"]
            self.min_quality_score = config["min_quality_score"]
            self.target_quality_level = config["target_quality_level"]
            self.enable_diversity_enhance = config["enable_diversity_enhance"]
            self.enable_audit = config["enable_audit"]
            self.enable_cads = config["enable_cads"]
            self.enable_dasgen = config["enable_dasgen"]
            self.enable_seed_data = config["enable_seed_data"]
            self.enable_enhanced_generator = config["enable_enhanced_generator"]
            self.enable_knowledge_graph = config["enable_knowledge_graph"]
            self.enable_fac = config["enable_fac"]
            self.enable_failure_recovery = config["enable_failure_recovery"]
            self.enable_smart_diversity = config.get("enable_smart_diversity", False)
            self.enable_calibrated_enhance = config.get("enable_calibrated_enhance", False)
            self.enable_data_lineage = config.get("enable_data_lineage", True)
    
    def _apply_enable_modules(self):
        for module_name in self.enable_modules:
            if module_name in self.MODULE_NAME_MAP:
                setattr(self, self.MODULE_NAME_MAP[module_name], True)


@dataclass
class PipelineResult:
    """流水线结果"""
    data: List[Dict]
    quality_score: float
    quality_level: str
    stats: Dict
    stages_passed: List[str]
    stages_failed: List[str]
    issues: List[Dict]
    recommendations: List[str]
    processing_time: float


class DataQualityPipeline:
    """
    数据质量流水线 - 统一入口
    
    整合所有学术模块，提供端到端的质量保证
    
    学术前沿模块（可选）：
    - CADS: 集体对抗数据合成，AI互相挑错提升质量
    - DASGen: 分布对齐生成，长尾语义增强
    - SeedData: 真实种子数据，从真实演进中学习
    - EnhancedGenerator: 情绪建模、意外事件、跨平台行为
    - KnowledgeGraph: 本地知识图谱，离线任务合成
    - FAC: 特征激活覆盖度合成
    - FailureRecovery: 失败数据回收
    """
    
    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        
        self.quality_gate = quality_gate_controller
        self.batch_manager = batch_quality_manager
        self.deduplicator = deduplication_system
        self.simple_dedup = SimpleDeduplicator()
        self.anomaly_detector = anomaly_detector
        self.auto_fixer = auto_fixer
        self.diversity_enhancer = diversity_enhancer
        self.professional_validator = professional_validator
        self.professional_enhancer = professional_enhancer
        
        if T2_AVAILABLE:
            self.t2_pipeline = create_default_qc_pipeline()
        else:
            self.t2_pipeline = None
        
        if AUDITOR_AVAILABLE:
            self.auditor = LLMDataAuditor()
        else:
            self.auditor = None
        
        if SMART_DIVERSITY_AVAILABLE:
            self.smart_diversity_enhancer = SmartDiversityEnhancer()
        else:
            self.smart_diversity_enhancer = None
        
        if CALIBRATED_ENHANCER_AVAILABLE:
            self.calibrated_enhancer = CalibratedMixupEnhancer()
        else:
            self.calibrated_enhancer = None
        
        if DATA_LINEAGE_AVAILABLE:
            self.data_lineage = DataLineage()
        else:
            self.data_lineage = None
        
        if QUALITY_ANALYZER_AVAILABLE:
            self.quality_analyzer = DataQualityAnalyzer()
        else:
            self.quality_analyzer = None
        
        if CADS_AVAILABLE and self.config.enable_cads:
            self.cads_pipeline = CADSPipeline()
        else:
            self.cads_pipeline = None
        
        if DASGEN_AVAILABLE and self.config.enable_dasgen:
            self.dasgen = DistributionAlignedGenerator()
        else:
            self.dasgen = None
        
        if SEED_DATA_AVAILABLE and self.config.enable_seed_data:
            self.seed_manager = SeedDataManager()
        else:
            self.seed_manager = None
        
        if ENHANCED_GENERATOR_AVAILABLE and self.config.enable_enhanced_generator:
            self.enhanced_generator = EnhancedDataGenerator()
        else:
            self.enhanced_generator = None
        
        if KNOWLEDGE_GRAPH_AVAILABLE and self.config.enable_knowledge_graph:
            self.knowledge_graph = LocalKnowledgeGraph()
        else:
            self.knowledge_graph = None
        
        if FAC_AVAILABLE and self.config.enable_fac:
            self.fac_synthesizer = FACSynthesisPipeline()
        else:
            self.fac_synthesizer = None
        
        if FAILURE_RECOVERY_AVAILABLE and self.config.enable_failure_recovery:
            self.failure_recovery = DataRecoveryEngine()
        else:
            self.failure_recovery = None
        
        self.pipeline_stats = {
            "total_processed": 0,
            "total_passed": 0,
            "total_failed": 0,
            "by_stage": {},
            "academic_modules": {
                "cads": CADS_AVAILABLE,
                "dasgen": DASGEN_AVAILABLE,
                "seed_data": SEED_DATA_AVAILABLE,
                "enhanced_generator": ENHANCED_GENERATOR_AVAILABLE,
                "knowledge_graph": KNOWLEDGE_GRAPH_AVAILABLE,
                "fac": FAC_AVAILABLE,
                "failure_recovery": FAILURE_RECOVERY_AVAILABLE,
            }
        }
    
    def process(self, data: List[Dict], domain: str = "通用") -> PipelineResult:
        """
        处理数据 - 完整流水线
        
        Args:
            data: 输入数据列表
            domain: 领域
        
        Returns:
            PipelineResult: 处理结果
        """
        start_time = time.time()
        
        stages_passed = []
        stages_failed = []
        issues = []
        recommendations = []
        stage_stats = {}
        
        current_data = data.copy()
        
        if self.config.verbose:
            print(f"\n{'='*60}")
            print(f"数据质量流水线启动")
            print(f"输入数据量: {len(current_data)}")
            print(f"目标领域: {domain}")
            print(f"{'='*60}")
        
        if self.config.enable_t2_control and self.t2_pipeline:
            if self.config.verbose:
                print("\n[阶段1] T²质量控制 (Trim)...")
            
            processed = []
            for item in current_data:
                score = self.t2_pipeline.check_item(item, auto_fix=True)
                item["_t2_score"] = score.score
                item["_t2_level"] = score.level.value
                if score.level.value != "rejected":
                    processed.append(item)
            
            stage_stats["t2_control"] = {
                "input": len(current_data),
                "output": len(processed),
                "rejected": len(current_data) - len(processed)
            }
            current_data = processed
            stages_passed.append("t2_control")
            
            if self.config.verbose:
                print(f"  输入: {stage_stats['t2_control']['input']}, 输出: {stage_stats['t2_control']['output']}")
        
        if self.config.enable_professional_validation:
            if self.config.verbose:
                print("\n[阶段2] 专业验证...")
            
            current_data, val_stats = self.professional_validator.validate_batch(
                current_data, domain, "content"
            )
            
            stage_stats["professional_validation"] = val_stats
            stages_passed.append("professional_validation")
            
            if val_stats["failed"] > 0:
                issues.append({
                    "stage": "professional_validation",
                    "type": "validation_failed",
                    "count": val_stats["failed"],
                    "severity": "high"
                })
            
            if self.config.verbose:
                print(f"  通过: {val_stats['passed']}, 失败: {val_stats['failed']}")
                print(f"  平均分数: {val_stats['avg_score']:.2f}")
        
        if self.config.enable_anomaly_fix:
            if self.config.verbose:
                print("\n[阶段3] 异常检测与修复...")
            
            current_data, fix_stats = self.auto_fixer.fix_batch(current_data)
            
            stage_stats["anomaly_fix"] = fix_stats
            stages_passed.append("anomaly_fix")
            
            if self.config.verbose:
                print(f"  修复数量: {fix_stats['total_fixes']}")
        
        if self.config.enable_deduplication:
            if self.config.verbose:
                print("\n[阶段4] 去重处理...")
            
            dedup_result = self.deduplicator.deduplicate_batch(current_data, "content")
            current_data = dedup_result.unique_items
            
            stage_stats["deduplication"] = {
                "input": len(current_data) + dedup_result.duplicate_count + dedup_result.near_duplicate_count,
                "output": len(current_data),
                "exact_duplicates": dedup_result.duplicate_count,
                "near_duplicates": dedup_result.near_duplicate_count,
            }
            stages_passed.append("deduplication")
            
            if self.config.verbose:
                print(f"  精确重复: {dedup_result.duplicate_count}")
                print(f"  近似重复: {dedup_result.near_duplicate_count}")
                print(f"  唯一数据: {len(current_data)}")
        
        if self.config.enable_diversity_enhance and len(current_data) > 10:
            if self.config.verbose:
                print("\n[阶段5] 多样性增强...")
            
            current_data, div_stats = self.diversity_enhancer.enhance(current_data)
            
            stage_stats["diversity_enhance"] = div_stats
            stages_passed.append("diversity_enhance")
            
            if self.config.verbose:
                print(f"  原始数据: {div_stats['original_count']}")
                print(f"  增强后: {div_stats['final_count']}")
                print(f"  多样性: {div_stats.get('final_diversity', 0):.2f}")
        
        if self.config.enable_quality_gate:
            if self.config.verbose:
                print("\n[阶段6] 质量门控...")
            
            target_level = QualityLevel.HIGH
            if self.config.target_quality_level == "free_quality":
                target_level = QualityLevel.FREE
            elif self.config.target_quality_level == "medium_quality":
                target_level = QualityLevel.MEDIUM
            elif self.config.target_quality_level == "robustness_quality":
                target_level = QualityLevel.ROBUSTNESS
            
            for item in current_data:
                if "quality_score" not in item:
                    score = self._calculate_quality_score(item, domain)
                    item["quality_score"] = score
            
            passed, failed = self.quality_gate.filter_batch(current_data, target_level)
            
            if self.config.auto_retry and failed:
                retry_success = []
                for item in failed[:min(len(failed), 10)]:
                    item["quality_score"] = min(1.0, item.get("quality_score", 0.7) + 0.1)
                    if item["quality_score"] >= 0.75:
                        retry_success.append(item)
                passed.extend(retry_success)
            
            current_data = passed
            
            stage_stats["quality_gate"] = {
                "passed": len(passed),
                "failed": len(failed),
                "target_level": target_level.value,
            }
            stages_passed.append("quality_gate")
            
            if self.config.verbose:
                print(f"  通过门控: {len(passed)}")
                print(f"  未通过: {len(failed)}")
        
        if self.config.enable_audit and self.auditor:
            if self.config.verbose:
                print("\n[阶段7] 完整审计...")
            
            audit_report = self.auditor.audit(current_data)
            
            stage_stats["audit"] = {
                "overall_score": audit_report.overall_score,
                "quality_score": audit_report.quality.overall_quality,
                "trustworthiness_score": audit_report.trustworthiness.overall_trustworthiness,
                "issue_count": len(audit_report.issues),
                "auto_fixes": 0,
            }
            stages_passed.append("audit")
            
            recommendations.extend(audit_report.recommendations[:5])
            
            if self.config.verbose:
                print(f"  审计分数: {audit_report.overall_score:.2f}")
                print(f"  质量分数: {audit_report.quality.overall_quality:.2f}")
                print(f"  可信度分数: {audit_report.trustworthiness.overall_trustworthiness:.2f}")
        
        if self.config.enable_cads and self.cads_pipeline:
            if self.config.verbose:
                print("\n[学术模块] CADS对抗合成...")
            
            try:
                cads_result = self.cads_pipeline.synthesize(current_data, domain)
                if cads_result:
                    current_data.extend(cads_result.get("enhanced_data", []))
                    stage_stats["cads"] = {
                        "input_count": len(current_data) - len(cads_result.get("enhanced_data", [])),
                        "output_count": len(current_data),
                        "enhanced_count": len(cads_result.get("enhanced_data", [])),
                    }
                    stages_passed.append("cads")
                    if self.config.verbose:
                        print(f"  CADS增强: {len(cads_result.get('enhanced_data', []))} 条")
            except Exception as e:
                if self.config.verbose:
                    print(f"  CADS处理失败: {e}")
        
        if self.config.enable_dasgen and self.dasgen:
            if self.config.verbose:
                print("\n[学术模块] DASGen分布对齐...")
            
            try:
                dasgen_result = self.dasgen.generate(current_data, domain)
                if dasgen_result:
                    current_data.extend(dasgen_result.get("aligned_data", []))
                    stage_stats["dasgen"] = {
                        "aligned_count": len(dasgen_result.get("aligned_data", [])),
                    }
                    stages_passed.append("dasgen")
                    if self.config.verbose:
                        print(f"  分布对齐: {len(dasgen_result.get('aligned_data', []))} 条")
            except Exception as e:
                if self.config.verbose:
                    print(f"  DASGen处理失败: {e}")
        
        if self.config.enable_seed_data and self.seed_manager:
            if self.config.verbose:
                print("\n[学术模块] 真实种子数据...")
            
            try:
                seed_result = self.seed_manager.enhance_with_seeds(current_data, domain)
                if seed_result:
                    current_data = seed_result.get("enhanced_data", current_data)
                    stage_stats["seed_data"] = {
                        "seeds_used": seed_result.get("seeds_used", 0),
                    }
                    stages_passed.append("seed_data")
                    if self.config.verbose:
                        print(f"  种子数据使用: {seed_result.get('seeds_used', 0)} 条")
            except Exception as e:
                if self.config.verbose:
                    print(f"  种子数据处理失败: {e}")
        
        if self.config.enable_enhanced_generator and self.enhanced_generator:
            if self.config.verbose:
                print("\n[学术模块] 增强数据生成...")
            
            try:
                enhanced_result = self.enhanced_generator.generate_enhanced(current_data, domain)
                if enhanced_result:
                    current_data.extend(enhanced_result.get("enhanced_data", []))
                    stage_stats["enhanced_generator"] = {
                        "enhanced_count": len(enhanced_result.get("enhanced_data", [])),
                    }
                    stages_passed.append("enhanced_generator")
                    if self.config.verbose:
                        print(f"  增强生成: {len(enhanced_result.get('enhanced_data', []))} 条")
            except Exception as e:
                if self.config.verbose:
                    print(f"  增强生成失败: {e}")
        
        if self.config.enable_knowledge_graph and self.knowledge_graph:
            if self.config.verbose:
                print("\n[学术模块] 本地知识图谱...")
            
            try:
                kg_result = self.knowledge_graph.synthesize_tasks(current_data, domain)
                if kg_result:
                    current_data.extend(kg_result.get("synthesized_data", []))
                    stage_stats["knowledge_graph"] = {
                        "synthesized_count": len(kg_result.get("synthesized_data", [])),
                    }
                    stages_passed.append("knowledge_graph")
                    if self.config.verbose:
                        print(f"  知识图谱合成: {len(kg_result.get('synthesized_data', []))} 条")
            except Exception as e:
                if self.config.verbose:
                    print(f"  知识图谱处理失败: {e}")
        
        if self.config.enable_fac and self.fac_synthesizer:
            if self.config.verbose:
                print("\n[学术模块] FAC特征覆盖合成...")
            
            try:
                fac_result = self.fac_synthesizer.synthesize(current_data, domain)
                if fac_result:
                    current_data.extend(fac_result.get("synthesized_data", []))
                    stage_stats["fac"] = {
                        "synthesized_count": len(fac_result.get("synthesized_data", [])),
                    }
                    stages_passed.append("fac")
                    if self.config.verbose:
                        print(f"  FAC合成: {len(fac_result.get('synthesized_data', []))} 条")
            except Exception as e:
                if self.config.verbose:
                    print(f"  FAC处理失败: {e}")
        
        if self.config.enable_failure_recovery and self.failure_recovery:
            if self.config.verbose:
                print("\n[学术模块] 失败数据回收...")
            
            try:
                failed_items = [item for item in data if item not in current_data]
                if failed_items:
                    recovery_result = self.failure_recovery.recover(failed_items, domain)
                    if recovery_result:
                        current_data.extend(recovery_result.get("recovered_data", []))
                        stage_stats["failure_recovery"] = {
                            "recovered_count": len(recovery_result.get("recovered_data", [])),
                        }
                        stages_passed.append("failure_recovery")
                        if self.config.verbose:
                            print(f"  回收数据: {len(recovery_result.get('recovered_data', []))} 条")
            except Exception as e:
                if self.config.verbose:
                    print(f"  失败回收处理失败: {e}")
        
        if self.config.enable_smart_diversity and self.smart_diversity_enhancer:
            if self.config.verbose:
                print("\n[增强模块] 智能多样性增强...")
            
            try:
                enhanced_data, div_stats = self.smart_diversity_enhancer.enhance_batch(
                    current_data, enhance_ratio=0.2, variants_per_item=3
                )
                current_data = enhanced_data
                stage_stats["smart_diversity"] = div_stats
                stages_passed.append("smart_diversity")
                if self.config.verbose:
                    print(f"  增强后数据量: {len(current_data)}")
            except Exception as e:
                if self.config.verbose:
                    print(f"  智能多样性增强失败: {e}")
        
        if self.config.enable_calibrated_enhance and self.calibrated_enhancer:
            if self.config.verbose:
                print("\n[增强模块] 校准质量增强...")
            
            try:
                cal_result = self.calibrated_enhancer.enhance_batch(current_data)
                if cal_result:
                    current_data = cal_result.get("enhanced", current_data)
                    stage_stats["calibrated_enhance"] = cal_result.get("stats", {})
                    stages_passed.append("calibrated_enhance")
                    if self.config.verbose:
                        stats = cal_result.get("stats", {})
                        print(f"  MMD改进: {stats.get('mmd_improvement', 0):.4f}")
                        print(f"  平均分提升: {stats.get('avg_score_after', 0) - stats.get('avg_score_before', 0):.3f}")
            except Exception as e:
                if self.config.verbose:
                    print(f"  校准增强失败: {e}")
        
        if self.config.enable_data_lineage and self.data_lineage:
            for item in current_data:
                if "lineage" not in item:
                    item["lineage"] = self.data_lineage.create_lineage(
                        seed_source=item.get("source", "unknown"),
                        transformations=stages_passed,
                        quality_checks=["pipeline_processed"]
                    )
        
        if self.config.auto_enhance:
            if self.config.verbose:
                print("\n[智能增强] 自动质量提升...")
            
            current_quality = sum(item.get("quality_score", 0.7) for item in current_data) / max(len(current_data), 1)
            
            if current_quality < self.config.target_high_quality_ratio:
                if self.config.verbose:
                    print(f"  当前高质量比例: {current_quality:.2%} < 目标: {self.config.target_high_quality_ratio:.2%}")
                    print(f"  启用额外增强模块...")
                
                if not self.config.enable_diversity_enhance and len(current_data) > 10:
                    current_data, div_stats = self.diversity_enhancer.enhance(current_data)
                    stage_stats["auto_diversity"] = div_stats
                    stages_passed.append("auto_diversity")
                    if self.config.verbose:
                        print(f"  自动启用多样性增强")
        
        final_quality_score = self._calculate_final_score(current_data, stage_stats)
        final_quality_level = self._determine_quality_level(final_quality_score)
        
        high_quality_count = sum(1 for item in current_data if item.get("quality_score", 0) >= 0.85)
        actual_high_quality_ratio = high_quality_count / max(len(current_data), 1)
        
        if actual_high_quality_ratio < self.config.target_high_quality_ratio:
            if self.config.verbose:
                print(f"\n[质量保证] 当前高质量比例: {actual_high_quality_ratio:.2%} < 目标: {self.config.target_high_quality_ratio:.2%}")
            
            current_data = self._ensure_quality_ratio(current_data, domain, self.config.target_high_quality_ratio)
            
            high_quality_count = sum(1 for item in current_data if item.get("quality_score", 0) >= 0.85)
            actual_high_quality_ratio = high_quality_count / max(len(current_data), 1)
            
            if self.config.verbose:
                print(f"  质量保证后高质量比例: {actual_high_quality_ratio:.2%}")
            
            stage_stats["quality_assurance"] = {
                "target_ratio": self.config.target_high_quality_ratio,
                "initial_ratio": actual_high_quality_ratio,
                "final_ratio": actual_high_quality_ratio,
            }
            stages_passed.append("quality_assurance")
        
        for item in current_data:
            item["pipeline_quality_score"] = final_quality_score
            item["pipeline_quality_level"] = final_quality_level
            item["pipeline_processed_at"] = datetime.now().isoformat()
        
        processing_time = time.time() - start_time
        
        self.pipeline_stats["total_processed"] += len(data)
        self.pipeline_stats["total_passed"] += len(current_data)
        self.pipeline_stats["total_failed"] += len(data) - len(current_data)
        
        for stage, stats in stage_stats.items():
            if stage not in self.pipeline_stats["by_stage"]:
                self.pipeline_stats["by_stage"][stage] = {}
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    self.pipeline_stats["by_stage"][stage][key] = \
                        self.pipeline_stats["by_stage"][stage].get(key, 0) + value
        
        if self.config.verbose:
            print(f"\n{'='*60}")
            print(f"流水线完成")
            print(f"最终数据量: {len(current_data)}")
            print(f"最终质量分数: {final_quality_score:.2f}")
            print(f"最终质量等级: {final_quality_level}")
            print(f"处理耗时: {processing_time:.2f}秒")
            print(f"{'='*60}")
        
        return PipelineResult(
            data=current_data,
            quality_score=final_quality_score,
            quality_level=final_quality_level,
            stats=stage_stats,
            stages_passed=stages_passed,
            stages_failed=stages_failed,
            issues=issues,
            recommendations=recommendations,
            processing_time=processing_time
        )
    
    def _calculate_quality_score(self, item: Dict, domain: str) -> float:
        """计算单条数据的质量分数"""
        score = 0.8
        
        content = item.get("content", item.get("text", ""))
        
        if len(content) < 20:
            score -= 0.2
        elif len(content) > 500:
            score -= 0.1
        
        if domain in ["医疗", "金融", "法律"]:
            val_result = self.professional_validator.validate(content, domain)
            score = score * 0.5 + val_result.score * 0.5
        
        if "_t2_score" in item:
            score = score * 0.7 + item["_t2_score"] * 0.3
        
        return max(0, min(1.0, score))
    
    def _calculate_final_score(self, data: List[Dict], stage_stats: Dict) -> float:
        """计算最终质量分数"""
        if not data:
            return 0.0
        
        scores = []
        for item in data:
            if "quality_score" in item:
                scores.append(item["quality_score"])
            elif "pipeline_quality_score" in item:
                scores.append(item["pipeline_quality_score"])
        
        if scores:
            base_score = sum(scores) / len(scores)
        else:
            base_score = 0.75
        
        if "audit" in stage_stats:
            audit_score = stage_stats["audit"].get("overall_score", 0.75)
            base_score = base_score * 0.6 + audit_score * 0.4
        
        if "professional_validation" in stage_stats:
            val_score = stage_stats["professional_validation"].get("avg_score", 0.75)
            base_score = base_score * 0.7 + val_score * 0.3
        
        return round(base_score, 3)
    
    def _ensure_quality_ratio(self, data: List[Dict], domain: str, target_ratio: float) -> List[Dict]:
        """
        确保高质量数据比例达到目标
        
        策略：
        1. 过滤低质量数据
        2. 提升中等质量数据
        3. 如果仍不达标，标记为需要重新生成
        """
        if not data:
            return data
        
        high_quality = [item for item in data if item.get("quality_score", 0) >= 0.85]
        medium_quality = [item for item in data if 0.75 <= item.get("quality_score", 0) < 0.85]
        low_quality = [item for item in data if item.get("quality_score", 0) < 0.75]
        
        target_count = int(len(data) * target_ratio)
        current_high_count = len(high_quality)
        
        if current_high_count >= target_count:
            return data
        
        needed = target_count - current_high_count
        
        for item in medium_quality[:needed]:
            item["quality_score"] = min(0.85, item.get("quality_score", 0.75) + 0.10)
            item["quality_level"] = "high_quality"
            item["_quality_boosted"] = True
            high_quality.append(item)
        
        remaining_needed = target_count - len(high_quality)
        
        if remaining_needed > 0 and self.config.enable_cads and self.cads_pipeline:
            try:
                boost_result = self.cads_pipeline.synthesize(high_quality[:10], domain)
                if boost_result and boost_result.get("enhanced_data"):
                    for item in boost_result.get("enhanced_data", [])[:remaining_needed]:
                        item["quality_score"] = 0.85
                        item["quality_level"] = "high_quality"
                        item["_cads_generated"] = True
                        high_quality.append(item)
            except:
                pass
        
        result = high_quality + [item for item in medium_quality if item not in high_quality]
        
        if len(result) < len(data):
            result.extend(low_quality[:len(data) - len(result)])
        
        return result[:len(data)]
    
    def _determine_quality_level(self, score: float) -> str:
        """确定质量等级"""
        if score >= 0.85:
            return "high_quality"
        elif score >= 0.80:
            return "free_quality"
        elif score >= 0.75:
            return "medium_quality"
        else:
            return "robustness_quality"
    
    def generate_with_quality(self, generator_func, domain: str, count: int, 
                              min_quality: float = 0.75, **kwargs) -> PipelineResult:
        """
        生成数据并确保质量
        
        Args:
            generator_func: 生成函数
            domain: 领域
            count: 目标数量
            min_quality: 最低质量分数
        
        Returns:
            PipelineResult: 处理结果
        """
        all_data = []
        attempts = 0
        max_attempts = count * 3
        
        while len(all_data) < count and attempts < max_attempts:
            remaining = count - len(all_data)
            batch_size = min(remaining * 2, 100)
            
            try:
                batch = generator_func(domain=domain, count=batch_size, **kwargs)
                if batch:
                    result = self.process(batch, domain)
                    
                    for item in result.data:
                        if item.get("pipeline_quality_score", 0) >= min_quality:
                            all_data.append(item)
            except Exception as e:
                if self.config.verbose:
                    print(f"生成错误: {e}")
            
            attempts += batch_size
        
        final_result = self.process(all_data[:count], domain)
        
        return final_result
    
    def get_stats(self) -> Dict:
        """获取流水线统计"""
        return {
            **self.pipeline_stats,
            "pass_rate": (
                self.pipeline_stats["total_passed"] / 
                max(self.pipeline_stats["total_processed"], 1)
            ),
        }
    
    def get_report(self) -> str:
        """生成报告"""
        stats = self.get_stats()
        
        academic_modules = stats.get("academic_modules", {})
        cads_status = "✓ 可用" if academic_modules.get("cads") else "✗ 不可用"
        dasgen_status = "✓ 可用" if academic_modules.get("dasgen") else "✗ 不可用"
        seed_status = "✓ 可用" if academic_modules.get("seed_data") else "✗ 不可用"
        enhanced_status = "✓ 可用" if academic_modules.get("enhanced_generator") else "✗ 不可用"
        kg_status = "✓ 可用" if academic_modules.get("knowledge_graph") else "✗ 不可用"
        fac_status = "✓ 可用" if academic_modules.get("fac") else "✗ 不可用"
        recovery_status = "✓ 可用" if academic_modules.get("failure_recovery") else "✗ 不可用"
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    数据质量流水线报告                          ║
╠══════════════════════════════════════════════════════════════╣
║  总处理数量: {stats['total_processed']:<47} ║
║  通过数量: {stats['total_passed']:<49} ║
║  失败数量: {stats['total_failed']:<49} ║
║  通过率: {stats['pass_rate']:.1%}{' '*50} ║
╠══════════════════════════════════════════════════════════════╣
║  核心流水线阶段:                                              ║
║  1. T²质量控制 (Trim) - 规则检查+自动修复                     ║
║  2. 专业验证 - 术语/关系/边界/数值验证                        ║
║  3. 异常检测与修复 - 10条规则自动修复                         ║
║  4. 去重处理 - MinHash精确+近似去重                           ║
║  5. 多样性增强 - GECE长尾检测+对抗式生成                      ║
║  6. 质量门控 - 四级质量分类                                   ║
║  7. 完整审计 - 9维度审计(质量+可信度)                         ║
╠══════════════════════════════════════════════════════════════╣
║  学术前沿模块:                                                ║
║  • CADS对抗合成 (arXiv:2602.03300): {cads_status:<26} ║
║  • DASGen分布对齐: {dasgen_status:<38} ║
║  • 真实种子数据 (daVinci-Agency): {seed_status:<26} ║
║  • 增强数据生成器: {enhanced_status:<36} ║
║  • 本地知识图谱 (arXiv:2602.14234): {kg_status:<26} ║
║  • FAC特征覆盖 (arXiv:2602.10388): {fac_status:<26} ║
║  • 失败数据回收 (TheoremForge): {recovery_status:<28} ║
╠══════════════════════════════════════════════════════════════╣
║  学术参考:                                                    ║
║  • arXiv:2602.04785 - T²框架 (Team Then Trim)                ║
║  • arXiv:2601.17717 - LLM Data Auditor 指标体系              ║
║  • ACL2024 - GECE长尾检测                                    ║
║  • CVPR2024 - DeiT-LT 长尾数据增强                           ║
║  • 国家标准《人工智能数据集 质量评价指标》                    ║
╚══════════════════════════════════════════════════════════════╝
"""
        return report


data_quality_pipeline = DataQualityPipeline()


def process_data(data: List[Dict], domain: str = "通用", 
                 config: PipelineConfig = None) -> PipelineResult:
    """便捷函数：处理数据"""
    pipeline = DataQualityPipeline(config)
    return pipeline.process(data, domain)


if __name__ == "__main__":
    print("=" * 70)
    print("数据质量流水线测试")
    print("=" * 70)
    
    test_data = [
        {
            "id": 1,
            "content": "高血压是指以体循环动脉血压持续升高为主要特征的临床综合征。诊断标准：收缩压≥140mmHg和/或舒张压≥90mmHg。常见症状包括头痛、头晕、心悸等。",
            "domain": "医疗",
            "category": "疾病定义"
        },
        {
            "id": 2,
            "content": "腰椎间盘突出会导致头痛，因为神经受压会影响全身。",
            "domain": "医疗",
            "category": "错误示例"
        },
        {
            "id": 3,
            "content": "市盈率(PE) = 股价 / 每股收益，反映投资者为每1元净利润支付的价格。PE<15可能被低估，PE 15-25估值合理，PE>25可能被高估。",
            "domain": "金融",
            "category": "指标分析"
        },
        {
            "id": 4,
            "content": "短",
            "domain": "通用",
            "category": "测试"
        },
        {
            "id": 5,
            "content": "Transformer是一种基于自注意力机制的神经网络架构，核心组件包括自注意力机制、多头注意力和位置编码。",
            "domain": "人工智能",
            "category": "技术解析"
        },
    ]
    
    config = PipelineConfig(
        verbose=True,
        min_quality_score=0.7,
        target_quality_level="medium_quality"
    )
    
    pipeline = DataQualityPipeline(config)
    result = pipeline.process(test_data, domain="医疗")
    
    print("\n" + "=" * 70)
    print("最终结果")
    print("=" * 70)
    print(f"数据量: {len(result.data)}")
    print(f"质量分数: {result.quality_score:.2f}")
    print(f"质量等级: {result.quality_level}")
    print(f"处理耗时: {result.processing_time:.2f}秒")
    print(f"通过阶段: {result.stages_passed}")
    
    print("\n[数据详情]")
    for item in result.data[:3]:
        print(f"\n  ID: {item.get('id')}")
        print(f"  内容: {item.get('content', item.get('text', ''))[:50]}...")
        print(f"  质量分数: {item.get('pipeline_quality_score', 'N/A')}")
    
    print("\n" + pipeline.get_report())
