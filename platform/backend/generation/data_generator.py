#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - 数据生成器
整合自 datagenpro/generators/data_generator.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from datagenpro.generators.data_generator import DataGenerator
    __all__ = ['DataGenerator']
except ImportError:
    class DataGenerator:
        """数据生成器 - 占位实现"""
        def __init__(self):
            pass
        def generate(self, domain, count, quality="standard"):
            return []
    
    __all__ = ['DataGenerator']
