#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - Copula分布生成器
整合自 generators/copula_generator.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from generators.copula_generator import CopulaGenerator
    __all__ = ['CopulaGenerator']
except ImportError:
    class CopulaGenerator:
        """Copula分布生成器 - 占位实现"""
        @staticmethod
        def sample_noise_level():
            return "medium"
        
        @staticmethod
        def sample_quality():
            return "medium"
        
        @staticmethod
        def sample_length():
            return 100
    
    __all__ = ['CopulaGenerator']
