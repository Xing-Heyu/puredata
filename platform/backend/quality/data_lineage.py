#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量层 - 数据血缘
整合自 filters/data_lineage.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from filters.data_lineage import DataLineage, LineageAwareGenerator
    __all__ = ['DataLineage', 'LineageAwareGenerator']
except ImportError:
    class DataLineage:
        """数据血缘 - 占位实现"""
        @staticmethod
        def create_lineage(seed_source, transformations, quality_checks):
            return {
                "seed_source": seed_source,
                "transformations": transformations,
                "quality_checks": quality_checks
            }
    
    class LineageAwareGenerator:
        """血缘感知生成器"""
        pass
    
    __all__ = ['DataLineage', 'LineageAwareGenerator']
