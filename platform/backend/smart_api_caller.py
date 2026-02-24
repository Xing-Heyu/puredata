#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能API调用器 - SmartAPICaller
包装千问API集成，提供统一接口
"""

import os
from typing import Dict, List, Optional, Any


class SmartAPICaller:
    """智能API调用器 - 带成本控制和缓存"""
    
    def __init__(self, api_key: str = None, use_cache: bool = True):
        self.api_key = api_key or os.environ.get('QIANWEN_API_KEY', '') or os.environ.get('DASHSCOPE_API_KEY', '')
        self.use_cache = use_cache
        self._api = None
        self._init_api()
    
    def _init_api(self):
        """初始化API"""
        try:
            from api.llm import QwenAPI, CostConfig
            config = CostConfig(
                cache_enabled=self.use_cache,
                fallback_to_local=True
            )
            self._api = QwenAPI(self.api_key, config)
            self.available = self._api.available
        except ImportError:
            try:
                from 千问API集成 import QwenAPI, CostConfig
                config = CostConfig(
                    cache_enabled=self.use_cache,
                    fallback_to_local=True
                )
                self._api = QwenAPI(self.api_key, config)
                self.available = self._api.available
            except ImportError:
                self._api = None
                self.available = False
    
    def call(self, prompt: str, model: str = "qwen-plus", 
             max_tokens: int = 500, temperature: float = 0.7) -> Dict:
        """调用API"""
        if self._api:
            return self._api.call(prompt, model, max_tokens, temperature, self.use_cache)
        
        return {
            "success": False,
            "response": "",
            "error": "API未初始化",
            "fallback": True
        }
    
    def generate_content(self, keyword: str, domain: str, style: str = "professional") -> str:
        """生成内容"""
        prompt = f"""请用{style}风格，为"{keyword}"这个{domain}领域的概念写一段介绍。
要求：
1. 内容准确、专业
2. 长度200-500字
3. 包含定义、应用场景、注意事项
"""
        result = self.call(prompt, max_tokens=800)
        return result.get("response", "")
    
    def batch_generate(self, keywords: List[str], domain: str) -> List[Dict]:
        """批量生成"""
        results = []
        for kw in keywords:
            content = self.generate_content(kw, domain)
            results.append({
                "keyword": kw,
                "content": content,
                "domain": domain
            })
        return results
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if self._api and hasattr(self._api, 'cost_controller'):
            return self._api.cost_controller.get_report()
        return {"available": self.available}
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        return self.available


smart_api_caller = SmartAPICaller()
