#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模板自动填充器 - 自动调用API生成领域模板
支持：千问API、本地模拟、智能缓存
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime

# 配置
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BACKEND_DIR, 'template_cache.json')
ENV_FILE = os.path.join(BACKEND_DIR, '..', '..', '.trae', 'skills', 'data-cleaner', '.env')

# 加载环境变量
def load_env():
    env_vars = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars

env = load_env()

class AITemplateFiller:
    """AI模板自动填充器"""
    
    def __init__(self, use_api=True):
        self.use_api = use_api
        self.api_key = env.get('QIANWEN_API_KEY', '')
        self.model = env.get('QIANWEN_MODEL', 'qwen-plus')
        self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        self.cache = self._load_cache()
        
        print(f"[AI填充器] 初始化完成")
        print(f"[AI填充器] API模式: {'启用' if self.use_api and self.api_key else '模拟模式'}")
    
    def _load_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def _call_qianwen_api(self, prompt):
        """调用千问API"""
        if not self.api_key:
            print("[AI填充器] 无API Key，使用模拟模式")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "system", "content": "你是一个专业的数据模板生成器，请严格按照JSON格式输出。"},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "result_format": "message"
            }
        }
        
        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('output', {}).get('choices', [{}])[0].get('message', {}).get('content', '')
                
        except urllib.error.HTTPError as e:
            print(f"[AI填充器] API错误: {e.code}")
            return None
        except Exception as e:
            print(f"[AI填充器] API异常: {e}")
            return None
    
    def _simulate_generation(self, domain):
        """模拟生成模板（无API时使用）"""
        domain_lower = domain.lower()
        
        # 领域关键词映射
        domain_keywords = {
            "药": ["购药", "咨询", "下单", "支付", "收货", "使用", "复购", "评价"],
            "餐饮": ["进店", "浏览菜单", "点餐", "支付", "就餐", "评价"],
            "酒店": ["搜索", "浏览", "预订", "支付", "入住", "退房", "评价"],
            "出行": ["搜索", "预订", "支付", "出行", "完成", "评价"],
            "教育": ["注册", "选课", "学习", "作业", "考试", "获证"],
            "健身": ["注册", "预约", "签到", "锻炼", "记录", "续费"],
            "宠物": ["注册", "预约", "送宠", "服务", "接宠", "评价"],
            "美容": ["预约", "到店", "服务", "支付", "评价", "复购"],
        }
        
        # 匹配领域
        behaviors = ["浏览", "选择", "确认", "支付", "完成", "评价"]
        for key, value in domain_keywords.items():
            if key in domain_lower:
                behaviors = value
                break
        
        return {
            "domain": domain,
            "behaviors": behaviors,
            "attributes": ["id", "amount", "rating", "timestamp"],
            "lifecycle": ["新手", "活跃", "稳定", "沉默", "流失"],
            "description": f"{domain}领域用户行为序列"
        }
    
    def generate_template(self, domain, use_cache=True):
        """生成领域模板"""
        if use_cache and domain in self.cache:
            print(f"[AI填充器] 使用缓存: {domain}")
            return self.cache[domain]
        
        prompt = f"""请为"{domain}"领域生成用户行为序列模板。

要求：
1. 生成5-10个核心用户行为（按顺序）
2. 每个行为要有合理的转移概率
3. 添加该领域特有的属性字段
4. 定义用户生命周期阶段

请严格按照以下JSON格式输出：
{{
    "domain": "{domain}",
    "behaviors": ["行为1", "行为2", ...],
    "transitions": {{
        "行为1": {{"行为2": 0.6, "行为3": 0.2, "离开": 0.2}},
        ...
    }},
    "attributes": ["属性1", "属性2", ...],
    "lifecycle": ["阶段1", "阶段2", ...],
    "description": "领域描述"
}}
"""
        
        if self.use_api and self.api_key:
            print(f"[AI填充器] 调用API生成: {domain}")
            result = self._call_qianwen_api(prompt)
            
            if result:
                try:
                    json_start = result.find('{')
                    json_end = result.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        template = json.loads(result[json_start:json_end])
                        template["generated_by"] = "knowledge_base"
                        template["generated_at"] = datetime.now().isoformat()
                        
                        self.cache[domain] = template
                        self._save_cache()
                        
                        print(f"[AI填充器] API生成成功: {domain}")
                        return template
                except json.JSONDecodeError:
                    print(f"[AI填充器] JSON解析失败")
        
        print(f"[AI填充器] 使用模拟生成: {domain}")
        template = self._simulate_generation(domain)
        template["generated_by"] = "simulation"
        template["generated_at"] = datetime.now().isoformat()
        
        self.cache[domain] = template
        self._save_cache()
        
        return template
    
    def batch_generate(self, domains):
        """批量生成模板"""
        results = {}
        for domain in domains:
            print(f"\n{'='*40}")
            print(f"处理领域: {domain}")
            print('='*40)
            
            template = self.generate_template(domain)
            results[domain] = template
            
            print(f"  行为: {template['behaviors']}")
            print(f"  属性: {template['attributes']}")
        
        return results
    
    def list_cached(self):
        """列出已缓存模板"""
        return list(self.cache.keys())


def main():
    print("\n" + "="*60)
    print("AI模板自动填充器")
    print("="*60)
    
    filler = AITemplateFiller(use_api=True)
    
    print("\n[1] 单个领域生成测试:")
    print("-" * 40)
    template = filler.generate_template("药水购买")
    print(f"领域: {template['domain']}")
    print(f"行为: {template['behaviors']}")
    print(f"属性: {template['attributes']}")
    print(f"生命周期: {template['lifecycle']}")
    print(f"生成方式: {template.get('generated_by', 'unknown')}")
    
    print("\n[2] 批量生成测试:")
    print("-" * 40)
    domains = ["奶茶店", "健身房", "宠物医院", "美容美发"]
    results = filler.batch_generate(domains)
    
    print("\n[3] 已缓存模板:")
    print("-" * 40)
    for domain in filler.list_cached():
        print(f"  - {domain}")
    
    print("\n" + "="*60)
    print("完成！模板已保存到 template_cache.json")
    print("="*60)


if __name__ == "__main__":
    main()
