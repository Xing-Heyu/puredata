#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板管理器
"""

import json
import os
from datetime import datetime

class TemplateManager:
    """模板管理器"""
    
    def __init__(self, template_file=None, cache_file=None):
        self.template_file = template_file or "prompt_templates.json"
        self.cache_file = cache_file or "template_cache.json"
        self.templates = {}
        self.cache = {}
        self._load()
    
    def _load(self):
        if os.path.exists(self.template_file):
            with open(self.template_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.templates = data.get('templates', {})
        
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
    
    def get(self, domain):
        if domain in self.templates:
            return self.templates[domain]
        if domain in self.cache:
            return self.cache[domain]
        return None
    
    def create(self, domain, behaviors, attributes=None):
        template = {
            "name": domain,
            "behaviors": behaviors,
            "attributes": attributes or [],
            "created_at": datetime.now().isoformat()
        }
        
        self.cache[domain] = template
        self._save_cache()
        
        return template
    
    def _save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def list(self):
        return {**self.templates, **self.cache}
