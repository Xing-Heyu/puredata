#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API层 - 千问API集成
整合自 千问API集成.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from 千问API集成 import QwenAPI, CostController, CostConfig, HybridDataGenerator
    __all__ = ['QwenAPI', 'CostController', 'CostConfig', 'HybridDataGenerator']
except ImportError:
    import json
    import hashlib
    import time
    import random
    from typing import Dict, List, Optional, Any
    from datetime import datetime
    from dataclasses import dataclass
    from threading import Lock
    
    try:
        import dashscope
        from dashscope import Generation
        DASHSCOPE_AVAILABLE = True
    except ImportError:
        DASHSCOPE_AVAILABLE = False
    
    @dataclass
    class CostConfig:
        """成本配置"""
        daily_budget: float = 10.0
        monthly_budget: float = 200.0
        price_per_1k_tokens: float = 0.008
        cache_enabled: bool = True
        fallback_to_local: bool = True
    
    class CostController:
        """成本控制器"""
        def __init__(self, config: CostConfig = None):
            self.config = config or CostConfig()
        
        def can_call_api(self, estimated_tokens: int = 500) -> tuple:
            return True, "OK"
        
        def record_usage(self, tokens: int, cost: float):
            pass
    
    class QwenAPI:
        """千问API客户端"""
        
        def __init__(self, api_key: str = None, config: CostConfig = None):
            self.api_key = api_key or os.environ.get('QIANWEN_API_KEY', '')
            self.config = config or CostConfig()
            self.cost_controller = CostController(self.config)
            self.cache = {}
        
        def generate(self, prompt: str, **kwargs) -> str:
            """生成文本"""
            if not DASHSCOPE_AVAILABLE or not self.api_key:
                return self._local_fallback(prompt)
            
            can_call, reason = self.cost_controller.can_call_api()
            if not can_call:
                return self._local_fallback(prompt)
            
            try:
                dashscope.api_key = self.api_key
                response = Generation.call(
                    model=kwargs.get('model', 'qwen-turbo'),
                    prompt=prompt,
                    max_tokens=kwargs.get('max_tokens', 500)
                )
                if response.status_code == 200:
                    return response.output.text
            except Exception as e:
                pass
            
            return self._local_fallback(prompt)
        
        def _local_fallback(self, prompt: str) -> str:
            """本地降级"""
            return f"[本地生成] {prompt[:50]}..."
    
    class HybridDataGenerator:
        """混合数据生成器 - API + 本地"""
        
        def __init__(self, api: QwenAPI = None):
            self.api = api or QwenAPI()
        
        def generate(self, word: str, domain: str, use_api: bool = True) -> str:
            if use_api and self.api.api_key:
                prompt = f"请用一句话介绍{domain}领域的{word}概念。"
                return self.api.generate(prompt)
            return f"{word}是{domain}领域的重要概念。"
    
    __all__ = ['QwenAPI', 'CostController', 'CostConfig', 'HybridDataGenerator']
