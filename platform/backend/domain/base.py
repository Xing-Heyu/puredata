#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域层 - 基类
整合自 domain_specialists/base_specialist.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from domain_specialists.base_specialist import DomainSpecialist
    __all__ = ['DomainSpecialist']
except ImportError:
    from abc import ABC, abstractmethod
    
    class DomainSpecialist(ABC):
        """领域专精基类 - 占位实现"""
        
        def __init__(self):
            self.domain = "通用"
            self.entities = {}
            self.relations = {}
            self.constraints = {}
            self.templates = {}
            self.knowledge = {}
        
        def generate(self, word, **kwargs):
            return f"{word}是{self.domain}领域的重要概念。"
        
        def validate_entity(self, entity):
            return True
        
        def validate_relation(self, relation):
            return True
    
    __all__ = ['DomainSpecialist']
