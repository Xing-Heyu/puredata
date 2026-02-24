#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DASGen - 分布对齐合成文本生成器
基于论文：《Distribution-Aligned Synthetic Text Generation via Tail-Aware Enhancement》

核心思想：
1. 在嵌入空间中对真实数据进行轻量级分析
2. 定位长尾语义区域
3. 引导生成模型生成分布对齐的合成文本
4. 不需要微调模型，模型无关、部署成本低

实现步骤：
1. 语义嵌入提取
2. 分布分析（识别长尾区域）
3. 尾部感知增强
4. 分布对齐生成
"""

import json
import math
import random
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import Counter, defaultdict
import statistics


@dataclass
class SemanticRegion:
    """语义区域"""
    region_id: str
    center: List[float]
    samples: List[str]
    frequency: int
    is_tail: bool
    importance_weight: float


@dataclass
class DistributionAnalysis:
    """分布分析结果"""
    total_regions: int
    tail_regions: int
    head_regions: int
    tail_coverage: float
    distribution_gini: float
    semantic_clusters: List[SemanticRegion]


class SemanticEmbedder:
    """
    语义嵌入器 - 简化版实现
    
    实际生产环境应使用：
    - sentence-transformers
    - OpenAI embeddings
    - 本地部署的embedding模型
    
    这里使用简化的TF-IDF + 降维方案
    """
    
    def __init__(self, embedding_dim: int = 64):
        self.embedding_dim = embedding_dim
        self.vocabulary = {}
        self.idf_weights = {}
        self.fitted = False
    
    def fit(self, texts: List[str]):
        """训练嵌入器"""
        doc_freq = Counter()
        all_terms = set()
        
        for text in texts:
            terms = self._tokenize(text)
            unique_terms = set(terms)
            all_terms.update(unique_terms)
            for term in unique_terms:
                doc_freq[term] += 1
        
        n_docs = len(texts)
        for term, freq in doc_freq.items():
            self.idf_weights[term] = math.log(n_docs / (1 + freq))
        
        sorted_terms = sorted(all_terms)
        self.vocabulary = {term: i for i, term in enumerate(sorted_terms[:self.embedding_dim * 2])}
        
        self.fitted = True
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        text = text.lower()
        for char in '，。！？、；：""''（）【】《》':
            text = text.replace(char, ' ')
        return text.split()
    
    def embed(self, text: str) -> List[float]:
        """生成嵌入向量"""
        if not self.fitted:
            return [0.0] * self.embedding_dim
        
        terms = self._tokenize(text)
        term_freq = Counter(terms)
        
        raw_vector = [0.0] * len(self.vocabulary)
        for term, idx in self.vocabulary.items():
            if term in term_freq:
                tf = term_freq[term] / len(terms) if terms else 0
                idf = self.idf_weights.get(term, 0)
                raw_vector[idx] = tf * idf
        
        while len(raw_vector) < self.embedding_dim:
            raw_vector.append(0.0)
        
        vector = raw_vector[:self.embedding_dim]
        
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成嵌入"""
        return [self.embed(text) for text in texts]


class DistributionAnalyzer:
    """
    分布分析器 - 识别长尾语义区域
    
    基于DASGen论文的核心方法：
    1. 将数据投影到语义空间
    2. 聚类识别语义区域
    3. 计算每个区域的频率
    4. 标记长尾区域
    """
    
    def __init__(self, n_clusters: int = 20, tail_threshold: float = 0.1):
        self.n_clusters = n_clusters
        self.tail_threshold = tail_threshold
        self.embedder = SemanticEmbedder()
        self.regions: List[SemanticRegion] = []
    
    def analyze(self, texts: List[str]) -> DistributionAnalysis:
        """分析数据分布"""
        self.embedder.fit(texts)
        
        embeddings = self.embedder.embed_batch(texts)
        
        clusters = self._cluster_embeddings(embeddings, texts)
        
        self.regions = self._identify_tail_regions(clusters)
        
        total_regions = len(self.regions)
        tail_regions = sum(1 for r in self.regions if r.is_tail)
        head_regions = total_regions - tail_regions
        
        tail_samples = sum(r.frequency for r in self.regions if r.is_tail)
        total_samples = sum(r.frequency for r in self.regions)
        tail_coverage = tail_samples / total_samples if total_samples > 0 else 0
        
        frequencies = [r.frequency for r in self.regions]
        gini = self._calculate_gini(frequencies)
        
        return DistributionAnalysis(
            total_regions=total_regions,
            tail_regions=tail_regions,
            head_regions=head_regions,
            tail_coverage=tail_coverage,
            distribution_gini=gini,
            semantic_clusters=self.regions
        )
    
    def _cluster_embeddings(self, embeddings: List[List[float]], 
                            texts: List[str]) -> Dict[int, List[Tuple[List[float], str]]]:
        """简化版聚类 - 使用K-means思想"""
        if not embeddings:
            return {}
        
        n = len(embeddings)
        k = min(self.n_clusters, n)
        
        indices = random.sample(range(n), k)
        centers = [embeddings[i] for i in indices]
        
        clusters = defaultdict(list)
        
        for i, (emb, text) in enumerate(zip(embeddings, texts)):
            min_dist = float('inf')
            best_cluster = 0
            
            for j, center in enumerate(centers):
                dist = self._cosine_distance(emb, center)
                if dist < min_dist:
                    min_dist = dist
                    best_cluster = j
            
            clusters[best_cluster].append((emb, text))
        
        return clusters
    
    def _cosine_distance(self, a: List[float], b: List[float]) -> float:
        """余弦距离"""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        
        if norm_a == 0 or norm_b == 0:
            return 1.0
        
        return 1 - dot / (norm_a * norm_b)
    
    def _identify_tail_regions(self, clusters: Dict[int, List[Tuple[List[float], str]]]) -> List[SemanticRegion]:
        """识别长尾区域"""
        regions = []
        
        frequencies = [len(samples) for samples in clusters.values()]
        if not frequencies:
            return regions
        
        total = sum(frequencies)
        avg_freq = total / len(frequencies)
        threshold = avg_freq * self.tail_threshold
        
        for cluster_id, samples in clusters.items():
            frequency = len(samples)
            
            if samples:
                center = [sum(emb[i] for emb, _ in samples) / len(samples) 
                         for i in range(len(samples[0][0]))]
            else:
                center = [0.0] * 64
            
            is_tail = frequency < threshold
            
            importance = 1.0 if is_tail else frequency / total
            
            region = SemanticRegion(
                region_id=f"region_{cluster_id}",
                center=center,
                samples=[text for _, text in samples[:10]],
                frequency=frequency,
                is_tail=is_tail,
                importance_weight=importance
            )
            regions.append(region)
        
        return regions
    
    def _calculate_gini(self, values: List[int]) -> float:
        """计算基尼系数"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        cumulative = 0
        gini_sum = 0
        
        for i, v in enumerate(sorted_values):
            cumulative += v
            gini_sum += cumulative
        
        total = sum(sorted_values)
        if total == 0:
            return 0.0
        
        gini = (2 * gini_sum / (n * total)) - (n + 1) / n
        return gini
    
    def get_tail_regions(self) -> List[SemanticRegion]:
        """获取长尾区域"""
        return [r for r in self.regions if r.is_tail]
    
    def get_enhancement_prompts(self) -> List[str]:
        """获取增强提示"""
        tail_regions = self.get_tail_regions()
        prompts = []
        
        for region in tail_regions:
            if region.samples:
                prompt = f"生成与以下内容语义相似但表达多样的数据：{'; '.join(region.samples[:3])}"
                prompts.append(prompt)
        
        return prompts


class TailAwareEnhancer:
    """
    尾部感知增强器 - DASGen核心组件
    
    功能：
    1. 识别需要增强的长尾区域
    2. 生成增强样本
    3. 保持分布对齐
    """
    
    def __init__(self, enhancement_ratio: float = 0.3):
        self.enhancement_ratio = enhancement_ratio
        self.analyzer = DistributionAnalyzer()
    
    def enhance(self, original_data: List[Dict], 
                target_count: int = None) -> Tuple[List[Dict], DistributionAnalysis]:
        """
        增强数据
        
        Args:
            original_data: 原始数据
            target_count: 目标数量（默认增加30%）
        
        Returns:
            增强后的数据 + 分布分析结果
        """
        texts = [json.dumps(item, ensure_ascii=False) for item in original_data]
        
        analysis = self.analyzer.analyze(texts)
        
        if target_count is None:
            target_count = int(len(original_data) * (1 + self.enhancement_ratio))
        
        enhanced_data = original_data.copy()
        
        tail_regions = self.analyzer.get_tail_regions()
        
        if tail_regions:
            samples_to_generate = target_count - len(original_data)
            
            for region in tail_regions:
                region_samples = int(samples_to_generate * region.importance_weight)
                
                for _ in range(region_samples):
                    new_sample = self._generate_enhanced_sample(original_data, region)
                    if new_sample:
                        enhanced_data.append(new_sample)
        
        return enhanced_data, analysis
    
    def _generate_enhanced_sample(self, original_data: List[Dict], 
                                   region: SemanticRegion) -> Optional[Dict]:
        """生成增强样本"""
        if not original_data:
            return None
        
        template = random.choice(original_data).copy()
        
        if region.samples:
            sample_text = random.choice(region.samples)
            
            variations = self._create_variations(sample_text)
            
            for key in template:
                if isinstance(template[key], str) and len(template[key]) > 0:
                    if random.random() < 0.3:
                        template[key] = random.choice(variations)
        
        template["_enhanced"] = True
        template["_source_region"] = region.region_id
        
        return template
    
    def _create_variations(self, text: str) -> List[str]:
        """创建文本变体"""
        variations = [text]
        
        words = text.split()
        if len(words) > 2:
            if random.random() < 0.5:
                shuffled = words.copy()
                random.shuffle(shuffled[1:-1])
                variations.append(' '.join(shuffled))
        
        synonyms = {
            "购买": ["下单", "买", "购入"],
            "浏览": ["查看", "看", "访问"],
            "商品": ["产品", "物品", "货品"],
            "用户": ["客户", "消费者", "买家"],
            "评价": ["评论", "反馈", "点评"],
        }
        
        for original, syns in synonyms.items():
            if original in text:
                new_text = text.replace(original, random.choice(syns))
                variations.append(new_text)
        
        return variations


class DistributionAlignedGenerator:
    """
    分布对齐生成器 - DASGen完整实现
    
    整合所有组件，提供端到端的分布对齐生成
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {
            "n_clusters": 20,
            "tail_threshold": 0.15,
            "enhancement_ratio": 0.3,
            "embedding_dim": 64,
        }
        
        self.embedder = SemanticEmbedder(self.config["embedding_dim"])
        self.analyzer = DistributionAnalyzer(
            n_clusters=self.config["n_clusters"],
            tail_threshold=self.config["tail_threshold"]
        )
        self.enhancer = TailAwareEnhancer(
            enhancement_ratio=self.config["enhancement_ratio"]
        )
    
    def generate(self, seed_data: List[Dict], count: int, 
                 preserve_distribution: bool = True) -> Dict:
        """
        生成分布对齐的数据
        
        Args:
            seed_data: 种子数据
            count: 生成数量
            preserve_distribution: 是否保持分布对齐
        
        Returns:
            生成结果，包含数据和分析报告
        """
        if preserve_distribution:
            enhanced_data, analysis = self.enhancer.enhance(seed_data, count)
        else:
            enhanced_data = self._simple_generate(seed_data, count)
            analysis = self.analyzer.analyze([json.dumps(d, ensure_ascii=False) for d in enhanced_data])
        
        return {
            "data": enhanced_data,
            "analysis": {
                "total_regions": analysis.total_regions,
                "tail_regions": analysis.tail_regions,
                "head_regions": analysis.head_regions,
                "tail_coverage": analysis.tail_coverage,
                "gini_coefficient": analysis.distribution_gini,
            },
            "tail_regions": [
                {
                    "region_id": r.region_id,
                    "frequency": r.frequency,
                    "samples": r.samples[:3],
                    "importance": r.importance_weight,
                }
                for r in analysis.semantic_clusters if r.is_tail
            ],
            "config": self.config,
        }
    
    def _simple_generate(self, seed_data: List[Dict], count: int) -> List[Dict]:
        """简单生成（不保持分布）"""
        result = []
        for _ in range(count):
            if seed_data:
                template = random.choice(seed_data).copy()
                template["_generated"] = True
                result.append(template)
        return result
    
    def analyze_distribution(self, data: List[Dict]) -> DistributionAnalysis:
        """分析数据分布"""
        texts = [json.dumps(item, ensure_ascii=False) for item in data]
        return self.analyzer.analyze(texts)
    
    def get_enhancement_recommendations(self, data: List[Dict]) -> List[str]:
        """获取增强建议"""
        analysis = self.analyze_distribution(data)
        recommendations = []
        
        if analysis.distribution_gini > 0.7:
            recommendations.append("数据分布过于集中，建议增加长尾数据")
        
        if analysis.tail_coverage < 0.1:
            recommendations.append("长尾覆盖不足，建议使用DASGen增强")
        
        tail_regions = [r for r in analysis.semantic_clusters if r.is_tail]
        if tail_regions:
            recommendations.append(f"发现 {len(tail_regions)} 个长尾区域需要增强")
        
        return recommendations


if __name__ == "__main__":
    print("=" * 60)
    print("DASGen 分布对齐生成器测试")
    print("=" * 60)
    
    seed_data = [
        {"user": "u001", "action": "浏览", "item": "手机"},
        {"user": "u002", "action": "购买", "item": "电脑"},
        {"user": "u003", "action": "浏览", "item": "手机"},
        {"user": "u004", "action": "收藏", "item": "耳机"},
        {"user": "u005", "action": "购买", "item": "手机"},
        {"user": "u006", "action": "浏览", "item": "手机"},
        {"user": "u007", "action": "购买", "item": "平板"},
        {"user": "u008", "action": "浏览", "item": "手机"},
        {"user": "u009", "action": "评价", "item": "键盘"},
        {"user": "u010", "action": "浏览", "item": "手机"},
    ]
    
    generator = DistributionAlignedGenerator()
    
    print("\n[1] 分布分析:")
    analysis = generator.analyze_distribution(seed_data)
    print(f"  总区域数: {analysis.total_regions}")
    print(f"  长尾区域: {analysis.tail_regions}")
    print(f"  头部区域: {analysis.head_regions}")
    print(f"  长尾覆盖: {analysis.tail_coverage:.2%}")
    print(f"  基尼系数: {analysis.distribution_gini:.4f}")
    
    print("\n[2] 增强建议:")
    recommendations = generator.get_enhancement_recommendations(seed_data)
    for rec in recommendations:
        print(f"  - {rec}")
    
    print("\n[3] 分布对齐生成:")
    result = generator.generate(seed_data, count=20, preserve_distribution=True)
    print(f"  生成数量: {len(result['data'])}")
    print(f"  长尾区域数: {result['analysis']['tail_regions']}")
    
    enhanced_count = sum(1 for d in result['data'] if d.get('_enhanced'))
    print(f"  增强样本数: {enhanced_count}")
    
    print("\n[4] 长尾区域详情:")
    for region in result['tail_regions'][:3]:
        print(f"  [{region['region_id']}] 频率: {region['frequency']}, 重要性: {region['importance']:.4f}")
        print(f"    样本: {region['samples'][:2]}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
