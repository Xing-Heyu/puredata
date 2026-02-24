#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量层 - 质量流水线
整合自 data_quality_pipeline.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from data_quality_pipeline import DataQualityPipeline, PipelineConfig
    __all__ = ['DataQualityPipeline', 'PipelineConfig']
except ImportError:
    class DataQualityPipeline:
        """数据质量流水线 - 占位实现"""
        def __init__(self):
            pass
        def process(self, data):
            return data
    
    class PipelineConfig:
        """流水线配置"""
        pass
    
    __all__ = ['DataQualityPipeline', 'PipelineConfig']
