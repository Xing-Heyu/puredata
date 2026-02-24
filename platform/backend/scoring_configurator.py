#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量评分配置器
- 权重可配置
- 阈值可配置
- 领域覆盖（不同领域不同侧重）
"""

import json
import os
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ScoringResult:
    final_score: float
    quality_tier: str
    components: Dict[str, float]
    domain: str
    config_used: Dict

class QualityScoringConfigurator:
    """质量评分配置器"""
    
    DEFAULT_CONFIG = {
        "weights": {
            "syntax": 0.30,
            "domain_terms": 0.40,
            "professional_correct": 0.20,
            "noise_detection": 0.10
        },
        "thresholds": {
            "high": 0.80,
            "medium": 0.60,
            "low": 0.40
        }
    }
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "scoring_config.json"
        )
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict:
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[评分配置器] 加载配置失败: {e}，使用默认配置")
        return {"scoring_config": self.DEFAULT_CONFIG}
    
    def _validate_config(self):
        scoring = self.config.get("scoring_config", {})
        weights = scoring.get("weights", self.DEFAULT_CONFIG["weights"])
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            print(f"[评分配置器] 警告: 权重总和={total}，应为1.0")
    
    def get_weights(self, domain: str = None) -> Dict[str, float]:
        scoring = self.config.get("scoring_config", {})
        base_weights = scoring.get("weights", self.DEFAULT_CONFIG["weights"]).copy()
        
        if domain:
            overrides = scoring.get("domain_overrides", {})
            if domain in overrides:
                domain_weights = overrides[domain].get("weights", {})
                for key in base_weights:
                    if key in domain_weights:
                        base_weights[key] = domain_weights[key]
        
        total = sum(base_weights.values())
        if abs(total - 1.0) > 0.01:
            for key in base_weights:
                base_weights[key] = base_weights[key] / total
        
        return base_weights
    
    def get_thresholds(self) -> Dict[str, float]:
        scoring = self.config.get("scoring_config", {})
        return scoring.get("thresholds", self.DEFAULT_CONFIG["thresholds"])
    
    def get_error_intensity(self) -> Dict:
        return self.config.get("error_intensity", {
            "light": {"score_penalty": 0.10, "ratio": 0.40},
            "medium": {"score_penalty": 0.25, "ratio": 0.40},
            "severe": {"score_penalty": 0.50, "ratio": 0.20}
        })
    
    def get_noise_scoring(self) -> Dict:
        return self.config.get("noise_scoring", {
            "label_error_penalty": 0.40,
            "domain_drift_penalty": 0.30,
            "concept_confusion_penalty": 0.20
        })
    
    def calculate_score(
        self,
        syntax_score: float,
        domain_terms_score: float,
        professional_correct_score: float,
        noise_detection_score: float,
        domain: str = None
    ) -> ScoringResult:
        weights = self.get_weights(domain)
        thresholds = self.get_thresholds()
        
        components = {
            "syntax": round(syntax_score * weights.get("syntax", 0.3), 3),
            "domain_terms": round(domain_terms_score * weights.get("domain_terms", 0.4), 3),
            "professional_correct": round(professional_correct_score * weights.get("professional_correct", 0.2), 3),
            "noise_detection": round(noise_detection_score * weights.get("noise_detection", 0.1), 3)
        }
        
        final_score = sum(components.values())
        final_score = max(0.0, min(1.0, final_score))
        
        if final_score >= thresholds["high"]:
            quality_tier = "high"
        elif final_score >= thresholds["medium"]:
            quality_tier = "medium"
        elif final_score >= thresholds["low"]:
            quality_tier = "low"
        else:
            quality_tier = "reject"
        
        return ScoringResult(
            final_score=round(final_score, 3),
            quality_tier=quality_tier,
            components=components,
            domain=domain or "通用",
            config_used={
                "weights": weights,
                "thresholds": thresholds
            }
        )
    
    def score_text(
        self,
        text: str,
        domain: str = None,
        domain_terms_hits: list = None,
        error_intensity: str = None,
        noise_type: str = None
    ) -> ScoringResult:
        syntax_score = self._calc_syntax_score(text)
        domain_terms_score = self._calc_domain_terms_score(text, domain_terms_hits)
        professional_correct_score = self._calc_professional_score(error_intensity)
        noise_detection_score = self._calc_noise_score(noise_type)
        
        return self.calculate_score(
            syntax_score,
            domain_terms_score,
            professional_correct_score,
            noise_detection_score,
            domain
        )
    
    def _calc_syntax_score(self, text: str) -> float:
        if not text:
            return 0.0
        
        score = 1.0
        
        punct_count = sum(1 for c in text if c in '。！？，、；：""''（）【】')
        if punct_count == 0 and len(text) > 50:
            score -= 0.2
        
        if len(text) < 20:
            score -= 0.3
        elif len(text) > 2000:
            score -= 0.1
        
        char_variety = len(set(text)) / len(text) if text else 0
        if char_variety < 0.1:
            score -= 0.2
        
        repeat_patterns = ['嗯嗯', '好的好的', '重复重复', '...']
        for pattern in repeat_patterns:
            if pattern in text:
                score -= 0.15
        
        return max(0.0, min(1.0, score))
    
    def _calc_domain_terms_score(self, text: str, hits: list = None) -> float:
        if not hits:
            return 0.5
        
        max_terms = self.config.get("scoring_config", {}).get("max_terms_for_full_score", 5)
        hit_ratio = min(1.0, len(hits) / max_terms)
        return 0.5 + hit_ratio * 0.5
    
    def _calc_professional_score(self, error_intensity: str = None) -> float:
        valid_intensities = ["light", "medium", "severe"]
        if error_intensity and error_intensity not in valid_intensities:
            error_intensity = None
        
        if not error_intensity:
            return 1.0
        
        intensity_config = self.get_error_intensity()
        if error_intensity in intensity_config:
            penalty = intensity_config[error_intensity].get("score_penalty", 0)
            return max(0.0, 1.0 - penalty)
        
        return 1.0
    
    def _calc_noise_score(self, noise_type: str = None) -> float:
        valid_noise_types = ["label_error", "domain_drift", "concept_confusion"]
        if noise_type and noise_type not in valid_noise_types:
            noise_type = None
        
        if not noise_type:
            return 1.0
        
        noise_config = self.get_noise_scoring()
        if noise_type == "label_error":
            return 1.0 - noise_config.get("label_error_penalty", 0.4)
        elif noise_type == "domain_drift":
            return 1.0 - noise_config.get("domain_drift_penalty", 0.3)
        elif noise_type == "concept_confusion":
            return 1.0 - noise_config.get("concept_confusion_penalty", 0.2)
        
        return 1.0
    
    def reload_config(self):
        """重新加载配置（热加载预留接口）"""
        self.config = self._load_config()
        self._validate_config()
        print("[评分配置器] 配置已重新加载")

scoring_configurator = QualityScoringConfigurator()

def get_scoring_configurator() -> QualityScoringConfigurator:
    return scoring_configurator

if __name__ == "__main__":
    print("="*60)
    print("质量评分配置器测试")
    print("="*60)
    
    configurator = QualityScoringConfigurator()
    
    print("\n【默认权重】")
    print(json.dumps(configurator.get_weights(), indent=2, ensure_ascii=False))
    
    print("\n【医疗领域权重】")
    print(json.dumps(configurator.get_weights("医疗"), indent=2, ensure_ascii=False))
    
    print("\n【劳动合同领域权重】")
    print(json.dumps(configurator.get_weights("劳动合同"), indent=2, ensure_ascii=False))
    
    print("\n【评分测试】")
    test_cases = [
        ("劳动合同", None, None, None),
        ("劳动合同", ["试用期", "经济补偿"], "medium", None),
        ("医疗", ["诊断", "治疗"], None, "label_error"),
        ("金融", ["股票", "债券"], "light", None),
    ]
    
    for domain, terms, error, noise in test_cases:
        result = configurator.score_text(
            "这是一段测试文本",
            domain=domain,
            domain_terms_hits=terms,
            error_intensity=error,
            noise_type=noise
        )
        print(f"\n领域: {domain}")
        print(f"  最终得分: {result.final_score}")
        print(f"  质量等级: {result.quality_tier}")
        print(f"  各项得分: {result.components}")
    
    print("\n" + "="*60)
    print("测试完成")
