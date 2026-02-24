#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块 - 导出
"""

from .domains_config import DOMAINS, get_keywords, get_available_domains, LazyDomains
from .templates_config import TEMPLATES, VARIATIONS, QUALITY_MODES, get_templates, get_variations, get_quality_modes

try:
    from .extended_knowledge_base import EXTENDED_KNOWLEDGE, get_extended_knowledge, get_all_keywords, get_keyword_count, get_domain_stats
except ImportError:
    EXTENDED_KNOWLEDGE = {}
    get_extended_knowledge = lambda: {}
    get_all_keywords = lambda: []
    get_keyword_count = lambda: 0
    get_domain_stats = lambda: {}

try:
    from .knowledge_expander import (
        KnowledgeExpander, KnowledgeEntry, WikidataAPI, WikipediaAPI,
        knowledge_expander, wikidata_api, wikipedia_api
    )
except ImportError:
    KnowledgeExpander = None
    KnowledgeEntry = None
    WikidataAPI = None
    WikipediaAPI = None
    knowledge_expander = None
    wikidata_api = None
    wikipedia_api = None

__all__ = [
    "DOMAINS",
    "get_keywords",
    "get_available_domains",
    "LazyDomains",
    "TEMPLATES",
    "VARIATIONS",
    "QUALITY_MODES",
    "get_templates",
    "get_variations",
    "get_quality_modes",
    "EXTENDED_KNOWLEDGE",
    "get_extended_knowledge",
    "get_all_keywords",
    "get_keyword_count",
    "get_domain_stats",
    "KnowledgeExpander",
    "KnowledgeEntry",
    "WikidataAPI",
    "WikipediaAPI",
    "knowledge_expander",
    "wikidata_api",
    "wikipedia_api",
]
