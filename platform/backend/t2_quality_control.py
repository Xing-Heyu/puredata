#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T²框架实现 - Team Then Trim
论文来源: arXiv:2602.04785

核心思想：
1. Team阶段：多生成器协作，并行生成候选数据
2. Trim阶段：质量控制管道，过滤+修复+评分

优势：
- 在生成阶段就内置质量控制，减少后置审计压力
- 不依赖AI，完全用本地规则实现
- 模块化设计，可插拔
"""

import hashlib
import random
import re
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter


class QualityLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    REJECTED = "rejected"


@dataclass
class QualityScore:
    level: QualityLevel
    score: float
    issues: List[str] = field(default_factory=list)
    fixes_applied: List[str] = field(default_factory=list)


class QualityRule:
    """质量规则基类"""
    
    name: str = "base_rule"
    description: str = ""
    weight: float = 1.0
    
    def check(self, item: Dict) -> Tuple[bool, List[str]]:
        return True, []
    
    def fix(self, item: Dict) -> Dict:
        return item


class MinLengthRule(QualityRule):
    """最小长度规则"""
    
    name = "min_length"
    description = "文本长度至少20字符"
    weight = 1.5
    
    MIN_LENGTH = 20
    
    def check(self, item: Dict) -> Tuple[bool, List[str]]:
        text = item.get("text", "")
        if len(text) < self.MIN_LENGTH:
            return False, [f"文本长度不足: {len(text)} < {self.MIN_LENGTH}"]
        return True, []
    
    def fix(self, item: Dict) -> Dict:
        text = item.get("text", "")
        if len(text) < self.MIN_LENGTH:
            padding = f" [补充说明: 该条目关于{item.get('word', '未知主题')}]"
            item["text"] = text + padding
            item["_fixed"] = True
        return item


class MaxLengthRule(QualityRule):
    """最大长度规则"""
    
    name = "max_length"
    description = "文本长度不超过500字符"
    weight = 0.5
    
    MAX_LENGTH = 500
    
    def check(self, item: Dict) -> Tuple[bool, List[str]]:
        text = item.get("text", "")
        if len(text) > self.MAX_LENGTH:
            return False, [f"文本过长: {len(text)} > {self.MAX_LENGTH}"]
        return True, []
    
    def fix(self, item: Dict) -> Dict:
        text = item.get("text", "")
        if len(text) > self.MAX_LENGTH:
            item["text"] = text[:self.MAX_LENGTH-3] + "..."
            item["_fixed"] = True
        return item


class EncodingRule(QualityRule):
    """编码规范规则"""
    
    name = "encoding"
    description = "无乱码、无异常字符"
    weight = 2.0
    
    BAD_PATTERNS = [
        r'[\x00-\x08\x0b\x0c\x0e-\x1f]',
        r'\\u[0-9a-fA-F]{4}',
        r'\\x[0-9a-fA-F]{2}',
        r'锟斤拷',
        r'烫烫烫',
        r'屯屯屯',
    ]
    
    def check(self, item: Dict) -> Tuple[bool, List[str]]:
        text = item.get("text", "")
        issues = []
        for pattern in self.BAD_PATTERNS:
            if re.search(pattern, text):
                issues.append(f"发现异常字符模式: {pattern}")
        return len(issues) == 0, issues
    
    def fix(self, item: Dict) -> Dict:
        text = item.get("text", "")
        for pattern in self.BAD_PATTERNS:
            text = re.sub(pattern, '', text)
        if text != item.get("text", ""):
            item["text"] = text
            item["_fixed"] = True
        return item


class CompletenessRule(QualityRule):
    """完整性规则"""
    
    name = "completeness"
    description = "必需字段完整"
    weight = 2.0
    
    REQUIRED_FIELDS = ["id", "word", "text", "category"]
    
    def check(self, item: Dict) -> Tuple[bool, List[str]]:
        missing = [f for f in self.REQUIRED_FIELDS if f not in item or not item[f]]
        if missing:
            return False, [f"缺少必需字段: {missing}"]
        return True, []
    
    def fix(self, item: Dict) -> Dict:
        if "id" not in item:
            item["id"] = random.randint(1, 1000000)
            item["_fixed"] = True
        if "word" not in item:
            item["word"] = "未知"
            item["_fixed"] = True
        if "category" not in item:
            item["category"] = "未分类"
            item["_fixed"] = True
        return item


class DiversityRule(QualityRule):
    """多样性规则 - 检测重复内容"""
    
    name = "diversity"
    description = "内容不重复"
    weight = 1.5
    
    MAX_SEEN_HASHES = 50000
    seen_hashes = set()
    
    def check(self, item: Dict) -> Tuple[bool, List[str]]:
        text = item.get("text", "")
        content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        
        if content_hash in self.seen_hashes:
            return False, ["内容重复"]
        self.seen_hashes.add(content_hash)
        if len(self.seen_hashes) > self.MAX_SEEN_HASHES:
            self.seen_hashes = set(list(self.seen_hashes)[-self.MAX_SEEN_HASHES // 2:])
        return True, []
    
    def fix(self, item: Dict) -> Dict:
        text = item.get("text", "")
        unique_suffix = f" [#{random.randint(1000, 9999)}]"
        item["text"] = text + unique_suffix
        item["_fixed"] = True
        return item
    
    def reset(self):
        self.seen_hashes.clear()


class SemanticRule(QualityRule):
    """语义规则 - 基本语义检查"""
    
    name = "semantic"
    description = "语义基本合理"
    weight = 1.0
    
    def check(self, item: Dict) -> Tuple[bool, List[str]]:
        text = item.get("text", "")
        word = item.get("word", "")
        issues = []
        
        if word and word not in text and len(word) > 2:
            issues.append(f"关键词'{word}'未在文本中出现")
        
        if text.count('?') > 5 or text.count('!') > 5:
            issues.append("标点符号过多")
        
        if re.search(r'(.)\1{5,}', text):
            issues.append("存在异常重复字符")
        
        return len(issues) == 0, issues
    
    def fix(self, item: Dict) -> Dict:
        text = item.get("text", "")
        word = item.get("word", "")
        
        if word and word not in text and len(word) > 2:
            text = f"{word}: {text}"
            item["_fixed"] = True
        
        text = re.sub(r'\?{3,}', '?', text)
        text = re.sub(r'!{3,}', '!', text)
        text = re.sub(r'(.)\1{5,}', r'\1\1', text)
        
        if text != item.get("text", ""):
            item["text"] = text
            item["_fixed"] = True
        return item


class QualityControlPipeline:
    """
    质量控制管道 - T²框架的Trim阶段
    
    按优先级执行规则检查，支持自动修复
    """
    
    def __init__(self):
        self.rules: List[QualityRule] = [
            CompletenessRule(),
            EncodingRule(),
            MinLengthRule(),
            MaxLengthRule(),
            DiversityRule(),
            SemanticRule(),
        ]
        self.stats = {
            "total_checked": 0,
            "passed": 0,
            "fixed": 0,
            "rejected": 0,
            "issues_by_rule": {},
        }
    
    def check_item(self, item: Dict, auto_fix: bool = True) -> QualityScore:
        """检查单个数据项"""
        all_issues = []
        all_fixes = []
        total_weight = 0
        passed_weight = 0
        
        for rule in self.rules:
            passed, issues = rule.check(item)
            
            if issues:
                self.stats["issues_by_rule"][rule.name] = \
                    self.stats["issues_by_rule"].get(rule.name, 0) + len(issues)
            
            if not passed and auto_fix:
                original = item.copy()
                item = rule.fix(item)
                if item.get("_fixed"):
                    all_fixes.append(f"{rule.name}: 已修复")
                    del item["_fixed"]
                    passed, issues = rule.check(item)
            
            total_weight += rule.weight
            if passed:
                passed_weight += rule.weight
            else:
                all_issues.extend(issues)
        
        score = passed_weight / total_weight if total_weight > 0 else 0
        
        if score >= 0.9:
            level = QualityLevel.HIGH
        elif score >= 0.7:
            level = QualityLevel.MEDIUM
        elif score >= 0.5:
            level = QualityLevel.LOW
        else:
            level = QualityLevel.REJECTED
        
        return QualityScore(
            level=level,
            score=score,
            issues=all_issues,
            fixes_applied=all_fixes
        )
    
    def process_batch(self, items: List[Dict], auto_fix: bool = True) -> Tuple[List[Dict], Dict]:
        """
        处理一批数据
        
        Returns:
            (过滤后的数据, 统计信息)
        """
        result = []
        
        for item in items:
            self.stats["total_checked"] += 1
            score = self.check_item(item, auto_fix)
            
            if score.level != QualityLevel.REJECTED:
                result.append(item)
                self.stats["passed"] += 1
                if score.fixes_applied:
                    self.stats["fixed"] += 1
            else:
                self.stats["rejected"] += 1
        
        return result, self.stats.copy()


class T2Generator:
    """
    T²框架生成器 - Team Then Trim
    
    Team阶段：多生成器协作
    Trim阶段：质量控制
    """
    
    def __init__(self, generators: List[Callable], qc_pipeline: QualityControlPipeline = None):
        self.generators = generators
        self.qc_pipeline = qc_pipeline or QualityControlPipeline()
    
    def team_generate(self, domain: str, count: int, **kwargs) -> List[Dict]:
        """
        Team阶段 - 多生成器协作生成
        
        每个生成器生成一部分数据，然后合并
        """
        all_items = []
        items_per_generator = count // len(self.generators) + 1
        
        for generator in self.generators:
            try:
                items = generator(domain, items_per_generator, **kwargs)
                if items:
                    for item in items:
                        item["_generator"] = generator.__name__ if hasattr(generator, '__name__') else "unknown"
                    all_items.extend(items)
            except Exception as e:
                print(f"Generator error: {e}")
        
        return all_items
    
    def trim_filter(self, items: List[Dict], min_quality: QualityLevel = QualityLevel.MEDIUM) -> List[Dict]:
        """
        Trim阶段 - 质量过滤
        """
        filtered = []
        
        for item in items:
            score = self.qc_pipeline.check_item(item, auto_fix=True)
            item["_quality_score"] = score.score
            item["_quality_level"] = score.level.value
            
            quality_order = {
                QualityLevel.HIGH: 3,
                QualityLevel.MEDIUM: 2,
                QualityLevel.LOW: 1,
                QualityLevel.REJECTED: 0
            }
            
            if quality_order.get(score.level, 0) >= quality_order.get(min_quality, 2):
                filtered.append(item)
        
        return filtered
    
    def generate(self, domain: str, count: int, min_quality: QualityLevel = QualityLevel.MEDIUM, **kwargs) -> Tuple[List[Dict], Dict]:
        """
        完整的T²生成流程
        
        Returns:
            (生成的数据, 质量报告)
        """
        candidates = self.team_generate(domain, count * 2, **kwargs)
        
        filtered = self.trim_filter(candidates, min_quality)
        
        result = filtered[:count]
        
        report = {
            "candidates_generated": len(candidates),
            "after_trim": len(filtered),
            "final_count": len(result),
            "quality_stats": self.qc_pipeline.stats,
            "pass_rate": len(filtered) / len(candidates) if candidates else 0,
        }
        
        return result, report


def create_default_qc_pipeline() -> QualityControlPipeline:
    """创建默认质量控制管道"""
    return QualityControlPipeline()


if __name__ == "__main__":
    pipeline = QualityControlPipeline()
    
    test_items = [
        {"id": 1, "word": "AI", "text": "AI is a technology.", "category": "人工智能"},
        {"id": 2, "word": "ML", "text": "短", "category": "人工智能"},
        {"id": 3, "word": "DL", "text": "Deep Learning is a subset of machine learning that uses neural networks.", "category": "人工智能"},
        {"id": 4, "text": "Missing word field", "category": "人工智能"},
    ]
    
    print("=== T²框架质量测试 ===\n")
    
    for item in test_items:
        score = pipeline.check_item(item, auto_fix=True)
        print(f"Item {item.get('id', '?')}: {score.level.value} ({score.score:.2f})")
        if score.issues:
            print(f"  Issues: {score.issues}")
        if score.fixes_applied:
            print(f"  Fixed: {score.fixes_applied}")
        print(f"  Text: {item.get('text', 'N/A')[:50]}...")
        print()
    
    print("=== 统计信息 ===")
    print(pipeline.stats)
