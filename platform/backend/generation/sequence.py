#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - 序列生成器
整合自 datagenpro/generators/sequence_generator.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from datagenpro.generators.sequence_generator import SequenceGenerator
    __all__ = ['SequenceGenerator']
except ImportError:
    class SequenceGenerator:
        """序列生成器 - 占位实现"""
        def __init__(self):
            pass
        def generate_sequence(self, length):
            return []
    
    __all__ = ['SequenceGenerator']
