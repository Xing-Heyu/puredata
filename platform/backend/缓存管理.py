#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理模块 - 兼容层
已整合到 datagenpro/utils/cache.py
此文件保留用于向后兼容
"""

from datagenpro.utils.cache import (
    CacheManager, LRUCache, FilePersistentCache, 
    cached, cache_manager, template_cache, domain_cache, result_cache
)

Cache = CacheManager

__all__ = ["Cache", "CacheManager", "LRUCache", "FilePersistentCache", 
           "cached", "cache_manager", "template_cache", "domain_cache", "result_cache"]
