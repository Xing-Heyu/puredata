#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - 高质量生成器
整合自 high_quality_generator.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from high_quality_generator import HighQualityGenerator, KnowledgeBase
    __all__ = ['HighQualityGenerator', 'KnowledgeBase']
except ImportError:
    class HighQualityGenerator:
        """高质量生成器 - 占位实现"""
        def __init__(self):
            pass
        def generate_single(self, word, domain, index):
            return None
    
    class KnowledgeBase:
        """知识库"""
        pass
    
    __all__ = ['HighQualityGenerator', 'KnowledgeBase']
