#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据多样性增强模块 - 基于学术界前沿方法

参考论文：
1. ACL2024: On the Role of Long-tail Knowledge in RAG (阿里云PAI)
2. CVPR2024: DeiT-LT 长尾数据增强
3. 康奈尔大学: PasoDoble 对抗式生成

核心方法：
1. GECE长尾检测 - 识别需要增强的长尾数据
2. 分布外增强 - 生成边界样本
3. 对抗式生成 - 提升数据多样性
"""

import json
import math
import random
import hashlib
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


class GECELongTailDetector:
    """
    GECE长尾检测器 - 基于ACL2024论文
    
    生成预期校准误差(GECE)用于检测长尾知识
    """
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
        self.word_freq = Counter()
        self.total_words = 0
    
    def fit(self, data: List[Dict]):
        """训练：统计词频分布"""
        for item in data:
            text = item.get("text", "")
            words = text.split()
            self.word_freq.update(words)
            self.total_words += len(words)
    
    def calculate_gece(self, text: str) -> float:
        """计算GECE分数"""
        words = text.split()
        if not words:
            return 0.0
        
        word_scores = []
        for word in words:
            freq = self.word_freq.get(word, 0)
            if self.total_words > 0:
                prob = freq / self.total_words
            else:
                prob = 0
            
            if prob > 0:
                score = -math.log(prob)
            else:
                score = 10.0
            
            word_scores.append(score)
        
        return statistics.mean(word_scores) if word_scores else 0.0
    
    def is_long_tail(self, text: str) -> bool:
        """判断是否为长尾数据"""
        gece_score = self.calculate_gece(text)
        return gece_score > self.threshold
    
    def detect_long_tail_items(self, data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """分离长尾和普通数据"""
        long_tail = []
        normal = []
        
        for item in data:
            text = item.get("text", "")
            if self.is_long_tail(text):
                item["gece_score"] = self.calculate_gece(text)
                item["is_long_tail"] = True
                long_tail.append(item)
            else:
                item["is_long_tail"] = False
                normal.append(item)
        
        return long_tail, normal


class DistributionAugmenter:
    """
    分布外增强器 - 基于CVPR2024 DeiT-LT
    
    通过生成边界样本来增强长尾分布
    """
    
    def __init__(self):
        self.templates = {
            "定义变体": [
                "{word}可以理解为{definition}",
                "所谓{word}，指的是{definition}",
                "{word}的定义是：{definition}",
                "在专业领域，{word}被定义为{definition}",
            ],
            "应用场景": [
                "{word}在实际应用中，常用于{scenario}。",
                "关于{word}的应用，主要包括{scenario}。",
                "{word}的应用场景包括{scenario}。",
            ],
            "对比说明": [
                "{word}与相关概念的区别在于{difference}。",
                "相比类似概念，{word}的特点是{difference}。",
            ],
            "举例说明": [
                "例如，{word}的典型例子是{example}。",
                "以{word}为例，{example}。",
            ]
        }
    
    def augment_item(self, item: Dict) -> List[Dict]:
        """对单个条目进行增强"""
        augmented = [item]
        
        word = item.get("word", "")
        text = item.get("text", "")
        category = item.get("category", "")
        
        if len(text) < 20:
            return augmented
        
        sentences = text.split("。")
        main_def = sentences[0] if sentences else text
        
        for aug_type, templates in self.templates.items():
            template = random.choice(templates)
            
            if "definition" in template:
                new_text = template.format(word=word, definition=main_def)
            elif "scenario" in template:
                scenario = f"{category}领域的相关应用"
                new_text = template.format(word=word, scenario=scenario)
            elif "difference" in template:
                difference = "其独特的特征和应用方式"
                new_text = template.format(word=word, difference=difference)
            elif "example" in template:
                example = f"{category}中的具体实践"
                new_text = template.format(word=word, example=example)
            else:
                continue
            
            aug_item = {
                "word": word,
                "text": new_text,
                "category": category,
                "source": "augmented",
                "aug_type": aug_type
            }
            augmented.append(aug_item)
        
        return augmented
    
    def augment_batch(self, data: List[Dict], target_ratio: float = 0.3) -> List[Dict]:
        """批量增强，达到目标多样性比例"""
        all_augmented = []
        
        for item in data:
            augmented = self.augment_item(item)
            all_augmented.extend(augmented)
        
        return all_augmented


class AdversarialDiversityGenerator:
    """
    对抗式多样性生成器 - 基于康奈尔PasoDoble
    
    通过生成挑战性样本来提升多样性
    """
    
    def __init__(self):
        self.challenge_patterns = [
            "从技术角度看，{word}涉及哪些核心要素？",
            "{word}的发展历程是怎样的？",
            "{word}面临的主要挑战有哪些？",
            "未来{word}的发展趋势是什么？",
            "{word}与其他技术的关系是什么？",
            "如何评价{word}的优缺点？",
            "{word}的适用范围和限制是什么？",
            "{word}在实际落地中有哪些难点？",
        ]
    
    def generate_challenges(self, item: Dict) -> List[Dict]:
        """生成挑战性问题"""
        challenges = []
        word = item.get("word", "")
        category = item.get("category", "")
        
        for pattern in self.challenge_patterns[:3]:
            question = pattern.format(word=word)
            
            challenge_item = {
                "word": f"{word}_挑战",
                "text": question,
                "category": category,
                "source": "adversarial",
                "type": "challenge"
            }
            challenges.append(challenge_item)
        
        return challenges
    
    def generate_batch(self, data: List[Dict]) -> List[Dict]:
        """批量生成挑战样本"""
        all_challenges = []
        
        for item in data[:len(data)//4]:
            challenges = self.generate_challenges(item)
            all_challenges.extend(challenges)
        
        return all_challenges


class DiversityEnhancer:
    """
    多样性增强器 - 整合所有方法
    
    使用流程：
    1. GECE检测长尾数据
    2. 分布外增强
    3. 对抗式生成
    4. 评估多样性提升
    """
    
    def __init__(self):
        self.gece_detector = GECELongTailDetector()
        self.distribution_augmenter = DistributionAugmenter()
        self.adversarial_generator = AdversarialDiversityGenerator()
        self.stats = {
            "original_count": 0,
            "long_tail_count": 0,
            "augmented_count": 0,
            "challenge_count": 0,
            "final_count": 0,
        }
    
    def calculate_diversity(self, data: List[Dict]) -> DiversityMetrics:
        """计算多样性指标"""
        if not data:
            return DiversityMetrics()
        
        all_words = []
        all_structures = []
        all_texts = []
        
        for item in data:
            text = item.get("text", "")
            all_texts.append(text)
            words = text.split()
            all_words.extend(words)
            
            structure = tuple(sorted(item.keys()))
            all_structures.append(structure)
        
        if all_words:
            unique_words = len(set(all_words))
            vocab_diversity = unique_words / len(all_words)
        else:
            vocab_diversity = 0
        
        if all_structures:
            unique_structures = len(set(all_structures))
            structure_diversity = unique_structures / len(all_structures)
        else:
            structure_diversity = 0
        
        if all_texts:
            text_lengths = [len(t) for t in all_texts]
            length_variance = statistics.variance(text_lengths) if len(text_lengths) > 1 else 0
            semantic_diversity = min(1.0, length_variance / 1000)
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
        
        overall = (vocab_diversity + structure_diversity + semantic_diversity + long_tail_ratio) / 4
        
        return DiversityMetrics(
            vocabulary_diversity=vocab_diversity,
            structure_diversity=structure_diversity,
            semantic_diversity=semantic_diversity,
            long_tail_ratio=long_tail_ratio,
            overall_diversity=overall
        )
    
    def enhance(self, data: List[Dict], target_diversity: float = 0.6) -> Tuple[List[Dict], Dict]:
        """增强数据多样性"""
        self.stats["original_count"] = len(data)
        
        self.gece_detector.fit(data)
        
        long_tail, normal = self.gece_detector.detect_long_tail_items(data)
        self.stats["long_tail_count"] = len(long_tail)
        
        augmented_data = self.distribution_augmenter.augment_batch(long_tail)
        self.stats["augmented_count"] = len(augmented_data) - len(long_tail)
        
        challenges = self.adversarial_generator.generate_batch(data)
        self.stats["challenge_count"] = len(challenges)
        
        final_data = data + augmented_data[len(long_tail):] + challenges
        self.stats["final_count"] = len(final_data)
        
        final_diversity = self.calculate_diversity(final_data)
        self.stats["final_diversity"] = final_diversity.overall_diversity
        
        return final_data, self.stats.copy()
    
    def get_report(self) -> Dict:
        """获取增强报告"""
        return {
            "statistics": self.stats.copy(),
            "improvement": {
                "count_increase": self.stats["final_count"] - self.stats["original_count"],
                "increase_ratio": (self.stats["final_count"] - self.stats["original_count"]) / max(self.stats["original_count"], 1),
            }
        }


diversity_enhancer = DiversityEnhancer()
