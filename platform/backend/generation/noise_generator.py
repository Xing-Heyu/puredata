#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - 噪声生成器
整合自 noise_generator.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from noise_generator import NoiseGenerator
    __all__ = ['NoiseGenerator']
except ImportError:
    class NoiseGenerator:
        """噪声生成器 - 占位实现"""
        def __init__(self):
            pass
        def add_noise(self, text, level="medium"):
            return text
    
    __all__ = ['NoiseGenerator']
