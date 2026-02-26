#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量报告模块
支持：质量评分、统计报告、质量建议
"""

import json
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import Counter
import math

@dataclass
class QualityScore:
    overall: float
    completeness: float
    consistency: float
    diversity: float
    validity: float
    readability: float

@dataclass
class QualityReport:
    score: QualityScore
    statistics: Dict
    issues: List[Dict]
    suggestions: List[str]
    grade: str

class DataQualityAnalyzer:
    """数据质量分析器"""
    
    MIN_TEXT_LENGTH = 10
    MAX_TEXT_LENGTH = 10000
    MIN_UNIQUE_RATIO = 0.1
    
    def __init__(self):
        self.issue_weights = {
            "empty_content": 0.3,
            "too_short": 0.15,
            "too_long": 0.05,
            "duplicate": 0.2,
            "invalid_encoding": 0.15,
            "low_diversity": 0.1,
            "format_error": 0.1
        }
    
    def analyze(self, data: List[Dict], text_field: str = "text") -> QualityReport:
        if not data:
            return QualityReport(
                score=QualityScore(0, 0, 0, 0, 0, 0),
                statistics={},
                issues=[{"type": "empty_data", "message": "数据集为空"}],
                suggestions=["请提供数据进行分析"],
                grade="F"
            )
        
        completeness = self._check_completeness(data, text_field)
        consistency = self._check_consistency(data, text_field)
        diversity = self._check_diversity(data, text_field)
        validity = self._check_validity(data, text_field)
        readability = self._check_readability(data, text_field)
        
        issues = self._find_issues(data, text_field)
        issue_penalty = self._calculate_issue_penalty(issues)
        
        overall = (completeness * 0.25 + consistency * 0.2 + diversity * 0.2 + 
                   validity * 0.2 + readability * 0.15) - issue_penalty * 0.2
        overall = max(0.0, min(1.0, overall))
        
        suggestions = self._generate_suggestions(issues, overall)
        statistics = self._generate_statistics(data, text_field)
        grade = self._calculate_grade(overall)
        
        return QualityReport(
            score=QualityScore(
                overall=round(overall, 2),
                completeness=round(completeness, 2),
                consistency=round(consistency, 2),
                diversity=round(diversity, 2),
                validity=round(validity, 2),
                readability=round(readability, 2)
            ),
            statistics=statistics,
            issues=issues,
            suggestions=suggestions,
            grade=grade
        )
    
    def _check_completeness(self, data: List[Dict], text_field: str) -> float:
        if not data:
            return 0.0
        
        total = len(data)
        complete = 0
        
        for item in data:
            if text_field in item and item[text_field]:
                text = str(item[text_field]).strip()
                if len(text) >= self.MIN_TEXT_LENGTH:
                    complete += 1
        
        return complete / total if total > 0 else 0.0
    
    def _check_consistency(self, data: List[Dict], text_field: str) -> float:
        if not data:
            return 0.0
        
        lengths = []
        formats = Counter()
        
        for item in data:
            if text_field in item and item[text_field]:
                text = str(item[text_field])
                lengths.append(len(text))
                
                if re.match(r'^[\u4e00-\u9fff]+', text):
                    formats['chinese'] += 1
                elif re.match(r'^[a-zA-Z]+', text):
                    formats['english'] += 1
                else:
                    formats['mixed'] += 1
        
        if not lengths:
            return 0.0
        
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        cv = std_dev / avg_len if avg_len > 0 else 1
        
        consistency_score = max(0, 1 - cv)
        
        dominant_format_ratio = formats.most_common(1)[0][1] / len(data) if formats and formats.most_common(1) else 0
        format_consistency = dominant_format_ratio
        
        return (consistency_score * 0.6 + format_consistency * 0.4)
    
    def _check_diversity(self, data: List[Dict], text_field: str) -> float:
        if not data:
            return 0.0
        
        texts = [str(item.get(text_field, "")) for item in data]
        unique_texts = set(texts)
        
        unique_ratio = len(unique_texts) / len(texts) if texts else 0
        
        words = []
        for text in texts:
            if len(text) > 10:
                chunk_size = min(10, len(text) // 3)
                for i in range(0, len(text) - chunk_size, chunk_size):
                    words.append(text[i:i+chunk_size])
        
        unique_words = len(set(words))
        total_words = len(words)
        word_diversity = unique_words / total_words if total_words > 0 else 0
        
        return unique_ratio * 0.5 + word_diversity * 0.5
    
    def _check_validity(self, data: List[Dict], text_field: str) -> float:
        if not data:
            return 0.0
        
        valid = 0
        total = len(data)
        
        for item in data:
            is_valid = True
            
            if text_field in item and item[text_field]:
                text = str(item[text_field])
                
                try:
                    text.encode('utf-8')
                except UnicodeDecodeError:
                    is_valid = False
                
                if len(text) > self.MAX_TEXT_LENGTH:
                    is_valid = False
                
                control_chars = sum(1 for c in text if ord(c) < 32 and c not in '\n\r\t')
                if control_chars > len(text) * 0.1:
                    is_valid = False
            
            if is_valid:
                valid += 1
        
        return valid / total if total > 0 else 0.0
    
    def _check_readability(self, data: List[Dict], text_field: str) -> float:
        if not data:
            return 0.0
        
        scores = []
        
        for item in data:
            if text_field not in item or not item[text_field]:
                continue
            
            text = str(item[text_field])
            score = 1.0
            
            if len(text) < 20:
                score -= 0.3
            
            punct_count = sum(1 for c in text if c in '。！？，、；：""''（）【】')
            if punct_count == 0 and len(text) > 50:
                score -= 0.2
            
            if text.isupper() or text.islower():
                score -= 0.1
            
            if len(text) > 0:
                char_variety = len(set(text)) / len(text)
                if char_variety < self.MIN_UNIQUE_RATIO:
                    score -= 0.2
            
            scores.append(max(0, score))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _find_issues(self, data: List[Dict], text_field: str) -> List[Dict]:
        issues = []
        seen_texts = {}
        
        for i, item in enumerate(data):
            if text_field not in item or not item[text_field]:
                issues.append({
                    "type": "empty_content",
                    "index": i,
                    "message": f"第{i+1}条数据内容为空"
                })
                continue
            
            text = str(item[text_field])
            
            if len(text) < self.MIN_TEXT_LENGTH:
                issues.append({
                    "type": "too_short",
                    "index": i,
                    "message": f"第{i+1}条数据过短（{len(text)}字符）"
                })
            
            if len(text) > self.MAX_TEXT_LENGTH:
                issues.append({
                    "type": "too_long",
                    "index": i,
                    "message": f"第{i+1}条数据过长（{len(text)}字符）"
                })
            
            text_hash = hash(text)
            if text_hash in seen_texts:
                issues.append({
                    "type": "duplicate",
                    "index": i,
                    "message": f"第{i+1}条与第{seen_texts[text_hash]+1}条重复"
                })
            else:
                seen_texts[text_hash] = i
        
        return issues[:20]
    
    def _calculate_issue_penalty(self, issues: List[Dict]) -> float:
        if not issues:
            return 0.0
        
        total_penalty = 0.0
        for issue in issues:
            issue_type = issue.get("type", "")
            weight = self.issue_weights.get(issue_type, 0.1)
            total_penalty += weight
        
        return min(1.0, total_penalty / len(issues)) if issues else 0.0
    
    def _generate_suggestions(self, issues: List[Dict], overall_score: float) -> List[str]:
        suggestions = []
        
        issue_types = Counter(issue["type"] for issue in issues)
        
        if issue_types["empty_content"] > 0:
            suggestions.append("建议过滤或填充空内容数据")
        
        if issue_types["too_short"] > 0:
            suggestions.append("建议设置最小文本长度阈值")
        
        if issue_types["duplicate"] > 0:
            suggestions.append("建议进行数据去重处理")
        
        if overall_score < 0.6:
            suggestions.append("数据质量较低，建议进行全面清洗")
        elif overall_score < 0.8:
            suggestions.append("数据质量良好，可进行局部优化")
        else:
            suggestions.append("数据质量优秀，可直接使用")
        
        return suggestions
    
    def _generate_statistics(self, data: List[Dict], text_field: str) -> Dict:
        if not data:
            return {}
        
        lengths = []
        for item in data:
            if text_field in item and item[text_field]:
                lengths.append(len(str(item[text_field])))
        
        if not lengths:
            return {"total_count": len(data)}
        
        return {
            "total_count": len(data),
            "avg_length": round(sum(lengths) / len(lengths), 1),
            "min_length": min(lengths),
            "max_length": max(lengths),
            "median_length": sorted(lengths)[len(lengths) // 2],
            "empty_count": sum(1 for l in lengths if l == 0),
            "short_count": sum(1 for l in lengths if 0 < l < self.MIN_TEXT_LENGTH)
        }
    
    def _calculate_grade(self, score: float) -> str:
        if score >= 0.9:
            return "A+"
        elif score >= 0.85:
            return "A"
        elif score >= 0.8:
            return "A-"
        elif score >= 0.75:
            return "B+"
        elif score >= 0.7:
            return "B"
        elif score >= 0.65:
            return "B-"
        elif score >= 0.6:
            return "C+"
        elif score >= 0.55:
            return "C"
        elif score >= 0.5:
            return "C-"
        elif score >= 0.4:
            return "D"
        else:
            return "F"

quality_analyzer = DataQualityAnalyzer()

def analyze_quality(data: List[Dict], text_field: str = "text") -> QualityReport:
    return quality_analyzer.analyze(data, text_field)

if __name__ == "__main__":
    test_data = [
        {"id": 1, "text": "这是一条测试数据，用于测试数据质量分析功能。"},
        {"id": 2, "text": "人工智能是计算机科学的一个分支，它企图了解智能的实质。"},
        {"id": 3, "text": "短文本"},
        {"id": 4, "text": ""},
        {"id": 5, "text": "机器学习是人工智能的核心，是使计算机具有智能的根本途径。"},
    ]
    
    print("="*60)
    print("数据质量分析测试")
    print("="*60)
    
    report = analyze_quality(test_data)
    
    print(f"\n总体评分: {report.score.overall} ({report.grade})")
    print(f"完整性: {report.score.completeness}")
    print(f"一致性: {report.score.consistency}")
    print(f"多样性: {report.score.diversity}")
    print(f"有效性: {report.score.validity}")
    print(f"可读性: {report.score.readability}")
    
    print(f"\n统计信息: {report.statistics}")
    print(f"\n问题列表: {report.issues}")
    print(f"\n建议: {report.suggestions}")
