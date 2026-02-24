#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层 - 缓存系统实现
整合自 datagenpro/utils/cache.py 和 缓存管理.py
"""

import json
import time
import hashlib
import threading
import os
from functools import wraps
from collections import OrderedDict
from datetime import datetime, timedelta

class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size=1000, ttl=3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.RLock()
    
    def _hash_key(self, key):
        if isinstance(key, (dict, list)):
            key = json.dumps(key, sort_keys=True)
        return hashlib.md5(str(key).encode()).hexdigest()
    
    def get(self, key):
        with self.lock:
            hashed_key = self._hash_key(key)
            if hashed_key not in self.cache:
                return None
            if time.time() - self.timestamps.get(hashed_key, 0) > self.ttl:
                del self.cache[hashed_key]
                del self.timestamps[hashed_key]
                return None
            self.cache.move_to_end(hashed_key)
            return self.cache[hashed_key]
    
    def set(self, key, value):
        with self.lock:
            hashed_key = self._hash_key(key)
            if hashed_key in self.cache:
                self.cache.move_to_end(hashed_key)
            else:
                while len(self.cache) >= self.max_size:
                    oldest = next(iter(self.cache))
                    del self.cache[oldest]
                    del self.timestamps[oldest]
            self.cache[hashed_key] = value
            self.timestamps[hashed_key] = time.time()
    
    def delete(self, key):
        with self.lock:
            hashed_key = self._hash_key(key)
            if hashed_key in self.cache:
                del self.cache[hashed_key]
                del self.timestamps[hashed_key]
    
    def clear(self):
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def get_stats(self):
        with self.lock:
            return {"size": len(self.cache), "max_size": self.max_size, "ttl": self.ttl}

class CacheManager:
    """缓存管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.caches = {}
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        redis_url = os.environ.get('REDIS_URL')
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
            except Exception:
                self.redis_client = None
    
    def get_cache(self, name="default", max_size=1000, ttl=3600):
        if name not in self.caches:
            self.caches[name] = LRUCache(max_size, ttl)
        return self.caches[name]
    
    def get(self, key, cache_name="default"):
        cache = self.get_cache(cache_name)
        return cache.get(key)
    
    def set(self, key, value, cache_name="default", ttl=None):
        cache = self.get_cache(cache_name)
        cache.set(key, value)
    
    def delete(self, key, cache_name="default"):
        cache = self.get_cache(cache_name)
        cache.delete(key)
    
    def clear_all(self):
        for cache in self.caches.values():
            cache.clear()

def cached(cache_name="default", ttl=3600, key_prefix=""):
    """缓存装饰器"""
    cache_manager = CacheManager()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(json.dumps([args, kwargs], sort_keys=True, default=str).encode()).hexdigest()}"
            result = cache_manager.get(cache_key, cache_name)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, cache_name, ttl)
            return result
        return wrapper
    return decorator

cache_manager = CacheManager()
template_cache = cache_manager.get_cache("templates", max_size=500, ttl=86400)
domain_cache = cache_manager.get_cache("domains", max_size=100, ttl=604800)
keyword_cache = cache_manager.get_cache("keywords", max_size=200, ttl=2592000)
api_cache = cache_manager.get_cache("api", max_size=1000, ttl=86400)

def invalidate_cache(domain=None, cache_type=None):
    """清理缓存 - 当知识图谱更新时调用"""
    if domain:
        domain_cache.delete(f"domain:{domain}")
        template_cache.delete(f"templates:{domain}")
        keyword_cache.delete(f"keywords:{domain}")
        print(f"[缓存清理] 已清理 {domain} 相关缓存")
    elif cache_type:
        if cache_type == "domain":
            domain_cache.clear()
        elif cache_type == "template":
            template_cache.clear()
        elif cache_type == "keyword":
            keyword_cache.clear()
        elif cache_type == "api":
            api_cache.clear()
        print(f"[缓存清理] 已清理 {cache_type} 缓存")
    else:
        cache_manager.clear_all()
        print("[缓存清理] 已清理所有缓存")

__all__ = ["CacheManager", "LRUCache", "cached", "cache_manager", "template_cache", "domain_cache", "keyword_cache", "api_cache", "invalidate_cache"]
