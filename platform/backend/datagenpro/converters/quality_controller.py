#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量控制器
"""

import random
from enum import Enum

class QualityLevel(Enum):
    PERFECT = "perfect"
    CLEAN = "clean"
    NORMAL = "normal"
    NOISY = "noisy"
    CHAOTIC = "chaotic"

class QualityController:
    """数据质量控制器"""
    
    CONFIGS = {
        QualityLevel.PERFECT: {"noise": 0, "error": 0, "completeness": 1.0},
        QualityLevel.CLEAN: {"noise": 0.05, "error": 0.01, "completeness": 0.99},
        QualityLevel.NORMAL: {"noise": 0.15, "error": 0.05, "completeness": 0.95},
        QualityLevel.NOISY: {"noise": 0.30, "error": 0.15, "completeness": 0.85},
        QualityLevel.CHAOTIC: {"noise": 0.50, "error": 0.30, "completeness": 0.60}
    }
    
    @staticmethod
    def apply(data, level=QualityLevel.NORMAL):
        """应用质量等级"""
        config = QualityController.CONFIGS.get(level, QualityController.CONFIGS[QualityLevel.NORMAL])
        
        results = []
        for item in data:
            if random.random() > config["completeness"]:
                continue
            
            processed = item.copy()
            
            if random.random() < config["noise"]:
                processed = QualityController._add_noise(processed)
            
            results.append(processed)
        
        return results
    
    @staticmethod
    def _add_noise(item):
        """添加噪声"""
        if "text" in item and len(item["text"]) > 10:
            text = item["text"]
            pos = random.randint(0, len(text) - 1)
            item["text"] = text[:pos] + " " + text[pos+1:]
        return item
