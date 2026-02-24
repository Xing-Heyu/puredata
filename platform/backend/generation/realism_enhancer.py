#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - 真实感增强器
整合自 generators/realism_enhancer.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from generators.realism_enhancer import RealismEnhancer
    __all__ = ['RealismEnhancer']
except ImportError:
    class RealismEnhancer:
        """真实感增强器 - 占位实现"""
        @staticmethod
        def add_realism(text, domain, level="medium"):
            return text
    
    __all__ = ['RealismEnhancer']
