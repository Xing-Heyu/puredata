#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域层 - 劳动合同专精
整合自 domain_specialists/labor_specialist.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from domain_specialists.labor_specialist import LaborSpecialist
    __all__ = ['LaborSpecialist']
except ImportError:
    from .base import DomainSpecialist
    
    class LaborSpecialist(DomainSpecialist):
        """劳动合同领域专精 - 占位实现"""
        
        def __init__(self):
            super().__init__()
            self.domain = "劳动合同"
    
    __all__ = ['LaborSpecialist']
