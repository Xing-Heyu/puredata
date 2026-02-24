#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
隐性噪音检测器
- 打分制（非布尔判断）
- 标签错误检测
- 领域偏移检测
- 概念混淆检测
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class NoiseDetectionResult:
    noise_score: float
    noise_type: Optional[str]
    related_score: float
    reason: str
    details: Dict

class ImplicitNoiseDetector:
    """隐性噪音检测器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "scoring_config.json"
        )
        self.noise_config = self._load_noise_config()
    
    def _load_noise_config(self) -> Dict:
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get("noise_scoring", {
                    "label_error_penalty": 0.40,
                    "domain_drift_penalty": 0.30,
                    "concept_confusion_penalty": 0.20
                })
        except Exception:
            pass
        return {
            "label_error_penalty": 0.40,
            "domain_drift_penalty": 0.30,
            "concept_confusion_penalty": 0.20
        }
    
    def detect(self, text: str, labeled_domain: str, domain_config_loader=None) -> NoiseDetectionResult:
        result = NoiseDetectionResult(
            noise_score=0.0,
            noise_type=None,
            related_score=1.0,
            reason="",
            details={}
        )
        
        label_error_score = self._detect_label_error(text, labeled_domain, domain_config_loader)
        domain_drift_score = self._detect_domain_drift(text, labeled_domain, domain_config_loader)
        concept_confusion_score = self._detect_concept_confusion(text, labeled_domain)
        
        result.details = {
            "label_error": label_error_score,
            "domain_drift": domain_drift_score,
            "concept_confusion": concept_confusion_score
        }
        
        detected_types = []
        
        if label_error_score > 0.5:
            detected_types.append("label_error")
            result.noise_type = "label_error"
            result.reason = "内容与标注领域不匹配"
        
        if domain_drift_score > 0.5:
            detected_types.append("domain_drift")
            if result.noise_type is None:
                result.noise_type = "domain_drift"
                result.reason = "内容偏移至相关领域"
        
        if concept_confusion_score > 0.5:
            detected_types.append("concept_confusion")
            if result.noise_type is None:
                result.noise_type = "concept_confusion"
                result.reason = "概念混淆，看似相关实则无关"
        
        for noise_type in detected_types:
            if noise_type == "label_error":
                result.noise_score += self.noise_config.get("label_error_penalty", 0.4)
            elif noise_type == "domain_drift":
                result.noise_score += self.noise_config.get("domain_drift_penalty", 0.3)
            elif noise_type == "concept_confusion":
                result.noise_score += self.noise_config.get("concept_confusion_penalty", 0.2)
        
        result.noise_score = min(1.0, result.noise_score)
        result.related_score = 1.0 - result.noise_score
        
        if result.noise_score == 0:
            result.reason = "内容与领域匹配"
        
        return result
    
    def _detect_label_error(self, text: str, labeled_domain: str, domain_config_loader) -> float:
        if not domain_config_loader:
            return 0.0
        
        try:
            from domain_config_loader import get_domain_config_loader
            loader = domain_config_loader or get_domain_config_loader()
            
            all_domains = loader.get_all_domains()
            if labeled_domain not in all_domains:
                return 0.0
            
            config = loader.get_config(labeled_domain)
            if not config:
                return 0.0
            
            core_terms = config.term_library.get("core_terms", [])
            hits = sum(1 for term in core_terms if term in text)
            
            if hits == 0:
                return 1.0
            elif hits < 3:
                return 0.5
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _detect_domain_drift(self, text: str, labeled_domain: str, domain_config_loader) -> float:
        if domain_config_loader:
            try:
                config = domain_config_loader.get_config(labeled_domain)
                if config:
                    border = config.domain_border
                    unrelated_domains = border.get("无关领域", [])
                    for domain_name in unrelated_domains:
                        if domain_name in text:
                            return 0.7
            except Exception:
                pass
        
        drift_keywords = {
            "劳动合同": {
                "个人所得税": ["个税", "税率", "纳税", "税务"],
                "民法典": ["侵权责任", "买卖合同", "租赁合同"],
                "刑法": ["犯罪", "刑罚", "刑事"]
            }
        }
        
        if labeled_domain in drift_keywords:
            for related_domain, keywords in drift_keywords[labeled_domain].items():
                for kw in keywords:
                    if kw in text:
                        return 0.7
        
        return 0.0
    
    def _detect_concept_confusion(self, text: str, labeled_domain: str) -> float:
        confusion_patterns = {
            "劳动合同": [
                ("腰间盘", "头痛"),
                ("感冒", "经济补偿"),
                ("股票", "加班费"),
                ("怀孕", "竞业限制")
            ]
        }
        
        if labeled_domain in confusion_patterns:
            for term1, term2 in confusion_patterns[labeled_domain]:
                if term1 in text and term2 in text:
                    return 0.8
        
        return 0.0
    
    def get_noise_level(self, noise_score: float) -> str:
        if noise_score >= 0.7:
            return "high"
        elif noise_score >= 0.4:
            return "medium"
        elif noise_score >= 0.1:
            return "low"
        else:
            return "none"

implicit_noise_detector = ImplicitNoiseDetector()

def get_implicit_noise_detector() -> ImplicitNoiseDetector:
    return implicit_noise_detector

if __name__ == "__main__":
    print("="*60)
    print("隐性噪音检测器测试")
    print("="*60)
    
    detector = ImplicitNoiseDetector()
    
    test_cases = [
        ("劳动合同", "劳动合同试用期最长6个月，试用期工资不得低于80%"),
        ("劳动合同", "工资超过5000要交个人所得税，税率是3%-45%"),
        ("劳动合同", "腰间盘突出会导致头痛和恶心"),
        ("劳动合同", "举证责任倒置适用于医疗纠纷、产品责任等侵权案件"),
        ("劳动合同", "试用期不需要缴纳社保，这是企业常见做法")
    ]
    
    for domain, text in test_cases:
        result = detector.detect(text, domain)
        print(f"\n领域: {domain}")
        print(f"文本: {text[:40]}...")
        print(f"噪音得分: {result.noise_score}")
        print(f"噪音类型: {result.noise_type or '无'}")
        print(f"相关度: {result.related_score}")
        print(f"原因: {result.reason}")
        print(f"噪音等级: {detector.get_noise_level(result.noise_score)}")
    
    print("\n" + "="*60)
    print("测试完成")
