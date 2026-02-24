#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量层 - 去重系统
整合自 filters/deduplication_system.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from filters.deduplication_system import DeduplicationSystem, MinHashDeduplicator
    __all__ = ['DeduplicationSystem', 'MinHashDeduplicator']
except ImportError:
    class DeduplicationSystem:
        """去重系统 - 占位实现"""
        def __init__(self):
            pass
        def is_duplicate(self, text):
            return False
        def add(self, text):
            pass
    
    class MinHashDeduplicator:
        """MinHash去重器"""
        pass
    
    __all__ = ['DeduplicationSystem', 'MinHashDeduplicator']
