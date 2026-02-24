#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域层 - AI专精
整合自 domain_specialists/ai_specialist.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from domain_specialists.ai_specialist import AISpecialist
    __all__ = ['AISpecialist']
except ImportError:
    from .base import DomainSpecialist
    
    class AISpecialist(DomainSpecialist):
        """AI领域专精 - 占位实现"""
        
        def __init__(self):
            super().__init__()
            self.domain = "人工智能"
    
    __all__ = ['AISpecialist']
