#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分批次质量门控系统 - Quality Gate System

质量等级划分：
- high_quality: ≥0.85分，高质量数据
- medium_quality: 0.70-0.85分，中等质量数据
- low_quality: <0.70分，低质量数据（用于鲁棒性测试）

核心功能：
1. 分批次质量门控
2. 自动重试机制
3. 质量等级分类
"""

import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class QualityLevel(Enum):
    """质量等级"""
    HIGH = "high_quality"
    FREE = "free_quality"
    MEDIUM = "medium_quality"
    ROBUSTNESS = "robustness_quality"


@dataclass
class QualityGate:
    """质量门控配置"""
    level: QualityLevel
    min_score: float
    max_score: float
    auto_retry: bool
    max_retries: int
    description: str


QUALITY_GATES = {
    QualityLevel.HIGH: QualityGate(
        level=QualityLevel.HIGH,
        min_score=0.85,
        max_score=1.0,
        auto_retry=True,
        max_retries=3,
        description="高质量数据 - 用于模型训练、知识库构建"
    ),
    QualityLevel.FREE: QualityGate(
        level=QualityLevel.FREE,
        min_score=0.80,
        max_score=0.85,
        auto_retry=True,
        max_retries=2,
        description="免费试用质量 - 展示平台能力，吸引用户"
    ),
    QualityLevel.MEDIUM: QualityGate(
        level=QualityLevel.MEDIUM,
        min_score=0.75,
        max_score=0.80,
        auto_retry=False,
        max_retries=0,
        description="普通质量 - 性价比之选，适合一般用途"
    ),
    QualityLevel.ROBUSTNESS: QualityGate(
        level=QualityLevel.ROBUSTNESS,
        min_score=0.0,
        max_score=0.75,
        auto_retry=False,
        max_retries=0,
        description="鲁棒性测试质量 - 用于压力测试、边界测试"
    ),
}


class QualityGateController:
    """
    质量门控控制器
    
    核心逻辑：
    1. 根据目标质量等级选择门控标准
    2. 自动检测数据质量等级
    3. 高质量数据不达标时自动重试
    """
    
    def __init__(self):
        self.stats = {
            "total_processed": 0,
            "high_quality": 0,
            "medium_quality": 0,
            "low_quality": 0,
            "retries": 0,
            "rejected": 0,
        }
    
    def classify_quality(self, score: float) -> QualityLevel:
        """分类质量等级"""
        if score >= 0.85:
            return QualityLevel.HIGH
        elif score >= 0.80:
            return QualityLevel.FREE
        elif score >= 0.75:
            return QualityLevel.MEDIUM
        else:
            return QualityLevel.ROBUSTNESS
    
    def check_gate(self, sample: Dict, target_level: QualityLevel) -> Tuple[bool, str]:
        """
        检查样本是否通过质量门控
        
        Args:
            sample: 数据样本
            target_level: 目标质量等级
            
        Returns:
            (是否通过, 原因说明)
        """
        score = sample.get("quality_score", 0)
        gate = QUALITY_GATES[target_level]
        
        self.stats["total_processed"] += 1
        
        actual_level = self.classify_quality(score)
        
        if actual_level == QualityLevel.HIGH:
            self.stats["high_quality"] += 1
        elif actual_level == QualityLevel.MEDIUM:
            self.stats["medium_quality"] += 1
        else:
            self.stats["low_quality"] += 1
        
        if score >= gate.min_score and score <= gate.max_score:
            return True, f"通过{target_level.value}门控，分数{score}"
        
        if target_level == QualityLevel.HIGH and score < gate.min_score:
            return False, f"分数{score}低于{target_level.value}最低要求{gate.min_score}"
        
        if target_level == QualityLevel.ROBUSTNESS and score > gate.max_score:
            return False, f"分数{score}高于{target_level.value}最高要求{gate.max_score}"
        
        if target_level == QualityLevel.MEDIUM:
            if score < gate.min_score:
                return False, f"分数{score}低于{target_level.value}最低要求{gate.min_score}"
            if score > gate.max_score:
                return False, f"分数{score}高于{target_level.value}最高要求{gate.max_score}，应归类为高质量"
        
        return True, f"通过{target_level.value}门控"
    
    def filter_batch(self, samples: List[Dict], target_level: QualityLevel) -> Tuple[List[Dict], List[Dict]]:
        """
        批量过滤
        
        Args:
            samples: 样本列表
            target_level: 目标质量等级
            
        Returns:
            (通过的样本, 未通过的样本)
        """
        passed = []
        failed = []
        
        for sample in samples:
            is_passed, reason = self.check_gate(sample, target_level)
            if is_passed:
                sample["quality_gate"] = {
                    "level": target_level.value,
                    "passed": True,
                    "reason": reason
                }
                passed.append(sample)
            else:
                sample["quality_gate"] = {
                    "level": target_level.value,
                    "passed": False,
                    "reason": reason
                }
                failed.append(sample)
                self.stats["rejected"] += 1
        
        return passed, failed
    
    def auto_retry_generate(self, sample: Dict, target_level: QualityLevel, 
                            generate_func, max_retries: int = None) -> Tuple[Dict, int]:
        """
        自动重试生成（仅用于高质量数据）
        
        Args:
            sample: 原始样本
            target_level: 目标质量等级
            generate_func: 生成函数
            max_retries: 最大重试次数
            
        Returns:
            (最终样本, 重试次数)
        """
        gate = QUALITY_GATES[target_level]
        
        if not gate.auto_retry:
            return sample, 0
        
        max_retries = max_retries or gate.max_retries
        retries = 0
        
        for i in range(max_retries):
            is_passed, _ = self.check_gate(sample, target_level)
            if is_passed:
                return sample, retries
            
            sample = generate_func()
            retries += 1
            self.stats["retries"] += 1
        
        sample["quality_gate"] = {
            "level": target_level.value,
            "passed": False,
            "retries": retries,
            "reason": f"重试{retries}次后仍未达标"
        }
        
        return sample, retries
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.stats["total_processed"]
        
        return {
            "total_processed": total,
            "quality_distribution": {
                "high_quality": self.stats["high_quality"],
                "medium_quality": self.stats["medium_quality"],
                "low_quality": self.stats["low_quality"],
            },
            "quality_rates": {
                "high_quality_rate": round(self.stats["high_quality"] / max(total, 1), 3),
                "medium_quality_rate": round(self.stats["medium_quality"] / max(total, 1), 3),
                "low_quality_rate": round(self.stats["low_quality"] / max(total, 1), 3),
            },
            "retries": self.stats["retries"],
            "rejected": self.stats["rejected"],
            "pass_rate": round((total - self.stats["rejected"]) / max(total, 1), 3),
        }


class BatchQualityManager:
    """
    批次质量管理器 - 管理不同质量等级的批次
    """
    
    def __init__(self):
        self.gate_controller = QualityGateController()
        self.batches = {
            QualityLevel.HIGH: [],
            QualityLevel.FREE: [],
            QualityLevel.MEDIUM: [],
            QualityLevel.ROBUSTNESS: [],
        }
    
    def add_to_batch(self, sample: Dict) -> QualityLevel:
        """将样本添加到对应质量等级的批次"""
        score = sample.get("quality_score", 0)
        level = self.gate_controller.classify_quality(score)
        
        sample["quality_level"] = level.value
        self.batches[level].append(sample)
        
        return level
    
    def add_batch(self, samples: List[Dict]) -> Dict:
        """批量添加样本"""
        distribution = {"high_quality": 0, "free_quality": 0, "medium_quality": 0, "robustness_quality": 0}
        
        for sample in samples:
            level = self.add_to_batch(sample)
            distribution[level.value] += 1
        
        return distribution
    
    def get_batch(self, level: QualityLevel) -> List[Dict]:
        """获取指定质量等级的批次"""
        return self.batches[level]
    
    def get_all_batches(self) -> Dict[str, List[Dict]]:
        """获取所有批次"""
        return {
            "high_quality": self.batches[QualityLevel.HIGH],
            "free_quality": self.batches[QualityLevel.FREE],
            "medium_quality": self.batches[QualityLevel.MEDIUM],
            "robustness_quality": self.batches[QualityLevel.ROBUSTNESS],
        }
    
    def clear_batches(self):
        """清空所有批次"""
        for level in self.batches:
            self.batches[level] = []
    
    def get_batch_stats(self) -> Dict:
        """获取批次统计"""
        return {
            "batch_sizes": {
                "high_quality": len(self.batches[QualityLevel.HIGH]),
                "medium_quality": len(self.batches[QualityLevel.MEDIUM]),
                "robustness_quality": len(self.batches[QualityLevel.ROBUSTNESS]),
            },
            "gate_stats": self.gate_controller.get_stats(),
        }


quality_gate_controller = QualityGateController()
batch_quality_manager = BatchQualityManager()
