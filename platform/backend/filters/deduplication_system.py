#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MinHash近似去重系统 - 基于学术前沿方法
参考: 
- MinHash LSH for Large-scale Language Model Data Deduplication
- FED: GPU-accelerated MinHash LSH Framework

核心功能:
1. 精确去重 - MD5哈希
2. 近似去重 - MinHash LSH
3. 相似度检测 - Jaccard相似度
"""

import re
import hashlib
import random
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class DedupResult:
    """去重结果"""
    unique_items: List[Dict]
    duplicate_count: int
    near_duplicate_count: int
    similarity_matrix: Dict[str, List[str]]


class MinHash:
    """MinHash实现 - 用于近似去重"""
    
    def __init__(self, num_hashes: int = 128):
        self.num_hashes = num_hashes
        self.max_hash = (1 << 32) - 1
        self.prime = 4294967311
        
        random.seed(42)
        self.a_coeffs = [random.randint(1, self.max_hash) for _ in range(num_hashes)]
        self.b_coeffs = [random.randint(0, self.max_hash) for _ in range(num_hashes)]
    
    def _tokenize(self, text: str, n: int = 3) -> List[str]:
        """N-gram分词"""
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text.lower())
        
        tokens = []
        for i in range(len(text) - n + 1):
            tokens.append(text[i:i+n])
        
        return tokens
    
    def _hash_token(self, token: str) -> int:
        """计算token的哈希值"""
        return int(hashlib.md5(token.encode()).hexdigest(), 16) % self.max_hash
    
    def compute_signature(self, text: str) -> List[int]:
        """计算文本的MinHash签名"""
        tokens = self._tokenize(text)
        
        if not tokens:
            return [self.max_hash] * self.num_hashes
        
        token_hashes = set(self._hash_token(t) for t in tokens)
        
        signature = []
        for i in range(self.num_hashes):
            min_hash = self.max_hash
            for h in token_hashes:
                hash_val = (self.a_coeffs[i] * h + self.b_coeffs[i]) % self.prime % self.max_hash
                if hash_val < min_hash:
                    min_hash = hash_val
            signature.append(min_hash)
        
        return signature
    
    def jaccard_similarity(self, sig1: List[int], sig2: List[int]) -> float:
        """计算两个签名的Jaccard相似度估计"""
        if len(sig1) != len(sig2):
            return 0.0
        
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)


class LSHIndex:
    """LSH索引 - 用于高效查找相似文档"""
    
    def __init__(self, num_bands: int = 16, num_rows: int = 8):
        self.num_bands = num_bands
        self.num_rows = num_rows
        self.tables = [defaultdict(set) for _ in range(num_bands)]
        self.minhash = MinHash(num_hashes=num_bands * num_rows)
    
    def _hash_band(self, band: List[int]) -> str:
        """计算band的哈希值"""
        return hashlib.md5(str(band).encode()).hexdigest()
    
    def index(self, doc_id: str, text: str) -> List[str]:
        """
        索引文档，返回相似的文档ID列表
        
        Args:
            doc_id: 文档ID
            text: 文档文本
            
        Returns:
            相似文档ID列表
        """
        signature = self.minhash.compute_signature(text)
        similar_docs = set()
        
        for band_idx in range(self.num_bands):
            start = band_idx * self.num_rows
            end = start + self.num_rows
            band = signature[start:end]
            band_hash = self._hash_band(band)
            
            similar_docs.update(self.tables[band_idx][band_hash])
            
            self.tables[band_idx][band_hash].add(doc_id)
        
        return list(similar_docs)
    
    def query(self, text: str) -> List[str]:
        """查询相似文档"""
        signature = self.minhash.compute_signature(text)
        similar_docs = set()
        
        for band_idx in range(self.num_bands):
            start = band_idx * self.num_rows
            end = start + self.num_rows
            band = signature[start:end]
            band_hash = self._hash_band(band)
            
            similar_docs.update(self.tables[band_idx][band_hash])
        
        return list(similar_docs)
    
    def clear(self):
        """清空索引"""
        self.tables = [defaultdict(set) for _ in range(self.num_bands)]


class DeduplicationSystem:
    """去重系统 - 统一入口"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.lsh_index = LSHIndex()
        self.minhash = MinHash()
        
        self.exact_hashes: Set[str] = set()
        self.signatures: Dict[str, List[int]] = {}
        
        self.stats = {
            "total_processed": 0,
            "exact_duplicates": 0,
            "near_duplicates": 0,
            "unique": 0
        }
    
    def _compute_exact_hash(self, text: str) -> str:
        """计算精确哈希"""
        normalized = re.sub(r'\s+', '', text.lower())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def is_duplicate(self, text: str, doc_id: str) -> Tuple[bool, str]:
        """
        检查是否重复
        
        Args:
            text: 文本内容
            doc_id: 文档ID
            
        Returns:
            (是否重复, 重复类型)
        """
        self.stats["total_processed"] += 1
        
        exact_hash = self._compute_exact_hash(text)
        if exact_hash in self.exact_hashes:
            self.stats["exact_duplicates"] += 1
            return True, "exact"
        
        signature = self.minhash.compute_signature(text)
        
        similar_docs = self.lsh_index.query(text)
        
        for similar_id in similar_docs:
            if similar_id in self.signatures:
                similarity = self.minhash.jaccard_similarity(
                    signature, 
                    self.signatures[similar_id]
                )
                if similarity >= self.similarity_threshold:
                    self.stats["near_duplicates"] += 1
                    return True, f"near_duplicate(similarity={similarity:.2f})"
        
        self.exact_hashes.add(exact_hash)
        self.signatures[doc_id] = signature
        self.lsh_index.index(doc_id, text)
        self.stats["unique"] += 1
        
        return False, "unique"
    
    def deduplicate_batch(self, items: List[Dict], text_field: str = "text") -> DedupResult:
        """
        批量去重
        
        Args:
            items: 数据列表
            text_field: 文本字段名
            
        Returns:
            DedupResult: 去重结果
        """
        unique_items = []
        duplicate_count = 0
        near_duplicate_count = 0
        similarity_groups = defaultdict(list)
        
        for i, item in enumerate(items):
            text = item.get(text_field, "")
            if not text:
                continue
            
            doc_id = item.get("id", f"doc_{i}")
            is_dup, dup_type = self.is_duplicate(text, str(doc_id))
            
            if not is_dup:
                unique_items.append(item)
            elif dup_type == "exact":
                duplicate_count += 1
            else:
                near_duplicate_count += 1
        
        return DedupResult(
            unique_items=unique_items,
            duplicate_count=duplicate_count,
            near_duplicate_count=near_duplicate_count,
            similarity_matrix=dict(similarity_groups)
        )
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.stats["total_processed"]
        return {
            **self.stats,
            "exact_dup_rate": round(self.stats["exact_duplicates"] / total, 3) if total > 0 else 0,
            "near_dup_rate": round(self.stats["near_duplicates"] / total, 3) if total > 0 else 0,
            "unique_rate": round(self.stats["unique"] / total, 3) if total > 0 else 0
        }
    
    def reset(self):
        """重置系统"""
        self.exact_hashes.clear()
        self.signatures.clear()
        self.lsh_index.clear()
        self.stats = {
            "total_processed": 0,
            "exact_duplicates": 0,
            "near_duplicates": 0,
            "unique": 0
        }


deduplication_system = DeduplicationSystem()


class SimpleDeduplicator:
    """简单去重器 - 用于小规模数据"""
    
    @staticmethod
    def deduplicate(items: List[Dict], text_field: str = "text") -> Tuple[List[Dict], Dict]:
        """
        简单去重
        
        Args:
            items: 数据列表
            text_field: 文本字段名
            
        Returns:
            (去重后的列表, 统计信息)
        """
        seen = set()
        unique = []
        duplicates = 0
        
        for item in items:
            text = item.get(text_field, "")
            if not text:
                continue
            
            normalized = re.sub(r'\s+', '', text.lower())
            h = hashlib.md5(normalized.encode()).hexdigest()
            
            if h not in seen:
                seen.add(h)
                unique.append(item)
            else:
                duplicates += 1
        
        stats = {
            "total": len(items),
            "unique": len(unique),
            "duplicates": duplicates,
            "dedup_rate": round(duplicates / len(items), 3) if items else 0
        }
        
        return unique, stats


simple_deduplicator = SimpleDeduplicator()
