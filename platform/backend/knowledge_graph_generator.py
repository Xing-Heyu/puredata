#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱和文献生成模块
"""

import os
import json
import re
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class KnowledgeRelationType(Enum):
    IS_A = "属于"
    HAS_SYMPTOM = "症状"
    TREATS = "治疗"
    CAUSES = "导致"
    DIAGNOSES = "诊断"
    PREVENTS = "预防"
    CONTAINS = "包含"
    RELATED_TO = "相关"
    PART_OF = "部分"
    USED_FOR = "用于"


@dataclass
class KnowledgeTriple:
    head: str
    relation: str
    tail: str
    confidence: float = 1.0
    source: str = "generated"
    
    def to_dict(self):
        return {
            "head": self.head,
            "relation": self.relation,
            "tail": self.tail,
            "confidence": self.confidence,
            "source": self.source
        }


class KnowledgeGraphGenerator:
    """知识图谱三元组生成器"""
    
    RELATION_TEMPLATES = {
        "医疗": {
            "疾病-症状": ["{head}的典型症状包括{tail}", "{head}患者常出现{tail}", "{tail}是{head}的常见表现"],
            "疾病-治疗": ["{head}可采用{tail}治疗", "{tail}用于治疗{head}", "{head}的治疗方案包括{tail}"],
            "疾病-检查": ["{head}需要通过{tail}诊断", "{tail}可用于诊断{head}", "{head}的诊断依赖{tail}"],
            "药物-适应症": ["{head}适用于{tail}", "{head}可用于治疗{tail}", "{tail}可使用{head}治疗"],
            "疾病-分类": ["{head}属于{tail}", "{head}是{tail}的一种", "{tail}包含{head}"],
        },
        "人工智能": {
            "技术-应用": ["{head}应用于{tail}", "{tail}是{head}的典型应用", "{head}在{tail}领域有广泛应用"],
            "技术-分类": ["{head}属于{tail}", "{head}是{tail}的分支", "{tail}包含{head}技术"],
            "算法-任务": ["{head}用于解决{tail}问题", "{tail}可使用{head}算法", "{head}适用于{tail}任务"],
        },
        "金融": {
            "产品-风险": ["{head}存在{tail}风险", "{tail}是{head}的主要风险", "{head}需关注{tail}风险"],
            "产品-收益": ["{head}可带来{tail}收益", "{tail}是{head}的收益来源", "{head}的收益包括{tail}"],
            "业务-监管": ["{head}受{tail}监管", "{tail}监管{head}业务", "{head}需遵守{tail}规定"],
            "舆情-股价": ["{head}导致{tail}", "{head}引发{tail}波动", "{tail}受{head}影响"],
            "ESG-评级": ["{head}影响{tail}", "{tail}因{head}调整", "{head}触发{tail}变化"],
            "事件-机构": ["{head}引发{tail}", "{tail}响应{head}", "{head}促使{tail}行动"],
            "政策-板块": ["{head}利好{tail}", "{tail}受益于{head}", "{head}推动{tail}上涨"],
        },
        "交通驾驶": {
            "场景-风险": ["{head}存在{tail}风险", "{tail}是{head}的主要风险", "{head}需警惕{tail}"],
            "场景-操作": ["{head}需要{tail}", "{tail}是{head}的正确操作", "{head}时应{tail}"],
            "设备-功能": ["{head}用于{tail}", "{tail}是{head}的功能", "{head}可实现{tail}"],
        },
        "劳动合同": {
            "条款-权益": ["{head}保障{tail}", "{tail}是{head}保障的权益", "{head}涉及{tail}"],
            "合同-义务": ["{head}规定{tail}", "{tail}是{head}的义务", "{head}要求{tail}"],
        }
    }
    
    ENTITY_TEMPLATES = {
        "医疗": {
            "疾病": ["高血压", "糖尿病", "冠心病", "脑卒中", "肺炎", "胃炎", "肝炎", "肾炎", "贫血", "骨折"],
            "症状": ["发热", "头痛", "咳嗽", "乏力", "恶心", "呕吐", "腹痛", "胸闷", "心悸", "水肿"],
            "药物": ["阿司匹林", "布洛芬", "青霉素", "头孢", "胰岛素", "降压药", "抗生素", "止痛药"],
            "检查": ["血常规", "CT", "MRI", "X光", "B超", "心电图", "胃镜", "肠镜", "尿检", "肝功能"],
            "科室": ["内科", "外科", "儿科", "妇科", "骨科", "神经科", "心血管科", "呼吸科", "消化科"],
        },
        "人工智能": {
            "技术": ["深度学习", "机器学习", "自然语言处理", "计算机视觉", "强化学习", "知识图谱"],
            "算法": ["CNN", "RNN", "Transformer", "LSTM", "GAN", "BERT", "GPT"],
            "应用": ["图像识别", "语音识别", "机器翻译", "智能问答", "推荐系统", "自动驾驶"],
        },
        "交通驾驶": {
            "场景": ["高速公路", "城市道路", "山区道路", "隧道", "桥梁", "路口", "匝道"],
            "风险": ["追尾", "侧翻", "碰撞", "失控", "爆胎", "疲劳驾驶", "酒驾"],
            "设备": ["前视镜", "后视镜", "刹车系统", "转向系统", "安全气囊", "ABS", "ESP"],
        },
        "金融": {
            "舆情事件": ["监管处罚", "业绩暴雷", "高管变动", "并购重组", "减持公告", "财务造假", "股权质押"],
            "ESG问题": ["环境污染", "碳排放超标", "劳动权益", "数据隐私", "商业道德", "供应链风险"],
            "股价表现": ["涨停", "跌停", "股价异动", "成交量放大", "换手率高", "市值蒸发"],
            "机构行为": ["增持", "减持", "清仓", "加仓", "调仓", "北向资金流入", "主力流出"],
            "政策因素": ["货币政策", "财政政策", "行业新规", "监管政策", "利率调整", "汇率波动"],
        }
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        self._qwen_api = None
    
    def _get_qwen_api(self):
        if self._qwen_api is None and self.api_key:
            try:
                from 千问API集成 import QwenAPI
                self._qwen_api = QwenAPI(self.api_key)
            except ImportError:
                pass
        return self._qwen_api
    
    def generate_triples_batch(self, domain: str, count: int, use_api: bool = True) -> List[KnowledgeTriple]:
        """批量生成知识图谱三元组"""
        triples = []
        
        if use_api:
            api_triples = self._generate_via_api(domain, count)
            if api_triples:
                triples.extend(api_triples)
        
        if len(triples) < count:
            template_triples = self._generate_via_templates(domain, count - len(triples))
            triples.extend(template_triples)
        
        return triples[:count]
    
    def _generate_via_api(self, domain: str, count: int) -> List[KnowledgeTriple]:
        """通过API生成三元组"""
        qwen_api = self._get_qwen_api()
        if not qwen_api:
            return []
        
        prompt = f"""请生成{count}条关于"{domain}"领域的知识图谱三元组。
三元组格式：(实体1, 关系, 实体2)

要求：
1. 实体要与{domain}领域相关
2. 关系要准确、专业
3. 三元组要有实际意义，可用于知识图谱构建
4. 按JSON数组格式输出：[{{"head": "实体1", "relation": "关系", "tail": "实体2"}}]

示例：
[
    {{"head": "高血压", "relation": "属于", "tail": "心血管疾病"}},
    {{"head": "阿司匹林", "relation": "治疗", "tail": "头痛"}},
    {{"head": "CT检查", "relation": "诊断", "tail": "脑出血"}}
]

只输出JSON数组，不要其他内容。"""

        try:
            result = qwen_api.call(prompt, max_tokens=4000)
            if result and result.get("response"):
                response_text = result["response"]
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    triples = []
                    for item in data[:count]:
                        triples.append(KnowledgeTriple(
                            head=item.get("head", ""),
                            relation=item.get("relation", ""),
                            tail=item.get("tail", ""),
                            confidence=0.9,
                            source="api_generated"
                        ))
                    return triples
        except Exception as e:
            print(f"[知识图谱] API生成失败: {e}")
        
        return []
    
    def _generate_via_templates(self, domain: str, count: int) -> List[KnowledgeTriple]:
        """通过模板生成三元组"""
        triples = []
        
        relation_templates = self.RELATION_TEMPLATES.get(domain, {})
        entities = self.ENTITY_TEMPLATES.get(domain, {})
        
        if not relation_templates or not entities:
            return self._generate_generic_triples(domain, count)
        
        entity_types = list(entities.keys())
        relations = list(relation_templates.keys())
        
        for i in range(count):
            relation_key = relations[i % len(relations)]
            relation_parts = relation_key.split("-")
            
            if len(relation_parts) == 2:
                head_type, tail_type = relation_parts
                
                head_entities = entities.get(head_type, [domain])
                tail_entities = entities.get(tail_type, [domain])
                
                head = head_entities[i % len(head_entities)]
                tail = tail_entities[(i + 1) % len(tail_entities)]
                
                relation = relation_key.replace("-", "-").replace("_", "与")
                
                triples.append(KnowledgeTriple(
                    head=head,
                    relation=relation,
                    tail=tail,
                    confidence=0.7,
                    source="template_generated"
                ))
        
        return triples
    
    def _generate_generic_triples(self, domain: str, count: int) -> List[KnowledgeTriple]:
        """生成通用三元组"""
        triples = []
        generic_relations = ["相关", "属于", "包含", "用于", "涉及"]
        
        for i in range(count):
            triples.append(KnowledgeTriple(
                head=f"{domain}概念{i+1}",
                relation=generic_relations[i % len(generic_relations)],
                tail=f"{domain}实体{i+1}",
                confidence=0.5,
                source="generic"
            ))
        
        return triples


class LiteratureGenerator:
    """医学/专业文献生成器"""
    
    LITERATURE_TEMPLATES = {
        "医疗": {
            "sections": ["摘要", "引言", "研究方法", "结果", "讨论", "结论", "参考文献"],
            "topics": [
                "糖尿病患者的血糖管理策略研究",
                "高血压药物治疗效果分析",
                "冠心病介入治疗临床研究",
                "抗生素合理用药探讨",
                "慢性病管理模式研究"
            ]
        },
        "人工智能": {
            "sections": ["摘要", "引言", "相关工作", "方法", "实验", "结论", "参考文献"],
            "topics": [
                "基于深度学习的图像识别研究",
                "自然语言处理技术在医疗领域的应用",
                "强化学习在机器人控制中的应用",
                "知识图谱构建方法研究",
                "大语言模型性能评估研究"
            ]
        },
        "金融": {
            "sections": ["摘要", "引言", "理论基础", "实证分析", "结论", "建议", "参考文献"],
            "topics": [
                "金融舆情对股价波动的影响机制研究",
                "ESG评级与上市公司股价相关性分析",
                "舆情事件驱动股价变动的传导路径研究",
                "基于舆情大数据的股价预测模型构建",
                "ESG负面事件对机构投资行为的影响分析"
            ]
        },
        "交通驾驶": {
            "sections": ["摘要", "引言", "研究背景", "分析方法", "研究结果", "结论", "参考文献"],
            "topics": [
                "智能驾驶安全技术研究",
                "交通事故风险因素分析",
                "ADAS系统有效性评估",
                "驾驶员行为特征研究",
                "道路安全改进措施分析"
            ]
        }
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        self._qwen_api = None
    
    def _get_qwen_api(self):
        if self._qwen_api is None and self.api_key:
            try:
                from 千问API集成 import QwenAPI
                self._qwen_api = QwenAPI(self.api_key)
            except ImportError:
                pass
        return self._qwen_api
    
    def generate_literature(self, domain: str, topic: str = None, length: int = 2000) -> Dict:
        """生成一篇文献"""
        qwen_api = self._get_qwen_api()
        
        template = self.LITERATURE_TEMPLATES.get(domain, self.LITERATURE_TEMPLATES["医疗"])
        sections = template["sections"]
        
        if not topic:
            topics = template["topics"]
            topic = topics[0]
        
        if qwen_api:
            return self._generate_via_api(domain, topic, sections, length)
        else:
            return self._generate_via_template(domain, topic, sections)
    
    def _generate_via_api(self, domain: str, topic: str, sections: List[str], length: int) -> Dict:
        """通过API生成文献"""
        qwen_api = self._get_qwen_api()
        
        sections_str = "、".join(sections)
        
        prompt = f"""请撰写一篇关于"{topic}"的{domain}领域专业文献。

要求：
1. 字数约{length}字
2. 包含以下章节：{sections_str}
3. 内容专业、准确、有学术价值
4. 使用规范的学术写作风格
5. 包含适当的数据、案例支撑

格式要求：
标题：[文献标题]

摘要：[200字左右的摘要]

[按章节结构组织正文内容]

参考文献：
[列出3-5条参考文献]"""

        try:
            result = qwen_api.call(prompt, max_tokens=4000)
            if result and result.get("response"):
                content = result["response"]
                return {
                    "title": self._extract_title(content, topic),
                    "topic": topic,
                    "domain": domain,
                    "content": content,
                    "word_count": len(content),
                    "sections": sections,
                    "source": "api_generated"
                }
        except Exception as e:
            print(f"[文献生成] API生成失败: {e}")
        
        return self._generate_via_template(domain, topic, sections)
    
    def _generate_via_template(self, domain: str, topic: str, sections: List[str]) -> Dict:
        """通过模板生成文献"""
        content_parts = [f"标题：{topic}\n"]
        
        for section in sections:
            if section == "摘要":
                content_parts.append(f"\n{section}：\n本文研究了{topic}相关问题，通过分析相关数据和案例，得出了重要结论。\n")
            elif section == "引言":
                content_parts.append(f"\n{section}：\n{topic}是{domain}领域的重要研究课题。随着技术发展，该领域取得了显著进展。\n")
            elif section == "参考文献":
                content_parts.append(f"\n{section}：\n[1] 张三. {topic}研究[J]. {domain}学报, 2024.\n[2] 李四. 相关领域分析[J]. 科技期刊, 2023.\n")
            else:
                content_parts.append(f"\n{section}：\n本部分对{topic}进行了深入分析，结合实际案例进行了探讨。\n")
        
        content = "".join(content_parts)
        
        return {
            "title": topic,
            "topic": topic,
            "domain": domain,
            "content": content,
            "word_count": len(content),
            "sections": sections,
            "source": "template_generated"
        }
    
    def _extract_title(self, content: str, default: str) -> str:
        """从内容中提取标题"""
        title_match = re.search(r'标题[：:]\s*(.+?)(?:\n|$)', content)
        if title_match:
            return title_match.group(1).strip()
        return default
    
    def generate_literature_batch(self, domain: str, count: int, length: int = 2000) -> List[Dict]:
        """批量生成文献"""
        literatures = []
        template = self.LITERATURE_TEMPLATES.get(domain, self.LITERATURE_TEMPLATES["医疗"])
        topics = template["topics"]
        
        for i in range(count):
            topic = topics[i % len(topics)] if i < len(topics) * 3 else f"{domain}研究课题{i+1}"
            lit = self.generate_literature(domain, topic, length)
            lit["id"] = i + 1
            literatures.append(lit)
        
        return literatures


def generate_knowledge_graph(domain: str, count: int, use_api: bool = True) -> List[Dict]:
    """生成知识图谱三元组"""
    generator = KnowledgeGraphGenerator()
    triples = generator.generate_triples_batch(domain, count, use_api)
    return [t.to_dict() for t in triples]


def generate_literature(domain: str, count: int = 1, length: int = 2000) -> List[Dict]:
    """生成文献"""
    generator = LiteratureGenerator()
    return generator.generate_literature_batch(domain, count, length)
