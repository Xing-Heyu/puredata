#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业错误生成器
- 错误强度分级（轻/中/重）
- 语义融合模板
- 拟真半真半假数据生成
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class HalfTrueResult:
    text: str
    correct_part: str
    error_part: str
    intensity: str
    quality_score: float
    quality_tier: str
    fusion_used: bool

class ProfessionalErrorGenerator:
    """专业错误生成器"""
    
    DEFAULT_FUSION_TEMPLATES = [
        "根据相关规定，{correct}。但实操中，{error}。",
        "{correct}。然而，部分企业存在{error}的情况。",
        "按照法律规定，{correct}。不过现实中，{error}也是常见现象。",
        "《相关法条》规定，{correct}。但很多企业会{error}。",
        "专业角度来说，{correct}。但在实际操作中，{error}。"
    ]
    
    INTENSITY_CONFIG = {
        "light": {
            "score_penalty": 0.10,
            "ratio": 0.40,
            "description": "表述不严谨，非核心违法",
            "quality_score_range": (0.70, 0.80)
        },
        "medium": {
            "score_penalty": 0.25,
            "ratio": 0.40,
            "description": "核心规则错误，常见企业违规",
            "quality_score_range": (0.55, 0.70)
        },
        "severe": {
            "score_penalty": 0.50,
            "ratio": 0.20,
            "description": "完全违背法条，极端错误",
            "quality_score_range": (0.35, 0.55)
        }
    }
    
    def __init__(self, domain_config_loader=None):
        self.domain_config_loader = domain_config_loader
    
    def generate(
        self,
        correct_rules: List[str],
        errors: List[str],
        intensity: str = "medium",
        fusion_templates: List[str] = None
    ) -> HalfTrueResult:
        if not correct_rules or not errors:
            return HalfTrueResult(
                text="",
                correct_part="",
                error_part="",
                intensity=intensity,
                quality_score=0.0,
                quality_tier="invalid",
                fusion_used=False
            )
        
        correct = random.choice(correct_rules)
        error = random.choice(errors)
        
        templates = fusion_templates or self.DEFAULT_FUSION_TEMPLATES
        template = random.choice(templates)
        
        text = template.replace("{正确规则}", correct).replace("{错误内容}", error)
        text = text.replace("{correct}", correct).replace("{error}", error)
        
        config = self.INTENSITY_CONFIG.get(intensity, self.INTENSITY_CONFIG["medium"])
        score_range = config["quality_score_range"]
        quality_score = round(random.uniform(*score_range), 2)
        
        if quality_score >= 0.75:
            quality_tier = "high"
        elif quality_score >= 0.50:
            quality_tier = "medium"
        else:
            quality_tier = "low"
        
        return HalfTrueResult(
            text=text,
            correct_part=correct,
            error_part=error,
            intensity=intensity,
            quality_score=quality_score,
            quality_tier=quality_tier,
            fusion_used=True
        )
    
    def generate_for_domain(
        self,
        domain: str,
        category: str,
        keyword: str,
        intensity: str = None
    ) -> HalfTrueResult:
        if not self.domain_config_loader:
            return self.generate([], [], intensity or "medium")
        
        if intensity is None:
            intensity = self._random_intensity()
        
        correct_rules = self.domain_config_loader.get_correct_rules(domain, category, keyword)
        errors = self.domain_config_loader.get_common_errors(domain, category, keyword, intensity)
        fusion_templates = self.domain_config_loader.get_fusion_templates(domain, category, keyword)
        
        return self.generate(correct_rules, errors, intensity, fusion_templates)
    
    def _random_intensity(self) -> str:
        r = random.random()
        if r < 0.40:
            return "light"
        elif r < 0.80:
            return "medium"
        else:
            return "severe"
    
    def generate_batch(
        self,
        domain: str,
        category: str,
        keywords: List[str],
        count: int = 10,
        intensity_distribution: Dict[str, float] = None
    ) -> List[HalfTrueResult]:
        if not keywords:
            return []
        
        if intensity_distribution is None:
            intensity_distribution = {"light": 0.4, "medium": 0.4, "severe": 0.2}
        
        results = []
        light_threshold = intensity_distribution.get("light", 0.4)
        medium_threshold = light_threshold + intensity_distribution.get("medium", 0.4)
        
        for i in range(count):
            keyword = keywords[i % len(keywords)]
            
            r = random.random()
            if r < light_threshold:
                intensity = "light"
            elif r < medium_threshold:
                intensity = "medium"
            else:
                intensity = "severe"
            
            result = self.generate_for_domain(domain, category, keyword, intensity)
            if result.text:
                results.append(result)
        
        return results

professional_error_generator = ProfessionalErrorGenerator()

def get_professional_error_generator(domain_config_loader=None) -> ProfessionalErrorGenerator:
    global professional_error_generator
    if domain_config_loader:
        professional_error_generator = ProfessionalErrorGenerator(domain_config_loader)
    return professional_error_generator

if __name__ == "__main__":
    print("="*60)
    print("专业错误生成器测试")
    print("="*60)
    
    generator = ProfessionalErrorGenerator()
    
    print("\n【测试1: 直接生成】")
    correct_rules = [
        "3年以上固定期限劳动合同，试用期不得超过6个月",
        "试用期工资不得低于劳动合同约定工资的80%"
    ]
    errors = [
        "试用期不需要缴纳社保",
        "试用期可以随时辞退员工"
    ]
    
    for intensity in ["light", "medium", "severe"]:
        result = generator.generate(correct_rules, errors, intensity)
        print(f"\n强度: {intensity}")
        print(f"  文本: {result.text}")
        print(f"  质量分: {result.quality_score}")
        print(f"  质量等级: {result.quality_tier}")
    
    print("\n【测试2: 领域配置生成】")
    try:
        from domain_config_loader import get_domain_config_loader
        loader = get_domain_config_loader()
        generator_with_loader = ProfessionalErrorGenerator(loader)
        
        keywords = ["试用期", "经济补偿", "加班费"]
        results = generator_with_loader.generate_batch("劳动合同", "核心条款", keywords, count=5)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. 强度: {result.intensity}")
            print(f"   文本: {result.text}")
            print(f"   质量分: {result.quality_score}")
    except Exception as e:
        print(f"领域配置加载失败: {e}")
    
    print("\n" + "="*60)
    print("测试完成")
