#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAC Synthesis - 特征激活覆盖度合成
基于论文：arXiv:2602.10388 "Less is Enough: Synthesizing Diverse Data in Feature Space of LLMs"

核心思想：
1. Feature Activation Coverage (FAC) - 衡量数据覆盖了多少模型特征
2. 稀疏自编码器 - 找出"缺失的特征"
3. 针对性生成 - 专门生成缺失特征的数据

为什么能解决"数据太规整"：
- 不是看文本像不像，而是看模型内部特征激活
- 找出模型没见过的特征，专门补充
- 让数据覆盖更多"意外"场景

成本：低 - 只需分析特征，不依赖大规模生成
"""

import json
import random
import hashlib
import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, Counter


@dataclass
class FeatureNode:
    """特征节点"""
    feature_id: str
    feature_type: str  # semantic, emotional, behavioral, contextual
    name: str
    activation_count: int
    coverage_ratio: float
    related_features: List[str]
    generation_hints: List[str]


@dataclass
class FACMetrics:
    """FAC指标"""
    total_features: int
    covered_features: int
    uncovered_features: int
    coverage_ratio: float
    feature_gini: float
    missing_feature_types: Dict[str, int]


@dataclass
class SynthesisTarget:
    """合成目标"""
    target_id: str
    missing_features: List[str]
    priority: float
    generation_strategy: str
    expected_coverage_gain: float


class SparseFeatureEncoder:
    """
    稀疏特征编码器 - 模拟稀疏自编码器功能
    
    核心功能：
    1. 将数据映射到特征空间
    2. 识别稀疏激活的特征
    3. 找出未激活（缺失）的特征
    """
    
    FEATURE_DIMENSIONS = {
        "semantic": [
            "购买意向", "浏览兴趣", "价格敏感", "品牌认知", "质量关注",
            "功能需求", "外观偏好", "服务期望", "物流要求", "售后关注"
        ],
        "emotional": [
            "喜悦", "愤怒", "悲伤", "恐惧", "惊讶",
            "期待", "信任", "厌恶", "犹豫", "冲动"
        ],
        "behavioral": [
            "主动搜索", "被动浏览", "比价行为", "收藏行为", "分享行为",
            "评价行为", "退货行为", "复购行为", "跨平台", "多设备"
        ],
        "contextual": [
            "工作时间", "休息时间", "通勤时间", "节假日", "促销期",
            "深夜时段", "周末", "月初", "月末", "季节性"
        ],
        "unexpected": [
            "意外中断", "价格变动", "库存变化", "系统故障", "客服介入",
            "优惠券过期", "限时抢购", "朋友推荐", "差评影响", "物流延迟"
        ]
    }
    
    def __init__(self, sparsity_threshold: float = 0.1):
        self.sparsity_threshold = sparsity_threshold
        self.feature_activations = defaultdict(int)
        self.total_samples = 0
    
    def encode(self, data: Dict) -> Dict[str, float]:
        """将数据编码为特征向量"""
        features = {}
        
        for feature_type, feature_list in self.FEATURE_DIMENSIONS.items():
            for feature in feature_list:
                activation = self._calculate_activation(data, feature_type, feature)
                features[f"{feature_type}_{feature}"] = activation
                
                if activation > self.sparsity_threshold:
                    self.feature_activations[f"{feature_type}_{feature}"] += 1
        
        self.total_samples += 1
        return features
    
    def _calculate_activation(self, data: Dict, feature_type: str, feature: str) -> float:
        """计算特征激活值"""
        text = json.dumps(data, ensure_ascii=False).lower()
        
        keyword_mappings = {
            "购买意向": ["购买", "下单", "支付", "买"],
            "浏览兴趣": ["浏览", "查看", "访问"],
            "价格敏感": ["价格", "便宜", "贵", "优惠"],
            "品牌认知": ["品牌", "牌子", "名牌"],
            "质量关注": ["质量", "品质", "好坏"],
            "喜悦": ["开心", "满意", "喜欢", "高兴"],
            "愤怒": ["生气", "愤怒", "差评", "投诉"],
            "犹豫": ["犹豫", "纠结", "考虑", "比较"],
            "冲动": ["冲动", "立刻", "马上", "立即"],
            "意外中断": ["中断", "打断", "离开"],
            "价格变动": ["涨价", "降价", "价格变动"],
            "库存变化": ["缺货", "库存", "售罄"],
        }
        
        keywords = keyword_mappings.get(feature, [feature])
        activation = sum(1 for kw in keywords if kw in text) / len(keywords)
        
        if random.random() < 0.1:
            activation += random.uniform(0, 0.2)
        
        return min(1.0, activation)
    
    def get_missing_features(self) -> List[FeatureNode]:
        """获取缺失的特征"""
        missing = []
        
        for feature_type, feature_list in self.FEATURE_DIMENSIONS.items():
            for feature in feature_list:
                feature_key = f"{feature_type}_{feature}"
                activation_count = self.feature_activations.get(feature_key, 0)
                coverage_ratio = activation_count / max(self.total_samples, 1)
                
                if coverage_ratio < self.sparsity_threshold:
                    missing.append(FeatureNode(
                        feature_id=feature_key,
                        feature_type=feature_type,
                        name=feature,
                        activation_count=activation_count,
                        coverage_ratio=coverage_ratio,
                        related_features=self._get_related_features(feature),
                        generation_hints=self._get_generation_hints(feature_type, feature)
                    ))
        
        return missing
    
    def _get_related_features(self, feature: str) -> List[str]:
        """获取相关特征"""
        relations = {
            "购买意向": ["价格敏感", "质量关注"],
            "犹豫": ["比价行为", "价格敏感"],
            "愤怒": ["退货行为", "客服介入"],
            "意外中断": ["犹豫", "冲动"],
        }
        return relations.get(feature, [])
    
    def _get_generation_hints(self, feature_type: str, feature: str) -> List[str]:
        """获取生成提示"""
        hints = {
            "unexpected": [
                f"添加{feature}场景",
                f"模拟用户遇到{feature}的反应",
                f"设计{feature}导致的行为变化"
            ],
            "emotional": [
                f"注入{feature}情绪",
                f"设计引发{feature}的事件",
                f"模拟{feature}状态下的决策"
            ],
            "behavioral": [
                f"增加{feature}动作",
                f"设计{feature}的场景",
                f"模拟{feature}的用户"
            ],
        }
        return hints.get(feature_type, [f"增加{feature}相关数据"])


class FACCalculator:
    """
    FAC计算器 - 计算特征激活覆盖度
    
    核心指标：
    1. Coverage Ratio - 覆盖率
    2. Feature Gini - 特征分布均匀度
    3. Missing Feature Types - 缺失特征类型分布
    """
    
    def __init__(self, encoder: SparseFeatureEncoder):
        self.encoder = encoder
    
    def calculate_fac(self) -> FACMetrics:
        """计算FAC指标"""
        total_features = sum(len(features) for features in 
                            SparseFeatureEncoder.FEATURE_DIMENSIONS.values())
        
        covered = sum(1 for count in self.encoder.feature_activations.values() 
                     if count > 0)
        
        missing = self.encoder.get_missing_features()
        missing_by_type = Counter(f.feature_type for f in missing)
        
        activations = list(self.encoder.feature_activations.values())
        if activations:
            sorted_activations = sorted(activations)
            n = len(sorted_activations)
            cumulative = sum((i + 1) * a for i, a in enumerate(sorted_activations))
            total = sum(sorted_activations)
            gini = (2 * cumulative) / (n * total) - (n + 1) / n if total > 0 else 0
        else:
            gini = 0
        
        return FACMetrics(
            total_features=total_features,
            covered_features=covered,
            uncovered_features=total_features - covered,
            coverage_ratio=covered / total_features if total_features > 0 else 0,
            feature_gini=gini,
            missing_feature_types=dict(missing_by_type)
        )


class TargetedSynthesizer:
    """
    针对性合成器 - 针对缺失特征生成数据
    
    核心功能：
    1. 识别高优先级缺失特征
    2. 生成针对性的数据
    3. 验证覆盖度提升
    """
    
    def __init__(self, encoder: SparseFeatureEncoder):
        self.encoder = encoder
        self.synthesis_history = []
    
    def identify_synthesis_targets(self, top_k: int = 10) -> List[SynthesisTarget]:
        """识别合成目标"""
        missing = self.encoder.get_missing_features()
        
        priority_scores = []
        for feature in missing:
            priority = self._calculate_priority(feature)
            priority_scores.append((feature, priority))
        
        priority_scores.sort(key=lambda x: x[1], reverse=True)
        
        targets = []
        for i, (feature, priority) in enumerate(priority_scores[:top_k]):
            target = SynthesisTarget(
                target_id=f"target_{i}_{feature.feature_id}",
                missing_features=[feature.feature_id] + feature.related_features[:2],
                priority=priority,
                generation_strategy=self._determine_strategy(feature),
                expected_coverage_gain=len([feature.feature_id] + feature.related_features[:2]) * 0.05
            )
            targets.append(target)
        
        return targets
    
    def _calculate_priority(self, feature: FeatureNode) -> float:
        """计算优先级"""
        type_weights = {
            "unexpected": 3.0,
            "emotional": 2.0,
            "behavioral": 1.5,
            "contextual": 1.0,
            "semantic": 0.5,
        }
        
        type_weight = type_weights.get(feature.feature_type, 1.0)
        coverage_weight = 1 - feature.coverage_ratio
        relation_weight = len(feature.related_features) * 0.2
        
        return type_weight * coverage_weight + relation_weight
    
    def _determine_strategy(self, feature: FeatureNode) -> str:
        """确定生成策略"""
        strategies = {
            "unexpected": "inject_unexpected_event",
            "emotional": "add_emotional_variation",
            "behavioral": "expand_behavior_sequence",
            "contextual": "change_context",
            "semantic": "enrich_semantic_content",
        }
        return strategies.get(feature.feature_type, "general_enhancement")
    
    def synthesize_for_target(self, target: SynthesisTarget, 
                               base_data: List[Dict]) -> List[Dict]:
        """为目标合成数据"""
        synthesized = []
        
        for missing_feature in target.missing_features:
            for base in base_data[:5]:
                new_data = self._generate_with_feature(base, missing_feature, 
                                                       target.generation_strategy)
                synthesized.append(new_data)
        
        self.synthesis_history.append({
            "target_id": target.target_id,
            "features_addressed": target.missing_features,
            "samples_generated": len(synthesized),
            "timestamp": datetime.now().isoformat()
        })
        
        return synthesized
    
    def _generate_with_feature(self, base: Dict, feature: str, 
                               strategy: str) -> Dict:
        """生成包含特定特征的数据"""
        new_data = base.copy()
        
        feature_parts = feature.split("_")
        if len(feature_parts) >= 2:
            feature_type = feature_parts[0]
            feature_name = "_".join(feature_parts[1:])
        else:
            feature_type = "general"
            feature_name = feature
        
        if strategy == "inject_unexpected_event":
            new_data["unexpected_event"] = {
                "type": feature_name,
                "impact": random.choice(["high", "medium", "low"]),
                "user_reaction": random.choice(["继续", "暂停", "放弃", "加速"])
            }
        
        elif strategy == "add_emotional_variation":
            new_data["emotion_state"] = {
                "type": feature_name,
                "intensity": round(random.uniform(0.3, 0.9), 2),
                "trigger": random.choice(["商品", "价格", "服务", "物流"])
            }
        
        elif strategy == "expand_behavior_sequence":
            if "actions" not in new_data:
                new_data["actions"] = []
            new_data["actions"].append({
                "type": feature_name,
                "timestamp_offset": random.randint(60, 600)
            })
        
        elif strategy == "change_context":
            new_data["context"] = {
                "time": feature_name,
                "device": random.choice(["mobile", "desktop", "tablet"]),
                "location": random.choice(["home", "work", "commute"])
            }
        
        new_data["_synthesized_for"] = feature
        new_data["_strategy"] = strategy
        
        return new_data


class FACSynthesisPipeline:
    """
    FAC合成流水线 - 整合所有组件
    
    核心流程：
    1. 分析现有数据的特征覆盖
    2. 识别缺失特征
    3. 针对性合成数据
    4. 验证覆盖度提升
    """
    
    def __init__(self):
        self.encoder = SparseFeatureEncoder()
        self.calculator = FACCalculator(self.encoder)
        self.synthesizer = TargetedSynthesizer(self.encoder)
        self.pipeline_stats = {
            "total_analyzed": 0,
            "total_synthesized": 0,
            "coverage_improvement": 0.0
        }
    
    def analyze(self, data: List[Dict]) -> FACMetrics:
        """分析数据"""
        for item in data:
            self.encoder.encode(item)
        
        self.pipeline_stats["total_analyzed"] = len(data)
        return self.calculator.calculate_fac()
    
    def synthesize(self, base_data: List[Dict], 
                   target_coverage: float = 0.8) -> Dict:
        """合成数据"""
        initial_metrics = self.calculator.calculate_fac()
        
        targets = self.synthesizer.identify_synthesis_targets(top_k=20)
        
        all_synthesized = []
        for target in targets:
            synthesized = self.synthesizer.synthesize_for_target(target, base_data)
            all_synthesized.extend(synthesized)
            
            for item in synthesized:
                self.encoder.encode(item)
        
        final_metrics = self.calculator.calculate_fac()
        
        self.pipeline_stats["total_synthesized"] = len(all_synthesized)
        self.pipeline_stats["coverage_improvement"] = (
            final_metrics.coverage_ratio - initial_metrics.coverage_ratio
        )
        
        return {
            "initial_coverage": initial_metrics.coverage_ratio,
            "final_coverage": final_metrics.coverage_ratio,
            "improvement": self.pipeline_stats["coverage_improvement"],
            "synthesized_data": all_synthesized,
            "targets_addressed": len(targets),
            "remaining_missing": final_metrics.uncovered_features,
            "missing_by_type": final_metrics.missing_feature_types
        }
    
    def get_report(self) -> Dict:
        """获取报告"""
        metrics = self.calculator.calculate_fac()
        
        return {
            "FAC Metrics": {
                "Total Features": metrics.total_features,
                "Covered": metrics.covered_features,
                "Uncovered": metrics.uncovered_features,
                "Coverage Ratio": f"{metrics.coverage_ratio:.2%}",
                "Feature Gini": f"{metrics.feature_gini:.4f}",
            },
            "Missing by Type": metrics.missing_feature_types,
            "Pipeline Stats": self.pipeline_stats,
            "Recommendations": self._generate_recommendations(metrics)
        }
    
    def _generate_recommendations(self, metrics: FACMetrics) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if metrics.coverage_ratio < 0.5:
            recommendations.append("覆盖率较低，建议增加数据多样性")
        
        missing_types = metrics.missing_feature_types
        if missing_types.get("unexpected", 0) > 5:
            recommendations.append("意外场景覆盖不足，建议增加意外事件数据")
        
        if missing_types.get("emotional", 0) > 5:
            recommendations.append("情绪维度覆盖不足，建议增加情绪变化数据")
        
        if metrics.feature_gini > 0.7:
            recommendations.append("特征分布不均匀，部分特征过度集中")
        
        return recommendations


if __name__ == "__main__":
    print("=" * 60)
    print("FAC Synthesis 测试 - 特征激活覆盖度合成")
    print("=" * 60)
    
    pipeline = FACSynthesisPipeline()
    
    test_data = [
        {"user": "u001", "action": "浏览", "item": "手机"},
        {"user": "u002", "action": "购买", "item": "电脑", "price": 5000},
        {"user": "u003", "action": "浏览", "item": "耳机"},
        {"user": "u004", "action": "收藏", "item": "键盘"},
        {"user": "u005", "action": "购买", "item": "鼠标", "price": 100},
    ]
    
    print("\n[1] 分析现有数据:")
    metrics = pipeline.analyze(test_data)
    print(f"  总特征数: {metrics.total_features}")
    print(f"  已覆盖: {metrics.covered_features}")
    print(f"  未覆盖: {metrics.uncovered_features}")
    print(f"  覆盖率: {metrics.coverage_ratio:.2%}")
    
    print("\n[2] 缺失特征类型分布:")
    for ftype, count in metrics.missing_feature_types.items():
        print(f"  {ftype}: {count}")
    
    print("\n[3] 针对性合成:")
    result = pipeline.synthesize(test_data)
    print(f"  初始覆盖率: {result['initial_coverage']:.2%}")
    print(f"  最终覆盖率: {result['final_coverage']:.2%}")
    print(f"  提升幅度: {result['improvement']:.2%}")
    print(f"  合成数据: {len(result['synthesized_data'])} 条")
    print(f"  目标数: {result['targets_addressed']}")
    
    print("\n[4] 示例合成数据:")
    for item in result['synthesized_data'][:3]:
        print(f"  {item.get('_synthesized_for', 'unknown')}: {item.get('unexpected_event') or item.get('emotion_state') or 'enhanced'}")
    
    print("\n[5] 完整报告:")
    report = pipeline.get_report()
    for key, value in report.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("测试完成! 解决'数据太规整'问题")
    print("=" * 60)
