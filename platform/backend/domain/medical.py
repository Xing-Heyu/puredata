#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域层 - 医疗专精
整合自 domain_specialists/medical_specialist.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from domain_specialists.medical_specialist import MedicalSpecialist
    __all__ = ['MedicalSpecialist']
except ImportError:
    from .base import DomainSpecialist
    
    class MedicalSpecialist(DomainSpecialist):
        """医疗领域专精 - 占位实现"""
        
        def __init__(self):
            super().__init__()
            self.domain = "医疗"
    
    __all__ = ['MedicalSpecialist']
