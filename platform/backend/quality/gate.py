#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量层 - 质量门控
整合自 filters/quality_gate.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from filters.quality_gate import QualityGateController, QualityLevel, BatchQualityManager
    __all__ = ['QualityGateController', 'QualityLevel', 'BatchQualityManager']
except ImportError:
    from enum import Enum
    
    class QualityLevel(Enum):
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"
        ROBUSTNESS = "robustness"
    
    class QualityGateController:
        """质量门控控制器 - 占位实现"""
        def __init__(self):
            pass
        def classify(self, text):
            return QualityLevel.MEDIUM
    
    class BatchQualityManager:
        """批量质量管理器"""
        pass
    
    __all__ = ['QualityGateController', 'QualityLevel', 'BatchQualityManager']
