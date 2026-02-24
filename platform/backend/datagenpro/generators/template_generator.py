#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板生成器
支持：预置模板、空白模板、AI动态生成
"""

import json
import os
from datetime import datetime

class TemplateGenerator:
    """模板生成器"""
    
    def __init__(self, template_dir=None):
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载预置模板"""
        template_file = os.path.join(self.template_dir, 'prompt_templates.json')
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.templates = data.get('templates', {})
    
    def get_template(self, domain):
        """获取模板"""
        return self.templates.get(domain)
    
    def create_from_behaviors(self, domain, behaviors, attributes=None):
        """从行为列表创建模板"""
        template = {
            "name": domain,
            "behaviors": behaviors,
            "attributes": attributes or [],
            "transitions": self._auto_generate_transitions(behaviors),
            "created_at": datetime.now().isoformat()
        }
        return template
    
    def _auto_generate_transitions(self, behaviors):
        """自动生成转移概率"""
        transitions = {}
        n = len(behaviors)
        
        for i, behavior in enumerate(behaviors):
            if i < n - 1:
                next_behavior = behaviors[i + 1]
                transitions[behavior] = {
                    next_behavior: 0.6,
                    behavior: 0.2,
                    "离开": 0.2
                }
            else:
                transitions[behavior] = {"离开": 1.0}
        
        return transitions
    
    def list_templates(self):
        """列出所有模板"""
        return list(self.templates.keys())
