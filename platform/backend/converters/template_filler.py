#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换层 - 模板填充器
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from prompt_manager import PromptTemplateManager
    TemplateFiller = PromptTemplateManager
    __all__ = ['TemplateFiller', 'PromptTemplateManager']
except ImportError:
    from typing import Dict, List, Any
    
    class TemplateFiller:
        """模板填充器 - 占位实现"""
        
        def __init__(self):
            self.templates: Dict[str, str] = {}
        
        def register_template(self, name: str, template: str):
            """注册模板"""
            self.templates[name] = template
        
        def fill(self, name: str, variables: Dict[str, Any]) -> str:
            """填充模板"""
            template = self.templates.get(name, "{text}")
            return template.format(**variables)
        
        def fill_batch(self, name: str, data: List[Dict]) -> List[str]:
            """批量填充"""
            return [self.fill(name, item) for item in data]
    
    PromptTemplateManager = TemplateFiller
    __all__ = ['TemplateFiller', 'PromptTemplateManager']
