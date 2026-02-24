#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量层 - 异常检测
整合自 filters/anomaly_detector.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from filters.anomaly_detector import AnomalyDetector, AutoAnomalyFixer
    __all__ = ['AnomalyDetector', 'AutoAnomalyFixer']
except ImportError:
    class AnomalyDetector:
        """异常检测器 - 占位实现"""
        def __init__(self):
            pass
        def detect(self, text):
            return []
    
    class AutoAnomalyFixer:
        """自动异常修复器"""
        pass
    
    __all__ = ['AnomalyDetector', 'AutoAnomalyFixer']
