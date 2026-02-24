#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据缓存模块
支持：相同参数复用结果、缓存过期、LRU淘汰
"""

import json
import os
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple
from collections import OrderedDict
import gzip
import base64

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BACKEND_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

class DataCache:
    """数据缓存管理器"""
    
    MAX_MEMORY_CACHE = 100
    CACHE_EXPIRE_HOURS = 24
    MAX_CACHE_SIZE_MB = 500
    
    def __init__(self):
        self.memory_cache: OrderedDict = OrderedDict()
        self.lock = threading.Lock()
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        # 延迟写入相关属性
        self._save_timer = None
        self._save_delay = 10.0  # 缓存索引延迟保存时间（秒）
        self._pending_save = False
        self._load_index()
    
    def _load_index(self):
        index_file = os.path.join(CACHE_DIR, 'index.json')
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cache_stats = data.get("stats", self.cache_stats)
    
    def _save_index(self, immediate=False):
        """保存缓存索引 - 支持延迟写入优化性能"""
        with self.lock:
            if immediate:
                # 立即保存
                self._do_save_index()
                self._pending_save = False
                if self._save_timer:
                    self._save_timer.cancel()
                    self._save_timer = None
            else:
                # 延迟保存
                self._pending_save = True
                if self._save_timer:
                    self._save_timer.cancel()
                
                self._save_timer = threading.Timer(self._save_delay, self._do_save_index)
                self._save_timer.daemon = True
                self._save_timer.start()
    
    def _do_save_index(self):
        """实际执行索引保存操作"""
        try:
            index_file = os.path.join(CACHE_DIR, 'index.json')
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "stats": self.cache_stats,
                    "updated_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            with self.lock:
                self._pending_save = False
        except Exception as e:
            print(f"[ERROR] 保存缓存索引失败: {e}")
    
    def _generate_key(self, params: Dict) -> str:
        sorted_params = json.dumps(params, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(sorted_params.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        return os.path.join(CACHE_DIR, f"{key}.json.gz")
    
    def _compress_data(self, data: Any) -> bytes:
        json_str = json.dumps(data, ensure_ascii=False)
        return gzip.compress(json_str.encode('utf-8'))
    
    def _decompress_data(self, compressed: bytes) -> Any:
        json_str = gzip.decompress(compressed).decode('utf-8')
        return json.loads(json_str)
    
    def _get_cache_size_mb(self) -> float:
        total_size = 0
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.json.gz'):
                filepath = os.path.join(CACHE_DIR, filename)
                total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)
    
    def _evict_old_cache(self):
        """缓存淘汰 - 线程安全"""
        if self._get_cache_size_mb() > self.MAX_CACHE_SIZE_MB:
            with self.lock:
                files = []
                for filename in os.listdir(CACHE_DIR):
                    if filename.endswith('.json.gz'):
                        filepath = os.path.join(CACHE_DIR, filename)
                        files.append((filepath, os.path.getmtime(filepath)))
                
                files.sort(key=lambda x: x[1])
                
                for filepath, _ in files[:len(files) // 3]:
                    try:
                        os.remove(filepath)
                        self.cache_stats["evictions"] += 1
                    except OSError:
                        # 文件可能已被其他线程删除，忽略错误
                        pass
    
    def get(self, params: Dict) -> Tuple[Optional[Any], bool]:
        key = self._generate_key(params)
        
        with self.lock:
            if key in self.memory_cache:
                cached = self.memory_cache[key]
                if datetime.now() < datetime.fromisoformat(cached["expires_at"]):
                    self.memory_cache.move_to_end(key)
                    self.cache_stats["hits"] += 1
                    self._save_index()
                    return cached["data"], True
                else:
                    del self.memory_cache[key]
        
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    compressed = f.read()
                
                data = self._decompress_data(compressed)
                
                with self.lock:
                    if len(self.memory_cache) >= self.MAX_MEMORY_CACHE:
                        self.memory_cache.popitem(last=False)
                    
                    self.memory_cache[key] = {
                        "data": data,
                        "expires_at": (datetime.now() + timedelta(hours=self.CACHE_EXPIRE_HOURS)).isoformat()
                    }
                
                self.cache_stats["hits"] += 1
                self._save_index()
                return data, True
            except Exception as e:
                print(f"[Cache] 读取缓存失败: {e}")
        
        self.cache_stats["misses"] += 1
        self._save_index()
        return None, False
    
    def set(self, params: Dict, data: Any, expire_hours: int = None) -> bool:
        key = self._generate_key(params)
        expire_hours = expire_hours or self.CACHE_EXPIRE_HOURS
        
        with self.lock:
            if len(self.memory_cache) >= self.MAX_MEMORY_CACHE:
                self.memory_cache.popitem(last=False)
            
            self.memory_cache[key] = {
                "data": data,
                "expires_at": (datetime.now() + timedelta(hours=expire_hours)).isoformat()
            }
        
        try:
            cache_path = self._get_cache_path(key)
            compressed = self._compress_data(data)
            
            with open(cache_path, 'wb') as f:
                f.write(compressed)
            
            self._evict_old_cache()
            self._save_index()
            
            return True
        except Exception as e:
            print(f"[Cache] 写入缓存失败: {e}")
            return False
    
    def invalidate(self, params: Dict) -> bool:
        key = self._generate_key(params)
        
        with self.lock:
            if key in self.memory_cache:
                del self.memory_cache[key]
        
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            os.remove(cache_path)
        
        return True
    
    def clear_all(self) -> int:
        count = 0
        
        with self.lock:
            self.memory_cache.clear()
        
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.json.gz'):
                filepath = os.path.join(CACHE_DIR, filename)
                os.remove(filepath)
                count += 1
        
        return count
    
    def get_stats(self) -> Dict:
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "evictions": self.cache_stats["evictions"],
            "hit_rate": round(hit_rate * 100, 2),
            "memory_cache_size": len(self.memory_cache),
            "disk_cache_size_mb": round(self._get_cache_size_mb(), 2),
            "max_size_mb": self.MAX_CACHE_SIZE_MB
        }

data_cache = DataCache()

if __name__ == "__main__":
    print("="*60)
    print("数据缓存测试")
    print("="*60)
    
    params = {"domain": "人工智能", "count": 100, "mode": "hybrid"}
    
    data, hit = data_cache.get(params)
    print(f"\n第一次查询: {'命中' if hit else '未命中'}")
    
    if not hit:
        test_data = [{"id": i, "text": f"测试数据{i}"} for i in range(100)]
        data_cache.set(params, test_data)
        print("数据已缓存")
    
    data, hit = data_cache.get(params)
    print(f"第二次查询: {'命中' if hit else '未命中'}")
    
    stats = data_cache.get_stats()
    print(f"\n缓存统计: {stats}")
