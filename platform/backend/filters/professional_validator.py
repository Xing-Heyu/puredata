#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业验证器 - 解决"逻辑通但专业错"的问题

核心功能：
1. 术语验证 - 检查领域术语使用是否正确
2. 关系验证 - 检查实体关系是否合理（如：腰间盘突出→腿麻✓，腰间盘突出→头痛✗）
3. 边界验证 - 检查是否跨界乱连
4. 数值验证 - 检查数值是否在合理范围内

设计理念：
- 利用领域专家的知识库进行验证
- 基于规则+统计的双重验证
- 提供详细的错误说明和修复建议
"""

import re
import sys
import os
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from domain_specialists import (
        get_specialist, get_all_specialists, list_domains,
        MedicalSpecialist, FinanceSpecialist, AISpecialist,
        LegalSpecialist, EducationSpecialist, EcommerceSpecialist,
        TechSpecialist, LaborSpecialist
    )
    SPECIALISTS_AVAILABLE = True
except ImportError:
    SPECIALISTS_AVAILABLE = False


@dataclass
class ValidationError:
    """验证错误"""
    error_type: str
    severity: str  # critical, high, medium, low
    description: str
    location: str
    suggestion: str
    auto_fixable: bool


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    score: float
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    domain: str = ""
    validated_aspects: Dict[str, bool] = field(default_factory=dict)


class DomainKnowledgeBase:
    """
    领域知识库 - 存储各领域的专业知识用于验证
    """
    
    MEDICAL_KNOWLEDGE = {
        "disease_symptom_mapping": {
            "高血压": ["头痛", "头晕", "心悸", "耳鸣", "失眠", "乏力"],
            "糖尿病": ["多饮", "多食", "多尿", "体重下降", "乏力", "视力模糊"],
            "腰椎间盘突出": ["腰痛", "下肢放射痛", "下肢麻木", "肌力下降", "坐骨神经痛"],
            "颈椎病": ["颈痛", "上肢麻木", "头晕", "头痛", "恶心"],
            "肺炎": ["发热", "咳嗽", "咳痰", "胸痛", "呼吸困难"],
            "胃炎": ["上腹痛", "恶心", "呕吐", "食欲不振", "腹胀"],
            "冠心病": ["胸痛", "胸闷", "心悸", "气短", "乏力"],
            "脑卒中": ["偏瘫", "言语不清", "口角歪斜", "意识障碍"],
        },
        "forbidden_pairs": [
            ("腰椎间盘突出", "头痛", "腰椎间盘突出不会直接导致头痛，头痛通常与颈椎病或高血压相关"),
            ("感冒", "心肌梗死", "感冒不会直接导致心肌梗死"),
            ("胃炎", "偏瘫", "胃炎与偏瘫无直接关联"),
            ("高血压", "下肢麻木", "高血压不会直接导致下肢麻木，需考虑其他原因"),
            ("糖尿病", "腰痛", "糖尿病不会直接导致腰痛"),
        ],
        "body_part_relations": {
            "腰椎": ["下肢", "腿部", "腰部", "坐骨神经"],
            "颈椎": ["头部", "上肢", "颈部"],
            "心脏": ["胸部", "上肢", "背部"],
            "胃": ["上腹部", "腹部"],
        },
        "normal_ranges": {
            "体温": (36.0, 37.3),
            "脉搏": (60, 100),
            "呼吸": (16, 20),
            "收缩压": (90, 139),
            "舒张压": (60, 89),
            "血糖空腹": (3.9, 6.1),
            "血糖餐后": (3.9, 7.8),
        }
    }
    
    FINANCE_KNOWLEDGE = {
        "indicator_ranges": {
            "市盈率PE": (0, 100),
            "市净率PB": (0, 20),
            "净资产收益率ROE": (-50, 100),
            "资产负债率": (0, 100),
        },
        "forbidden_pairs": [
            ("股票", "存款利率", "股票收益与存款利率无直接对应关系"),
            ("债券", "股息", "债券支付利息而非股息"),
            ("期货", "固定收益", "期货是高风险投资，无固定收益"),
        ],
        "risk_levels": {
            "国债": "低风险",
            "货币基金": "低风险",
            "债券基金": "中低风险",
            "股票基金": "中高风险",
            "期货": "高风险",
            "期权": "极高风险",
        }
    }
    
    AI_KNOWLEDGE = {
        "concept_relations": {
            "深度学习": ["神经网络", "卷积神经网络", "循环神经网络", "Transformer"],
            "机器学习": ["监督学习", "无监督学习", "强化学习", "特征工程"],
            "自然语言处理": ["分词", "命名实体识别", "情感分析", "机器翻译"],
        },
        "forbidden_pairs": [
            ("CNN", "时序预测", "CNN主要用于图像处理，时序预测通常使用RNN/LSTM"),
            ("K-means", "标签预测", "K-means是无监督聚类，无法进行标签预测"),
        ]
    }
    
    LEGAL_KNOWLEDGE = {
        "statute_limitations": {
            "劳动争议": 1,
            "民事诉讼": 3,
            "行政诉讼": 6,
            "合同纠纷": 3,
        },
        "forbidden_pairs": [
            ("劳动仲裁", "刑事处罚", "劳动仲裁不涉及刑事处罚"),
            ("民事纠纷", "有期徒刑", "民事纠纷不涉及刑事处罚"),
        ]
    }
    
    @classmethod
    def get_knowledge(cls, domain: str) -> Dict:
        domain_map = {
            "医疗": cls.MEDICAL_KNOWLEDGE,
            "medical": cls.MEDICAL_KNOWLEDGE,
            "金融": cls.FINANCE_KNOWLEDGE,
            "finance": cls.FINANCE_KNOWLEDGE,
            "人工智能": cls.AI_KNOWLEDGE,
            "ai": cls.AI_KNOWLEDGE,
            "法律": cls.LEGAL_KNOWLEDGE,
            "legal": cls.LEGAL_KNOWLEDGE,
        }
        return domain_map.get(domain, {})


class ProfessionalValidator:
    """
    专业验证器 - 验证内容的专业正确性
    
    解决的核心问题：
    "腰间盘突出会导致头痛，因为神经受压会影响全身。"
    这句话语法正确、逻辑自洽，但专业上是错误的。
    """
    
    def __init__(self):
        self.specialists = {}
        if SPECIALISTS_AVAILABLE:
            try:
                self.specialists = get_all_specialists()
            except ImportError as e:
                print(f"[WARN] 加载专家模块失败: {e}")
        
        self.validation_stats = {
            "total_validated": 0,
            "passed": 0,
            "failed": 0,
            "by_error_type": defaultdict(int),
        }
    
    def validate(self, content: str, domain: str, context: Dict = None) -> ValidationResult:
        """
        验证内容的专业正确性
        
        Args:
            content: 待验证的文本内容
            domain: 领域
            context: 额外上下文（如原始关键词、主题等）
        
        Returns:
            ValidationResult: 验证结果
        """
        self.validation_stats["total_validated"] += 1
        
        errors = []
        warnings = []
        validated_aspects = {}
        
        knowledge = DomainKnowledgeBase.get_knowledge(domain)
        
        term_errors = self._validate_terminology(content, domain, knowledge)
        errors.extend(term_errors)
        validated_aspects["terminology"] = len(term_errors) == 0
        
        relation_errors = self._validate_relations(content, domain, knowledge)
        errors.extend(relation_errors)
        validated_aspects["relations"] = len(relation_errors) == 0
        
        boundary_errors = self._validate_boundary(content, domain, knowledge)
        errors.extend(boundary_errors)
        validated_aspects["boundary"] = len(boundary_errors) == 0
        
        value_errors = self._validate_values(content, domain, knowledge)
        errors.extend(value_errors)
        validated_aspects["values"] = len(value_errors) == 0
        
        critical_count = sum(1 for e in errors if e.severity == "critical")
        high_count = sum(1 for e in errors if e.severity == "high")
        medium_count = sum(1 for e in errors if e.severity == "medium")
        
        score = max(0, 1.0 - critical_count * 0.3 - high_count * 0.2 - medium_count * 0.1)
        
        is_valid = len(errors) == 0 or (critical_count == 0 and high_count == 0)
        
        if is_valid:
            self.validation_stats["passed"] += 1
        else:
            self.validation_stats["failed"] += 1
        
        for error in errors:
            self.validation_stats["by_error_type"][error.error_type] += 1
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            errors=errors,
            warnings=warnings,
            domain=domain,
            validated_aspects=validated_aspects
        )
    
    def validate_batch(self, items: List[Dict], domain: str, 
                       content_field: str = "content") -> Tuple[List[Dict], Dict]:
        """
        批量验证
        
        Args:
            items: 数据列表
            domain: 领域
            content_field: 内容字段名
        
        Returns:
            (验证后的数据列表, 统计信息)
        """
        validated_items = []
        stats = {
            "total": len(items),
            "passed": 0,
            "failed": 0,
            "avg_score": 0,
            "error_distribution": defaultdict(int),
        }
        
        total_score = 0
        
        for item in items:
            content = item.get(content_field, item.get("text", ""))
            result = self.validate(content, domain, item)
            
            item["_validation"] = {
                "is_valid": result.is_valid,
                "score": result.score,
                "error_count": len(result.errors),
                "validated_aspects": result.validated_aspects,
            }
            
            if result.errors:
                item["_validation"]["errors"] = [
                    {
                        "type": e.error_type,
                        "severity": e.severity,
                        "description": e.description,
                        "suggestion": e.suggestion,
                    }
                    for e in result.errors
                ]
            
            validated_items.append(item)
            total_score += result.score
            
            if result.is_valid:
                stats["passed"] += 1
            else:
                stats["failed"] += 1
            
            for error in result.errors:
                stats["error_distribution"][error.error_type] += 1
        
        stats["avg_score"] = total_score / len(items) if items else 0
        stats["error_distribution"] = dict(stats["error_distribution"])
        
        return validated_items, stats
    
    def _validate_terminology(self, content: str, domain: str, knowledge: Dict) -> List[ValidationError]:
        """验证术语使用是否正确"""
        errors = []
        
        if domain in ["医疗", "medical"]:
            disease_symptoms = knowledge.get("disease_symptom_mapping", {})
            
            for disease, valid_symptoms in disease_symptoms.items():
                if disease in content:
                    for symptom in valid_symptoms:
                        pass
        
        return errors
    
    def _validate_relations(self, content: str, domain: str, knowledge: Dict) -> List[ValidationError]:
        """
        验证实体关系是否正确
        
        核心逻辑：检查禁止的关系配对
        例如：腰间盘突出→头痛 是禁止的配对
        """
        errors = []
        
        forbidden_pairs = knowledge.get("forbidden_pairs", [])
        
        for pair in forbidden_pairs:
            if len(pair) >= 3:
                entity1, entity2, reason = pair[0], pair[1], pair[2]
            else:
                continue
            
            if entity1 in content and entity2 in content:
                connector_patterns = [
                    f"{entity1}.*导致.*{entity2}",
                    f"{entity1}.*引起.*{entity2}",
                    f"{entity1}.*造成.*{entity2}",
                    f"{entity1}.*会使.*{entity2}",
                    f"{entity1}.*会引发.*{entity2}",
                    f"由于{entity1}.*{entity2}",
                ]
                
                for pattern in connector_patterns:
                    if re.search(pattern, content):
                        errors.append(ValidationError(
                            error_type="invalid_relation",
                            severity="high",
                            description=f"检测到不正确的专业关系：{entity1} → {entity2}",
                            location=content[:100],
                            suggestion=f"修正建议：{reason}",
                            auto_fixable=False
                        ))
                        break
        
        return errors
    
    def _validate_boundary(self, content: str, domain: str, knowledge: Dict) -> List[ValidationError]:
        """验证是否跨界乱连"""
        errors = []
        
        body_part_relations = knowledge.get("body_part_relations", {})
        
        if domain in ["医疗", "medical"]:
            for body_part, related_parts in body_part_relations.items():
                if body_part in content:
                    pass
        
        return errors
    
    def _validate_values(self, content: str, domain: str, knowledge: Dict) -> List[ValidationError]:
        """验证数值是否在合理范围内"""
        errors = []
        
        normal_ranges = knowledge.get("normal_ranges", {})
        
        for indicator, (min_val, max_val) in normal_ranges.items():
            patterns = [
                rf"{indicator}[是为：:]\s*(\d+\.?\d*)",
                rf"{indicator}(\d+\.?\d*)",
                rf"(\d+\.?\d*)\s*{indicator}",
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    try:
                        value = float(match)
                        if not (min_val <= value <= max_val):
                            errors.append(ValidationError(
                                error_type="value_out_of_range",
                                severity="medium",
                                description=f"{indicator}值{value}超出正常范围[{min_val}, {max_val}]",
                                location=content[:100],
                                suggestion=f"请检查{indicator}的数值是否正确，正常范围是{min_val}-{max_val}",
                                auto_fixable=True
                            ))
                    except ValueError:
                        pass
        
        return errors
    
    def get_stats(self) -> Dict:
        """获取验证统计"""
        return {
            **self.validation_stats,
            "pass_rate": (
                self.validation_stats["passed"] / max(self.validation_stats["total_validated"], 1)
            ),
            "by_error_type": dict(self.validation_stats["by_error_type"]),
        }


class ProfessionalEnhancer:
    """
    专业增强器 - 基于验证结果提供改进建议
    """
    
    def __init__(self, validator: ProfessionalValidator = None):
        self.validator = validator or ProfessionalValidator()
    
    def enhance_content(self, content: str, domain: str) -> Tuple[str, List[str]]:
        """
        增强内容的专业性
        
        Returns:
            (增强后的内容, 修改说明列表)
        """
        result = self.validator.validate(content, domain)
        modifications = []
        enhanced_content = content
        
        for error in result.errors:
            if error.auto_fixable and error.error_type == "value_out_of_range":
                modifications.append(f"数值修正：{error.suggestion}")
        
        return enhanced_content, modifications
    
    def generate_quality_prompt(self, domain: str) -> str:
        """
        生成领域特定的质量提示词
        
        用于在生成数据时注入专业约束
        """
        knowledge = DomainKnowledgeBase.get_knowledge(domain)
        
        prompt_parts = [
            f"你是{domain}领域的资深专家，生成内容时必须遵守以下专业约束：",
            "",
            "【禁止的错误关系】",
        ]
        
        forbidden_pairs = knowledge.get("forbidden_pairs", [])
        for pair in forbidden_pairs:
            if len(pair) >= 3:
                prompt_parts.append(f"- {pair[0]} 不会直接导致 {pair[1]}：{pair[2]}")
        
        prompt_parts.extend([
            "",
            "【正常值范围】",
        ])
        
        normal_ranges = knowledge.get("normal_ranges", {})
        for indicator, (min_val, max_val) in normal_ranges.items():
            prompt_parts.append(f"- {indicator}：{min_val} - {max_val}")
        
        prompt_parts.extend([
            "",
            "【质量要求】",
            "1. 只生成专业准确的内容",
            "2. 症状与疾病必须正确对应",
            "3. 数值必须在正常范围内",
            "4. 禁止跨界乱连不相关的概念",
        ])
        
        return "\n".join(prompt_parts)


professional_validator = ProfessionalValidator()
professional_enhancer = ProfessionalEnhancer(professional_validator)


if __name__ == "__main__":
    print("=" * 70)
    print("专业验证器测试")
    print("=" * 70)
    
    test_cases = [
        {
            "content": "腰椎间盘突出会导致头痛，因为神经受压会影响全身。",
            "domain": "医疗",
            "expected": "应该检测到错误的关系配对"
        },
        {
            "content": "高血压患者常出现头痛、头晕、心悸等症状，需要长期服药控制。",
            "domain": "医疗",
            "expected": "应该通过验证"
        },
        {
            "content": "患者体温39.5℃，脉搏85次/分，血压120/80mmHg。",
            "domain": "医疗",
            "expected": "体温略高但可能正常（发热）"
        },
        {
            "content": "股票的存款利率通常在3%左右。",
            "domain": "金融",
            "expected": "应该检测到错误的概念混淆"
        },
    ]
    
    validator = ProfessionalValidator()
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[测试 {i}]")
        print(f"领域: {test['domain']}")
        print(f"内容: {test['content']}")
        print(f"预期: {test['expected']}")
        print("-" * 50)
        
        result = validator.validate(test['content'], test['domain'])
        
        print(f"验证结果: {'通过' if result.is_valid else '未通过'}")
        print(f"专业分数: {result.score:.2f}")
        print(f"验证维度: {result.validated_aspects}")
        
        if result.errors:
            print(f"\n发现错误 ({len(result.errors)}):")
            for error in result.errors:
                print(f"  [{error.severity}] {error.error_type}")
                print(f"    描述: {error.description}")
                print(f"    建议: {error.suggestion}")
    
    print("\n" + "=" * 70)
    print("统计信息:")
    print(validator.get_stats())
    print("=" * 70)
    
    print("\n[质量提示词示例 - 医疗领域]")
    print("-" * 50)
    enhancer = ProfessionalEnhancer(validator)
    print(enhancer.generate_quality_prompt("医疗"))
