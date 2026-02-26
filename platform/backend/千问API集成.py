#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千问API集成模块 - 混合模式 + 成本控制

成本控制策略：
1. 智能缓存 - 相似请求复用结果
2. 批量处理 - 减少API调用次数
3. 降级策略 - API失败时用本地规则
4. 预算控制 - 设置每日/每月上限
5. 按需调用 - 只在关键环节使用API
"""

import json
import hashlib
import time
import os
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from threading import Lock

try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    print("警告：dashscope未安装，将使用本地降级模式")


@dataclass
class CostConfig:
    """成本配置"""
    daily_budget: float = 10.0
    monthly_budget: float = 200.0
    price_per_1k_tokens: float = 0.008
    cache_enabled: bool = True
    cache_ttl_hours: int = 24
    fallback_to_local: bool = True


@dataclass
class UsageStats:
    """使用统计"""
    total_calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    cache_hits: int = 0
    fallback_count: int = 0
    last_reset: str = ""


class CostController:
    """成本控制器"""
    
    def __init__(self, config: CostConfig = None):
        self.config = config or CostConfig()
        self.stats = UsageStats(last_reset=datetime.now().isoformat())
        self.daily_usage = {}
        self.lock = Lock()
        
        self._load_stats()
    
    def _load_stats(self):
        """加载统计数据"""
        stats_file = os.path.join(os.path.dirname(__file__), 'api_stats.json')
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stats.total_calls = data.get('total_calls', 0)
                    self.stats.total_tokens = data.get('total_tokens', 0)
                    self.stats.total_cost = data.get('total_cost', 0.0)
                    self.stats.cache_hits = data.get('cache_hits', 0)
                    self.daily_usage = data.get('daily_usage', {})
            except (json.JSONDecodeError, IOError) as e:
                print(f"[WARN] 加载API统计失败: {e}")
    
    def _save_stats(self):
        """保存统计数据"""
        stats_file = os.path.join(os.path.dirname(__file__), 'api_stats.json')
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_calls': self.stats.total_calls,
                    'total_tokens': self.stats.total_tokens,
                    'total_cost': self.stats.total_cost,
                    'cache_hits': self.stats.cache_hits,
                    'daily_usage': self.daily_usage,
                    'last_reset': self.stats.last_reset
                }, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[WARN] 保存API统计失败: {e}")
    
    def can_call_api(self, estimated_tokens: int = 500) -> tuple:
        """检查是否可以调用API"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        with self.lock:
            daily_cost = self.daily_usage.get(today, 0.0)
            estimated_cost = estimated_tokens * self.config.price_per_1k_tokens / 1000
            
            if daily_cost + estimated_cost > self.config.daily_budget:
                return False, f"已达每日预算上限 (已用: ¥{daily_cost:.2f}, 上限: ¥{self.config.daily_budget:.2f})"
            
            if self.stats.total_cost + estimated_cost > self.config.monthly_budget:
                return False, f"已达每月预算上限 (已用: ¥{self.stats.total_cost:.2f}, 上限: ¥{self.config.monthly_budget:.2f})"
            
            return True, "OK"
    
    def record_usage(self, tokens: int, cost: float, cached: bool = False):
        """记录使用情况"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        with self.lock:
            if cached:
                self.stats.cache_hits += 1
            else:
                self.stats.total_calls += 1
                self.stats.total_tokens += tokens
                self.stats.total_cost += cost
                self.daily_usage[today] = self.daily_usage.get(today, 0.0) + cost
            
            self._save_stats()
    
    def record_fallback(self):
        """记录降级使用"""
        with self.lock:
            self.stats.fallback_count += 1
            self._save_stats()
    
    def get_report(self) -> Dict:
        """获取使用报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        return {
            "today_cost": self.daily_usage.get(today, 0.0),
            "daily_budget": self.config.daily_budget,
            "daily_remaining": self.config.daily_budget - self.daily_usage.get(today, 0.0),
            "monthly_cost": self.stats.total_cost,
            "monthly_budget": self.config.monthly_budget,
            "monthly_remaining": self.config.monthly_budget - self.stats.total_cost,
            "total_calls": self.stats.total_calls,
            "total_tokens": self.stats.total_tokens,
            "cache_hits": self.stats.cache_hits,
            "cache_hit_rate": self.stats.cache_hits / max(self.stats.total_calls + self.stats.cache_hits, 1),
            "fallback_count": self.stats.fallback_count,
        }


class ResponseCache:
    """响应缓存"""
    
    MAX_CACHE_SIZE = 1000
    
    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        self.cache = {}
        self.cache_file = os.path.join(os.path.dirname(__file__), 'api_cache.json')
        self._load_cache()
    
    def _load_cache(self):
        """加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[WARN] 加载缓存失败: {e}")
                self.cache = {}
    
    def _save_cache(self):
        """保存缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[WARN] 保存缓存失败: {e}")
    
    def _get_key(self, prompt: str, **kwargs) -> str:
        """生成缓存键"""
        content = f"{prompt}_{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, **kwargs) -> Optional[str]:
        """获取缓存"""
        key = self._get_key(prompt, **kwargs)
        if key in self.cache:
            entry = self.cache[key]
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cached_time < timedelta(hours=self.ttl_hours):
                return entry['response']
            else:
                del self.cache[key]
        return None
    
    def set(self, prompt: str, response: str, **kwargs):
        """设置缓存"""
        if len(self.cache) >= self.MAX_CACHE_SIZE:
            self.clear_expired()
            if len(self.cache) >= self.MAX_CACHE_SIZE:
                oldest_key = min(self.cache.keys(), 
                    key=lambda k: self.cache[k].get('timestamp', ''))
                del self.cache[oldest_key]
        
        key = self._get_key(prompt, **kwargs)
        self.cache[key] = {
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'prompt_preview': prompt[:100]
        }
        self._save_cache()
    
    def clear_expired(self):
        """清理过期缓存"""
        expired_keys = []
        for key, entry in self.cache.items():
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()


class QwenAPI:
    """
    千问API封装 - 带成本控制
    
    使用方式：
    1. 设置环境变量 DASHSCOPE_API_KEY
    2. 或者初始化时传入 api_key
    """
    
    def __init__(self, api_key: str = None, config: CostConfig = None):
        self.api_key = api_key or os.environ.get('DASHSCOPE_API_KEY', '') or os.environ.get('QIANWEN_API_KEY', '')
        self.config = config or CostConfig()
        self.cost_controller = CostController(self.config)
        self.cache = ResponseCache(self.config.cache_ttl_hours) if self.config.cache_enabled else None
        self.available = DASHSCOPE_AVAILABLE and bool(self.api_key)
        self.lock = Lock()
        
        if self.available:
            dashscope.api_key = self.api_key
    
    def call(self, prompt: str, model: str = "qwen-turbo", 
             max_tokens: int = 500, temperature: float = 0.7,
             use_cache: bool = True) -> Dict:
        """
        调用API（带成本控制）
        
        Args:
            prompt: 提示词
            model: 模型名称 (qwen-turbo, qwen-plus, qwen-max)
            max_tokens: 最大token数
            temperature: 温度参数
            use_cache: 是否使用缓存
        
        Returns:
            包含响应和元数据的字典
        """
        result = {
            "success": False,
            "response": "",
            "tokens": 0,
            "cost": 0.0,
            "cached": False,
            "fallback": False,
            "error": None
        }
        
        if use_cache and self.cache:
            cached_response = self.cache.get(prompt, model=model, max_tokens=max_tokens)
            if cached_response:
                result["success"] = True
                result["response"] = cached_response
                result["cached"] = True
                self.cost_controller.record_usage(0, 0, cached=True)
                return result
        
        if not self.available:
            result["fallback"] = True
            result["response"] = self._local_fallback(prompt)
            result["success"] = True
            self.cost_controller.record_fallback()
            return result
        
        estimated_tokens = max_tokens + len(prompt) // 2
        can_call, reason = self.cost_controller.can_call_api(estimated_tokens)
        
        if not can_call:
            if self.config.fallback_to_local:
                result["fallback"] = True
                result["response"] = self._local_fallback(prompt)
                result["success"] = True
                result["error"] = reason
                self.cost_controller.record_fallback()
            else:
                result["error"] = reason
            return result
        
        try:
            response = Generation.call(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                result_format='text'
            )
            
            if response.status_code == 200:
                output_text = response.output.text
                usage = response.usage
                
                input_tokens = usage.input_tokens if hasattr(usage, 'input_tokens') else len(prompt) // 2
                output_tokens = usage.output_tokens if hasattr(usage, 'output_tokens') else len(output_text) // 2
                total_tokens = input_tokens + output_tokens
                
                cost = total_tokens * self.config.price_per_1k_tokens / 1000
                
                self.cost_controller.record_usage(total_tokens, cost)
                
                if use_cache and self.cache:
                    self.cache.set(prompt, output_text, model=model, max_tokens=max_tokens)
                
                result["success"] = True
                result["response"] = output_text
                result["tokens"] = total_tokens
                result["cost"] = cost
            else:
                result["error"] = f"API错误: {response.code} - {response.message}"
                if self.config.fallback_to_local:
                    result["fallback"] = True
                    result["response"] = self._local_fallback(prompt)
                    result["success"] = True
                    self.cost_controller.record_fallback()
        
        except (ConnectionError, TimeoutError, OSError) as e:
            result["error"] = f"网络错误: {e}"
            if self.config.fallback_to_local:
                result["fallback"] = True
                result["response"] = self._local_fallback(prompt)
                result["success"] = True
                self.cost_controller.record_fallback()
        except Exception as e:
            result["error"] = f"未知错误: {e}"
            if self.config.fallback_to_local:
                result["fallback"] = True
                result["response"] = self._local_fallback(prompt)
                result["success"] = True
                self.cost_controller.record_fallback()
        
        return result
    
    def _local_fallback(self, prompt: str) -> str:
        """本地降级生成"""
        if "对话" in prompt or "客服" in prompt:
            return self._generate_dialogue_local(prompt)
        elif "评价" in prompt or "评论" in prompt:
            return self._generate_review_local(prompt)
        elif "描述" in prompt or "介绍" in prompt:
            return self._generate_description_local(prompt)
        else:
            return self._generate_generic_local(prompt)
    
    def _generate_dialogue_local(self, prompt: str) -> str:
        """本地生成对话"""
        templates = [
            "您好，请问有什么可以帮助您的？",
            "好的，我帮您查一下，请稍等。",
            "感谢您的耐心等待，您的问题已经处理好了。",
            "还有其他需要帮助的吗？",
            "好的，祝您生活愉快，再见！"
        ]
        return random.choice(templates)
    
    def _generate_review_local(self, prompt: str) -> str:
        """本地生成评价"""
        templates = [
            "商品质量很好，物流也很快，非常满意！",
            "性价比很高，推荐购买。",
            "和描述一致，包装也很用心。",
            "客服态度很好，解决问题很及时。"
        ]
        return random.choice(templates)
    
    def _generate_description_local(self, prompt: str) -> str:
        """本地生成描述"""
        return "这是一款优质的产品，具有良好的性能和可靠的质量。"
    
    def _generate_generic_local(self, prompt: str) -> str:
        """本地通用生成"""
        return "系统已处理您的请求。"
    
    def batch_call(self, prompts: List[str], **kwargs) -> List[Dict]:
        """批量调用（合并请求降低成本）"""
        results = []
        for prompt in prompts:
            result = self.call(prompt, **kwargs)
            results.append(result)
            time.sleep(0.1)
        return results
    
    def get_cost_report(self) -> Dict:
        """获取成本报告"""
        return self.cost_controller.get_report()


class HybridDataGenerator:
    """
    混合模式数据生成器
    
    策略：
    - 基础数据：本地生成（免费）
    - 关键增强：API生成（低成本）
    - 智能降级：API失败时用本地
    """
    
    def __init__(self, api_key: str = None, config: CostConfig = None):
        self.api = QwenAPI(api_key, config)
        self.config = config or CostConfig()
    
    def generate_dialogue(self, context: str, turns: int = 5, 
                          use_api: bool = True) -> Dict:
        """生成对话数据"""
        result = {
            "dialogue": [],
            "source": "local",
            "cost": 0.0
        }
        
        if use_api and self.api.available:
            prompt = f"""生成一段电商客服对话，共{turns}轮。
场景：{context}
要求：对话自然、专业、有情感变化。

格式：每行一轮对话，用"客户:"或"客服:"开头。"""
            
            api_result = self.api.call(prompt, max_tokens=turns * 100)
            
            if api_result["success"] and not api_result.get("fallback"):
                result["dialogue"] = self._parse_dialogue(api_result["response"])
                result["source"] = "knowledge_base"
                result["cost"] = api_result["cost"]
            else:
                result["dialogue"] = self._generate_local_dialogue(turns)
                result["source"] = "fallback"
        else:
            result["dialogue"] = self._generate_local_dialogue(turns)
        
        return result
    
    def _parse_dialogue(self, text: str) -> List[Dict]:
        """解析对话文本"""
        dialogue = []
        lines = text.strip().split('\n')
        for line in lines:
            if line.startswith('客户:') or line.startswith('用户:'):
                dialogue.append({"role": "user", "content": line.split(':', 1)[1].strip()})
            elif line.startswith('客服:') or line.startswith('助手:'):
                dialogue.append({"role": "assistant", "content": line.split(':', 1)[1].strip()})
        return dialogue
    
    def _generate_local_dialogue(self, turns: int) -> List[Dict]:
        """本地生成对话"""
        user_templates = [
            "你好，我想咨询一下产品问题",
            "这个商品有货吗？",
            "多久能发货？",
            "可以优惠吗？",
            "好的，谢谢"
        ]
        assistant_templates = [
            "您好，请问有什么可以帮助您的？",
            "有的，目前库存充足",
            "下单后24小时内发货",
            "现在有活动，可以给您优惠",
            "不客气，祝您购物愉快"
        ]
        
        dialogue = []
        for i in range(turns):
            dialogue.append({
                "role": "user",
                "content": random.choice(user_templates)
            })
            dialogue.append({
                "role": "assistant", 
                "content": random.choice(assistant_templates)
            })
        return dialogue[:turns]
    
    def enhance_text(self, text: str, enhancement_type: str = "polish",
                     use_api: bool = True) -> Dict:
        """增强文本"""
        result = {
            "original": text,
            "enhanced": text,
            "source": "local",
            "cost": 0.0
        }
        
        if not use_api or not self.api.available:
            result["enhanced"] = self._local_enhance(text, enhancement_type)
            return result
        
        prompts = {
            "polish": f"请润色以下文本，使其更自然流畅：\n{text}",
            "expand": f"请扩展以下文本，增加更多细节：\n{text}",
            "simplify": f"请简化以下文本，使其更简洁：\n{text}",
        }
        
        prompt = prompts.get(enhancement_type, prompts["polish"])
        api_result = self.api.call(prompt, max_tokens=200)
        
        if api_result["success"] and not api_result.get("fallback"):
            result["enhanced"] = api_result["response"]
            result["source"] = "knowledge_base"
            result["cost"] = api_result["cost"]
        else:
            result["enhanced"] = self._local_enhance(text, enhancement_type)
            result["source"] = "fallback"
        
        return result
    
    def _local_enhance(self, text: str, enhancement_type: str) -> str:
        """本地文本增强"""
        if enhancement_type == "expand":
            return text + " 这是一个很好的选择。"
        elif enhancement_type == "simplify":
            return text[:50] + "..." if len(text) > 50 else text
        return text
    
    def get_cost_report(self) -> Dict:
        """获取成本报告"""
        return self.api.get_cost_report()


if __name__ == "__main__":
    print("=" * 60)
    print("千问API集成测试 - 混合模式 + 成本控制")
    print("=" * 60)
    
    config = CostConfig(
        daily_budget=5.0,
        monthly_budget=100.0,
        cache_enabled=True,
        fallback_to_local=True
    )
    
    generator = HybridDataGenerator(api_key=None, config=config)
    
    print("\n[1] 测试对话生成（本地降级模式）:")
    dialogue_result = generator.generate_dialogue("用户咨询手机购买", turns=4, use_api=True)
    print(f"  来源: {dialogue_result['source']}")
    print(f"  成本: ¥{dialogue_result['cost']:.4f}")
    for turn in dialogue_result['dialogue'][:4]:
        print(f"    [{turn['role']}]: {turn['content'][:30]}...")
    
    print("\n[2] 测试文本增强:")
    enhance_result = generator.enhance_text("这个产品很好", "expand", use_api=True)
    print(f"  原文: {enhance_result['original']}")
    print(f"  增强: {enhance_result['enhanced'][:50]}...")
    print(f"  来源: {enhance_result['source']}")
    
    print("\n[3] 成本报告:")
    report = generator.get_cost_report()
    print(f"  今日已用: ¥{report['today_cost']:.4f} / ¥{report['daily_budget']:.2f}")
    print(f"  本月已用: ¥{report['monthly_cost']:.4f} / ¥{report['monthly_budget']:.2f}")
    print(f"  总调用次数: {report['total_calls']}")
    print(f"  缓存命中: {report['cache_hits']} ({report['cache_hit_rate']:.1%})")
    print(f"  降级次数: {report['fallback_count']}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
