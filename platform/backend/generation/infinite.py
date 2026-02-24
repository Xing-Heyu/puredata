#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - 无限数据生成器
整合自 infinite_data_generator.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from infinite_data_generator import InfiniteDataGenerator, GenerationConfig
    __all__ = ['InfiniteDataGenerator', 'GenerationConfig']
except ImportError:
    class InfiniteDataGenerator:
        """无限数据生成器 - 占位实现"""
        def __init__(self):
            pass
        def generate(self, domain, count):
            return []
    
    class GenerationConfig:
        """生成配置"""
        pass
    
    __all__ = ['InfiniteDataGenerator', 'GenerationConfig']
