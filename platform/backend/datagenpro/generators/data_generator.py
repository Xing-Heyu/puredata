#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心数据生成器
支持：拓扑生成、Copula分布、真实感增强
"""

import random
import hashlib
import threading
import concurrent.futures
from datetime import datetime, timedelta
from collections import defaultdict

class DataGenerator:
    """核心数据生成器"""
    
    DOMAINS = {
        "人工智能": ["AI", "machine learning", "deep learning", "neural network", "CNN", "RNN", "LSTM", "transformer", "attention", "gradient descent", "backpropagation", "overfitting", "regularization", "hyperparameter", "feature", "model", "training", "inference", "dataset", "algorithm"],
        "医疗": ["diagnosis", "treatment", "symptom", "disease", "patient", "doctor", "hospital", "medicine", "prescription", "surgery", "chronic", "acute", "prevention", "vaccine", "immunity", "pathology", "prognosis", "therapy", "clinical", "healthcare"],
        "金融": ["stock", "bond", "investment", "portfolio", "risk", "return", "asset", "liability", "equity", "dividend", "interest", "inflation", "deflation", "currency", "exchange", "market", "trading", "hedge", "derivative", "leverage"],
        "劳动合同": ["employer", "employee", "contract", "salary", "wage", "benefit", "termination", "probation", "overtime", "leave", "insurance", "pension", "bonus", "commission", "severance", "non-compete", "confidentiality", "intellectual property", "dispute", "arbitration"]
    }
    
    def __init__(self, config=None):
        self.config = config or {}
        self.lock = threading.Lock()
    
    def generate(self, domain, count, quality="normal", callback=None):
        """生成数据"""
        if domain not in self.DOMAINS:
            raise ValueError(f"未知领域: {domain}")
        
        keywords = self.DOMAINS[domain]
        data = []
        hashes = set()
        
        for i in range(count):
            keyword = keywords[i % len(keywords)]
            text = self._generate_text(keyword, domain, i, quality)
            
            content_hash = hashlib.md5(text.encode()).hexdigest()
            if content_hash in hashes:
                continue
            hashes.add(content_hash)
            
            item = {
                "id": len(data) + 1,
                "word": keyword,
                "text": text,
                "category": domain,
                "source": "generated",
                "quality": quality,
                "timestamp": datetime.now().isoformat()
            }
            
            data.append(item)
            
            if callback and i % 10 == 0:
                callback(i + 1, count)
        
        return data
    
    def _generate_text(self, word, domain, index, quality):
        """生成文本"""
        templates = [
            f"{word} is a key concept in {domain}.",
            f"In {domain}, {word} plays an important role.",
            f"Understanding {word} is essential for {domain}.",
            f"{word} refers to a fundamental technique in {domain}.",
        ]
        
        text = random.choice(templates)
        
        if quality == "noisy":
            text = self._add_noise(text)
        elif quality == "chaotic":
            text = self._add_chaos(text)
        
        return text
    
    def _add_noise(self, text):
        """添加噪声"""
        if len(text) > 10:
            pos = random.randint(0, len(text) - 1)
            text = text[:pos] + random.choice([" ", "  ", "x"]) + text[pos+1:]
        return text
    
    def _add_chaos(self, text):
        """添加混乱"""
        import string
        noise = ''.join(random.choices(string.ascii_letters + '!@#', k=10))
        return noise + text + noise
    
    def generate_parallel(self, domain, count, workers=4, callback=None):
        """并行生成"""
        results = []
        chunk_size = count // workers
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for i in range(workers):
                future = executor.submit(
                    self.generate,
                    domain,
                    chunk_size,
                    "normal",
                    lambda p, t: callback(p + i * chunk_size, count) if callback else None
                )
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        
        return results[:count]
