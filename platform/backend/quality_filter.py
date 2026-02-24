#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量过滤器 - QualityFilter
整合专业验证器和质量门控，提供统一的质量检查接口

功能：
1. 文本质量检查
2. 专业内容验证
3. 质量评分
4. 过滤建议
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class QualityCheckResult:
    """质量检查结果"""
    passed: bool
    score: float
    text_length_ok: bool
    has_meaningful_content: bool
    professional_valid: bool
    issues: List[str]
    suggestions: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "score": self.score,
            "text_length_ok": self.text_length_ok,
            "has_meaningful_content": self.has_meaningful_content,
            "professional_valid": self.professional_valid,
            "issues": self.issues,
            "suggestions": self.suggestions
        }


class QualityFilter:
    """质量过滤器"""
    
    MIN_TEXT_LENGTH = 20
    MAX_TEXT_LENGTH = 10000
    
    STOP_WORDS = {
        "的", "是", "在", "了", "和", "与", "或", "等", "及",
        "the", "a", "an", "is", "are", "was", "were", "be", "been"
    }
    
    def __init__(self, min_length: int = None, use_professional_validation: bool = True):
        self.min_length = min_length or self.MIN_TEXT_LENGTH
        self.use_professional_validation = use_professional_validation
        self.stats = {
            "total_checked": 0,
            "passed": 0,
            "failed": 0,
            "avg_score": 0.0
        }
        self._scores = []
        
        if use_professional_validation:
            try:
                from filters.professional_validator import professional_validator
                self.validator = professional_validator
            except ImportError:
                self.validator = None
        else:
            self.validator = None
    
    def check(self, text: str, domain: str = None) -> QualityCheckResult:
        """
        检查文本质量
        
        Args:
            text: 待检查文本
            domain: 领域（用于专业验证）
            
        Returns:
            QualityCheckResult: 检查结果
        """
        self.stats["total_checked"] += 1
        
        issues = []
        suggestions = []
        score = 1.0
        
        text_length_ok = len(text) >= self.min_length
        if not text_length_ok:
            issues.append(f"文本长度不足（{len(text)} < {self.min_length}）")
            suggestions.append("增加内容长度")
            score *= 0.5
        
        has_meaningful_content = self._check_meaningful_content(text)
        if not has_meaningful_content:
            issues.append("内容缺乏实质性信息")
            suggestions.append("添加更多实质性内容")
            score *= 0.6
        
        professional_valid = True
        if self.validator and domain:
            try:
                result = self.validator.validate(text, domain)
                professional_valid = result.is_valid
                if not professional_valid:
                    issues.extend([e.get("message", str(e)) for e in result.errors[:3]])
                    suggestions.append("修正专业内容错误")
                    score *= 0.7
            except Exception as e:
                pass
        
        if self._has_repetition(text):
            issues.append("存在重复内容")
            suggestions.append("减少重复表述")
            score *= 0.8
        
        if self._has_formatting_issues(text):
            issues.append("格式问题")
            suggestions.append("修正格式")
            score *= 0.9
        
        passed = len(issues) == 0 and score >= 0.6
        
        if passed:
            self.stats["passed"] += 1
        else:
            self.stats["failed"] += 1
        
        self._scores.append(score)
        self.stats["avg_score"] = sum(self._scores) / len(self._scores)
        
        return QualityCheckResult(
            passed=passed,
            score=round(score, 3),
            text_length_ok=text_length_ok,
            has_meaningful_content=has_meaningful_content,
            professional_valid=professional_valid,
            issues=issues,
            suggestions=suggestions
        )
    
    def _check_meaningful_content(self, text: str) -> bool:
        """检查是否有实质性内容"""
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text)
        meaningful_words = [w for w in words if w.lower() not in self.STOP_WORDS and len(w) > 1]
        return len(meaningful_words) >= 3
    
    def _has_repetition(self, text: str) -> bool:
        """检查是否有重复内容"""
        for length in range(10, min(50, len(text) // 2)):
            for i in range(len(text) - length * 2):
                segment = text[i:i+length]
                if text.count(segment) > 2:
                    return True
        return False
    
    def _has_formatting_issues(self, text: str) -> bool:
        """检查格式问题"""
        if text.count('。') > 50:
            return True
        if text.count('，') > 100:
            return True
        if '...' in text * 3:
            return True
        return False
    
    def filter_batch(self, items: List[Dict], domain: str = None) -> Tuple[List[Dict], List[Dict]]:
        """批量过滤"""
        passed = []
        failed = []
        
        for item in items:
            text = item.get("text", item.get("content", ""))
            result = self.check(text, domain)
            
            if result.passed:
                item["quality_check"] = result.to_dict()
                passed.append(item)
            else:
                item["quality_check"] = result.to_dict()
                failed.append(item)
        
        return passed, failed
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.stats["total_checked"]
        return {
            "total_checked": total,
            "passed": self.stats["passed"],
            "failed": self.stats["failed"],
            "pass_rate": round(self.stats["passed"] / max(total, 1), 3),
            "avg_score": round(self.stats["avg_score"], 3)
        }
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            "total_checked": 0,
            "passed": 0,
            "failed": 0,
            "avg_score": 0.0
        }
        self._scores = []


quality_filter = QualityFilter()
