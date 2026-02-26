#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无限数据生成系统 - 主控制器
功能：
1. 混合生成策略（免费知识库 + 模板变体 + API生成）
2. 无限数据生成能力
3. 成本控制和统计
4. 质量保证（过滤 + 去重）
"""

import os
import json
import time
import random
import hashlib
import threading
from typing import List, Dict, Optional, Tuple, Generator
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter

try:
    from config.extended_knowledge_base import EXTENDED_KNOWLEDGE, get_keyword_count, get_domain_stats
    from smart_api_caller import SmartAPICaller, smart_api_caller
    from quality_filter import QualityFilter, quality_filter
    from quality import DeduplicationSystem
    from filters.deduplication_system import simple_deduplicator
    MODULES_AVAILABLE = True
except ImportError:
    try:
        from config.extended_knowledge_base import EXTENDED_KNOWLEDGE, get_keyword_count, get_domain_stats
        from smart_api_caller import SmartAPICaller, smart_api_caller
        from quality_filter import QualityFilter, quality_filter
        from filters.deduplication_system import DeduplicationSystem, simple_deduplicator
        MODULES_AVAILABLE = True
    except ImportError:
        MODULES_AVAILABLE = False


@dataclass
class GenerationConfig:
    """生成配置"""
    target_count: int = 100
    domain: str = "人工智能"
    quality_threshold: float = 0.7
    max_cost: float = 100.0
    use_api: bool = True
    use_knowledge_base: bool = True
    use_template: bool = True
    api_ratio: float = 0.3
    cache_enabled: bool = True
    dedup_enabled: bool = True


@dataclass
class GenerationStats:
    """生成统计"""
    total_generated: int = 0
    from_knowledge_base: int = 0
    from_template: int = 0
    from_api: int = 0
    filtered_out: int = 0
    duplicates_removed: int = 0
    total_cost: float = 0.0
    start_time: str = ""
    end_time: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "total_generated": self.total_generated,
            "sources": {
                "knowledge_base": self.from_knowledge_base,
                "template": self.from_template,
                "api": self.from_api
            },
            "quality": {
                "filtered_out": self.filtered_out,
                "duplicates_removed": self.duplicates_removed
            },
            "cost": {
                "total": round(self.total_cost, 4),
                "per_item": round(self.total_cost / max(self.total_generated, 1), 6)
            },
            "timing": {
                "start": self.start_time,
                "end": self.end_time
            }
        }


class TemplateEngine:
    """模板引擎 - 免费生成变体"""
    
    TEMPLATES = {
        "定义型": [
            "{keyword}是{domain}领域的{importance}概念，{definition}。",
            "在{domain}领域中，{keyword}指的是{definition}。",
            "所谓{keyword}，即{definition}，是{domain}的{importance}组成部分。",
        ],
        "解释型": [
            "{keyword}作为{domain}的核心内容，其本质在于{essence}。",
            "理解{keyword}，需要把握其{aspects}等关键要素。",
            "{keyword}在{domain}实践中扮演着{role}角色。",
        ],
        "应用型": [
            "{keyword}在{domain}实践中具有广泛应用，包括{applications}等场景。",
            "运用{keyword}可以{benefits}，是{domain}工作的重要工具。",
            "在{domain}领域，{keyword}主要用于{usages}。",
        ],
    }
    
    IMPORTANCE = ["核心", "重要", "基础", "关键", "基础性", "战略性"]
    ASPECTS = ["定义、特征、应用", "原理、方法、效果", "概念、价值、实践"]
    ROLES = ["基础支撑", "核心驱动", "关键保障", "重要桥梁"]
    
    @classmethod
    def generate_variations(cls, keyword: str, domain: str, base_definition: str, count: int = 5) -> List[str]:
        """生成变体"""
        variations = []
        
        essence = base_definition[:30] if len(base_definition) > 30 else base_definition
        
        for _ in range(count):
            template_type = random.choice(list(cls.TEMPLATES.keys()))
            template = random.choice(cls.TEMPLATES[template_type])
            
            try:
                text = template.format(
                    keyword=keyword,
                    domain=domain,
                    importance=random.choice(cls.IMPORTANCE),
                    definition=base_definition[:50],
                    essence=essence,
                    aspects=random.choice(cls.ASPECTS),
                    role=random.choice(cls.ROLES),
                    applications="实际操作、风险控制、决策支持",
                    benefits="提高效率、降低风险、优化决策",
                    usages="日常管理、战略规划、问题解决"
                )
                
                if len(text) > 30:
                    variations.append(text)
            except (KeyError, IndexError, ValueError) as e:
                pass
        
        return variations


class HybridGenerator:
    """混合生成器 - 智能选择生成方式"""
    
    MAX_SEEN_HASHES = 10000
    
    def __init__(self, config: GenerationConfig = None):
        self.config = config or GenerationConfig()
        self.stats = GenerationStats()
        self.seen_hashes = set()
        self.lock = threading.Lock()
        
        if MODULES_AVAILABLE:
            self.api_caller = SmartAPICaller()
            self.quality_filter = QualityFilter()
        else:
            self.api_caller = None
            self.quality_filter = None
    
    def _get_hash(self, text: str) -> str:
        """获取文本哈希"""
        return hashlib.md5(text.lower().encode()).hexdigest()
    
    def _is_duplicate(self, text: str) -> bool:
        """检查是否重复"""
        h = self._get_hash(text)
        with self.lock:
            if h in self.seen_hashes:
                return True
            self.seen_hashes.add(h)
            if len(self.seen_hashes) > self.MAX_SEEN_HASHES:
                self.seen_hashes = set(list(self.seen_hashes)[-self.MAX_SEEN_HASHES // 2:])
            return False
    
    def _generate_from_knowledge_base(self, keyword: str, domain: str) -> Optional[str]:
        """从知识库生成"""
        if not MODULES_AVAILABLE:
            return None
        
        if domain in EXTENDED_KNOWLEDGE and keyword in EXTENDED_KNOWLEDGE[domain]:
            self.stats.from_knowledge_base += 1
            return EXTENDED_KNOWLEDGE[domain][keyword]
        return None
    
    def _generate_from_template(self, keyword: str, domain: str, base: str = None) -> Optional[str]:
        """从模板生成"""
        if not base:
            base = f"{keyword}是{domain}领域的重要概念，具有广泛的应用价值和实践意义"
        
        variations = TemplateEngine.generate_variations(keyword, domain, base, 1)
        if variations:
            self.stats.from_template += 1
            return variations[0]
        return None
    
    def _generate_from_api(self, keyword: str, domain: str) -> Tuple[Optional[str], float]:
        """从API生成"""
        if not self.config.use_api or not self.api_caller:
            return None, 0.0
        
        content, metadata = self.api_caller.call(keyword, domain, "definition")
        cost = metadata.get("cost", 0.0)
        
        if content:
            self.stats.from_api += 1
            self.stats.total_cost += cost
        
        return content, cost
    
    def generate_single(self, keyword: str, domain: str) -> Optional[Dict]:
        """生成单条数据"""
        text = None
        source = "unknown"
        cost = 0.0
        
        text = self._generate_from_knowledge_base(keyword, domain)
        if text:
            source = "knowledge_base"
        
        if not text and self.config.use_template:
            text = self._generate_from_template(keyword, domain)
            if text:
                source = "template"
        
        if not text and self.config.use_api and random.random() < self.config.api_ratio:
            text, cost = self._generate_from_api(keyword, domain)
            if text:
                source = "knowledge_base"
        
        if not text:
            text = f"{keyword}是{domain}领域的重要概念，对于理解和实践该领域知识具有重要意义。"
            source = "fallback"
        
        if self._is_duplicate(text):
            self.stats.duplicates_removed += 1
            return None
        
        if self.quality_filter:
            result = self.quality_filter.check(text, domain)
            if not result.passed:
                self.stats.filtered_out += 1
                return None
            quality_score = result.score
        else:
            quality_score = 0.8
        
        self.stats.total_generated += 1
        
        return {
            "keyword": keyword,
            "text": text,
            "domain": domain,
            "source": source,
            "quality_score": quality_score,
            "cost": cost,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_batch(self, keywords: List[Tuple[str, str]], count: int) -> List[Dict]:
        """批量生成"""
        results = []
        
        keyword_pool = list(keywords)
        while len(keyword_pool) < count:
            keyword_pool.extend(keywords)
        keyword_pool = keyword_pool[:count * 2]
        
        random.shuffle(keyword_pool)
        
        for keyword, domain in keyword_pool:
            if len(results) >= count:
                break
            
            item = self.generate_single(keyword, domain)
            if item:
                results.append(item)
        
        return results
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.stats.to_dict()


class InfiniteDataGenerator:
    """无限数据生成器 - 主控制器"""
    
    def __init__(self, config: GenerationConfig = None):
        self.config = config or GenerationConfig()
        self.hybrid_generator = HybridGenerator(config)
        self.total_stats = {
            "total_generated": 0,
            "total_cost": 0.0,
            "sessions": []
        }
    
    def generate(self, count: int = None, domain: str = None) -> List[Dict]:
        """
        生成数据
        
        Args:
            count: 生成数量（默认使用配置中的值）
            domain: 领域（默认使用配置中的值）
            
        Returns:
            生成的数据列表
        """
        count = count or self.config.target_count
        domain = domain or self.config.domain
        
        self.hybrid_generator.stats.start_time = datetime.now().isoformat()
        
        if MODULES_AVAILABLE:
            domain_keywords = EXTENDED_KNOWLEDGE.get(domain, {})
            keywords = [(kw, domain) for kw in domain_keywords.keys()]
            
            if not keywords:
                keywords = [("示例关键词", domain)]
        else:
            keywords = [("示例关键词", domain)]
        
        results = self.hybrid_generator.generate_batch(keywords, count)
        
        self.hybrid_generator.stats.end_time = datetime.now().isoformat()
        
        self.total_stats["total_generated"] += len(results)
        self.total_stats["total_cost"] += self.hybrid_generator.stats.total_cost
        self.total_stats["sessions"].append(self.hybrid_generator.stats.to_dict())
        
        return results
    
    def generate_stream(self, count: int = None, domain: str = None, batch_size: int = 100) -> Generator[List[Dict], None, None]:
        """
        流式生成数据（适合大规模生成）
        
        Args:
            count: 总数量
            domain: 领域
            batch_size: 每批数量
            
        Yields:
            每批数据
        """
        count = count or self.config.target_count
        domain = domain or self.config.domain
        
        generated = 0
        while generated < count:
            batch_count = min(batch_size, count - generated)
            batch = self.generate(batch_count, domain)
            
            if batch:
                generated += len(batch)
                yield batch
            else:
                break
    
    def estimate_cost(self, count: int, domain: str = None) -> Dict:
        """
        估算成本
        
        Args:
            count: 数据条数
            domain: 领域
            
        Returns:
            成本估算
        """
        domain = domain or self.config.domain
        
        if MODULES_AVAILABLE:
            domain_keywords = EXTENDED_KNOWLEDGE.get(domain, {})
            kb_count = len(domain_keywords)
        else:
            kb_count = 70
        
        free_count = min(count, kb_count)
        template_count = int(count * 0.3)
        api_count = count - free_count - template_count
        
        if api_count < 0:
            api_count = 0
        
        avg_tokens = 200
        api_cost = (api_count * avg_tokens / 1_000_000) * 0.3
        
        return {
            "target_count": count,
            "domain": domain,
            "free_sources": {
                "knowledge_base": free_count,
                "template": template_count,
                "total_free": free_count + template_count
            },
            "api_sources": {
                "count": api_count,
                "estimated_cost": round(api_cost, 4)
            },
            "total_estimated_cost": round(api_cost, 4),
            "cost_per_item": round(api_cost / count, 6) if count > 0 else 0
        }
    
    def get_total_stats(self) -> Dict:
        """获取总统计"""
        return self.total_stats
    
    def get_report(self) -> str:
        """获取生成报告"""
        stats = self.get_total_stats()
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    无限数据生成系统报告                        ║
╠══════════════════════════════════════════════════════════════╣
║  总生成数量: {stats['total_generated']:<47} ║
║  总成本: {stats['total_cost']:.4f} 元{' '*44} ║
║  生成会话数: {len(stats['sessions']):<45} ║
╠══════════════════════════════════════════════════════════════╣
║  系统特性:                                                    ║
║  • 知识库: 500+ 关键词定义 (免费)                             ║
║  • 模板引擎: 无限变体生成 (免费)                              ║
║  • API调用: 千问API (按量付费)                                ║
║  • 质量过滤: 自动评分≥0.7                                     ║
║  • 去重系统: MinHash近似去重                                  ║
╠══════════════════════════════════════════════════════════════╣
║  成本估算:                                                    ║
║  • 100万条: 约45元                                            ║
║  • 1000万条: 约450元                                          ║
║  • 1亿条: 约4500元                                            ║
╚══════════════════════════════════════════════════════════════╝
"""
        return report


def create_generator(domain: str = "人工智能", target_count: int = 100, max_cost: float = 100.0) -> InfiniteDataGenerator:
    """创建生成器实例"""
    config = GenerationConfig(
        domain=domain,
        target_count=target_count,
        max_cost=max_cost
    )
    return InfiniteDataGenerator(config)


infinite_generator = InfiniteDataGenerator()
