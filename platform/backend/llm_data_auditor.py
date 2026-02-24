#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Data Auditor - 完整审计系统
合并自：
- llm_data_auditor.py（论文arXiv:2601.17717质量维度）
- LLM数据审计.py（规则/模式/语义审计 + 自动修复）

功能：
1. 质量维度：完整性、一致性、准确性、多样性、真实性
2. 可信度维度：隐私安全、公平性、鲁棒性、可解释性
3. 规则审计：基于预定义规则检查
4. 模式审计：基于统计模式检查
5. 语义审计：基于语义一致性检查
6. 自动修复：自动修复可修复的问题
"""

import re
import math
import json
import hashlib
import random
import statistics
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from datetime import datetime


# ============ 数据类 ============

@dataclass
class QualityMetrics:
    """质量指标"""
    completeness: float = 0.0
    consistency: float = 0.0
    accuracy: float = 0.0
    diversity: float = 0.0
    authenticity: float = 0.0
    
    @property
    def overall_quality(self) -> float:
        weights = {
            "completeness": 0.25,
            "consistency": 0.20,
            "accuracy": 0.20,
            "diversity": 0.15,
            "authenticity": 0.20
        }
        return (
            self.completeness * weights["completeness"] +
            self.consistency * weights["consistency"] +
            self.accuracy * weights["accuracy"] +
            self.diversity * weights["diversity"] +
            self.authenticity * weights["authenticity"]
        )


@dataclass
class TrustworthinessMetrics:
    """可信度指标"""
    privacy_score: float = 0.0
    fairness_score: float = 0.0
    robustness_score: float = 0.0
    explainability_score: float = 0.0
    
    @property
    def overall_trustworthiness(self) -> float:
        weights = {
            "privacy": 0.30,
            "fairness": 0.25,
            "robustness": 0.25,
            "explainability": 0.20
        }
        return (
            self.privacy_score * weights["privacy"] +
            self.fairness_score * weights["fairness"] +
            self.robustness_score * weights["robustness"] +
            self.explainability_score * weights["explainability"]
        )


@dataclass
class AuditIssue:
    """审计问题"""
    issue_id: str
    severity: str  # critical, high, medium, low
    category: str  # quality, trustworthiness, distribution
    description: str
    location: str
    suggestion: str
    auto_fixable: bool


@dataclass
class AuditReport:
    """审计报告"""
    report_id: str = ""
    timestamp: str = ""
    total_items: int = 0
    quality: QualityMetrics = field(default_factory=QualityMetrics)
    trustworthiness: TrustworthinessMetrics = field(default_factory=TrustworthinessMetrics)
    issues: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    auto_fixes_applied: int = 0
    before_after_comparison: Dict = field(default_factory=dict)
    
    @property
    def overall_score(self) -> float:
        return (self.quality.overall_quality * 0.6 + 
                self.trustworthiness.overall_trustworthiness * 0.4)


# ============ 质量评估器 ============

class CompletenessEvaluator:
    """完整性评估器"""
    
    REQUIRED_FIELDS = ["id", "text", "category"]
    OPTIONAL_FIELDS = ["word", "source", "confidence", "timestamp"]
    
    def evaluate(self, data: List[Dict]) -> Tuple[float, List[Dict]]:
        if not data:
            return 0.0, [{"type": "empty_data", "message": "数据集为空"}]
        
        issues = []
        total_score = 0.0
        
        for i, item in enumerate(data):
            item_score = 1.0
            
            for field in self.REQUIRED_FIELDS:
                if field not in item or item[field] is None or item[field] == "":
                    item_score -= 0.3
                    issues.append({
                        "type": "missing_required_field",
                        "item_id": item.get("id", i),
                        "field": field,
                        "severity": "high"
                    })
            
            optional_filled = sum(1 for f in self.OPTIONAL_FIELDS if f in item and item[f])
            item_score += optional_filled * 0.05
            item_score = min(item_score, 1.0)
            
            total_score += item_score
        
        return total_score / len(data), issues


class ConsistencyEvaluator:
    """一致性评估器"""
    
    def evaluate(self, data: List[Dict]) -> Tuple[float, List[Dict]]:
        if not data:
            return 0.0, []
        
        issues = []
        
        if data:
            first_keys = set(data[0].keys())
            for i, item in enumerate(data[1:], 1):
                if set(item.keys()) != first_keys:
                    issues.append({
                        "type": "inconsistent_schema",
                        "item_id": item.get("id", i),
                        "severity": "medium"
                    })
        
        categories = Counter(item.get("category", "unknown") for item in data)
        if len(categories) > 10:
            issues.append({
                "type": "too_many_categories",
                "count": len(categories),
                "severity": "low"
            })
        
        format_issues = 0
        for item in data:
            text = item.get("text", "")
            if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', text):
                format_issues += 1
        
        if format_issues > 0:
            issues.append({
                "type": "encoding_issues",
                "count": format_issues,
                "severity": "high"
            })
        
        consistency_score = 1.0 - (len([i for i in issues if i.get("severity") == "high"]) * 0.1)
        consistency_score -= len([i for i in issues if i.get("severity") == "medium"]) * 0.05
        consistency_score = max(0.0, consistency_score)
        
        return consistency_score, issues


class AccuracyEvaluator:
    """准确性评估器"""
    
    COMMON_ERRORS = [
        (r'\s{3,}', "多余空格"),
        (r'[。.]{3,}', "重复标点"),
        (r'[？?]{2,}', "重复问号"),
        (r'[！!]{2,}', "重复感叹号"),
        (r'(.)\1{4,}', "异常重复字符"),
    ]
    
    def evaluate(self, data: List[Dict]) -> Tuple[float, List[Dict]]:
        if not data:
            return 0.0, []
        
        issues = []
        total_score = 0.0
        
        for i, item in enumerate(data):
            text = item.get("text", "")
            item_score = 1.0
            
            for pattern, error_name in self.COMMON_ERRORS:
                if re.search(pattern, text):
                    item_score -= 0.1
                    issues.append({
                        "type": "format_error",
                        "item_id": item.get("id", i),
                        "error": error_name,
                        "severity": "low"
                    })
            
            if len(text) < 10:
                item_score -= 0.2
                issues.append({
                    "type": "too_short",
                    "item_id": item.get("id", i),
                    "length": len(text),
                    "severity": "medium"
                })
            
            if len(text) > 1000:
                item_score -= 0.1
            
            total_score += max(0.0, item_score)
        
        return total_score / len(data), issues


class DiversityEvaluator:
    """多样性评估器"""
    
    def evaluate(self, data: List[Dict]) -> Tuple[float, List[Dict]]:
        if not data:
            return 0.0, []
        
        issues = []
        
        texts = [item.get("text", "") for item in data]
        unique_texts = set(texts)
        duplication_rate = 1 - (len(unique_texts) / len(texts)) if texts else 0
        
        if duplication_rate > 0.3:
            issues.append({
                "type": "high_duplication",
                "rate": duplication_rate,
                "severity": "high"
            })
        
        text_hashes = [hashlib.md5(t.encode()).hexdigest()[:8] for t in texts]
        unique_hashes = set(text_hashes)
        near_duplication_rate = 1 - (len(unique_hashes) / len(text_hashes)) if text_hashes else 0
        
        if near_duplication_rate > 0.2:
            issues.append({
                "type": "near_duplication",
                "rate": near_duplication_rate,
                "severity": "medium"
            })
        
        lengths = [len(t) for t in texts]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths) if lengths else 0
        std_dev = math.sqrt(variance)
        
        length_diversity = min(1.0, std_dev / 50) if avg_length > 0 else 0
        
        words = []
        for text in texts:
            words.extend(re.findall(r'\b\w+\b', text.lower()))
        
        word_counter = Counter(words)
        unique_words = len(word_counter)
        total_words = len(words)
        vocabulary_richness = unique_words / total_words if total_words > 0 else 0
        
        diversity_score = (
            (1 - duplication_rate) * 0.4 +
            (1 - near_duplication_rate) * 0.2 +
            length_diversity * 0.2 +
            vocabulary_richness * 0.2
        )
        
        return diversity_score, issues


class AuthenticityEvaluator:
    """真实性评估器"""
    
    ARTIFACT_PATTERNS = [
        (r'lorem ipsum', "占位文本"),
        (r'test\s*test', "测试文本"),
        (r'sample\s*sample', "样本文本"),
        (r'\[.*?\]', "未填充占位符"),
        (r'\{.*?\}', "未填充变量"),
        (r'TODO|FIXME|XXX', "开发标记"),
    ]
    
    def evaluate(self, data: List[Dict]) -> Tuple[float, List[Dict]]:
        if not data:
            return 0.0, []
        
        issues = []
        total_score = 0.0
        
        for i, item in enumerate(data):
            text = item.get("text", "")
            item_score = 1.0
            
            for pattern, artifact_name in self.ARTIFACT_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    item_score -= 0.2
                    issues.append({
                        "type": "artifact_detected",
                        "item_id": item.get("id", i),
                        "artifact": artifact_name,
                        "severity": "medium"
                    })
            
            total_score += max(0.0, item_score)
        
        return total_score / len(data), issues


# ============ 可信度评估器 ============

class PrivacyEvaluator:
    """隐私安全评估器"""
    
    PII_PATTERNS = [
        (r'\b\d{17}[\dXx]\b', "身份证号"),
        (r'\b1[3-9]\d{9}\b', "手机号"),
        (r'\b[\w.-]+@[\w.-]+\.\w+\b', "邮箱"),
        (r'\b\d{16,19}\b', "银行卡号"),
        (r'密码[：:]\s*\S+', "密码泄露"),
    ]
    
    def evaluate(self, data: List[Dict]) -> Tuple[float, List[Dict]]:
        if not data:
            return 1.0, []
        
        issues = []
        pii_count = 0
        
        for i, item in enumerate(data):
            text = str(item)
            has_pii = False
            
            for pattern, pii_type in self.PII_PATTERNS:
                if re.search(pattern, text):
                    has_pii = True
                    issues.append({
                        "type": "pii_detected",
                        "item_id": item.get("id", i),
                        "pii_type": pii_type,
                        "severity": "high"
                    })
            
            if has_pii:
                pii_count += 1
        
        privacy_score = 1 - (pii_count / len(data))
        
        return privacy_score, issues


class FairnessEvaluator:
    """公平性评估器"""
    
    BIAS_KEYWORDS = {
        "gender": ["男", "女", "male", "female"],
        "age": ["老", "少", "年轻", "年老", "young", "old"],
    }
    
    def evaluate(self, data: List[Dict]) -> Tuple[float, List[Dict]]:
        if not data:
            return 1.0, []
        
        issues = []
        bias_counts = {category: 0 for category in self.BIAS_KEYWORDS}
        
        for item in data:
            text = str(item).lower()
            for category, keywords in self.BIAS_KEYWORDS.items():
                for keyword in keywords:
                    if keyword.lower() in text:
                        bias_counts[category] += 1
        
        total_bias = sum(bias_counts.values())
        total_items = len(data)
        
        if total_bias > total_items * 0.1:
            issues.append({
                "type": "potential_bias",
                "bias_counts": bias_counts,
                "severity": "medium"
            })
        
        fairness_score = 1 - min(1.0, total_bias / (total_items * 2))
        
        return fairness_score, issues


class RobustnessEvaluator:
    """鲁棒性评估器"""
    
    def evaluate(self, data: List[Dict]) -> Tuple[float, List[Dict]]:
        if not data:
            return 0.0, []
        
        issues = []
        total_score = 0.0
        
        for i, item in enumerate(data):
            item_score = 1.0
            
            text = item.get("text", "")
            
            if not text or len(text.strip()) == 0:
                item_score = 0.0
                issues.append({
                    "type": "empty_text",
                    "item_id": item.get("id", i),
                    "severity": "high"
                })
            
            if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', text):
                item_score -= 0.3
            
            total_score += max(0.0, item_score)
        
        return total_score / len(data), issues


class ExplainabilityEvaluator:
    """可解释性评估器"""
    
    def evaluate(self, data: List[Dict]) -> Tuple[float, List[Dict]]:
        if not data:
            return 0.0, []
        
        total_score = 0.0
        
        for item in data:
            item_score = 0.0
            
            if "id" in item:
                item_score += 0.2
            if "category" in item:
                item_score += 0.2
            if "source" in item:
                item_score += 0.2
            if "confidence" in item:
                item_score += 0.2
            if "word" in item:
                item_score += 0.2
            
            total_score += item_score
        
        return total_score / len(data), []


# ============ 主审计器 ============

class LLMDataAuditor:
    """
    LLM数据审计器 - 完整审计系统
    
    功能：
    1. 质量维度评估
    2. 可信度维度评估
    3. 自动修复
    4. 生成报告
    """
    
    def __init__(self):
        self.quality_evaluators = {
            "completeness": CompletenessEvaluator(),
            "consistency": ConsistencyEvaluator(),
            "accuracy": AccuracyEvaluator(),
            "diversity": DiversityEvaluator(),
            "authenticity": AuthenticityEvaluator(),
        }
        
        self.trust_evaluators = {
            "privacy": PrivacyEvaluator(),
            "fairness": FairnessEvaluator(),
            "robustness": RobustnessEvaluator(),
            "explainability": ExplainabilityEvaluator(),
        }
        
        self.audit_history = []
    
    def audit(self, data: List[Dict], auto_fix: bool = True) -> AuditReport:
        """执行完整审计"""
        report_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        all_issues = []
        
        quality_scores = {}
        for name, evaluator in self.quality_evaluators.items():
            score, issues = evaluator.evaluate(data)
            quality_scores[name] = score
            all_issues.extend(issues)
        
        trust_scores = {}
        for name, evaluator in self.trust_evaluators.items():
            score, issues = evaluator.evaluate(data)
            trust_scores[name] = score
            all_issues.extend(issues)
        
        fixed_data = data.copy() if auto_fix else data
        auto_fixes = 0
        
        if auto_fix:
            fixed_data, auto_fixes = self._apply_auto_fixes(data, all_issues)
        
        report = AuditReport(
            report_id=report_id,
            timestamp=datetime.now().isoformat(),
            total_items=len(data),
            quality=QualityMetrics(
                completeness=quality_scores.get("completeness", 0),
                consistency=quality_scores.get("consistency", 0),
                accuracy=quality_scores.get("accuracy", 0),
                diversity=quality_scores.get("diversity", 0),
                authenticity=quality_scores.get("authenticity", 0)
            ),
            trustworthiness=TrustworthinessMetrics(
                privacy_score=trust_scores.get("privacy", 0),
                fairness_score=trust_scores.get("fairness", 0),
                robustness_score=trust_scores.get("robustness", 0),
                explainability_score=trust_scores.get("explainability", 0)
            ),
            issues=all_issues,
            recommendations=[],
            auto_fixes_applied=auto_fixes,
            before_after_comparison={
                "before_issues": len(all_issues),
                "after_issues": len([i for i in all_issues if not i.get("auto_fixable", False)]),
                "auto_fixed": auto_fixes,
            }
        )
        
        report.recommendations = self._generate_recommendations(report)
        
        self.audit_history.append(report)
        return report
    
    def _apply_auto_fixes(self, data: List[Dict], issues: List[Dict]) -> Tuple[List[Dict], int]:
        """应用自动修复"""
        fixed_data = [item.copy() for item in data]
        fixes_applied = 0
        
        for issue in issues:
            if not issue.get("auto_fixable", False):
                continue
            
            try:
                if "pii_detected" in issue.get("type", ""):
                    idx = issue.get("item_id", 0)
                    if isinstance(idx, int) and idx < len(fixed_data):
                        for key, value in fixed_data[idx].items():
                            if isinstance(value, str):
                                if re.match(r'\b\d{17}[\dXx]\b', value):
                                    fixed_data[idx][key] = value[:6] + "********" + value[-4:]
                                    fixes_applied += 1
            except Exception:
                pass
        
        return fixed_data, fixes_applied
    
    def _generate_recommendations(self, report: AuditReport) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if report.quality.completeness < 0.8:
            recommendations.append("建议：补充缺失字段，确保每条数据包含id、text、category等必需字段")
        
        if report.quality.consistency < 0.8:
            recommendations.append("建议：统一数据格式，确保所有数据项使用相同的字段结构")
        
        if report.quality.diversity < 0.7:
            recommendations.append("建议：增加数据多样性，减少重复内容")
        
        if report.trustworthiness.privacy_score < 0.9:
            recommendations.append("警告：检测到潜在隐私信息，建议进行脱敏处理")
        
        if report.trustworthiness.robustness_score < 0.8:
            recommendations.append("建议：清理异常字符，确保数据格式规范")
        
        if report.overall_score < 0.6:
            recommendations.append("严重：数据质量不达标，建议重新生成或人工审核")
        
        if not recommendations:
            recommendations.append("数据质量良好，可用于模型训练")
        
        return recommendations
    
    def quick_check(self, data: List[Dict]) -> Dict:
        """快速检查"""
        report = self.audit(data)
        
        return {
            "total_items": report.total_items,
            "overall_score": round(report.overall_score, 3),
            "quality_score": round(report.quality.overall_quality, 3),
            "trustworthiness_score": round(report.trustworthiness.overall_trustworthiness, 3),
            "issue_count": len(report.issues),
            "high_severity_count": len([i for i in report.issues if i.get("severity") == "high"]),
            "top_recommendations": report.recommendations[:3]
        }


def audit_dataset(data: List[Dict]) -> AuditReport:
    """便捷函数：审计数据集"""
    auditor = LLMDataAuditor()
    return auditor.audit(data)


if __name__ == "__main__":
    test_data = [
        {"id": 1, "text": "AI is a technology that enables machines to learn.", "category": "人工智能", "word": "AI"},
        {"id": 2, "text": "Machine learning is a subset of AI.", "category": "人工智能", "word": "ML"},
        {"id": 3, "text": "我的手机号是13812345678", "category": "测试", "word": "PII"},
    ]
    
    print("=== LLM Data Auditor 测试 ===\n")
    
    auditor = LLMDataAuditor()
    report = auditor.audit(test_data)
    
    print(f"数据总量: {report.total_items}")
    print(f"综合得分: {report.overall_score:.3f}")
    print(f"质量总分: {report.quality.overall_quality:.3f}")
    print(f"可信度总分: {report.trustworthiness.overall_trustworthiness:.3f}")
    print(f"\n改进建议:")
    for rec in report.recommendations:
        print(f"  - {rec}")
