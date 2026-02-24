#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
垂直领域词库校验层
解决问题：逻辑通但专业错误（如"腰间盘"+"头痛"乱连）

功能：
1. 核心术语命中检测 - 加分
2. 禁止关联词检测 - 降分/过滤
3. 重复句子检测 - 过滤
4. 并行权重评分
"""

import re
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

DOMAIN_TERM_LIBRARIES = {
    "人工智能": {
        "core_terms": [
            "深度学习", "机器学习", "神经网络", "卷积神经网络", "循环神经网络",
            "Transformer", "注意力机制", "自然语言处理", "计算机视觉", "强化学习",
            "生成对抗网络", "自编码器", "迁移学习", "预训练", "微调", "词向量",
            "嵌入", "损失函数", "优化器", "梯度下降", "反向传播", "过拟合",
            "正则化", "Dropout", "Batch Normalization", "超参数", "特征提取",
            "模型压缩", "知识蒸馏", "联邦学习", "多模态", "大语言模型", "GPT",
            "BERT", "参数量", "推理", "训练", "数据集", "标注", "监督学习",
            "无监督学习", "半监督学习", "零样本", "少样本", "提示工程"
        ],
        "forbidden_pairs": [
            ("腰间盘", "头痛"),
            ("感冒", "神经网络"),
            ("怀孕", "梯度下降"),
            ("手术", "模型训练"),
        ],
        "required_density": 0.02
    },
    "医疗": {
        "core_terms": [
            "诊断", "治疗", "症状", "病理", "临床", "患者", "医学影像", "CT", "MRI",
            "超声", "心电图", "化验", "血常规", "尿常规", "肝功能", "肾功能",
            "血糖", "血压", "体温", "脉搏", "呼吸", "处方", "用药", "剂量",
            "不良反应", "禁忌症", "适应症", "手术", "麻醉", "康复", "预后",
            "并发症", "病史", "体格检查", "影像学", "实验室检查", "门诊",
            "住院", "急诊", "重症", "护理", "医嘱", "病历", "随访"
        ],
        "forbidden_pairs": [
            ("腰间盘", "头痛"),
            ("感冒", "手术切除"),
            ("发烧", "化疗"),
            ("轻微擦伤", "ICU"),
            ("普通感冒", "肿瘤切除"),
        ],
        "required_density": 0.03
    },
    "金融": {
        "core_terms": [
            "股票", "债券", "基金", "期货", "期权", "衍生品", "风险控制", "流动性",
            "偿付能力", "资产负债", "收益率", "波动率", "对冲", "套利", "杠杆",
            "保证金", "清算", "结算", "托管", "信用评级", "违约风险", "市场风险",
            "操作风险", "合规", "监管", "资本充足率", "不良资产", "拨备覆盖率",
            "净息差", "ROE", "ROA", "市盈率", "市净率", "估值", "IPO", "并购",
            "重组", "分红", "股息", "利息", "本金", "投资组合", "资产配置"
        ],
        "forbidden_pairs": [
            ("腰间盘", "股票"),
            ("感冒", "收益率"),
            ("怀孕", "杠杆"),
            ("手术", "投资组合"),
        ],
        "required_density": 0.025
    },
    "劳动合同": {
        "core_terms": [
            "劳动合同", "用人单位", "劳动者", "工资", "薪酬", "社保", "五险一金",
            "加班", "休假", "年假", "病假", "产假", "婚假", "试用期", "转正",
            "解除合同", "终止合同", "经济补偿", "赔偿金", "违约金", "竞业限制",
            "保密协议", "培训协议", "服务期", "工伤", "职业病", "劳动仲裁",
            "劳动争议", "调解", "诉讼", "举证", "证据", "合同期限", "工作内容",
            "工作地点", "工作时间", "休息休假", "劳动保护", "劳动条件"
        ],
        "forbidden_pairs": [
            ("腰间盘", "劳动合同"),
            ("感冒", "经济补偿"),
            ("股票", "加班费"),
        ],
        "required_density": 0.03
    }
}

@dataclass
class ValidationResult:
    score_adjustment: float
    passed: bool
    core_term_hits: List[str]
    forbidden_violations: List[Tuple[str, str]]
    repetition_count: int
    domain_confidence: float

class DomainValidator:
    """垂直领域校验器"""
    
    def __init__(self):
        self.term_libraries = DOMAIN_TERM_LIBRARIES
        self.weights = {
            "core_term_hit": 0.3,
            "forbidden_pair": -0.5,
            "repetition": -0.2,
            "domain_confidence": 0.2
        }
        self.repetition_threshold = 3
    
    def validate(self, text: str, domain: str, context_texts: List[str] = None) -> ValidationResult:
        if domain not in self.term_libraries:
            domain = "人工智能"
        
        library = self.term_libraries[domain]
        core_terms = library["core_terms"]
        forbidden_pairs = library["forbidden_pairs"]
        required_density = library.get("required_density", 0.02)
        
        core_term_hits = self._find_core_terms(text, core_terms)
        forbidden_violations = self._check_forbidden_pairs(text, forbidden_pairs)
        repetition_count = self._check_repetition(text, context_texts or [])
        domain_confidence = self._calculate_domain_confidence(text, core_terms, required_density)
        
        score_adjustment = 0.0
        score_adjustment += len(core_term_hits) * self.weights["core_term_hit"] * 0.1
        score_adjustment += len(forbidden_violations) * self.weights["forbidden_pair"]
        score_adjustment += min(repetition_count, 3) * self.weights["repetition"]
        score_adjustment += domain_confidence * self.weights["domain_confidence"]
        
        passed = len(forbidden_violations) == 0 and repetition_count < self.repetition_threshold
        
        return ValidationResult(
            score_adjustment=max(-0.5, min(0.3, score_adjustment)),
            passed=passed,
            core_term_hits=core_term_hits,
            forbidden_violations=forbidden_violations,
            repetition_count=repetition_count,
            domain_confidence=domain_confidence
        )
    
    def _find_core_terms(self, text: str, core_terms: List[str]) -> List[str]:
        hits = []
        for term in core_terms:
            if term in text:
                hits.append(term)
        return hits
    
    def _check_forbidden_pairs(self, text: str, forbidden_pairs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        violations = []
        for term1, term2 in forbidden_pairs:
            if term1 in text and term2 in text:
                violations.append((term1, term2))
        return violations
    
    def _check_repetition(self, text: str, context_texts: List[str]) -> int:
        if not context_texts:
            return 0
        
        count = 0
        sentences = re.split(r'[。！？\n]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        for sentence in sentences:
            for ctx in context_texts[-20:]:
                if sentence in ctx:
                    count += 1
                    break
        
        return count
    
    def _calculate_domain_confidence(self, text: str, core_terms: List[str], required_density: float = 0.02) -> float:
        if not text:
            return 0.0
        
        hit_count = sum(1 for term in core_terms if term in text)
        text_len = len(text)
        
        if text_len < 50:
            return min(1.0, hit_count * 0.1)
        
        density = hit_count / (text_len / 100)
        
        if density >= required_density:
            return min(1.0, 0.7 + (density - required_density) * 2)
        else:
            return min(0.6, density / required_density * 0.6)

class ParallelQualityScorer:
    """并行权重评分器"""
    
    def __init__(self):
        self.weights = {
            "base_quality": 0.40,
            "domain_validation": 0.25,
            "readability": 0.15,
            "diversity": 0.10,
            "length_score": 0.10
        }
        self.domain_validator = DomainValidator()
    
    def score(self, text: str, domain: str, base_score: float = 0.7,
              context_texts: List[str] = None) -> Dict:
        domain_result = self.domain_validator.validate(text, domain, context_texts)
        
        readability = self._score_readability(text)
        diversity = self._score_diversity(text, context_texts or [])
        length_score = self._score_length(text)
        
        final_score = (
            base_score * self.weights["base_quality"] +
            (base_score + domain_result.score_adjustment) * self.weights["domain_validation"] +
            readability * self.weights["readability"] +
            diversity * self.weights["diversity"] +
            length_score * self.weights["length_score"]
        )
        
        final_score = max(0.0, min(1.0, final_score))
        
        return {
            "final_score": round(final_score, 3),
            "components": {
                "base_quality": round(base_score, 3),
                "domain_adjustment": round(domain_result.score_adjustment, 3),
                "readability": round(readability, 3),
                "diversity": round(diversity, 3),
                "length_score": round(length_score, 3)
            },
            "validation": {
                "passed": domain_result.passed,
                "core_term_hits": domain_result.core_term_hits[:5],
                "forbidden_violations": domain_result.forbidden_violations,
                "repetition_count": domain_result.repetition_count,
                "domain_confidence": round(domain_result.domain_confidence, 3)
            },
            "quality_tier": self._get_quality_tier(final_score)
        }
    
    def _score_readability(self, text: str) -> float:
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
        
        return max(0.0, score)
    
    def _score_diversity(self, text: str, context_texts: List[str]) -> float:
        if not context_texts:
            return 1.0
        
        sentences = set(re.split(r'[。！？\n]', text))
        sentences = {s.strip() for s in sentences if len(s.strip()) > 10}
        
        if not sentences:
            return 0.5
        
        unique_count = 0
        for sentence in sentences:
            is_unique = True
            for ctx in context_texts[-10:]:
                if sentence in ctx:
                    is_unique = False
                    break
            if is_unique:
                unique_count += 1
        
        return unique_count / len(sentences) if sentences else 0.5
    
    def _score_length(self, text: str) -> float:
        length = len(text)
        
        if length < 30:
            return 0.3
        elif length < 50:
            return 0.5
        elif length < 100:
            return 0.7
        elif length < 300:
            return 1.0
        elif length < 500:
            return 0.9
        elif length < 1000:
            return 0.8
        else:
            return 0.7
    
    def _get_quality_tier(self, score: float) -> str:
        if score >= 0.85:
            return "high"
        elif score >= 0.70:
            return "medium"
        elif score >= 0.50:
            return "low"
        else:
            return "reject"

domain_validator = DomainValidator()
parallel_scorer = ParallelQualityScorer()

def validate_domain(text: str, domain: str, context: List[str] = None) -> ValidationResult:
    return domain_validator.validate(text, domain, context)

def score_quality(text: str, domain: str, base_score: float = 0.7, context: List[str] = None) -> Dict:
    return parallel_scorer.score(text, domain, base_score, context)

if __name__ == "__main__":
    print("="*60)
    print("垂直领域校验测试")
    print("="*60)
    
    test_cases = [
        ("深度学习是机器学习的一个分支，通过神经网络实现特征提取。", "人工智能"),
        ("腰间盘突出会导致头痛和恶心。", "医疗"),
        ("股票投资需要注意风险控制和资产配置。", "金融"),
        ("劳动合同应当明确约定工资标准和加班费计算方式。", "劳动合同"),
    ]
    
    context = []
    
    for text, domain in test_cases:
        print(f"\n领域: {domain}")
        print(f"文本: {text[:50]}...")
        
        result = score_quality(text, domain, 0.7, context)
        
        print(f"最终得分: {result['final_score']}")
        print(f"质量等级: {result['quality_tier']}")
        print(f"核心术语命中: {result['validation']['core_term_hits']}")
        print(f"禁止关联违规: {result['validation']['forbidden_violations']}")
        print(f"通过校验: {result['validation']['passed']}")
        
        context.append(text)
    
    print("\n" + "="*60)
    print("测试完成")
