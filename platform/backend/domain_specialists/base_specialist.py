#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域专精化基类
每个垂直领域都需要继承此类并实现专精逻辑
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
import os
import random

class DomainSpecialist(ABC):
    """领域专精基类"""
    
    domain_name: str = "base"
    domain_display_name: str = "基础领域"
    
    def __init__(self):
        self.entities = self._load_entities()
        self.relations = self._load_relations()
        self.constraints = self._load_constraints()
        self.templates = self._load_templates()
        self.knowledge = self._load_knowledge()
    
    @abstractmethod
    def _load_entities(self) -> Dict[str, List[str]]:
        """加载领域实体"""
        pass
    
    @abstractmethod
    def _load_relations(self) -> Dict[str, List[str]]:
        """加载实体关系"""
        pass
    
    @abstractmethod
    def _load_constraints(self) -> Dict[str, Any]:
        """加载约束规则"""
        pass
    
    @abstractmethod
    def _load_templates(self) -> Dict[str, List[str]]:
        """加载专精模板"""
        pass
    
    @abstractmethod
    def _load_knowledge(self) -> Dict[str, Any]:
        """加载领域知识"""
        pass
    
    def validate_entity(self, entity_type: str, entity_value: str) -> bool:
        """验证实体是否合法"""
        if entity_type not in self.entities:
            return False
        return entity_value in self.entities[entity_type] or entity_type == "custom"
    
    def validate_relation(self, relation: str, source_type: str, target_type: str) -> bool:
        """验证关系是否合法"""
        key = f"{source_type}_{relation}_{target_type}"
        return key in self.relations or relation in self.relations.get("allowed", [])
    
    def apply_constraints(self, data: Dict) -> Dict:
        """应用约束规则"""
        for key, rule in self.constraints.items():
            if key in data:
                if rule.get("type") == "range":
                    data[key] = max(rule["min"], min(rule["max"], data[key]))
                elif rule.get("type") == "enum":
                    if data[key] not in rule["values"]:
                        data[key] = random.choice(rule["values"])
                elif rule.get("type") == "format":
                    data[key] = rule["pattern"].format(**data)
        return data
    
    def generate(self, count: int = 10, quality: str = "clean") -> List[Dict]:
        """生成数据"""
        results = []
        for i in range(count):
            item = self._generate_single(i, quality)
            if item:
                item = self.apply_constraints(item)
                results.append(item)
        return results
    
    @abstractmethod
    def _generate_single(self, index: int, quality: str) -> Optional[Dict]:
        """生成单条数据"""
        pass
    
    def get_domain_info(self) -> Dict:
        """获取领域信息"""
        return {
            "name": self.domain_name,
            "display_name": self.domain_display_name,
            "entity_types": list(self.entities.keys()),
            "entity_count": sum(len(v) for v in self.entities.values()),
            "template_count": sum(len(v) for v in self.templates.values()),
            "has_knowledge": len(self.knowledge) > 0
        }
