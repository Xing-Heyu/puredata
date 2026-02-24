#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - 拓扑生成器
整合自 simple_main.py 中的 TopologyGenerator 类
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import simple_main
    TopologyGenerator = simple_main.TopologyGenerator
    __all__ = ['TopologyGenerator']
except ImportError:
    class TopologyGenerator:
        """拓扑生成器 - 占位实现"""
        @staticmethod
        def generate_realistic_entry(word, domain, index, keywords, noise_level="medium", realism="medium"):
            return f"{word}是{domain}领域的重要概念。", "medium"
    
    __all__ = ['TopologyGenerator']
