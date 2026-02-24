#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域层 - 金融专精
整合自 domain_specialists/finance_specialist.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from domain_specialists.finance_specialist import FinanceSpecialist
    __all__ = ['FinanceSpecialist']
except ImportError:
    from .base import DomainSpecialist
    
    class FinanceSpecialist(DomainSpecialist):
        """金融领域专精 - 占位实现"""
        
        def __init__(self):
            super().__init__()
            self.domain = "金融"
    
    __all__ = ['FinanceSpecialist']
