#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词模板管理器 - 动态扩展领域模板
支持：预置模板、AI动态生成、智能缓存、空白模板填充
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'prompt_templates.json')
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'template_cache.json')
BLANK_TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'blank_template.json')

class PromptTemplateManager:
    """提示词模板管理器"""
    
    MAX_CACHE_SIZE = 500
    
    def __init__(self):
        self.templates = {}
        self.cache = {}
        self.blank_template = {}
        self.usage_count = defaultdict(int)
        self._load_templates()
        self._load_cache()
        self._load_blank_template()
    
    def _load_blank_template(self):
        """加载空白模板"""
        if os.path.exists(BLANK_TEMPLATE_FILE):
            with open(BLANK_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.blank_template = data.get('blank_template', {})
                self.fill_rules = data.get('fill_rules', {})
        print(f"[模板管理器] 已加载空白模板框架")
    
    def _load_templates(self):
        """加载预置模板"""
        if os.path.exists(TEMPLATE_FILE):
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.templates = data.get('templates', {})
                self.config = data.get('generation_config', {})
        print(f"[模板管理器] 已加载 {len(self.templates)} 个预置模板")
    
    def _load_cache(self):
        """加载缓存模板"""
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
        print(f"[模板管理器] 已加载 {len(self.cache)} 个缓存模板")
    
    def _save_cache(self):
        """保存缓存"""
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def list_templates(self):
        """列出所有可用模板"""
        result = []
        
        for name, template in self.templates.items():
            result.append({
                "name": name,
                "type": "preset",
                "description": template.get("description", ""),
                "behaviors": template.get("behaviors", []),
                "usage_count": self.usage_count.get(name, 0)
            })
        
        for name, template in self.cache.items():
            if name not in self.templates:
                result.append({
                    "name": name,
                    "type": "cached",
                    "description": template.get("description", "AI动态生成"),
                    "behaviors": template.get("behaviors", []),
                    "usage_count": self.usage_count.get(name, 0),
                    "cached_at": template.get("cached_at", "")
                })
        
        return result
    
    def get_template(self, domain):
        """获取模板 - 优先预置，其次缓存"""
        self.usage_count[domain] += 1
        
        if domain in self.templates:
            print(f"[模板管理器] 使用预置模板: {domain}")
            return self.templates[domain]
        
        if domain in self.cache:
            cached = self.cache[domain]
            cached_time = datetime.fromisoformat(cached.get("cached_at", "2000-01-01"))
            ttl_days = self.config.get("cache_ttl_days", 30)
            
            if datetime.now() - cached_time < timedelta(days=ttl_days):
                print(f"[模板管理器] 使用缓存模板: {domain}")
                return cached
            else:
                del self.cache[domain]
        
        return None
    
    def generate_template_with_ai(self, domain, custom_prompt=None):
        """使用AI动态生成模板（模拟）"""
        print(f"[模板管理器] AI动态生成模板: {domain}")
        
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = f"生成{domain}领域的用户行为序列模板"
        
        default_behaviors = ["浏览", "搜索", "选择", "确认", "完成", "评价"]
        
        template = {
            "name": domain,
            "description": f"{domain}领域用户行为序列",
            "prompt": prompt,
            "behaviors": default_behaviors,
            "attributes": ["id", "amount", "rating"],
            "lifecycle": ["新手", "活跃", "稳定", "沉默", "流失"],
            "generated_by": "ai",
            "cached_at": datetime.now().isoformat()
        }
        
        return template
    
    def cache_template(self, domain, template):
        """缓存模板"""
        if len(self.cache) >= self.MAX_CACHE_SIZE:
            oldest_key = min(self.cache.keys(), 
                key=lambda k: self.cache[k].get("cached_at", ""))
            del self.cache[oldest_key]
            print(f"[模板管理器] 缓存已满，移除最旧模板: {oldest_key}")
        
        template["cached_at"] = datetime.now().isoformat()
        self.cache[domain] = template
        self._save_cache()
        print(f"[模板管理器] 已缓存模板: {domain}")
    
    def should_cache(self, domain):
        """判断是否应该缓存"""
        threshold = self.config.get("cache_threshold", 5)
        return self.usage_count[domain] >= threshold
    
    def get_or_generate(self, domain, custom_prompt=None):
        """获取或生成模板 - 智能策略"""
        template = self.get_template(domain)
        
        if template:
            return template
        
        template = self.generate_template_with_ai(domain, custom_prompt)
        
        if self.should_cache(domain):
            self.cache_template(domain, template)
        
        return template
    
    def create_from_prompt(self, domain, behaviors, attributes=None, lifecycle=None):
        """从用户输入创建模板"""
        template = {
            "name": domain,
            "description": f"{domain}领域用户行为序列",
            "prompt": f"生成{domain}用户行为序列，包含：{', '.join(behaviors)}等行为",
            "behaviors": behaviors,
            "attributes": attributes or ["id"],
            "lifecycle": lifecycle or ["新手", "活跃", "稳定", "沉默", "流失"],
            "generated_by": "user",
            "cached_at": datetime.now().isoformat()
        }
        
        self.cache_template(domain, template)
        return template
    
    def fill_blank_template(self, domain, behaviors, transitions=None, time_intervals=None, attributes=None, lifecycle=None):
        """填充空白模板 - 最灵活的方式"""
        import copy
        template = copy.deepcopy(self.blank_template)
        
        template["name"] = domain
        template["description"] = f"{domain}领域用户行为序列"
        template["behaviors"] = behaviors
        template["attributes"] = attributes or []
        template["lifecycle"] = lifecycle or ["新手", "活跃", "稳定", "沉默", "流失"]
        
        if transitions:
            template["transitions"] = transitions
        else:
            template["transitions"] = self._auto_generate_transitions(behaviors)
        
        if time_intervals:
            template["time_intervals"] = time_intervals
        else:
            template["time_intervals"] = self._auto_generate_time_intervals(behaviors)
        
        template["generated_by"] = "blank_fill"
        template["cached_at"] = datetime.now().isoformat()
        
        self.cache_template(domain, template)
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
                transitions[behavior] = {
                    behavior: 0.3,
                    "离开": 0.7
                }
        
        return transitions
    
    def _auto_generate_time_intervals(self, behaviors):
        """自动生成时间间隔"""
        intervals = {}
        
        for i in range(len(behaviors) - 1):
            key = f"({behaviors[i]}, {behaviors[i+1]})"
            intervals[key] = {
                "min_minutes": 1,
                "max_minutes": 1440
            }
        
        return intervals
    
    def quick_create(self, domain, behaviors, **kwargs):
        """快速创建模板 - 一行代码搞定"""
        return self.fill_blank_template(domain, behaviors, **kwargs)
    
    def to_behavior_config(self, template):
        """将模板转换为行为配置"""
        behaviors = template.get("behaviors", [])
        
        transitions = {}
        for i, behavior in enumerate(behaviors):
            if i < len(behaviors) - 1:
                next_behavior = behaviors[i + 1]
                transitions[behavior] = {
                    next_behavior: 0.6,
                    "离开": 0.2,
                    behavior: 0.2
                }
            else:
                transitions[behavior] = {"离开": 0.7, behavior: 0.3}
        
        time_intervals = {}
        for i in range(len(behaviors) - 1):
            time_intervals[(behaviors[i], behaviors[i+1])] = (1, 1440)
        
        return {
            "sequence": behaviors,
            "transitions": transitions,
            "time_intervals": time_intervals,
            "attributes": template.get("attributes", []),
            "lifecycle": template.get("lifecycle", [])
        }

manager = PromptTemplateManager()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("提示词模板管理器 - 测试")
    print("="*50)
    
    print("\n[1] 预置模板列表:")
    for t in manager.list_templates():
        print(f"    - {t['name']} ({t['type']}): {t['description'][:30]}...")
    
    print("\n[2] 空白模板填充 - 最灵活方式:")
    blank = manager.fill_blank_template(
        domain="宠物护理",
        behaviors=["注册", "预约洗澡", "送宠", "服务", "接宠", "评价", "续费"],
        attributes=["pet_type", "service_type", "cost"],
        lifecycle=["新客户", "活跃", "稳定", "沉默", "流失"]
    )
    print(f"    领域: {blank['name']}")
    print(f"    行为: {blank['behaviors']}")
    print(f"    属性: {blank['attributes']}")
    print(f"    生命周期: {blank['lifecycle']}")
    
    print("\n[3] 快速创建 - 一行代码:")
    quick = manager.quick_create("奶茶店", ["进店", "点单", "支付", "取餐", "评价"])
    print(f"    领域: {quick['name']}")
    print(f"    行为: {quick['behaviors']}")
    
    print("\n[4] 自动生成转移概率:")
    config = manager.to_behavior_config(quick)
    print(f"    示例: {list(config['transitions'].items())[0]}")
    
    print("\n[5] 空白模板框架展示:")
    print(f"    模板结构: {list(manager.blank_template.keys())}")
