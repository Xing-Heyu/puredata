#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量评估系统 - 学术级评估框架
基于论文：《The LLM Data Auditor》质量+可信度双维度评估体系

质量维度：
1. 完整性 - 数据是否完整
2. 一致性 - 数据是否自洽
3. 准确性 - 数据是否准确
4. 多样性 - 数据是否覆盖广泛
5. 真实性 - 数据是否像真实数据

可信度维度：
1. 隐私安全 - 是否泄露敏感信息
2. 公平性 - 是否存在偏见
3. 鲁棒性 - 是否稳定可靠
4. 可解释性 - 是否可追溯
"""

import json
import math
import random
import hashlib
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter, defaultdict
import statistics


@dataclass
class QualityMetrics:
    """质量指标"""
    completeness: float = 0.0
    consistency: float = 0.0
    accuracy: float = 0.0
    diversity: float = 0.0
    authenticity: float = 0.0
    overall_quality: float = 0.0


@dataclass
class TrustworthinessMetrics:
    """可信度指标"""
    privacy_score: float = 0.0
    fairness_score: float = 0.0
    robustness_score: float = 0.0
    explainability_score: float = 0.0
    overall_trustworthiness: float = 0.0


@dataclass
class EvaluationReport:
    """评估报告"""
    dataset_id: str
    timestamp: str
    sample_size: int
    quality: QualityMetrics
    trustworthiness: TrustworthinessMetrics
    tail_distribution: Dict[str, float]
    issues: List[Dict]
    recommendations: List[str]
    comparison_with_baseline: Dict[str, float]


class DataQualityEvaluator:
    """
    数据质量评估器
    
    实现《The LLM Data Auditor》论文中的质量评估框架
    """
    
    SENSITIVE_PATTERNS = [
        r'\b\d{17}[\dXx]\b',
        r'\b\d{15}\b',
        r'\b1[3-9]\d{9}\b',
        r'\b[\w\.-]+@[\w\.-]+\.\w+\b',
        r'\b\d{16,19}\b',
        r'密码[：:]\s*\S+',
        r'账号[：:]\s*\S+',
    ]
    
    BIAS_KEYWORDS = {
        "性别偏见": ["男", "女", "他", "她", "先生", "女士", "帅哥", "美女"],
        "年龄偏见": ["年轻人", "老年人", "中年人", "80后", "90后", "00后"],
        "地域偏见": ["北方人", "南方人", "城里人", "乡下人"],
        "职业偏见": ["程序员", "销售", "老板", "打工"],
    }
    
    def __init__(self):
        self.evaluation_history = []
    
    def evaluate_dataset(self, data: List[Dict], reference_data: List[Dict] = None) -> EvaluationReport:
        """
        评估数据集
        
        Args:
            data: 待评估数据
            reference_data: 参考数据（真实数据，用于对比）
        
        Returns:
            完整的评估报告
        """
        dataset_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        quality = self._evaluate_quality(data, reference_data)
        trustworthiness = self._evaluate_trustworthiness(data)
        tail_distribution = self._analyze_tail_distribution(data)
        issues = self._detect_issues(data, quality, trustworthiness)
        recommendations = self._generate_recommendations(quality, trustworthiness, issues)
        comparison = self._compare_with_baseline(quality, trustworthiness)
        
        report = EvaluationReport(
            dataset_id=dataset_id,
            timestamp=datetime.now().isoformat(),
            sample_size=len(data),
            quality=quality,
            trustworthiness=trustworthiness,
            tail_distribution=tail_distribution,
            issues=issues,
            recommendations=recommendations,
            comparison_with_baseline=comparison
        )
        
        self.evaluation_history.append(report)
        return report
    
    def _evaluate_quality(self, data: List[Dict], reference_data: List[Dict] = None) -> QualityMetrics:
        """评估质量维度"""
        metrics = QualityMetrics()
        
        if not data:
            return metrics
        
        metrics.completeness = self._calculate_completeness(data)
        metrics.consistency = self._calculate_consistency(data)
        metrics.accuracy = self._calculate_accuracy(data, reference_data)
        metrics.diversity = self._calculate_diversity(data)
        metrics.authenticity = self._calculate_authenticity(data, reference_data)
        
        weights = {
            "completeness": 0.2,
            "consistency": 0.2,
            "accuracy": 0.2,
            "diversity": 0.2,
            "authenticity": 0.2,
        }
        
        metrics.overall_quality = (
            metrics.completeness * weights["completeness"] +
            metrics.consistency * weights["consistency"] +
            metrics.accuracy * weights["accuracy"] +
            metrics.diversity * weights["diversity"] +
            metrics.authenticity * weights["authenticity"]
        )
        
        return metrics
    
    def _calculate_completeness(self, data: List[Dict]) -> float:
        """计算完整性"""
        if not data:
            return 0.0
        
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        if not all_keys:
            return 0.0
        
        completeness_scores = []
        for item in data:
            filled_keys = sum(1 for k in all_keys if k in item and item[k] is not None and item[k] != "")
            completeness_scores.append(filled_keys / len(all_keys))
        
        return statistics.mean(completeness_scores) if completeness_scores else 0.0
    
    def _calculate_consistency(self, data: List[Dict]) -> float:
        """计算一致性"""
        if len(data) < 2:
            return 1.0
        
        type_consistency = self._check_type_consistency(data)
        format_consistency = self._check_format_consistency(data)
        value_consistency = self._check_value_consistency(data)
        
        return (type_consistency + format_consistency + value_consistency) / 3
    
    def _check_type_consistency(self, data: List[Dict]) -> float:
        """检查类型一致性"""
        type_patterns = defaultdict(Counter)
        
        for item in data:
            for key, value in item.items():
                value_type = type(value).__name__
                type_patterns[key][value_type] += 1
        
        consistency_scores = []
        for key, type_counts in type_patterns.items():
            total = sum(type_counts.values())
            max_count = max(type_counts.values())
            consistency_scores.append(max_count / total)
        
        return statistics.mean(consistency_scores) if consistency_scores else 1.0
    
    def _check_format_consistency(self, data: List[Dict]) -> float:
        """检查格式一致性"""
        format_patterns = defaultdict(Counter)
        
        for item in data:
            for key, value in item.items():
                if isinstance(value, str):
                    if re.match(r'\d{4}-\d{2}-\d{2}', value):
                        format_patterns[key]["date"] += 1
                    elif re.match(r'\d+:\d+', value):
                        format_patterns[key]["time"] += 1
                    elif re.match(r'https?://', value):
                        format_patterns[key]["url"] += 1
                    else:
                        format_patterns[key]["text"] += 1
        
        consistency_scores = []
        for key, format_counts in format_patterns.items():
            total = sum(format_counts.values())
            max_count = max(format_counts.values())
            consistency_scores.append(max_count / total)
        
        return statistics.mean(consistency_scores) if consistency_scores else 1.0
    
    def _check_value_consistency(self, data: List[Dict]) -> float:
        """检查值一致性"""
        value_ranges = defaultdict(list)
        
        for item in data:
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    value_ranges[key].append(value)
        
        consistency_scores = []
        for key, values in value_ranges.items():
            if len(values) < 2:
                continue
            
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0
            
            if mean_val != 0:
                cv = std_val / abs(mean_val)
                consistency = max(0, 1 - cv)
            else:
                consistency = 1.0 if std_val == 0 else 0.5
            
            consistency_scores.append(consistency)
        
        return statistics.mean(consistency_scores) if consistency_scores else 1.0
    
    def _calculate_accuracy(self, data: List[Dict], reference_data: List[Dict] = None) -> float:
        """计算准确性"""
        if not reference_data:
            return 0.7
        
        data_keys = set()
        for item in data:
            data_keys.update(item.keys())
        
        ref_keys = set()
        for item in reference_data:
            ref_keys.update(item.keys())
        
        key_overlap = len(data_keys & ref_keys) / max(len(data_keys | ref_keys), 1)
        
        data_values = []
        for item in data:
            for v in item.values():
                if isinstance(v, (str, int, float)):
                    data_values.append(str(v))
        
        ref_values = []
        for item in reference_data:
            for v in item.values():
                if isinstance(v, (str, int, float)):
                    ref_values.append(str(v))
        
        if data_values and ref_values:
            data_vocab = set(' '.join(data_values).split())
            ref_vocab = set(' '.join(ref_values).split())
            vocab_overlap = len(data_vocab & ref_vocab) / max(len(data_vocab | ref_vocab), 1)
        else:
            vocab_overlap = 0.5
        
        return (key_overlap + vocab_overlap) / 2
    
    def _calculate_diversity(self, data: List[Dict]) -> float:
        """计算多样性"""
        if not data:
            return 0.0
        
        unique_structures = set()
        for item in data:
            structure = tuple(sorted(item.keys()))
            unique_structures.add(structure)
        
        structure_diversity = len(unique_structures) / max(len(data), 1)
        
        all_values = []
        for item in data:
            for v in item.values():
                if isinstance(v, str):
                    all_values.append(v)
        
        if all_values:
            unique_values = set(all_values)
            value_diversity = len(unique_values) / max(len(all_values), 1)
        else:
            value_diversity = 0.5
        
        all_texts = ' '.join([str(v) for item in data for v in item.values() if isinstance(v, str)])
        if all_texts:
            words = all_texts.split()
            word_freq = Counter(words)
            total_words = len(words)
            if total_words > 0:
                entropy = -sum((count/total_words) * math.log2(count/total_words) 
                              for count in word_freq.values())
                max_entropy = math.log2(len(word_freq)) if len(word_freq) > 1 else 1
                normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
            else:
                normalized_entropy = 0
        else:
            normalized_entropy = 0.5
        
        return (structure_diversity + value_diversity + normalized_entropy) / 3
    
    def _calculate_authenticity(self, data: List[Dict], reference_data: List[Dict] = None) -> float:
        """计算真实性"""
        authenticity_scores = []
        
        pattern_score = self._check_realistic_patterns(data)
        authenticity_scores.append(pattern_score)
        
        noise_score = self._check_natural_noise(data)
        authenticity_scores.append(noise_score)
        
        outlier_score = self._check_natural_outliers(data)
        authenticity_scores.append(outlier_score)
        
        return statistics.mean(authenticity_scores)
    
    def _check_realistic_patterns(self, data: List[Dict]) -> float:
        """检查是否有真实数据模式"""
        time_fields = 0
        time_valid = 0
        
        for item in data:
            for key, value in item.items():
                if isinstance(value, str):
                    if re.match(r'\d{4}-\d{2}-\d{2}', value):
                        time_fields += 1
                        try:
                            datetime.strptime(value[:10], '%Y-%m-%d')
                            time_valid += 1
                        except ValueError:
                            pass
        
        if time_fields == 0:
            return 0.7
        
        return time_valid / time_fields
    
    def _check_natural_noise(self, data: List[Dict]) -> float:
        """检查是否有自然噪声"""
        text_values = []
        for item in data:
            for v in item.values():
                if isinstance(v, str) and len(v) > 10:
                    text_values.append(v)
        
        if not text_values:
            return 0.7
        
        has_typos = any(any(c.isupper() and i > 0 and text[i-1].islower() 
                           for i, c in enumerate(text)) 
                       for text in text_values)
        
        has_variations = len(set(len(t) for t in text_values)) > 1
        
        noise_indicators = sum([has_typos, has_variations])
        return min(1.0, 0.5 + noise_indicators * 0.25)
    
    def _check_natural_outliers(self, data: List[Dict]) -> float:
        """检查是否有自然离群值"""
        numeric_values = []
        for item in data:
            for v in item.values():
                if isinstance(v, (int, float)):
                    numeric_values.append(v)
        
        if len(numeric_values) < 10:
            return 0.7
        
        mean_val = statistics.mean(numeric_values)
        std_val = statistics.stdev(numeric_values)
        
        if std_val == 0:
            return 0.5
        
        outliers = sum(1 for v in numeric_values if abs(v - mean_val) > 2 * std_val)
        outlier_ratio = outliers / len(numeric_values)
        
        ideal_outlier_ratio = 0.05
        deviation = abs(outlier_ratio - ideal_outlier_ratio)
        
        return max(0, 1 - deviation * 2)
    
    def _evaluate_trustworthiness(self, data: List[Dict]) -> TrustworthinessMetrics:
        """评估可信度维度"""
        metrics = TrustworthinessMetrics()
        
        if not data:
            return metrics
        
        metrics.privacy_score = self._calculate_privacy_score(data)
        metrics.fairness_score = self._calculate_fairness_score(data)
        metrics.robustness_score = self._calculate_robustness_score(data)
        metrics.explainability_score = self._calculate_explainability_score(data)
        
        weights = {
            "privacy": 0.3,
            "fairness": 0.25,
            "robustness": 0.25,
            "explainability": 0.2,
        }
        
        metrics.overall_trustworthiness = (
            metrics.privacy_score * weights["privacy"] +
            metrics.fairness_score * weights["fairness"] +
            metrics.robustness_score * weights["robustness"] +
            metrics.explainability_score * weights["explainability"]
        )
        
        return metrics
    
    def _calculate_privacy_score(self, data: List[Dict]) -> float:
        """计算隐私安全分数"""
        total_items = len(data)
        if total_items == 0:
            return 1.0
        
        sensitive_count = 0
        for item in data:
            item_str = json.dumps(item, ensure_ascii=False)
            for pattern in self.SENSITIVE_PATTERNS:
                if re.search(pattern, item_str):
                    sensitive_count += 1
                    break
        
        leak_ratio = sensitive_count / total_items
        return max(0, 1 - leak_ratio * 2)
    
    def _calculate_fairness_score(self, data: List[Dict]) -> float:
        """计算公平性分数"""
        bias_counts = defaultdict(int)
        total_items = len(data)
        
        if total_items == 0:
            return 1.0
        
        for item in data:
            item_str = json.dumps(item, ensure_ascii=False)
            for bias_type, keywords in self.BIAS_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in item_str:
                        bias_counts[bias_type] += 1
                        break
        
        if not bias_counts:
            return 1.0
        
        max_bias_ratio = max(count / total_items for count in bias_counts.values())
        
        return max(0, 1 - max_bias_ratio)
    
    def _calculate_robustness_score(self, data: List[Dict]) -> float:
        """计算鲁棒性分数"""
        if len(data) < 10:
            return 0.7
        
        size_variance = statistics.variance([len(str(item)) for item in data])
        size_score = min(1, size_variance / 1000)
        
        key_sets = [frozenset(item.keys()) for item in data]
        unique_key_sets = len(set(key_sets))
        structure_score = 1 - (unique_key_sets - 1) / max(len(data) - 1, 1)
        
        return (size_score + structure_score) / 2
    
    def _calculate_explainability_score(self, data: List[Dict]) -> float:
        """计算可解释性分数"""
        if not data:
            return 0.0
        
        explainability_scores = []
        
        for item in data[:min(100, len(data))]:
            score = 0
            
            if isinstance(item, dict):
                score += 0.3
                
                if any('_' in k or '-' in k for k in item.keys()):
                    score += 0.2
                
                if any(k in ['id', 'timestamp', 'created_at', 'type', 'action'] for k in item.keys()):
                    score += 0.3
                
                if any(isinstance(v, (str, int, float, bool)) for v in item.values()):
                    score += 0.2
            
            explainability_scores.append(score)
        
        return statistics.mean(explainability_scores) if explainability_scores else 0.0
    
    def _analyze_tail_distribution(self, data: List[Dict]) -> Dict[str, float]:
        """分析长尾分布"""
        all_values = []
        for item in data:
            for v in item.values():
                if isinstance(v, str):
                    all_values.append(v)
                elif isinstance(v, (int, float)):
                    all_values.append(str(v))
        
        if not all_values:
            return {"head_ratio": 0, "tail_ratio": 0, "gini_coefficient": 0}
        
        freq = Counter(all_values)
        sorted_freq = sorted(freq.values(), reverse=True)
        total = sum(sorted_freq)
        
        if total == 0:
            return {"head_ratio": 0, "tail_ratio": 0, "gini_coefficient": 0}
        
        top_10_count = sum(sorted_freq[:max(1, len(sorted_freq) // 10)])
        head_ratio = top_10_count / total
        
        tail_threshold = len(sorted_freq) * 0.9
        tail_count = sum(sorted_freq[int(tail_threshold):])
        tail_ratio = tail_count / total
        
        cumulative = 0
        gini_sum = 0
        for i, f in enumerate(sorted_freq):
            cumulative += f
            gini_sum += cumulative
        gini = (2 * gini_sum / (len(sorted_freq) * total)) - (len(sorted_freq) + 1) / len(sorted_freq)
        
        return {
            "head_ratio": round(head_ratio, 4),
            "tail_ratio": round(tail_ratio, 4),
            "gini_coefficient": round(gini, 4)
        }
    
    def _detect_issues(self, data: List[Dict], quality: QualityMetrics, 
                       trustworthiness: TrustworthinessMetrics) -> List[Dict]:
        """检测问题"""
        issues = []
        
        if quality.completeness < 0.8:
            issues.append({
                "type": "quality",
                "severity": "high" if quality.completeness < 0.5 else "medium",
                "message": f"数据完整性不足 ({quality.completeness:.2%})",
                "suggestion": "检查缺失字段，补充必要数据"
            })
        
        if quality.consistency < 0.7:
            issues.append({
                "type": "quality",
                "severity": "medium",
                "message": f"数据一致性较低 ({quality.consistency:.2%})",
                "suggestion": "统一数据格式和类型"
            })
        
        if quality.diversity < 0.5:
            issues.append({
                "type": "quality",
                "severity": "high",
                "message": f"数据多样性不足 ({quality.diversity:.2%})",
                "suggestion": "增加数据样本的多样性，避免模式重复"
            })
        
        if trustworthiness.privacy_score < 0.9:
            issues.append({
                "type": "trustworthiness",
                "severity": "high",
                "message": f"存在隐私泄露风险 ({trustworthiness.privacy_score:.2%})",
                "suggestion": "检测到敏感信息，需要进行脱敏处理"
            })
        
        if trustworthiness.fairness_score < 0.8:
            issues.append({
                "type": "trustworthiness",
                "severity": "medium",
                "message": f"可能存在偏见问题 ({trustworthiness.fairness_score:.2%})",
                "suggestion": "检查数据中的偏见关键词，平衡数据分布"
            })
        
        tail_dist = self._analyze_tail_distribution(data)
        if tail_dist["gini_coefficient"] > 0.8:
            issues.append({
                "type": "distribution",
                "severity": "high",
                "message": f"数据分布过于集中 (基尼系数: {tail_dist['gini_coefficient']:.2f})",
                "suggestion": "增加长尾数据，使用DASGen方法增强分布对齐"
            })
        
        return issues
    
    def _generate_recommendations(self, quality: QualityMetrics, 
                                   trustworthiness: TrustworthinessMetrics,
                                   issues: List[Dict]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        high_severity = [i for i in issues if i["severity"] == "high"]
        if high_severity:
            recommendations.append(f"【紧急】发现 {len(high_severity)} 个高严重性问题，需优先处理")
        
        if quality.diversity < 0.6:
            recommendations.append("建议使用DASGen长尾增强方法提升数据多样性")
        
        if trustworthiness.privacy_score < 0.95:
            recommendations.append("建议对敏感数据进行脱敏或匿名化处理")
        
        if quality.authenticity < 0.7:
            recommendations.append("建议引入真实种子数据作为生成基础")
        
        if quality.overall_quality < 0.7:
            recommendations.append("建议使用LLM数据审计功能进行自动优化")
        
        if quality.overall_quality > 0.8 and trustworthiness.overall_trustworthiness > 0.8:
            recommendations.append("数据质量良好，可用于模型训练")
        
        return recommendations
    
    def _compare_with_baseline(self, quality: QualityMetrics, 
                                trustworthiness: TrustworthinessMetrics) -> Dict[str, float]:
        """与基准对比"""
        baseline = {
            "quality": 0.75,
            "trustworthiness": 0.85,
            "diversity": 0.60,
            "authenticity": 0.65,
        }
        
        return {
            "quality_diff": round(quality.overall_quality - baseline["quality"], 4),
            "trustworthiness_diff": round(trustworthiness.overall_trustworthiness - baseline["trustworthiness"], 4),
            "diversity_diff": round(quality.diversity - baseline["diversity"], 4),
            "authenticity_diff": round(quality.authenticity - baseline["authenticity"], 4),
        }
    
    def generate_report_json(self, report: EvaluationReport) -> str:
        """生成JSON格式报告"""
        report_dict = {
            "dataset_id": report.dataset_id,
            "timestamp": report.timestamp,
            "sample_size": report.sample_size,
            "quality": {
                "completeness": round(report.quality.completeness, 4),
                "consistency": round(report.quality.consistency, 4),
                "accuracy": round(report.quality.accuracy, 4),
                "diversity": round(report.quality.diversity, 4),
                "authenticity": round(report.quality.authenticity, 4),
                "overall_quality": round(report.quality.overall_quality, 4),
            },
            "trustworthiness": {
                "privacy_score": round(report.trustworthiness.privacy_score, 4),
                "fairness_score": round(report.trustworthiness.fairness_score, 4),
                "robustness_score": round(report.trustworthiness.robustness_score, 4),
                "explainability_score": round(report.trustworthiness.explainability_score, 4),
                "overall_trustworthiness": round(report.trustworthiness.overall_trustworthiness, 4),
            },
            "tail_distribution": report.tail_distribution,
            "issues": report.issues,
            "recommendations": report.recommendations,
            "comparison_with_baseline": report.comparison_with_baseline,
        }
        
        return json.dumps(report_dict, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("=" * 60)
    print("数据质量评估系统测试")
    print("=" * 60)
    
    test_data = [
        {"user_id": "u001", "action": "浏览", "item": "商品A", "timestamp": "2024-01-15 10:30:00"},
        {"user_id": "u002", "action": "购买", "item": "商品B", "timestamp": "2024-01-15 11:00:00"},
        {"user_id": "u003", "action": "浏览", "item": "商品C", "timestamp": "2024-01-15 11:30:00"},
        {"user_id": "u001", "action": "收藏", "item": "商品A", "timestamp": "2024-01-15 12:00:00"},
        {"user_id": "u004", "action": "购买", "item": "商品D", "timestamp": "2024-01-15 12:30:00"},
    ]
    
    evaluator = DataQualityEvaluator()
    report = evaluator.evaluate_dataset(test_data)
    
    print("\n[质量指标]")
    print(f"  完整性: {report.quality.completeness:.2%}")
    print(f"  一致性: {report.quality.consistency:.2%}")
    print(f"  准确性: {report.quality.accuracy:.2%}")
    print(f"  多样性: {report.quality.diversity:.2%}")
    print(f"  真实性: {report.quality.authenticity:.2%}")
    print(f"  综合质量: {report.quality.overall_quality:.2%}")
    
    print("\n[可信度指标]")
    print(f"  隐私安全: {report.trustworthiness.privacy_score:.2%}")
    print(f"  公平性: {report.trustworthiness.fairness_score:.2%}")
    print(f"  鲁棒性: {report.trustworthiness.robustness_score:.2%}")
    print(f"  可解释性: {report.trustworthiness.explainability_score:.2%}")
    print(f"  综合可信度: {report.trustworthiness.overall_trustworthiness:.2%}")
    
    print("\n[长尾分布]")
    print(f"  头部占比: {report.tail_distribution['head_ratio']:.2%}")
    print(f"  尾部占比: {report.tail_distribution['tail_ratio']:.2%}")
    print(f"  基尼系数: {report.tail_distribution['gini_coefficient']:.4f}")
    
    print("\n[问题检测]")
    for issue in report.issues:
        print(f"  [{issue['severity']}] {issue['message']}")
    
    print("\n[改进建议]")
    for rec in report.recommendations:
        print(f"  - {rec}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
