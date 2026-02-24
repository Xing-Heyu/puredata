#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级采样系统 - 学术前沿采样策略
解决伪随机重复问题，实现真随机+多样性保证

参考研究:
- Zipf定律: 自然语言中词频服从幂律分布
- 拒绝采样: 按目标分布采样
- 蓄水池采样: 大规模数据流均匀采样
- 多样性采样: 确保覆盖所有类别
"""

import random
import secrets
import math
import hashlib
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class AdvancedSampler:
    """高级采样器 - 多策略采样系统"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is None:
            seed = secrets.randbits(64)
        self.master_seed = seed
        self.rng = random.Random(seed)
        self.sampling_history = defaultdict(int)
        self.diversity_tracker = set()
    
    def _get_crypto_random(self, max_val: int) -> int:
        return secrets.randbelow(max_val)
    
    def true_random_sample(self, items: List[Any], count: int) -> List[Any]:
        if not items:
            return []
        
        result = []
        for _ in range(count):
            idx = self._get_crypto_random(len(items))
            result.append(items[idx])
        
        return result
    
    def zipf_sample(self, items: List[Any], count: int, alpha: float = 1.5) -> List[Any]:
        if not items:
            return []
        
        n = len(items)
        ranks = list(range(1, n + 1))
        
        weights = [1.0 / (r ** alpha) for r in ranks]
        total = sum(weights)
        weights = [w / total for w in weights]
        
        result = []
        for _ in range(count):
            item = self.rng.choices(items, weights=weights, k=1)[0]
            result.append(item)
        
        return result
    
    def uniform_random_sample(self, items: List[Any], count: int) -> List[Any]:
        if not items:
            return []
        
        return [self.rng.choice(items) for _ in range(count)]
    
    def diversity_aware_sample(self, items: List[Any], count: int, 
                                min_coverage: float = 0.8) -> List[Any]:
        if not items:
            return []
        
        n = len(items)
        coverage_target = int(n * min_coverage)
        
        uncovered = [item for item in items if item not in self.diversity_tracker]
        
        result = []
        
        if uncovered and len(result) < coverage_target:
            needed = min(coverage_target, count // 2)
            sample_size = min(needed, len(uncovered))
            sampled = self.rng.sample(uncovered, sample_size)
            result.extend(sampled)
            for item in sampled:
                self.diversity_tracker.add(item)
        
        remaining = count - len(result)
        if remaining > 0:
            result.extend(self.rng.choices(items, k=remaining))
        
        return result
    
    def rejection_sample(self, items: List[Any], count: int,
                         quality_scores: Dict[Any, float],
                         min_quality: float = 0.5) -> List[Any]:
        if not items or not quality_scores:
            return self.uniform_random_sample(items, count)
        
        max_attempts = count * 10
        result = []
        attempts = 0
        
        while len(result) < count and attempts < max_attempts:
            attempts += 1
            candidate = self.rng.choice(items)
            quality = quality_scores.get(candidate, 0.5)
            
            accept_prob = quality
            
            if self.rng.random() < accept_prob:
                result.append(candidate)
        
        if len(result) < count:
            remaining = count - len(result)
            result.extend(self.rng.choices(items, k=remaining))
        
        return result
    
    def stratified_sample(self, items: List[Any], count: int,
                          strata: Dict[str, List[Any]]) -> List[Any]:
        if not strata:
            return self.uniform_random_sample(items, count)
        
        result = []
        strata_count = len(strata)
        per_stratum = count // strata_count
        remainder = count % strata_count
        
        for i, (stratum_name, stratum_items) in enumerate(strata.items()):
            stratum_count = per_stratum + (1 if i < remainder else 0)
            if stratum_items:
                sampled = self.rng.choices(stratum_items, k=stratum_count)
                result.extend(sampled)
        
        return result
    
    def reservoir_sample(self, items: List[Any], k: int) -> List[Any]:
        if not items:
            return []
        
        if len(items) <= k:
            return list(items)
        
        reservoir = items[:k]
        
        for i in range(k, len(items)):
            j = self.rng.randint(0, i)
            if j < k:
                reservoir[j] = items[i]
        
        return reservoir
    
    def hybrid_sample(self, items: List[Any], count: int,
                      strategy: str = "auto") -> List[Any]:
        if not items:
            return []
        
        if strategy == "auto":
            n = len(items)
            if count > n * 2:
                strategy = "zipf"
            elif count > n:
                strategy = "diversity"
            else:
                strategy = "uniform"
        
        if strategy == "uniform":
            return self.uniform_random_sample(items, count)
        elif strategy == "zipf":
            return self.zipf_sample(items, count)
        elif strategy == "diversity":
            return self.diversity_aware_sample(items, count)
        elif strategy == "true_random":
            return self.true_random_sample(items, count)
        else:
            return self.uniform_random_sample(items, count)
    
    def get_sampling_stats(self) -> Dict[str, Any]:
        return {
            "master_seed": self.master_seed,
            "unique_items_sampled": len(self.diversity_tracker),
            "total_samples": sum(self.sampling_history.values()),
            "distribution": dict(self.sampling_history)
        }
    
    def reset_diversity_tracker(self):
        self.diversity_tracker.clear()
        self.sampling_history.clear()


class TemplateSampler:
    """模板采样器 - 确保模板多样性"""
    
    def __init__(self, templates: Dict[str, List[str]]):
        self.templates = templates
        self.sampler = AdvancedSampler()
        self.usage_count = defaultdict(lambda: defaultdict(int))
    
    def sample_template(self, domain: str, keyword: str) -> Tuple[str, int]:
        if domain not in self.templates:
            domain = list(self.templates.keys())[0]
        
        available = self.templates[domain]
        
        usage = self.usage_count[domain]
        weights = []
        for i, tmpl in enumerate(available):
            count = usage.get(i, 0)
            weight = 1.0 / (count + 1)
            weights.append(weight)
        
        total = sum(weights)
        weights = [w / total for w in weights]
        
        idx = self.sampler.rng.choices(range(len(available)), weights=weights, k=1)[0]
        
        self.usage_count[domain][idx] += 1
        
        return available[idx], idx
    
    def get_template_diversity(self, domain: str) -> float:
        if domain not in self.usage_count:
            return 0.0
        
        usage = self.usage_count[domain]
        if not usage:
            return 0.0
        
        total = sum(usage.values())
        if total == 0:
            return 0.0
        
        unique_templates = len(usage)
        total_templates = len(self.templates.get(domain, []))
        
        return unique_templates / total_templates if total_templates > 0 else 0.0


class KeywordSampler:
    """关键词采样器 - 多策略关键词选择"""
    
    def __init__(self, keywords: Dict[str, List[str]]):
        self.keywords = keywords
        self.sampler = AdvancedSampler()
        self.keyword_history = defaultdict(int)
    
    def sample_keywords(self, domain: str, count: int, 
                        strategy: str = "diversity_zipf") -> List[str]:
        if domain not in self.keywords:
            domain = list(self.keywords.keys())[0]
        
        items = self.keywords[domain]
        
        if strategy == "diversity_zipf":
            return self._diversity_zipf_sample(items, count)
        elif strategy == "true_random":
            return self.sampler.true_random_sample(items, count)
        elif strategy == "zipf":
            return self.sampler.zipf_sample(items, count)
        elif strategy == "uniform":
            return self.sampler.uniform_random_sample(items, count)
        else:
            return self.sampler.hybrid_sample(items, count)
    
    def _diversity_zipf_sample(self, items: List[str], count: int) -> List[str]:
        n = len(items)
        coverage_target = min(n, int(count * 0.6))
        
        uncovered = [item for item in items if self.keyword_history[item] == 0]
        
        result = []
        
        if uncovered:
            sample_size = min(coverage_target, len(uncovered))
            sampled = self.sampler.rng.sample(uncovered, sample_size)
            result.extend(sampled)
            for item in sampled:
                self.keyword_history[item] += 1
        
        remaining = count - len(result)
        if remaining > 0:
            zipf_sampled = self.sampler.zipf_sample(items, remaining)
            result.extend(zipf_sampled)
            for item in zipf_sampled:
                self.keyword_history[item] += 1
        
        return result
    
    def get_keyword_stats(self) -> Dict[str, Any]:
        total = sum(self.keyword_history.values())
        unique = len([k for k, v in self.keyword_history.items() if v > 0])
        
        return {
            "total_samples": total,
            "unique_keywords": unique,
            "coverage": unique / len(self.keyword_history) if self.keyword_history else 0,
            "distribution": dict(sorted(self.keyword_history.items(), key=lambda x: -x[1])[:10])
        }


def create_sampler(keywords: Dict[str, List[str]], 
                   templates: Dict[str, List[str]]) -> Tuple[KeywordSampler, TemplateSampler]:
    keyword_sampler = KeywordSampler(keywords)
    template_sampler = TemplateSampler(templates)
    return keyword_sampler, template_sampler


if __name__ == "__main__":
    print("\n" + "="*70)
    print("高级采样系统测试 - 解决伪随机重复问题")
    print("="*70)
    
    test_keywords = {
        "人工智能": ["AI", "ML", "DL", "NLP", "CV", "RL", "GPT", "BERT", "CNN", "RNN"]
    }
    
    test_templates = {
        "人工智能": [
            "{word} is important.",
            "{word} plays a key role.",
            "Understanding {word} is crucial.",
            "{word} has revolutionized the field.",
            "The concept of {word} is fundamental."
        ]
    }
    
    keyword_sampler, template_sampler = create_sampler(test_keywords, test_templates)
    
    print("\n[1] 对比: 伪随机 vs 真随机")
    print("-"*70)
    
    print("\n伪随机 (确定性循环 - 当前代码的问题):")
    pseudo_result = []
    for i in range(20):
        idx = i % len(test_keywords["人工智能"])
        pseudo_result.append(test_keywords["人工智能"][idx])
    print(f"  结果: {pseudo_result}")
    print(f"  问题: 每次运行都一样，按固定顺序重复")
    
    print("\n真随机 (加密安全随机):")
    true_random = keyword_sampler.sampler.true_random_sample(test_keywords["人工智能"], 20)
    print(f"  结果: {true_random}")
    print(f"  优势: 每次运行不同，真随机分布")
    
    print("\n[2] Zipf定律采样 (模拟真实数据分布)")
    print("-"*70)
    
    zipf_result = keyword_sampler.sampler.zipf_sample(test_keywords["人工智能"], 50)
    from collections import Counter
    freq = Counter(zipf_result)
    print(f"  词频分布: {dict(freq)}")
    print(f"  特点: 常见词出现更频繁，符合自然语言规律")
    
    print("\n[3] 多样性采样 (确保覆盖所有关键词)")
    print("-"*70)
    
    keyword_sampler.keyword_history.clear()
    diversity_result = keyword_sampler.sample_keywords("人工智能", 20, "diversity_zipf")
    stats = keyword_sampler.get_keyword_stats()
    print(f"  采样结果: {diversity_result}")
    print(f"  覆盖率: {stats['coverage']*100:.1f}%")
    print(f"  唯一关键词: {stats['unique_keywords']}/{len(test_keywords['人工智能'])}")
    
    print("\n[4] 采样策略对比")
    print("-"*70)
    
    strategies = ["uniform", "zipf", "diversity_zipf", "true_random"]
    for strategy in strategies:
        keyword_sampler.keyword_history.clear()
        result = keyword_sampler.sample_keywords("人工智能", 30, strategy)
        unique = len(set(result))
        print(f"  {strategy:15s}: 唯一词数={unique:2d}, 覆盖率={unique/len(test_keywords['人工智能'])*100:.0f}%")
    
    print("\n" + "="*70)
    print("结论: 使用 diversity_zipf 策略，既保证多样性又符合真实分布")
    print("="*70)
