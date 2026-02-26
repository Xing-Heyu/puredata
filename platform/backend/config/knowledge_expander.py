#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库扩展模块 - Wikidata API集成

数据来源：
1. Wikidata (CC0协议) - 完全免费，可商用
2. Wikipedia (CC BY-SA) - 免费，需署名
3. 千问API - 付费补充

许可证说明：
- Wikidata: CC0 Public Domain Dedication (可商用)
- Wikipedia: CC BY-SA 4.0 (可商用，需署名)
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import time
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class KnowledgeEntry:
    """知识条目"""
    word: str
    definition: str
    source: str
    language: str
    confidence: float
    entity_id: str = ""
    categories: List[str] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []


class WikidataAPI:
    """
    Wikidata API客户端
    
    许可证: CC0 Public Domain Dedication
    官网: https://www.wikidata.org
    API文档: https://www.wikidata.org/w/api.php
    
    特点：
    - 完全免费
    - 可商用
    - 支持300+语言
    - 超过1亿条实体
    """
    
    BASE_URL = "https://www.wikidata.org/w/api.php"
    
    def __init__(self, cache_file: str = None):
        self.cache_file = cache_file or os.path.join(
            os.path.dirname(__file__), '..', 'wikidata_cache.json'
        )
        self.cache = self._load_cache()
        self.request_count = 0
        self.last_request_time = 0
    
    def _load_cache(self) -> Dict:
        """加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError):
                return {}
        return {}
    
    def _save_cache(self):
        """保存缓存"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Wikidata] Cache save error: {e}")
    
    def _rate_limit(self):
        """速率限制"""
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.1:
            time.sleep(0.1 - elapsed)
        self.last_request_time = time.time()
    
    def search_entity(self, word: str, language: str = "zh") -> Optional[Dict]:
        """
        搜索实体
        
        Args:
            word: 搜索词
            language: 语言代码 (zh, en, etc.)
            
        Returns:
            实体信息或None
        """
        cache_key = f"{language}_{word}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        self._rate_limit()
        
        params = {
            "action": "wbsearchentities",
            "search": word,
            "language": language,
            "format": "json",
            "limit": 5,
            "type": "item"
        }
        
        try:
            url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'PureData/2.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if data.get("search"):
                result = data["search"][0]
                self.cache[cache_key] = result
                self._save_cache()
                return result
        except Exception as e:
            print(f"[Wikidata] Search error: {e}")
        
        return None
    
    def get_entity(self, entity_id: str, language: str = "zh") -> Optional[Dict]:
        """
        获取实体详情
        
        Args:
            entity_id: Wikidata实体ID (如Q123)
            language: 语言代码
            
        Returns:
            实体详情或None
        """
        cache_key = f"entity_{entity_id}_{language}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        self._rate_limit()
        
        params = {
            "action": "wbgetentities",
            "ids": entity_id,
            "languages": language,
            "format": "json"
        }
        
        try:
            url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'PureData/2.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if entity_id in data.get("entities", {}):
                result = data["entities"][entity_id]
                self.cache[cache_key] = result
                self._save_cache()
                return result
        except Exception as e:
            print(f"[Wikidata] Get entity error: {e}")
        
        return None
    
    def get_definition(self, word: str, language: str = "zh") -> Optional[KnowledgeEntry]:
        """
        获取词语定义
        
        Args:
            word: 词语
            language: 语言代码
            
        Returns:
            知识条目或None
        """
        search_result = self.search_entity(word, language)
        
        if not search_result:
            if language != "en":
                search_result = self.search_entity(word, "en")
            
            if not search_result:
                return None
        
        entity_id = search_result.get("id", "")
        label = search_result.get("label", word)
        description = search_result.get("description", "")
        
        if not description:
            entity = self.get_entity(entity_id, language)
            if entity:
                descriptions = entity.get("descriptions", {})
                if language in descriptions:
                    description = descriptions[language].get("value", "")
                elif "en" in descriptions:
                    description = descriptions["en"].get("value", "")
        
        if not description:
            return None
        
        return KnowledgeEntry(
            word=label,
            definition=description,
            source="wikidata",
            language=language,
            confidence=0.9,
            entity_id=entity_id
        )
    
    def batch_get_definitions(self, words: List[str], language: str = "zh") -> Dict[str, KnowledgeEntry]:
        """批量获取定义"""
        results = {}
        
        for word in words:
            entry = self.get_definition(word, language)
            if entry:
                results[word] = entry
            time.sleep(0.1)
        
        return results


class WikipediaAPI:
    """
    Wikipedia API客户端
    
    许可证: CC BY-SA 4.0 (可商用，需署名)
    官网: https://www.wikipedia.org
    
    特点：
    - 免费
    - 可商用（需署名）
    - 内容丰富
    """
    
    BASE_URL = "https://{lang}.wikipedia.org/w/api.php"
    
    def __init__(self, cache_file: str = None):
        self.cache_file = cache_file or os.path.join(
            os.path.dirname(__file__), '..', 'wikipedia_cache.json'
        )
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError):
                return {}
        return {}
    
    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except (IOError, OSError) as e:
            print(f"[WARN] 保存知识库缓存失败: {e}")
    
    def get_summary(self, word: str, language: str = "zh") -> Optional[KnowledgeEntry]:
        """获取词条摘要"""
        cache_key = f"{language}_{word}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            return KnowledgeEntry(**cached)
        
        url = self.BASE_URL.format(lang=language)
        
        params = {
            "action": "query",
            "titles": word,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "exsentences": 3,
            "format": "json"
        }
        
        try:
            url = f"{url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'PureData/2.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                if page_id != "-1" and "extract" in page:
                    extract = page["extract"]
                    if len(extract) > 50:
                        entry = KnowledgeEntry(
                            word=word,
                            definition=extract[:300],
                            source="wikipedia",
                            language=language,
                            confidence=0.85
                        )
                        
                        self.cache[cache_key] = {
                            "word": entry.word,
                            "definition": entry.definition,
                            "source": entry.source,
                            "language": entry.language,
                            "confidence": entry.confidence
                        }
                        self._save_cache()
                        
                        return entry
        except Exception as e:
            print(f"[Wikipedia] Error: {e}")
        
        return None


class KnowledgeExpander:
    """
    知识库扩展器 - 整合多个数据源
    
    优先级：
    1. Wikidata (CC0, 免费, 可商用)
    2. Wikipedia (CC BY-SA, 免费, 可商用)
    3. 千问API (付费, 高质量)
    """
    
    def __init__(self):
        self.wikidata = WikidataAPI()
        self.wikipedia = WikipediaAPI()
        self.stats = {
            "wikidata_hits": 0,
            "wikipedia_hits": 0,
            "api_calls": 0,
            "total_expanded": 0
        }
    
    def expand_definition(self, word: str, language: str = "zh") -> Optional[KnowledgeEntry]:
        """扩展单个词语的定义"""
        entry = self.wikidata.get_definition(word, language)
        if entry and len(entry.definition) > 20:
            self.stats["wikidata_hits"] += 1
            self.stats["total_expanded"] += 1
            return entry
        
        entry = self.wikipedia.get_summary(word, language)
        if entry and len(entry.definition) > 30:
            self.stats["wikipedia_hits"] += 1
            self.stats["total_expanded"] += 1
            return entry
        
        if language != "en":
            entry = self.wikidata.get_definition(word, "en")
            if entry and len(entry.definition) > 20:
                self.stats["wikidata_hits"] += 1
                self.stats["total_expanded"] += 1
                return entry
        
        return None
    
    def expand_batch(self, words: List[str], language: str = "zh") -> Dict[str, KnowledgeEntry]:
        """批量扩展"""
        results = {}
        
        for word in words:
            entry = self.expand_definition(word, language)
            if entry:
                results[word] = entry
            time.sleep(0.15)
        
        return results
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.stats.copy()


knowledge_expander = KnowledgeExpander()
wikidata_api = WikidataAPI()
wikipedia_api = WikipediaAPI()
