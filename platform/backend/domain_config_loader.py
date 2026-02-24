#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域配置加载器
- 结构化分层配置加载
- 版本管理
- 热加载预留接口
"""

import json
import os
import random
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class DomainKnowledge:
    domain: str
    version: str
    knowledge: Dict
    domain_border: Dict
    term_library: Dict
    raw_config: Dict

class DomainConfigLoader:
    """领域配置加载器"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(
            os.path.dirname(__file__), "domain_configs"
        )
        self.configs: Dict[str, DomainKnowledge] = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            return
        
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.config_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    domain = config.get("domain", filename.replace('.json', ''))
                    self.configs[domain] = DomainKnowledge(
                        domain=domain,
                        version=config.get("version", "v1.0"),
                        knowledge=config.get("knowledge", {}),
                        domain_border=config.get("domain_border", {}),
                        term_library=config.get("term_library", {}),
                        raw_config=config
                    )
                except Exception as e:
                    print(f"[领域配置] 加载失败: {filename}, 错误: {e}")
    
    def get_config(self, domain: str) -> Optional[DomainKnowledge]:
        return self.configs.get(domain)
    
    def get_all_domains(self) -> List[str]:
        return list(self.configs.keys())
    
    def get_correct_rules(self, domain: str, category: str, keyword: str) -> List[str]:
        config = self.get_config(domain)
        if not config:
            return []
        
        knowledge = config.knowledge.get(category, {})
        item = knowledge.get(keyword, {})
        return item.get("正确规则", [])
    
    def get_common_errors(self, domain: str, category: str, keyword: str, intensity: str = None) -> List[str]:
        config = self.get_config(domain)
        if not config:
            return []
        
        knowledge = config.knowledge.get(category, {})
        item = knowledge.get(keyword, {})
        errors = item.get("常见错误", {})
        
        if intensity:
            return errors.get(intensity, [])
        
        all_errors = []
        for level_errors in errors.values():
            all_errors.extend(level_errors)
        return all_errors
    
    def get_fusion_templates(self, domain: str, category: str, keyword: str) -> List[str]:
        config = self.get_config(domain)
        if not config:
            return []
        
        knowledge = config.knowledge.get(category, {})
        item = knowledge.get(keyword, {})
        return item.get("融合模板", [])
    
    def get_domain_border(self, domain: str) -> Dict:
        config = self.get_config(domain)
        if not config:
            return {}
        return config.domain_border
    
    def get_forbidden_pairs(self, domain: str) -> List[tuple]:
        config = self.get_config(domain)
        if not config:
            return []
        
        pairs = config.term_library.get("forbidden_pairs", [])
        return [tuple(pair) if isinstance(pair, list) else pair for pair in pairs]
    
    def is_in_domain(self, domain: str, text: str) -> Dict:
        config = self.get_config(domain)
        if not config:
            return {"in_domain": True, "confidence": 0.5, "reason": "无配置"}
        
        border = config.domain_border
        core_terms = config.term_library.get("core_terms", [])
        
        core_hit = sum(1 for term in core_terms if term in text)
        
        related_domains = border.get("相关领域", [])
        unrelated_domains = border.get("无关领域", [])
        
        border_examples = border.get("边界示例", [])
        border_penalty = 0.0
        border_details = []
        
        for example in border_examples:
            keyword = example.get("关键词", "")
            if keyword in text:
                not_belong = example.get("不属于", [])
                for nb in not_belong:
                    if nb in text:
                        border_penalty += 0.15
                        border_details.append(f"{keyword}+{nb}")
        
        unrelated_hit = 0
        for unrelated in unrelated_domains:
            if unrelated in text:
                unrelated_hit += 1
        
        confidence = min(1.0, core_hit / 5) - unrelated_hit * 0.2 - border_penalty
        confidence = max(0.0, min(1.0, confidence))
        
        in_domain = confidence >= 0.5
        
        reason = ""
        if core_hit > 0:
            reason = f"命中{core_hit}个核心术语"
        if unrelated_hit > 0:
            reason += f"，包含{unrelated_hit}个无关领域内容"
        if border_details:
            reason += f"，边界违规: {', '.join(border_details)}"
        
        return {
            "in_domain": in_domain,
            "confidence": round(confidence, 2),
            "core_term_hits": core_hit,
            "unrelated_hits": unrelated_hit,
            "border_violations": border_details,
            "reason": reason
        }
    
    def generate_half_true_text(self, domain: str, category: str, keyword: str, intensity: str = "medium") -> Dict:
        correct_rules = self.get_correct_rules(domain, category, keyword)
        errors = self.get_common_errors(domain, category, keyword, intensity)
        templates = self.get_fusion_templates(domain, category, keyword)
        
        if not correct_rules or not errors:
            return {"success": False, "reason": "缺少配置数据"}
        
        correct = random.choice(correct_rules)
        error = random.choice(errors)
        
        if templates:
            template = random.choice(templates)
            text = template.replace("{正确规则}", correct).replace("{错误内容}", error)
        else:
            text = f"{correct}，但{error}。"
        
        return {
            "success": True,
            "text": text,
            "correct_part": correct,
            "error_part": error,
            "intensity": intensity,
            "quality_tier": "medium"
        }
    
    def reload_config(self, domain: str = None):
        try:
            if domain:
                filepath = os.path.join(self.config_dir, f"{domain}.json")
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    self.configs[domain] = DomainKnowledge(
                        domain=domain,
                        version=config.get("version", "v1.0"),
                        knowledge=config.get("knowledge", {}),
                        domain_border=config.get("domain_border", {}),
                        term_library=config.get("term_library", {}),
                        raw_config=config
                    )
            else:
                self._load_all_configs()
            
            print(f"[领域配置] 配置已重新加载: {domain or '全部'}")
        except json.JSONDecodeError as e:
            print(f"[领域配置] JSON解析失败: {e}")
        except Exception as e:
            print(f"[领域配置] 重新加载失败: {e}")

domain_config_loader = DomainConfigLoader()

def get_domain_config_loader() -> DomainConfigLoader:
    return domain_config_loader

if __name__ == "__main__":
    print("="*60)
    print("领域配置加载器测试")
    print("="*60)
    
    loader = DomainConfigLoader()
    
    print(f"\n已加载领域: {loader.get_all_domains()}")
    
    config = loader.get_config("劳动合同")
    if config:
        print(f"\n【劳动合同配置】")
        print(f"  版本: {config.version}")
        print(f"  知识分类: {list(config.knowledge.keys())}")
    
    print(f"\n【试用期正确规则】")
    rules = loader.get_correct_rules("劳动合同", "核心条款", "试用期")
    for i, rule in enumerate(rules[:3], 1):
        print(f"  {i}. {rule}")
    
    print(f"\n【试用期常见错误(中度)】")
    errors = loader.get_common_errors("劳动合同", "核心条款", "试用期", "medium")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    
    print(f"\n【生成半真半假文本】")
    result = loader.generate_half_true_text("劳动合同", "核心条款", "试用期", "medium")
    if result["success"]:
        print(f"  文本: {result['text']}")
        print(f"  正确部分: {result['correct_part']}")
        print(f"  错误部分: {result['error_part']}")
    
    print(f"\n【领域边界检测】")
    test_texts = [
        "劳动合同试用期最长6个月，试用期工资不得低于80%",
        "工资超过5000要交个人所得税，税率是3%-45%",
        "腰间盘突出会导致头痛和恶心"
    ]
    for text in test_texts:
        result = loader.is_in_domain("劳动合同", text)
        print(f"  文本: {text[:30]}...")
        print(f"    结果: {'在领域内' if result['in_domain'] else '不在领域内'}, 置信度: {result['confidence']}")
    
    print("\n" + "="*60)
    print("测试完成")
