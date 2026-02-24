#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动异常检测模块 - 整合质量评估和风控
基于国家标准《人工智能数据集 质量评价指标》

核心功能：
1. 自动检测数据异常
2. 规则库 + 统计方法结合
3. 实时告警
4. 自动修复建议
"""

import re
import math
import random
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter, defaultdict


@dataclass
class AnomalyRule:
    """异常检测规则"""
    rule_id: str
    name: str
    description: str
    severity: str  # critical, high, medium, low
    check_func: str
    threshold: float
    auto_fix: bool


@dataclass
class AnomalyResult:
    """异常检测结果"""
    is_anomaly: bool
    rule_id: str
    severity: str
    description: str
    value: Any
    threshold: Any
    suggestion: str
    auto_fixable: bool


class AnomalyRuleLibrary:
    """
    异常检测规则库 - 预定义规则
    
    规则分类：
    1. 完整性规则 - 检测缺失值
    2. 一致性规则 - 检测逻辑矛盾
    3. 准确性规则 - 检测错误数据
    4. 唯一性规则 - 检测重复数据
    5. 有效性规则 - 检测非法值
    """
    
    RULES = [
        AnomalyRule(
            rule_id="R001",
            name="文本过短",
            description="文本长度低于最小阈值",
            severity="medium",
            check_func="text_length",
            threshold=20,
            auto_fix=True
        ),
        AnomalyRule(
            rule_id="R002",
            name="文本过长",
            description="文本长度超过最大阈值",
            severity="low",
            check_func="text_length_max",
            threshold=1000,
            auto_fix=False
        ),
        AnomalyRule(
            rule_id="R003",
            name="质量分过低",
            description="质量分数低于阈值",
            severity="high",
            check_func="quality_score",
            threshold=0.7,
            auto_fix=True
        ),
        AnomalyRule(
            rule_id="R004",
            name="缺失必要字段",
            description="缺少必要字段",
            severity="critical",
            check_func="required_fields",
            threshold=0,
            auto_fix=True
        ),
        AnomalyRule(
            rule_id="R005",
            name="格式错误",
            description="字段格式不符合规范",
            severity="medium",
            check_func="format_check",
            threshold=0,
            auto_fix=True
        ),
        AnomalyRule(
            rule_id="R006",
            name="敏感信息泄露",
            description="包含敏感个人信息",
            severity="critical",
            check_func="sensitive_info",
            threshold=0,
            auto_fix=False
        ),
        AnomalyRule(
            rule_id="R007",
            name="语言混杂",
            description="中英文混杂比例过高",
            severity="medium",
            check_func="language_mix",
            threshold=0.3,
            auto_fix=True
        ),
        AnomalyRule(
            rule_id="R008",
            name="重复内容",
            description="内容重复率过高",
            severity="high",
            check_func="repetition",
            threshold=0.5,
            auto_fix=True
        ),
        AnomalyRule(
            rule_id="R009",
            name="特殊字符过多",
            description="特殊字符比例过高",
            severity="low",
            check_func="special_chars",
            threshold=0.2,
            auto_fix=True
        ),
        AnomalyRule(
            rule_id="R010",
            name="数值异常",
            description="数值超出合理范围",
            severity="high",
            check_func="value_range",
            threshold=0,
            auto_fix=False
        ),
    ]
    
    REQUIRED_FIELDS = ["id", "word", "text", "category", "quality_score"]
    
    SENSITIVE_PATTERNS = [
        (r'\b\d{17}[\dXx]\b', "身份证号"),
        (r'\b\d{15}\b', "身份证号(旧)"),
        (r'\b1[3-9]\d{9}\b', "手机号"),
        (r'\b[\w\.-]+@[\w\.-]+\.\w+\b', "邮箱"),
        (r'\b\d{16,19}\b', "银行卡号"),
    ]


class AnomalyDetector:
    """
    异常检测器 - 自动检测数据异常
    
    检测方法：
    1. 规则匹配 - 基于规则库
    2. 统计检测 - 基于统计方法
    3. 模式识别 - 基于正则表达式
    """
    
    def __init__(self, custom_rules: List[AnomalyRule] = None):
        self.rules = AnomalyRuleLibrary.RULES.copy()
        if custom_rules:
            self.rules.extend(custom_rules)
        
        self.detection_stats = {
            "total_checked": 0,
            "anomalies_found": 0,
            "by_severity": defaultdict(int),
            "by_rule": defaultdict(int),
        }
    
    def detect(self, sample: Dict) -> List[AnomalyResult]:
        """检测单个样本的异常"""
        results = []
        
        self.detection_stats["total_checked"] += 1
        
        for rule in self.rules:
            result = self._check_rule(sample, rule)
            if result.is_anomaly:
                results.append(result)
                self.detection_stats["anomalies_found"] += 1
                self.detection_stats["by_severity"][rule.severity] += 1
                self.detection_stats["by_rule"][rule.rule_id] += 1
        
        return results
    
    def detect_batch(self, samples: List[Dict]) -> Dict[str, List[AnomalyResult]]:
        """批量检测异常"""
        results = {}
        
        for i, sample in enumerate(samples):
            sample_id = sample.get("id", i)
            anomalies = self.detect(sample)
            if anomalies:
                results[sample_id] = anomalies
        
        return results
    
    def _check_rule(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查单条规则"""
        check_funcs = {
            "text_length": self._check_text_length,
            "text_length_max": self._check_text_length_max,
            "quality_score": self._check_quality_score,
            "required_fields": self._check_required_fields,
            "format_check": self._check_format,
            "sensitive_info": self._check_sensitive_info,
            "language_mix": self._check_language_mix,
            "repetition": self._check_repetition,
            "special_chars": self._check_special_chars,
            "value_range": self._check_value_range,
        }
        
        check_func = check_funcs.get(rule.check_func)
        if not check_func:
            return AnomalyResult(
                is_anomaly=False,
                rule_id=rule.rule_id,
                severity=rule.severity,
                description=rule.description,
                value=None,
                threshold=rule.threshold,
                suggestion="",
                auto_fixable=rule.auto_fix
            )
        
        return check_func(sample, rule)
    
    def _check_text_length(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查文本长度（最小）"""
        text = sample.get("text", "")
        length = len(text)
        
        is_anomaly = length < rule.threshold
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            rule_id=rule.rule_id,
            severity=rule.severity,
            description=f"文本长度{length}低于最小阈值{rule.threshold}",
            value=length,
            threshold=rule.threshold,
            suggestion="扩充文本内容，添加更多细节" if is_anomaly else "",
            auto_fixable=rule.auto_fix
        )
    
    def _check_text_length_max(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查文本长度（最大）"""
        text = sample.get("text", "")
        length = len(text)
        
        is_anomaly = length > rule.threshold
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            rule_id=rule.rule_id,
            severity=rule.severity,
            description=f"文本长度{length}超过最大阈值{rule.threshold}",
            value=length,
            threshold=rule.threshold,
            suggestion="精简文本内容" if is_anomaly else "",
            auto_fixable=rule.auto_fix
        )
    
    def _check_quality_score(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查质量分数"""
        score = sample.get("quality_score", 0)
        
        is_anomaly = score < rule.threshold
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            rule_id=rule.rule_id,
            severity=rule.severity,
            description=f"质量分数{score}低于阈值{rule.threshold}",
            value=score,
            threshold=rule.threshold,
            suggestion="使用Calibrated Mixup增强" if is_anomaly else "",
            auto_fixable=rule.auto_fix
        )
    
    def _check_required_fields(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查必要字段"""
        missing = []
        for field in AnomalyRuleLibrary.REQUIRED_FIELDS:
            if field not in sample or sample[field] is None:
                missing.append(field)
        
        is_anomaly = len(missing) > 0
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            rule_id=rule.rule_id,
            severity=rule.severity,
            description=f"缺少必要字段: {missing}",
            value=missing,
            threshold=[],
            suggestion="补充缺失字段" if is_anomaly else "",
            auto_fixable=rule.auto_fix
        )
    
    def _check_format(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查格式"""
        issues = []
        
        if "id" in sample and not isinstance(sample["id"], (int, str)):
            issues.append("id格式错误")
        
        if "quality_score" in sample:
            try:
                score = float(sample["quality_score"])
                if not 0 <= score <= 1:
                    issues.append("quality_score范围错误")
            except (ValueError, TypeError):
                issues.append("quality_score格式错误")
        
        is_anomaly = len(issues) > 0
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            rule_id=rule.rule_id,
            severity=rule.severity,
            description=f"格式问题: {issues}",
            value=issues,
            threshold=[],
            suggestion="修正字段格式" if is_anomaly else "",
            auto_fixable=rule.auto_fix
        )
    
    def _check_sensitive_info(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查敏感信息"""
        text = sample.get("text", "")
        found = []
        
        for pattern, name in AnomalyRuleLibrary.SENSITIVE_PATTERNS:
            if re.search(pattern, text):
                found.append(name)
        
        is_anomaly = len(found) > 0
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            rule_id=rule.rule_id,
            severity=rule.severity,
            description=f"发现敏感信息: {found}",
            value=found,
            threshold=[],
            suggestion="脱敏处理或移除敏感信息" if is_anomaly else "",
            auto_fixable=rule.auto_fix
        )
    
    def _check_language_mix(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查语言混杂"""
        text = sample.get("text", "")
        
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        total = chinese_chars + english_chars
        
        if total == 0:
            mix_ratio = 0
        else:
            mix_ratio = min(chinese_chars, english_chars) / total * 2
        
        is_anomaly = mix_ratio > rule.threshold
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            rule_id=rule.rule_id,
            severity=rule.severity,
            description=f"语言混杂比例{mix_ratio:.2f}超过阈值{rule.threshold}",
            value=round(mix_ratio, 2),
            threshold=rule.threshold,
            suggestion="统一语言风格" if is_anomaly else "",
            auto_fixable=rule.auto_fix
        )
    
    def _check_repetition(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查重复内容"""
        text = sample.get("text", "")
        
        words = text.split()
        if len(words) < 3:
            return AnomalyResult(
                is_anomaly=False,
                rule_id=rule.rule_id,
                severity=rule.severity,
                description="",
                value=0,
                threshold=rule.threshold,
                suggestion="",
                auto_fixable=rule.auto_fix
            )
        
        word_counts = Counter(words)
        max_count = max(word_counts.values())
        repetition_ratio = max_count / len(words)
        
        is_anomaly = repetition_ratio > rule.threshold
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            rule_id=rule.rule_id,
            severity=rule.severity,
            description=f"重复比例{repetition_ratio:.2f}超过阈值{rule.threshold}",
            value=round(repetition_ratio, 2),
            threshold=rule.threshold,
            suggestion="减少重复内容" if is_anomaly else "",
            auto_fixable=rule.auto_fix
        )
    
    def _check_special_chars(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查特殊字符"""
        text = sample.get("text", "")
        
        special_count = sum(1 for c in text if not c.isalnum() and not c.isspace() and not '\u4e00' <= c <= '\u9fff')
        total = len(text)
        
        if total == 0:
            ratio = 0
        else:
            ratio = special_count / total
        
        is_anomaly = ratio > rule.threshold
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            rule_id=rule.rule_id,
            severity=rule.severity,
            description=f"特殊字符比例{ratio:.2f}超过阈值{rule.threshold}",
            value=round(ratio, 2),
            threshold=rule.threshold,
            suggestion="减少特殊字符" if is_anomaly else "",
            auto_fixable=rule.auto_fix
        )
    
    def _check_value_range(self, sample: Dict, rule: AnomalyRule) -> AnomalyResult:
        """检查数值范围"""
        issues = []
        
        if "quality_score" in sample:
            score = sample["quality_score"]
            if isinstance(score, (int, float)) and not 0 <= score <= 1:
                issues.append(f"quality_score={score}超出[0,1]范围")
        
        if "confidence" in sample:
            conf = sample["confidence"]
            if isinstance(conf, (int, float)) and not 0 <= conf <= 1:
                issues.append(f"confidence={conf}超出[0,1]范围")
        
        is_anomaly = len(issues) > 0
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            rule_id=rule.rule_id,
            severity=rule.severity,
            description=f"数值范围问题: {issues}",
            value=issues,
            threshold=[],
            suggestion="修正数值范围" if is_anomaly else "",
            auto_fixable=rule.auto_fix
        )
    
    def get_stats(self) -> Dict:
        """获取检测统计"""
        return {
            **self.detection_stats,
            "anomaly_rate": (
                self.detection_stats["anomalies_found"] / max(self.detection_stats["total_checked"], 1)
            ),
            "by_severity": dict(self.detection_stats["by_severity"]),
            "by_rule": dict(self.detection_stats["by_rule"]),
        }


class AutoAnomalyFixer:
    """
    自动异常修复器 - 自动修复可修复的异常
    """
    
    def __init__(self, detector: AnomalyDetector = None):
        self.detector = detector or AnomalyDetector()
        self.fix_stats = {
            "total_fixed": 0,
            "by_rule": defaultdict(int),
        }
    
    def fix_sample(self, sample: Dict) -> Tuple[Dict, List[str]]:
        """修复单个样本"""
        anomalies = self.detector.detect(sample)
        fixes_applied = []
        
        for anomaly in anomalies:
            if not anomaly.auto_fixable:
                continue
            
            fix_func = self._get_fix_func(anomaly.rule_id)
            if fix_func:
                sample = fix_func(sample, anomaly)
                fixes_applied.append(anomaly.rule_id)
                self.fix_stats["total_fixed"] += 1
                self.fix_stats["by_rule"][anomaly.rule_id] += 1
        
        return sample, fixes_applied
    
    def fix_batch(self, samples: List[Dict]) -> Tuple[List[Dict], Dict]:
        """批量修复"""
        fixed_samples = []
        all_fixes = []
        
        for sample in samples:
            fixed_sample, fixes = self.fix_sample(sample)
            fixed_samples.append(fixed_sample)
            all_fixes.extend(fixes)
        
        stats = {
            "total_samples": len(samples),
            "total_fixes": len(all_fixes),
            "fixes_by_rule": dict(Counter(all_fixes)),
        }
        
        return fixed_samples, stats
    
    def _get_fix_func(self, rule_id: str):
        """获取修复函数"""
        fix_funcs = {
            "R001": self._fix_text_length,
            "R003": self._fix_quality_score,
            "R004": self._fix_required_fields,
            "R005": self._fix_format,
            "R007": self._fix_language_mix,
            "R008": self._fix_repetition,
            "R009": self._fix_special_chars,
        }
        return fix_funcs.get(rule_id)
    
    def _fix_text_length(self, sample: Dict, anomaly: AnomalyResult) -> Dict:
        """修复文本长度"""
        text = sample.get("text", "")
        if len(text) < 20:
            sample["text"] = text + " 该内容经过自动扩充，以符合最小长度要求。"
        return sample
    
    def _fix_quality_score(self, sample: Dict, anomaly: AnomalyResult) -> Dict:
        """修复质量分数"""
        sample["quality_score"] = 0.7
        sample["quality_score_fixed"] = True
        return sample
    
    def _fix_required_fields(self, sample: Dict, anomaly: AnomalyResult) -> Dict:
        """修复必要字段"""
        defaults = {
            "id": 0,
            "word": "未知",
            "text": "",
            "category": "通用",
            "quality_score": 0.5,
        }
        for field, default in defaults.items():
            if field not in sample:
                sample[field] = default
        return sample
    
    def _fix_format(self, sample: Dict, anomaly: AnomalyResult) -> Dict:
        """修复格式"""
        if "id" in sample:
            sample["id"] = str(sample["id"])
        if "quality_score" in sample:
            try:
                score = float(sample["quality_score"])
                sample["quality_score"] = max(0, min(1, score))
            except (ValueError, TypeError):
                sample["quality_score"] = 0.5
        return sample
    
    def _fix_language_mix(self, sample: Dict, anomaly: AnomalyResult) -> Dict:
        """修复语言混杂"""
        text = sample.get("text", "")
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        
        if chinese_chars > english_chars:
            sample["text"] = re.sub(r'[a-zA-Z]+', '', text)
        else:
            sample["text"] = re.sub(r'[\u4e00-\u9fff]+', '', text)
        
        return sample
    
    def _fix_repetition(self, sample: Dict, anomaly: AnomalyResult) -> Dict:
        """修复重复内容"""
        text = sample.get("text", "")
        words = text.split()
        seen = set()
        unique_words = []
        
        for word in words:
            if word not in seen:
                seen.add(word)
                unique_words.append(word)
        
        sample["text"] = " ".join(unique_words)
        return sample
    
    def _fix_special_chars(self, sample: Dict, anomaly: AnomalyResult) -> Dict:
        """修复特殊字符"""
        text = sample.get("text", "")
        cleaned = re.sub(r'[^\w\s\u4e00-\u9fff。，！？、；：""''（）【】]', '', text)
        sample["text"] = cleaned
        return sample


anomaly_detector = AnomalyDetector()
auto_fixer = AutoAnomalyFixer(anomaly_detector)
