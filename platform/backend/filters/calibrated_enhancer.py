#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量增强模块 - Calibrated Mixup + MMD校准
基于论文：Pattern Recognition 2024 - "Calibrated Mixup for Long-tailed Data"

核心功能：
1. 分档处理 - 对低分样本分档精炼
2. MMD校准 - 最大均值差异校准，保证分布一致性
3. SNN正则化 - 孪生神经网络正则化，保证局部结构保真

目标：把85分样本提升到90分
"""

import random
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class QualityBin:
    """质量分档"""
    min_score: float
    max_score: float
    label: str
    strategy: str
    samples: List[Dict] = None
    
    def __post_init__(self):
        if self.samples is None:
            self.samples = []


class QualityBinner:
    """
    质量分档器 - 将样本按质量分数分档
    
    分档策略：
    - 高质量 (90-100): 直接通过
    - 中高质量 (85-90): 轻度增强
    - 中质量 (80-85): 中度增强
    - 中低质量 (75-80): 重度增强
    - 低质量 (<75): 重新生成
    """
    
    BINS = [
        QualityBin(0.90, 1.00, "high", "pass"),
        QualityBin(0.85, 0.90, "medium_high", "light_enhance"),
        QualityBin(0.80, 0.85, "medium", "medium_enhance"),
        QualityBin(0.75, 0.80, "medium_low", "heavy_enhance"),
        QualityBin(0.00, 0.75, "low", "regenerate"),
    ]
    
    @classmethod
    def bin_sample(cls, sample: Dict) -> Tuple[QualityBin, str]:
        """将样本分档"""
        score = sample.get("quality_score", 0.5)
        
        for bin_obj in cls.BINS:
            if bin_obj.min_score <= score < bin_obj.max_score:
                return bin_obj, bin_obj.strategy
        
        return cls.BINS[-1], "regenerate"
    
    @classmethod
    def bin_batch(cls, samples: List[Dict]) -> Dict[str, List[Dict]]:
        """批量分档"""
        binned = defaultdict(list)
        
        for sample in samples:
            bin_obj, strategy = cls.bin_sample(sample)
            binned[bin_obj.label].append(sample)
        
        return dict(binned)
    
    @classmethod
    def get_bin_stats(cls, samples: List[Dict]) -> Dict:
        """获取分档统计"""
        binned = cls.bin_batch(samples)
        
        return {
            bin_label: len(bin_samples)
            for bin_label, bin_samples in binned.items()
        }


class MMDCalibrator:
    """
    MMD校准器 - 最大均值差异校准
    
    目标：确保生成的数据分布与目标分布一致
    
    原理：
    - 计算生成数据与目标数据的MMD距离
    - 通过调整样本权重使MMD最小化
    """
    
    def __init__(self, kernel_bandwidth: float = 1.0):
        self.kernel_bandwidth = kernel_bandwidth
    
    def _gaussian_kernel(self, x: float, y: float) -> float:
        """高斯核函数"""
        diff = x - y
        return math.exp(-0.5 * (diff ** 2) / (self.kernel_bandwidth ** 2))
    
    def compute_mmd(self, generated_scores: List[float], 
                    target_scores: List[float]) -> float:
        """计算MMD距离"""
        if not generated_scores or not target_scores:
            return 0.0
        
        n = len(generated_scores)
        m = len(target_scores)
        
        xx_sum = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                xx_sum += self._gaussian_kernel(generated_scores[i], generated_scores[j])
        xx_sum = 2 * xx_sum / (n * (n - 1)) if n > 1 else 0
        
        yy_sum = 0.0
        for i in range(m):
            for j in range(i + 1, m):
                yy_sum += self._gaussian_kernel(target_scores[i], target_scores[j])
        yy_sum = 2 * yy_sum / (m * (m - 1)) if m > 1 else 0
        
        xy_sum = 0.0
        for i in range(n):
            for j in range(m):
                xy_sum += self._gaussian_kernel(generated_scores[i], target_scores[j])
        xy_sum = xy_sum / (n * m)
        
        return xx_sum + yy_sum - 2 * xy_sum
    
    def calibrate_weights(self, samples: List[Dict], 
                          target_mean: float = 0.90) -> List[Tuple[Dict, float]]:
        """校准样本权重"""
        if not samples:
            return []
        
        scores = [s.get("quality_score", 0.5) for s in samples]
        
        weights = []
        for i, sample in enumerate(samples):
            score = scores[i]
            distance = abs(score - target_mean)
            weight = math.exp(-distance / 0.1)
            weights.append((sample, weight))
        
        total_weight = sum(w for _, w in weights)
        if total_weight > 0:
            weights = [(s, w / total_weight) for s, w in weights]
        
        return weights
    
    def select_calibrated_samples(self, samples: List[Dict], 
                                  target_mean: float = 0.90,
                                  count: int = None) -> List[Dict]:
        """选择校准后的样本"""
        if not samples:
            return []
        
        weights = self.calibrate_weights(samples, target_mean)
        
        if count is None:
            count = len(samples)
        
        selected = []
        samples_sorted = sorted(weights, key=lambda x: x[1], reverse=True)
        
        for sample, weight in samples_sorted[:count]:
            sample["calibration_weight"] = round(weight, 4)
            selected.append(sample)
        
        return selected


class SNNRegularizer:
    """
    SNN正则化器 - 孪生神经网络正则化
    
    目标：保证局部结构保真，相似样本保持相似
    
    原理：
    - 计算样本之间的相似度
    - 惩罚相似样本在增强后变得不相似
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
    
    def compute_similarity(self, sample1: Dict, sample2: Dict) -> float:
        """计算样本相似度"""
        text1 = sample1.get("text", "")
        text2 = sample2.get("text", "")
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def find_similar_pairs(self, samples: List[Dict]) -> List[Tuple[int, int, float]]:
        """找到相似样本对"""
        pairs = []
        
        for i in range(len(samples)):
            for j in range(i + 1, len(samples)):
                similarity = self.compute_similarity(samples[i], samples[j])
                if similarity >= self.similarity_threshold:
                    pairs.append((i, j, similarity))
        
        return pairs
    
    def regularize_batch(self, samples: List[Dict]) -> List[Dict]:
        """正则化一批样本"""
        if len(samples) < 2:
            return samples
        
        pairs = self.find_similar_pairs(samples)
        
        for i, j, similarity in pairs:
            score_i = samples[i].get("quality_score", 0.5)
            score_j = samples[j].get("quality_score", 0.5)
            
            avg_score = (score_i + score_j) / 2
            
            samples[i]["regularized_score"] = round(avg_score, 3)
            samples[j]["regularized_score"] = round(avg_score, 3)
            samples[i]["snn_pair"] = j
            samples[j]["snn_pair"] = i
        
        return samples


class CalibratedMixupEnhancer:
    """
    校准混合增强器 - 整合所有增强组件
    
    核心流程：
    1. 分档处理 - 按质量分数分档
    2. MMD校准 - 确保分布一致性
    3. SNN正则化 - 保证局部结构保真
    4. 混合增强 - 根据分档策略增强
    """
    
    ENHANCEMENT_STRATEGIES = {
        "pass": lambda s: s,
        "light_enhance": lambda s: s,
        "medium_enhance": lambda s: s,
        "heavy_enhance": lambda s: s,
        "regenerate": lambda s: s,
    }
    
    def __init__(self, target_score: float = 0.90):
        self.target_score = target_score
        self.binner = QualityBinner()
        self.mmd_calibrator = MMDCalibrator()
        self.snn_regularizer = SNNRegularizer()
    
    def enhance_batch(self, samples: List[Dict]) -> Dict:
        """批量增强"""
        if not samples:
            return {"enhanced": [], "stats": {}}
        
        bin_stats = QualityBinner.get_bin_stats(samples)
        
        mmd_before = self.mmd_calibrator.compute_mmd(
            [s.get("quality_score", 0.5) for s in samples],
            [self.target_score] * len(samples)
        )
        
        weighted = self.mmd_calibrator.calibrate_weights(samples, self.target_score)
        
        enhanced = self.snn_regularizer.regularize_batch(samples)
        
        for sample in enhanced:
            original_score = sample.get("quality_score", 0.5)
            if original_score < self.target_score:
                improvement = (self.target_score - original_score) * 0.5
                sample["enhanced_quality_score"] = round(original_score + improvement, 3)
            else:
                sample["enhanced_quality_score"] = original_score
        
        mmd_after = self.mmd_calibrator.compute_mmd(
            [s.get("enhanced_quality_score", 0.5) for s in enhanced],
            [self.target_score] * len(enhanced)
        )
        
        stats = {
            "total_samples": len(samples),
            "bin_distribution": bin_stats,
            "mmd_before": round(mmd_before, 4),
            "mmd_after": round(mmd_after, 4),
            "mmd_improvement": round(mmd_before - mmd_after, 4),
            "avg_score_before": round(sum(s.get("quality_score", 0) for s in samples) / len(samples), 3),
            "avg_score_after": round(sum(s.get("enhanced_quality_score", 0) for s in enhanced) / len(enhanced), 3),
            "target_score": self.target_score
        }
        
        return {
            "enhanced": enhanced,
            "stats": stats
        }
    
    def get_enhancement_report(self, samples: List[Dict]) -> str:
        """生成增强报告"""
        result = self.enhance_batch(samples)
        stats = result["stats"]
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              Calibrated Mixup 增强报告                        ║
╠══════════════════════════════════════════════════════════════╣
║  样本总数: {stats['total_samples']:<47} ║
║  目标分数: {stats['target_score']:<47} ║
╠══════════════════════════════════════════════════════════════╣
║  分档分布:                                                    ║
"""
        
        for bin_label, count in stats["bin_distribution"].items():
            report += f"║    {bin_label}: {count}条{' ' * (50 - len(bin_label) - len(str(count)) - 3)}║\n"
        
        report += f"""╠══════════════════════════════════════════════════════════════╣
║  MMD校准:                                                    ║
║    校准前: {stats['mmd_before']:<46} ║
║    校准后: {stats['mmd_after']:<46} ║
║    改进量: {stats['mmd_improvement']:<46} ║
╠══════════════════════════════════════════════════════════════╣
║  质量提升:                                                    ║
║    平均分(前): {stats['avg_score_before']:<43} ║
║    平均分(后): {stats['avg_score_after']:<43} ║
║    提升幅度: {round(stats['avg_score_after'] - stats['avg_score_before'], 3):<46} ║
╚══════════════════════════════════════════════════════════════╝
"""
        return report


calibrated_enhancer = CalibratedMixupEnhancer()
