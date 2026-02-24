#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataGen Pro - 缓存管理模块（整合版）
支持内存缓存、Redis缓存、文件持久化

整合自：
- 缓存管理.py（完整功能）
- 原有cache.py

功能：
- LRU缓存实现
- Redis双层缓存
- TTL过期控制
- 装饰器支持
- 文件持久化
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
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "ttl": self.ttl
            }

class FilePersistentCache:
    """文件持久化缓存"""
    
    def __init__(self, cache_file=None, ttl_seconds=3600):
        self.cache_file = cache_file or "cache.json"
        self.ttl_seconds = ttl_seconds
        self.data = {}
        self.lock = threading.Lock()
        self._load()
    
    def _load(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
    
    def _save(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[FileCache] 保存失败: {e}")
    
    def get(self, key):
        with self.lock:
            if key in self.data:
                item = self.data[key]
                cached_time = datetime.fromisoformat(item.get("cached_at", "2000-01-01"))
                if datetime.now() - cached_time < timedelta(seconds=self.ttl_seconds):
                    return item.get("value")
                else:
                    del self.data[key]
                    self._save()
        return None
    
    def set(self, key, value):
        with self.lock:
            self.data[key] = {
                "value": value,
                "cached_at": datetime.now().isoformat()
            }
            self._save()
    
    def delete(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                self._save()
    
    def clear(self):
        with self.lock:
            self.data = {}
            self._save()

class CacheManager:
    """缓存管理器 - 支持内存、Redis、文件三层缓存"""
    
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
        self.file_caches = {}
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        redis_url = os.environ.get('REDIS_URL')
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                print("[Cache] Redis连接成功")
            except Exception as e:
                print(f"[Cache] Redis连接失败: {e}")
                self.redis_client = None
    
    def get_cache(self, name="default", max_size=1000, ttl=3600):
        if name not in self.caches:
            self.caches[name] = LRUCache(max_size, ttl)
        return self.caches[name]
    
    def get_file_cache(self, name="default", ttl=3600):
        cache_file = f"cache_{name}.json"
        if name not in self.file_caches:
            self.file_caches[name] = FilePersistentCache(cache_file, ttl)
        return self.file_caches[name]
    
    def get(self, key, cache_name="default", use_file=False):
        if self.redis_client:
            try:
                value = self.redis_client.get(f"{cache_name}:{key}")
                if value:
                    return json.loads(value)
            except Exception:
                pass
        
        cache = self.get_cache(cache_name)
        result = cache.get(key)
        
        if result is None and use_file:
            file_cache = self.get_file_cache(cache_name)
            result = file_cache.get(key)
            if result is not None:
                cache.set(key, result)
        
        return result
    
    def set(self, key, value, cache_name="default", ttl=None, persist=False):
        if self.redis_client:
            try:
                ttl = ttl or 3600
                self.redis_client.setex(
                    f"{cache_name}:{key}",
                    ttl,
                    json.dumps(value)
                )
            except Exception:
                pass
        
        cache = self.get_cache(cache_name)
        cache.set(key, value)
        
        if persist:
            file_cache = self.get_file_cache(cache_name)
            file_cache.set(key, value)
    
    def delete(self, key, cache_name="default", persist=False):
        if self.redis_client:
            try:
                self.redis_client.delete(f"{cache_name}:{key}")
            except Exception:
                pass
        
        cache = self.get_cache(cache_name)
        cache.delete(key)
        
        if persist:
            file_cache = self.get_file_cache(cache_name)
            file_cache.delete(key)
    
    def clear_all(self):
        for cache in self.caches.values():
            cache.clear()
        
        for file_cache in self.file_caches.values():
            file_cache.clear()
        
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception:
                pass

def cached(cache_name="default", ttl=3600, key_prefix="", persist=False):
    """缓存装饰器"""
    cache_manager = CacheManager()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(json.dumps([args, kwargs], sort_keys=True, default=str).encode()).hexdigest()}"
            
            result = cache_manager.get(cache_key, cache_name, use_file=persist)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, cache_name, ttl, persist=persist)
            
            return result
        
        return wrapper
    return decorator

template_cache = CacheManager().get_cache("templates", max_size=500, ttl=7200)
domain_cache = CacheManager().get_cache("domains", max_size=100, ttl=3600)
result_cache = CacheManager().get_cache("results", max_size=200, ttl=1800)

cache_manager = CacheManager()

Cache = CacheManager

__all__ = ["Cache", "CacheManager", "LRUCache", "FilePersistentCache", "cached", "cache_manager", 
           "template_cache", "domain_cache", "result_cache"]
