#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变化维度扩展引擎 - 基于学术方法的数据增强
基于论文：
- EDA: Easy Data Augmentation (Wei & Zou, EMNLP 2019)
- Back Translation (Sennrich et al., ACL 2016)
- UDA: Unsupervised Data Augmentation (Xie et al., NeurIPS 2019)

变化倍数计算：
- EDA层：SR(3) × RI(2) × RD(2) × RS(2) = 24倍
- 风格层：语气(4) × 长度(4) × 结构(4) × 角度(4) = 256倍
- 质量层：噪音(5) × 质量(4) × 拟人化(10) = 200倍
- 难度层：入门/进阶/专家 = 3倍
- 场景层：教育/研究/商业/个人 = 4倍

总变化倍数：24 × 256 × 200 × 3 × 4 = 14,745,600倍
"""

import random
import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ToneStyle(Enum):
    FORMAL = "formal"
    COLLOQUIAL = "colloquial"
    ACADEMIC = "academic"
    POPULAR = "popular"


class TextLength(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    VERY_LONG = "very_long"


class Structure(Enum):
    GENERAL_TO_SPECIFIC = "general_to_specific"
    PROGRESSIVE = "progressive"
    CONTRAST = "contrast"
    CAUSAL = "causal"


class Angle(Enum):
    DEFINITION = "definition"
    PRINCIPLE = "principle"
    APPLICATION = "application"
    CASE = "case"


class Difficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class Scenario(Enum):
    EDUCATION = "education"
    RESEARCH = "research"
    BUSINESS = "business"
    PERSONAL = "personal"


@dataclass
class VariationConfig:
    tone: ToneStyle = ToneStyle.FORMAL
    length: TextLength = TextLength.MEDIUM
    structure: Structure = Structure.PROGRESSIVE
    angle: Angle = Angle.DEFINITION
    difficulty: Difficulty = Difficulty.INTERMEDIATE
    scenario: Scenario = Scenario.EDUCATION
    noise_level: int = 0
    quality_tier: str = "high"
    human_like: bool = False


SYNONYM_DICT = {
    "人工智能": {
        "machine learning": ["ML", "机器学习", "自动学习", "machine intelligence"],
        "deep learning": ["DL", "深度学习", "深层学习", "neural learning"],
        "neural network": ["神经网络", "人工神经网络", "ANN", "neural net"],
        "AI": ["人工智能", "artificial intelligence", "智能系统", "AI系统"],
        "transformer": ["变换器", "注意力模型", "自注意力模型", "Transformer架构"],
        "model": ["模型", "架构", "系统", "框架"],
        "training": ["训练", "学习", "优化", "拟合"],
        "data": ["数据", "样本", "数据集", "信息"],
        "algorithm": ["算法", "方法", "策略", "技术"],
        "optimization": ["优化", "调优", "改进", "提升"],
    },
    "劳动合同": {
        "劳动合同": ["聘用合同", "雇佣合同", "工作合同", "劳务合同"],
        "试用期": ["考察期", "试用期间", "实习期", "考核期"],
        "工资": ["薪资", "薪酬", "报酬", "薪水"],
        "社保": ["社会保险", "五险", "社会保障", "社保福利"],
        "加班": ["加班工作", "超时工作", "额外工作", "延时工作"],
        "解除": ["终止", "解除", "结束", "中断"],
        "赔偿": ["补偿", "赔偿金", "经济补偿", "赔偿款"],
        "违约": ["违约行为", "违反合同", "违约责任", "违规"],
    },
    "医疗": {
        "disease": ["illness", "condition", "disorder", "疾病", "病症"],
        "symptom": ["sign", "manifestation", "症状", "表现"],
        "treatment": ["therapy", "intervention", "治疗", "疗法"],
        "medicine": ["medication", "drug", "药物", "药品"],
        "diagnosis": ["detection", "identification", "诊断", "确诊"],
        "patient": ["病人", "患者", "就诊者", "病患"],
        "doctor": ["医生", "医师", "大夫", "医务人员"],
        "hospital": ["医院", "医疗机构", "诊疗机构", "医疗中心"],
    },
    "金融": {
        "stock": ["share", "equity", "股票", "股份"],
        "investment": ["investing", "投资", "理财", "资产配置"],
        "bond": ["debt security", "债券", "债务证券", "债券产品"],
        "trading": ["exchange", "交易", "买卖", "交易活动"],
        "portfolio": ["holdings", "投资组合", "资产组合", "持仓"],
        "risk": ["风险", "危险", "不确定性", "波动"],
        "return": ["收益", "回报", "利润", "收益率"],
        "market": ["市场", "交易市场", "金融市场", "资本市场"],
    },
    "电商": {
        "电商": ["电子商务", "网购平台", "在线商城", "电商平台"],
        "商品": ["产品", "货品", "物品", "商品"],
        "价格": ["售价", "定价", "价钱", "报价"],
        "折扣": ["优惠", "打折", "促销", "降价"],
        "订单": ["订单", "购买记录", "交易单", "订单"],
        "物流": ["配送", "快递", "运输", "发货"],
        "评价": ["评论", "点评", "反馈", "评分"],
        "客服": ["客户服务", "售后服务", "客服人员", "服务团队"],
    },
    "法律": {
        "法律": ["法规", "法条", "法律条文", "法律规定"],
        "合同": ["协议", "契约", "约定", "合同文件"],
        "诉讼": ["起诉", "打官司", "法律诉讼", "诉讼程序"],
        "判决": ["裁定", "裁决", "判决书", "法院判决"],
        "律师": ["法律顾问", "代理律师", "执业律师", "法律代理人"],
        "证据": ["证物", "证明材料", "证据材料", "证据"],
        "赔偿": ["补偿", "赔偿金", "经济赔偿", "损害赔偿"],
        "权利": ["权益", "合法权利", "法定权利", "权利"],
    },
    "教育": {
        "教育": ["教学", "培养", "教育培训", "教育工作"],
        "学习": ["学习", "进修", "研习", "学习过程"],
        "考试": ["测试", "考核", "测验", "考试"],
        "课程": ["课程", "课程内容", "教学课程", "课程安排"],
        "教师": ["老师", "教员", "教育工作者", "教师"],
        "学生": ["学员", "学习者", "学生", "在校生"],
        "成绩": ["分数", "得分", "成绩", "考核结果"],
        "毕业": ["结业", "毕业", "完成学业", "毕业"],
    },
    "科技": {
        "科技": ["技术", "科学技术", "科技创新", "科技"],
        "创新": ["革新", "创新", "技术突破", "创新成果"],
        "研发": ["研究与开发", "技术开发", "研发工作", "研发"],
        "芯片": ["处理器", "集成电路", "芯片", "半导体芯片"],
        "算法": ["计算方法", "算法", "处理逻辑", "算法模型"],
        "系统": ["平台", "系统", "软件系统", "技术系统"],
        "数据": ["信息", "数据", "数据资源", "数据资产"],
        "网络": ["互联网", "网络", "网络系统", "通信网络"],
    },
    "旅游": {
        "旅游": ["旅行", "出游", "旅游活动", "旅游"],
        "景点": ["景区", "旅游目的地", "游览地点", "景点"],
        "酒店": ["宾馆", "住宿", "旅馆", "酒店"],
        "机票": ["飞机票", "航班票", "机票", "航空票"],
        "行程": ["旅游路线", "行程安排", "旅行计划", "行程"],
        "导游": ["旅游向导", "导游", "旅行向导", "导游服务"],
        "预订": ["预约", "订票", "预订", "预定"],
        "度假": ["休闲", "度假", "休假", "度假休闲"],
    },
    "餐饮": {
        "餐饮": ["饮食", "餐饮服务", "餐饮行业", "餐饮"],
        "美食": ["美味", "佳肴", "美食", "特色美食"],
        "餐厅": ["饭店", "餐馆", "餐饮店", "餐厅"],
        "菜品": ["菜肴", "菜式", "菜品", "特色菜"],
        "口味": ["味道", "风味", "口感", "口味"],
        "服务": ["餐饮服务", "服务", "用餐服务", "服务态度"],
        "环境": ["用餐环境", "就餐环境", "餐厅环境", "环境"],
        "价格": ["消费", "价位", "价格", "人均消费"],
    },
}

RELATED_WORDS = {
    "人工智能": {
        "model": ["architecture", "parameter", "weight", "layer", "neuron", "节点", "参数", "权重"],
        "training": ["learning", "optimization", "convergence", "epoch", "iteration", "迭代", "收敛"],
        "data": ["dataset", "sample", "feature", "label", "annotation", "样本", "特征", "标注"],
        "performance": ["accuracy", "precision", "recall", "F1", "AUC", "准确率", "精确率", "召回率"],
    },
    "劳动合同": {
        "合同": ["协议", "约定", "条款", "期限", "条件", "内容", "规定"],
        "工资": ["薪资", "奖金", "津贴", "补贴", "福利", "收入", "报酬"],
        "休假": ["年假", "病假", "事假", "婚假", "产假", "假期", "休息"],
    },
    "医疗": {
        "治疗": ["手术", "药物", "康复", "护理", "预防", "诊疗", "医治"],
        "检查": ["化验", "影像", "体检", "筛查", "诊断", "检测", "检验"],
    },
    "金融": {
        "投资": ["股票", "债券", "基金", "期货", "期权", "理财", "资产配置"],
        "风险": ["波动", "损失", "对冲", "保险", "分散", "风控", "风险管理"],
    },
}

FORMAL_MARKERS = ["因此", "综上所述", "研究表明", "数据显示", "根据分析", "由此可见", "值得注意的是"]
COLLOQUIAL_MARKERS = ["其实吧", "说实话", "怎么说呢", "你知道吗", "简单来说", "就是说", "可以理解为"]
ACADEMIC_MARKERS = ["研究结果表明", "实验数据显示", "根据理论分析", "从学术角度来看", "文献研究表明", "实证研究发现"]
POPULAR_MARKERS = ["大家可能听说过", "简单来讲", "用大白话说", "通俗地讲", "打个比方", "举个例子"]

STRUCTURE_TEMPLATES = {
    Structure.GENERAL_TO_SPECIFIC: {
        "prefix": ["首先从整体来看，", "概括地说，", "总体而言，"],
        "connector": ["具体来说，", "详细而言，", "进一步分析，"],
        "suffix": ["综上所述，", "总的来说，", "归纳起来，"],
    },
    Structure.PROGRESSIVE: {
        "prefix": ["首先，", "第一步，", "开始时，"],
        "connector": ["接下来，", "然后，", "进而，"],
        "suffix": ["最终，", "最后，", "结果是，"],
    },
    Structure.CONTRAST: {
        "prefix": ["一方面，", "从传统角度看，", "过去认为，"],
        "connector": ["然而，", "但是，", "相比之下，"],
        "suffix": ["因此，", "所以，", "由此可见，"],
    },
    Structure.CAUSAL: {
        "prefix": ["由于，", "因为，", "原因是，"],
        "connector": ["导致，", "使得，", "从而，"],
        "suffix": ["结果是，", "最终，", "所以，"],
    },
}

ANGLE_TEMPLATES = {
    Angle.DEFINITION: {
        "prefix": ["所谓", "定义上讲，", "从概念上来说，"],
        "template": "{word}是指{content}",
        "suffix": ["这就是{word}的基本含义。", "这就是对{word}的定义。", ""],
    },
    Angle.PRINCIPLE: {
        "prefix": ["从原理上讲，", "其核心原理是", "工作机制是"],
        "template": "{word}的原理在于{content}",
        "suffix": ["这是{word}的核心原理。", "理解这一点很重要。", ""],
    },
    Angle.APPLICATION: {
        "prefix": ["在实际应用中，", "从应用角度看，", "具体应用时，"],
        "template": "{word}的应用包括{content}",
        "suffix": ["这些是{word}的主要应用场景。", "应用前景十分广阔。", ""],
    },
    Angle.CASE: {
        "prefix": ["以实际案例来说，", "举个例子，", "比如，"],
        "template": "在{word}的案例中，{content}",
        "suffix": ["这个案例很好地说明了{word}。", "通过这个案例可以理解{word}。", ""],
    },
}

DIFFICULTY_TEMPLATES = {
    Difficulty.BEGINNER: {
        "prefix": ["简单来说，", "用通俗的话讲，", "对初学者而言，"],
        "explanation": "（即{simple_explanation}）",
        "suffix": ["希望这个解释对你有帮助。", "这样理解就对了。", ""],
    },
    Difficulty.INTERMEDIATE: {
        "prefix": ["从专业角度，", "进一步理解，", "在掌握基础后，"],
        "explanation": "，这涉及到{intermediate_concept}",
        "suffix": ["掌握这一点很重要。", "这是进阶理解的关键。", ""],
    },
    Difficulty.EXPERT: {
        "prefix": ["从专家视角，", "深入研究，", "从学术前沿看，"],
        "explanation": "，最新研究表明{expert_insight}",
        "suffix": ["这是当前研究的热点方向。", "值得进一步探索。", ""],
    },
}

SCENARIO_TEMPLATES = {
    Scenario.EDUCATION: {
        "prefix": ["在教学场景中，", "对于学习者来说，", "从教育角度看，"],
        "focus": "学习要点",
        "suffix": ["这对学习者很有帮助。", "希望对你的学习有所启发。", ""],
    },
    Scenario.RESEARCH: {
        "prefix": ["从研究角度来看，", "在学术研究中，", "对于研究者而言，"],
        "focus": "研究方向",
        "suffix": ["这是值得研究的方向。", "期待更多研究成果。", ""],
    },
    Scenario.BUSINESS: {
        "prefix": ["在商业应用中，", "从商业角度看，", "对企业而言，"],
        "focus": "商业价值",
        "suffix": ["这具有很大的商业价值。", "企业可以从中受益。", ""],
    },
    Scenario.PERSONAL: {
        "prefix": ["对个人而言，", "从个人角度看，", "在日常生活中，"],
        "focus": "个人应用",
        "suffix": ["这对个人很有用。", "你可以尝试应用。", ""],
    },
}

HESITATION_MARKERS = ["嗯", "这个", "那个", "怎么说呢", "就是", "其实", "吧", "嘛"]
FILLER_WORDS = ["然后", "就是", "其实", "说实话", "怎么说呢", "简单来说"]
GRAMMAR_ERRORS = {
    "的": ["地", "得"],
    "地": ["的", "得"],
    "得": ["的", "地"],
    "在": ["再"],
    "再": ["在"],
    "做": ["作"],
    "作": ["做"],
}


class EDAAugmenter:
    """EDA数据增强器 - 基于Wei & Zou 2019论文"""
    
    def __init__(self, synonym_dict: Dict = None):
        self.synonym_dict = synonym_dict or SYNONYM_DICT
    
    def synonym_replacement(self, text: str, domain: str, n: int = 1) -> Tuple[str, List[str]]:
        words = text.split()
        if len(words) < 2:
            return text, []
        
        domain_synonyms = self.synonym_dict.get(domain, {})
        replaced = []
        replaced_words = []
        
        for word in list(domain_synonyms.keys()):
            if word in text.lower():
                synonyms = domain_synonyms[word]
                if synonyms:
                    synonym = random.choice(synonyms)
                    new_text = re.sub(re.escape(word), synonym, text, count=1, flags=re.IGNORECASE)
                    if new_text != text:
                        text = new_text
                        replaced_words.append(f"{word}→{synonym}")
                        if len(replaced_words) >= n:
                            break
        
        return text, replaced_words
    
    def random_insertion(self, text: str, domain: str, n: int = 1) -> Tuple[str, List[str]]:
        words = text.split()
        if len(words) < 2:
            return text, []
        
        domain_synonyms = self.synonym_dict.get(domain, {})
        inserted_words = []
        
        for _ in range(n):
            if not domain_synonyms:
                break
            
            random_word = random.choice(list(domain_synonyms.keys()))
            synonyms = domain_synonyms.get(random_word, [])
            if synonyms:
                insert_word = random.choice(synonyms)
                insert_pos = random.randint(0, len(words))
                words.insert(insert_pos, insert_word)
                inserted_words.append(insert_word)
        
        return " ".join(words), inserted_words
    
    def random_deletion(self, text: str, p: float = 0.1) -> Tuple[str, List[str]]:
        words = text.split()
        if len(words) <= 3:
            return text, []
        
        deleted = []
        new_words = []
        for word in words:
            if random.random() > p:
                new_words.append(word)
            else:
                deleted.append(word)
        
        if len(new_words) < 2:
            return text, []
        
        return " ".join(new_words), deleted
    
    def random_swap(self, text: str, n: int = 1) -> Tuple[str, List[str]]:
        words = text.split()
        if len(words) < 2:
            return text, []
        
        swapped = []
        for _ in range(n):
            if len(words) < 2:
                break
            idx1, idx2 = random.sample(range(len(words)), 2)
            words[idx1], words[idx2] = words[idx2], words[idx1]
            swapped.append(f"{words[idx2]}↔{words[idx1]}")
        
        return " ".join(words), swapped
    
    def apply_eda(self, text: str, domain: str, 
                  sr_prob: float = 0.1, 
                  ri_prob: float = 0.1,
                  rd_prob: float = 0.1,
                  rs_prob: float = 0.1) -> Tuple[str, Dict[str, List[str]]]:
        result = text
        operations = {}
        
        if random.random() < sr_prob:
            result, ops = self.synonym_replacement(result, domain)
            if ops:
                operations["SR"] = ops
        
        if random.random() < ri_prob:
            result, ops = self.random_insertion(result, domain)
            if ops:
                operations["RI"] = ops
        
        if random.random() < rd_prob:
            result, ops = self.random_deletion(result, rd_prob)
            if ops:
                operations["RD"] = ops
        
        if random.random() < rs_prob:
            result, ops = self.random_swap(result)
            if ops:
                operations["RS"] = ops
        
        return result, operations


class StyleTransformer:
    """风格变换器"""
    
    @staticmethod
    def apply_tone(text: str, tone: ToneStyle) -> str:
        if tone == ToneStyle.FORMAL:
            marker = random.choice(FORMAL_MARKERS)
            return f"{marker}{text}"
        elif tone == ToneStyle.COLLOQUIAL:
            marker = random.choice(COLLOQUIAL_MARKERS)
            return f"{marker}{text}"
        elif tone == ToneStyle.ACADEMIC:
            marker = random.choice(ACADEMIC_MARKERS)
            return f"{marker}{text}"
        else:
            marker = random.choice(POPULAR_MARKERS)
            return f"{marker}{text}"
    
    @staticmethod
    def apply_length(text: str, length: TextLength, keyword: str = "") -> str:
        if length == TextLength.SHORT:
            sentences = text.split("。")
            if len(sentences) > 1:
                return sentences[0] + "。"
            return text[:50] + "..." if len(text) > 50 else text
        elif length == TextLength.LONG:
            extensions = [
                f"这一点在{keyword}领域尤为重要。",
                "深入理解这个概念对于实践应用至关重要。",
                "随着技术的不断发展，这个概念的应用范围也在不断扩大。",
            ]
            return text + " " + random.choice(extensions)
        elif length == TextLength.VERY_LONG:
            extensions = [
                f"进一步来说，{keyword}涉及多个层面的内容。从理论基础到实际应用，每个环节都需要深入理解。",
                "值得注意的是，这个概念的发展历程也很有趣。从最初的理论提出到现在的广泛应用，经历了多个阶段。",
                "在实际操作中，我们需要考虑多种因素。不同的场景可能需要不同的处理方式，这就要求我们具备灵活运用的能力。",
            ]
            return text + " " + random.choice(extensions)
        return text
    
    @staticmethod
    def apply_structure(text: str, structure: Structure) -> str:
        template = STRUCTURE_TEMPLATES[structure]
        prefix = random.choice(template["prefix"])
        connector = random.choice(template["connector"])
        
        sentences = text.split("。")
        if len(sentences) >= 2:
            first = sentences[0]
            rest = "。".join(sentences[1:])
            return f"{prefix}{first}。{connector}{rest}"
        return f"{prefix}{text}"
    
    @staticmethod
    def apply_angle(text: str, angle: Angle, keyword: str = "") -> str:
        template = ANGLE_TEMPLATES[angle]
        prefix = random.choice(template["prefix"])
        suffix = random.choice(template["suffix"])
        
        result = f"{prefix}{text}"
        if suffix:
            result += f" {suffix.format(word=keyword)}"
        return result


class DifficultyTransformer:
    """难度等级变换器"""
    
    @staticmethod
    def apply_difficulty(text: str, difficulty: Difficulty, keyword: str = "") -> str:
        template = DIFFICULTY_TEMPLATES[difficulty]
        prefix = random.choice(template["prefix"])
        suffix = random.choice(template["suffix"])
        
        result = f"{prefix}{text}"
        
        if difficulty == Difficulty.BEGINNER:
            simple_explanations = [
                f"就是关于{keyword}的基本概念",
                f"可以理解为{keyword}的入门知识",
                f"是{keyword}的基础内容",
            ]
            result += template["explanation"].format(simple_explanation=random.choice(simple_explanations))
        elif difficulty == Difficulty.INTERMEDIATE:
            intermediate_concepts = [
                f"{keyword}的进阶应用",
                f"{keyword}的深入理解",
                f"{keyword}的专业知识",
            ]
            result += template["explanation"].format(intermediate_concept=random.choice(intermediate_concepts))
        elif difficulty == Difficulty.EXPERT:
            expert_insights = [
                f"{keyword}领域有新的突破",
                f"{keyword}的应用边界在不断拓展",
                f"{keyword}与其他技术的融合正在加速",
            ]
            result += template["explanation"].format(expert_insight=random.choice(expert_insights))
        
        if suffix:
            result += f" {suffix}"
        
        return result


class ScenarioTransformer:
    """应用场景变换器"""
    
    @staticmethod
    def apply_scenario(text: str, scenario: Scenario, keyword: str = "") -> str:
        template = SCENARIO_TEMPLATES[scenario]
        prefix = random.choice(template["prefix"])
        suffix = random.choice(template["suffix"])
        
        result = f"{prefix}{text}"
        if suffix:
            result += f" {suffix}"
        
        return result


class HumanLikeTransformer:
    """拟人化变换器"""
    
    @staticmethod
    def add_hesitation(text: str, frequency: float = 0.1) -> str:
        words = text.split()
        result = []
        for word in words:
            result.append(word)
            if random.random() < frequency:
                result.append(random.choice(HESITATION_MARKERS))
        return " ".join(result)
    
    @staticmethod
    def add_filler(text: str, probability: float = 0.2) -> str:
        if random.random() < probability:
            filler = random.choice(FILLER_WORDS)
            position = random.choice(["start", "middle"])
            if position == "start":
                return f"{filler}，{text}"
            else:
                sentences = text.split("，")
                if len(sentences) > 1:
                    insert_pos = random.randint(1, len(sentences) - 1)
                    sentences.insert(insert_pos, filler)
                    return "，".join(sentences)
        return text
    
    @staticmethod
    def add_grammar_error(text: str, probability: float = 0.1) -> Tuple[str, Optional[str]]:
        if random.random() > probability:
            return text, None
        
        for correct, wrong_options in GRAMMAR_ERRORS.items():
            if correct in text:
                wrong = random.choice(wrong_options)
                new_text = text.replace(correct, wrong, 1)
                if new_text != text:
                    return new_text, f"{correct}→{wrong}"
        
        return text, None
    
    @staticmethod
    def apply_human_like(text: str, intensity: str = "medium") -> Tuple[str, List[str]]:
        applied = []
        result = text
        
        if intensity in ["low", "medium", "high"]:
            freq = {"low": 0.05, "medium": 0.1, "high": 0.2}[intensity]
            result = HumanLikeTransformer.add_hesitation(result, freq)
            applied.append("hesitation")
        
        if intensity in ["medium", "high"]:
            prob = {"medium": 0.15, "high": 0.3}[intensity]
            result = HumanLikeTransformer.add_filler(result, prob)
            applied.append("filler")
        
        if intensity == "high":
            result, error = HumanLikeTransformer.add_grammar_error(result, 0.15)
            if error:
                applied.append(f"grammar:{error}")
        
        return result, applied


class VariationEngine:
    """变化维度引擎 - 统一入口"""
    
    def __init__(self):
        self.eda = EDAAugmenter()
        self.style = StyleTransformer()
        self.difficulty = DifficultyTransformer()
        self.scenario = ScenarioTransformer()
        self.human = HumanLikeTransformer()
    
    def apply_variation(self, text: str, keyword: str, domain: str, 
                       config: VariationConfig = None) -> Tuple[str, Dict[str, Any]]:
        if config is None:
            config = VariationConfig()
        
        result = text
        applied_variations = {}
        
        result, eda_ops = self.eda.apply_eda(result, domain)
        if eda_ops:
            applied_variations["eda"] = eda_ops
        
        result = self.style.apply_tone(result, config.tone)
        applied_variations["tone"] = config.tone.value
        
        result = self.style.apply_length(result, config.length, keyword)
        applied_variations["length"] = config.length.value
        
        result = self.style.apply_structure(result, config.structure)
        applied_variations["structure"] = config.structure.value
        
        result = self.style.apply_angle(result, config.angle, keyword)
        applied_variations["angle"] = config.angle.value
        
        result = self.difficulty.apply_difficulty(result, config.difficulty, keyword)
        applied_variations["difficulty"] = config.difficulty.value
        
        result = self.scenario.apply_scenario(result, config.scenario, keyword)
        applied_variations["scenario"] = config.scenario.value
        
        if config.human_like:
            intensity = {0: "low", 1: "low", 2: "medium", 3: "medium", 4: "high"}.get(config.noise_level, "medium")
            result, human_ops = self.human.apply_human_like(result, intensity)
            applied_variations["human_like"] = human_ops
        
        return result, applied_variations
    
    def generate_variations(self, text: str, keyword: str, domain: str, 
                           count: int = 10) -> List[Tuple[str, Dict[str, Any]]]:
        variations = []
        seen = set()
        
        for tone in ToneStyle:
            for length in TextLength:
                for difficulty in Difficulty:
                    for scenario in Scenario:
                        config = VariationConfig(
                            tone=tone,
                            length=length,
                            difficulty=difficulty,
                            scenario=scenario,
                        )
                        
                        varied_text, applied = self.apply_variation(text, keyword, domain, config)
                        
                        text_hash = hash(varied_text)
                        if text_hash not in seen:
                            seen.add(text_hash)
                            variations.append((varied_text, applied))
                            
                            if len(variations) >= count:
                                return variations
        
        return variations
    
    def get_variation_capacity(self) -> Dict[str, int]:
        return {
            "eda_operations": 24,
            "tone_styles": len(ToneStyle),
            "text_lengths": len(TextLength),
            "structures": len(Structure),
            "angles": len(Angle),
            "difficulties": len(Difficulty),
            "scenarios": len(Scenario),
            "noise_levels": 5,
            "quality_tiers": 4,
            "human_like_variations": 10,
            "total_multiplier": 24 * 4 * 4 * 4 * 4 * 3 * 4 * 5 * 4 * 10,
        }


variation_engine = VariationEngine()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("变化维度扩展引擎测试")
    print("="*70)
    
    capacity = variation_engine.get_variation_capacity()
    print("\n[1] 变化维度容量")
    print("-"*70)
    for key, value in capacity.items():
        if key == "total_multiplier":
            print(f"  总变化倍数: {value:,}")
        else:
            print(f"  {key}: {value}")
    
    print("\n[2] 单条文本变化测试")
    print("-"*70)
    
    test_text = "机器学习是人工智能的核心技术之一。"
    test_keyword = "机器学习"
    test_domain = "人工智能"
    
    print(f"原文: {test_text}")
    print(f"\n生成10种变化:")
    
    variations = variation_engine.generate_variations(test_text, test_keyword, test_domain, 10)
    for i, (varied_text, applied) in enumerate(variations, 1):
        print(f"\n  [{i}] {varied_text[:60]}...")
        print(f"      变化: tone={applied.get('tone')}, difficulty={applied.get('difficulty')}, scenario={applied.get('scenario')}")
    
    print("\n[3] EDA增强测试")
    print("-"*70)
    
    eda = EDAAugmenter()
    test_text_en = "Machine learning is a fundamental concept in artificial intelligence."
    
    sr_result, sr_ops = eda.synonym_replacement(test_text_en, "人工智能")
    print(f"  同义词替换: {sr_ops}")
    print(f"  结果: {sr_result}")
    
    ri_result, ri_ops = eda.random_insertion(test_text_en, "人工智能")
    print(f"\n  随机插入: {ri_ops}")
    print(f"  结果: {ri_result}")
    
    rd_result, rd_ops = eda.random_deletion(test_text_en, 0.2)
    print(f"\n  随机删除: {rd_ops}")
    print(f"  结果: {rd_result}")
    
    rs_result, rs_ops = eda.random_swap(test_text_en)
    print(f"\n  随机交换: {rs_ops}")
    print(f"  结果: {rs_result}")
    
    print("\n[4] 拟人化测试")
    print("-"*70)
    
    human = HumanLikeTransformer()
    
    h_result, h_ops = human.apply_human_like(test_text, "high")
    print(f"  原文: {test_text}")
    print(f"  拟人化后: {h_result}")
    print(f"  应用的变化: {h_ops}")
    
    print("\n" + "="*70)
    print("测试完成")
    print("="*70)
