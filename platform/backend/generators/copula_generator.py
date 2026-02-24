#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成器模块 - Copula分布生成器
"""

import random
import math


class CopulaGenerator:
    """Copula分布生成器 - 控制文本长度和质量分布"""
    
    LENGTH_PARAMS = {
        "min": 20,
        "max": 200,
        "mode": 60,
        "std": 30
    }
    
    QUALITY_PARAMS = {
        "high": 0.3,
        "medium": 0.5,
        "low": 0.2
    }
    
    NOISE_LEVELS = {
        "low": 0.1,
        "medium": 0.2,
        "high": 0.3
    }
    
    @staticmethod
    def sample_length():
        """采样目标长度"""
        params = CopulaGenerator.LENGTH_PARAMS
        length = random.gauss(params["mode"], params["std"])
        return max(params["min"], min(params["max"], int(length)))
    
    @staticmethod
    def sample_quality():
        """采样质量等级"""
        r = random.random()
        if r < CopulaGenerator.QUALITY_PARAMS["high"]:
            return "high"
        elif r < CopulaGenerator.QUALITY_PARAMS["high"] + CopulaGenerator.QUALITY_PARAMS["medium"]:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def sample_noise_level():
        """采样噪声级别"""
        return random.choices(
            ["low", "medium", "high"],
            weights=[0.3, 0.5, 0.2]
        )[0]
    
    @staticmethod
    def adjust_text_length(text, target_length):
        """调整文本长度"""
        current_length = len(text)
        
        if current_length >= target_length:
            return text[:target_length]
        
        padding = " " * (target_length - current_length)
        return text + padding
