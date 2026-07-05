#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - 拓扑生成器
"""

import random


class TopologyGenerator:
    """拓扑生成器 - 生成有拓扑关联的数据"""
    
    NOISE_LEVELS = {
        "low": 0.1,
        "medium": 0.2,
        "high": 0.3
    }
    
    @staticmethod
    def add_noise(text, level="medium"):
        """添加噪声"""
        noise_rate = TopologyGenerator.NOISE_LEVELS.get(level, 0.2)
        chars = list(text)
        
        for i in range(len(chars)):
            if random.random() < noise_rate * 0.1:
                if chars[i].isupper():
                    chars[i] = chars[i].lower() if random.random() > 0.5 else chars[i]
                elif chars[i].islower():
                    chars[i] = chars[i].upper() if random.random() > 0.7 else chars[i]
        
        return ''.join(chars)
    
    @staticmethod
    def add_structure_variations(text, domain, index):
        """添加结构变化"""
        structures = [
            text,
            f"【{domain}】{text}",
            f"参考：{text}",
            f"注：{text}",
            f"说明：{text}",
        ]
        return random.choice(structures)
    
    @staticmethod
    def add_context_chain(text, word, domain, related_words):
        """添加上下文链"""
        if random.random() > 0.3 or not related_words:
            return text
        
        related = random.choice(related_words)
        context_additions = [
            f" 这与{related}密切相关。",
            f" 类似概念包括{related}。",
            f" 常与{related}一起讨论。",
            "",
        ]
        return text + random.choice(context_additions)
    
    @staticmethod
    def add_quality_variation(text, quality="medium"):
        """添加质量变化"""
        if quality == "high":
            return text
        
        variations = {
            "low": [
                lambda t: t.lower(),
                lambda t: t + "...",
            ],
            "medium": [
                lambda t: t,
                lambda t: t.strip() + ".",
            ]
        }
        
        funcs = variations.get(quality, variations["medium"])
        return random.choice(funcs)(text)


__all__ = ['TopologyGenerator']
