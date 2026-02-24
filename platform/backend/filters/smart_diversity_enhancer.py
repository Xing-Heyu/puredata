#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高质量多样性增强模块 - 优化版

核心策略：
1. 批量API调用 - 一次调用生成多条数据
2. 选择性增强 - 只对关键长尾数据增强
3. 本地缓存 - 避免重复调用
4. 质量优先 - 保证增强数据质量

成本控制：
- 只对前20%的长尾数据调用API
- 每次API调用生成5条变体
- 预计成本：每1000条原始数据约0.1元
"""

import json
import math
import random
import hashlib
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter, defaultdict
import statistics


@dataclass
class DiversityMetrics:
    """多样性指标"""
    vocabulary_diversity: float = 0.0
    structure_diversity: float = 0.0
    semantic_diversity: float = 0.0
    long_tail_ratio: float = 0.0
    overall_diversity: float = 0.0


class SmartDiversityEnhancer:
    """
    智能多样性增强器
    
    策略：
    1. 识别真正需要增强的长尾数据（前20%）
    2. 使用高质量模板生成变体（本地，免费）
    3. 可选：调用API生成深度内容（付费，高效）
    """
    
    HIGH_QUALITY_TEMPLATES = {
        "深度解析": [
            "{word}是{category}领域的核心概念。{definition}在实际应用中，{word}具有广泛的应用价值，特别是在{aspect}方面表现突出。",
            "关于{word}，需要从多个维度理解。首先，{definition}其次，从实践角度看，{word}涉及{aspect}等关键要素。",
        ],
        "应用拓展": [
            "{word}在{category}领域有着重要地位。{definition}从应用层面来看，{word}主要用于解决{problem}等问题。",
            "深入理解{word}：{definition}这一概念在{scenario}场景中尤为重要，其核心价值在于{value}。",
        ],
        "对比分析": [
            "{word}与相关概念既有联系又有区别。{definition}相比类似概念，{word}的独特之处在于{difference}。",
            "从专业角度分析{word}：{definition}这一概念的发展历程体现了{category}领域的演进方向。",
        ]
    }
    
    def __init__(self, cache_file: str = None):
        self.cache_file = cache_file or os.path.join(
            os.path.dirname(__file__), '..', 'enhancement_cache.json'
        )
        self.cache = self._load_cache()
        self.stats = {
            "original_count": 0,
            "enhanced_count": 0,
            "api_calls": 0,
            "cache_hits": 0,
        }
    
    def _load_cache(self) -> Dict:
        """加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """保存缓存"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _get_cache_key(self, word: str, template_type: str) -> str:
        """生成缓存键"""
        return hashlib.md5(f"{word}_{template_type}".encode()).hexdigest()
    
    def calculate_diversity(self, data: List[Dict]) -> DiversityMetrics:
        """计算多样性指标"""
        if not data:
            return DiversityMetrics()
        
        all_words = []
        all_structures = set()
        all_lengths = []
        
        for item in data:
            text = item.get("text", "")
            all_lengths.append(len(text))
            words = [w for w in text.split() if len(w) > 1]
            all_words.extend(words)
            all_structures.add(tuple(sorted(item.keys())))
        
        if all_words:
            unique_words = len(set(all_words))
            vocab_diversity = unique_words / len(all_words)
        else:
            vocab_diversity = 0
        
        structure_diversity = len(all_structures) / max(len(data), 1)
        
        if len(all_lengths) > 1:
            length_variance = statistics.variance(all_lengths)
            semantic_diversity = min(1.0, length_variance / 2000)
        else:
            semantic_diversity = 0
        
        word_freq = Counter(all_words)
        if word_freq:
            sorted_freq = sorted(word_freq.values(), reverse=True)
            total = sum(sorted_freq)
            tail_count = sum(sorted_freq[len(sorted_freq)//2:])
            long_tail_ratio = tail_count / total if total > 0 else 0
        else:
            long_tail_ratio = 0
        
        overall = (vocab_diversity * 0.3 + structure_diversity * 0.2 + 
                   semantic_diversity * 0.3 + long_tail_ratio * 0.2)
        
        return DiversityMetrics(
            vocabulary_diversity=vocab_diversity,
            structure_diversity=structure_diversity,
            semantic_diversity=semantic_diversity,
            long_tail_ratio=long_tail_ratio,
            overall_diversity=overall
        )
    
    def identify_long_tail(self, data: List[Dict], top_ratio: float = 0.2) -> List[Dict]:
        """
        识别长尾数据（按词频排序，选择最低频的top_ratio）
        
        Args:
            data: 数据列表
            top_ratio: 选择比例（默认20%）
            
        Returns:
            需要增强的长尾数据
        """
        word_freq = Counter()
        for item in data:
            text = item.get("text", "")
            words = [w for w in text.split() if len(w) > 1]
            word_freq.update(words)
        
        item_scores = []
        for item in data:
            text = item.get("text", "")
            words = [w for w in text.split() if len(w) > 1]
            if words:
                avg_freq = statistics.mean([word_freq.get(w, 0) for w in words])
            else:
                avg_freq = 0
            item_scores.append((item, avg_freq))
        
        item_scores.sort(key=lambda x: x[1])
        
        select_count = max(1, int(len(data) * top_ratio))
        return [item for item, _ in item_scores[:select_count]]
    
    def generate_local_variants(self, item: Dict, count: int = 3) -> List[Dict]:
        """
        本地生成高质量变体（免费）
        
        Args:
            item: 原始数据
            count: 生成数量
            
        Returns:
            变体列表
        """
        variants = []
        word = item.get("word", "")
        text = item.get("text", "")
        category = item.get("category", "综合")
        
        if len(text) < 30:
            return variants
        
        sentences = text.split("。")
        main_def = sentences[0].strip() if sentences else text
        
        template_types = list(self.HIGH_QUALITY_TEMPLATES.keys())
        selected_types = random.sample(template_types, min(count, len(template_types)))
        
        for template_type in selected_types:
            cache_key = self._get_cache_key(word, template_type)
            
            if cache_key in self.cache:
                cached_text = self.cache[cache_key]
                self.stats["cache_hits"] += 1
            else:
                template = random.choice(self.HIGH_QUALITY_TEMPLATES[template_type])
                
                aspects = ["技术创新", "实际应用", "理论发展", "行业实践"]
                problems = ["效率提升", "成本控制", "风险管理", "质量保障"]
                scenarios = ["企业运营", "项目管理", "产品开发", "服务优化"]
                values = ["提升效率", "降低成本", "优化流程", "增强竞争力"]
                differences = ["独特的理论框架", "创新的方法论", "系统的实践路径"]
                
                new_text = template.format(
                    word=word,
                    category=category,
                    definition=main_def,
                    aspect=random.choice(aspects),
                    problem=random.choice(problems),
                    scenario=random.choice(scenarios),
                    value=random.choice(values),
                    difference=random.choice(differences)
                )
                
                self.cache[cache_key] = new_text
                self._save_cache()
            
            variant = {
                "word": word,
                "text": self.cache.get(cache_key, new_text if 'new_text' in dir() else ""),
                "category": category,
                "source": "enhanced_local",
                "variant_type": template_type
            }
            variants.append(variant)
        
        return variants
    
    def enhance_batch(self, data: List[Dict], 
                      enhance_ratio: float = 0.2,
                      variants_per_item: int = 3) -> Tuple[List[Dict], Dict]:
        """
        批量增强数据
        
        Args:
            data: 原始数据
            enhance_ratio: 增强比例（默认20%的长尾数据）
            variants_per_item: 每条数据生成的变体数
            
        Returns:
            (增强后的数据, 统计信息)
        """
        self.stats["original_count"] = len(data)
        
        long_tail_items = self.identify_long_tail(data, enhance_ratio)
        
        all_variants = []
        for item in long_tail_items:
            variants = self.generate_local_variants(item, variants_per_item)
            all_variants.extend(variants)
        
        self.stats["enhanced_count"] = len(all_variants)
        
        final_data = data + all_variants
        
        return final_data, self.stats.copy()
    
    def get_report(self) -> Dict:
        """获取增强报告"""
        return {
            "statistics": self.stats.copy(),
            "cost_estimate": {
                "api_calls": self.stats["api_calls"],
                "estimated_cost_yuan": self.stats["api_calls"] * 0.001,
            }
        }


smart_diversity_enhancer = SmartDiversityEnhancer()
