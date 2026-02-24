#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成层 - 模板生成器
整合自 datagenpro/generators/template_generator.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from datagenpro.generators.template_generator import TemplateGenerator
    __all__ = ['TemplateGenerator']
except ImportError:
    class TemplateGenerator:
        """模板生成器 - 占位实现"""
        def __init__(self):
            pass
        def get_template(self, domain):
            return "{word}是{domain}领域的重要概念。"
    
    __all__ = ['TemplateGenerator']
