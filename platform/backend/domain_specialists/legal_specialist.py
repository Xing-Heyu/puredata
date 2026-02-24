#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法律领域专精化模块
法律术语、案例分析、法规解读
"""

from .base_specialist import DomainSpecialist
from typing import Dict, List, Any, Optional
import random

class LegalSpecialist(DomainSpecialist):
    """法律领域专精生成器"""
    
    domain_name = "legal"
    domain_display_name = "法律"
    
    def _load_entities(self) -> Dict[str, List[str]]:
        return {
            "law_branches": [
                "民法", "刑法", "行政法", "商法", "经济法", "劳动法",
                "婚姻法", "继承法", "合同法", "公司法", "知识产权法"
            ],
            "case_types": [
                "民事案件", "刑事案件", "行政案件", "经济纠纷", "劳动争议",
                "合同纠纷", "侵权纠纷", "婚姻家庭纠纷", "房产纠纷", "债务纠纷"
            ],
            "parties": [
                "原告", "被告", "申请人", "被申请人", "第三人",
                "上诉人", "被上诉人", "申诉人", "受害人", "犯罪嫌疑人"
            ],
            "legal_documents": [
                "起诉状", "答辩状", "上诉状", "申诉状", "判决书",
                "裁定书", "调解书", "执行申请书", "证据清单", "代理词"
            ],
            "courts": [
                "基层人民法院", "中级人民法院", "高级人民法院", "最高人民法院",
                "专门人民法院", "知识产权法院", "互联网法院"
            ],
            "legal_actions": [
                "起诉", "应诉", "上诉", "申诉", "抗诉", "撤诉",
                "调解", "仲裁", "执行", "保全"
            ],
            "evidence_types": [
                "书证", "物证", "视听资料", "电子数据", "证人证言",
                "鉴定意见", "勘验笔录", "当事人陈述"
            ],
            "judgments": [
                "支持诉讼请求", "驳回诉讼请求", "部分支持", "调解结案",
                "撤回起诉", "发回重审", "改判", "维持原判"
            ],
            "legal_rights": [
                "财产权", "人身权", "知识产权", "继承权", "债权",
                "物权", "股权", "劳动权", "消费者权益"
            ],
            "legal_duties": [
                "履行合同义务", "承担侵权责任", "支付赔偿金", "返还财产",
                "消除影响", "恢复名誉", "赔礼道歉"
            ]
        }
    
    def _load_relations(self) -> Dict[str, List[str]]:
        return {
            "plaintiff_sues_defendant": ["起诉", "控告", "申请"],
            "court_hears_case": ["审理", "裁判", "调解"],
            "evidence_proves_fact": ["证明", "证实", "佐证"],
            "judgment_resolves_dispute": ["解决", "处理", "终结"],
            "allowed": ["依据", "根据", "参照", "适用"]
        }
    
    def _load_constraints(self) -> Dict[str, Any]:
        return {
            "amount_min": {"type": "range", "min": 1000, "max": 100000000},
            "sentence_years": {"type": "range", "min": 0.5, "max": 25},
            "appeal_days": {"type": "enum", "values": [10, 15, 30]}
        }
    
    def _load_templates(self) -> Dict[str, List[str]]:
        return {
            "case_description": [
                "{plaintiff}与{defendant}{case_type}一案，由{court}受理。",
                "本案系{case_type}，{plaintiff}诉称：{claim}。",
                "{court}审理查明：{fact}。"
            ],
            "legal_basis": [
                "依据《{law_name}》第{article}条规定，{legal_principle}。",
                "根据{law_name}相关规定，{application}。",
                "本案适用《{law_name}》，{reason}。"
            ],
            "judgment_result": [
                "判决如下：{judgment_content}。案件受理费{cost}元，由{bearer}负担。",
                "本院认为：{reasoning}。依照{legal_basis}，判决{judgment}。",
                "经审理，{fact_finding}，判决{judgment}。"
            ],
            "evidence_analysis": [
                "关于{evidence}，经质证，{analysis}，本院{adoption}。",
                "{party}提交的{evidence}，{credibility}，予以{adoption}。",
                "证据{evidence}证明{fact}，{party}对此{response}。"
            ],
            "legal_opinion": [
                "律师意见：{opinion}。法律依据：{legal_basis}。",
                "代理词：{content}。请求法院{request}。",
                "法律建议：{advice}。风险提示：{risk}。"
            ],
            "contract_clause": [
                "合同第{clause_num}条约定：{clause_content}。",
                "双方约定：{agreement}。违约责任：{liability}。",
                "合同条款：{term}。效力认定：{validity}。"
            ],
            "procedure_notice": [
                "本院定于{date}在{venue}公开审理本案，{parties_info}。",
                "上诉期限：判决书送达之日起{days}日内。上诉法院：{appeal_court}。",
                "执行申请期限：判决生效后{years}年内。"
            ],
            "rights_protection": [
                "{party}享有{right}，{basis}。",
                "权益受损时，可{remedy}，时效为{limitation}年。",
                "维权途径：{channel}。所需材料：{materials}。"
            ]
        }
    
    def _load_knowledge(self) -> Dict[str, Any]:
        return {
            "statute_limitations": {
                "一般诉讼时效": 3,
                "劳动争议仲裁": 1,
                "行政诉讼": 6
            },
            "court_levels": {
                "基层人民法院": "一审案件",
                "中级人民法院": "一审、二审案件",
                "高级人民法院": "二审、再审案件"
            },
            "burden_of_proof": {
                "民事案件": "谁主张谁举证",
                "刑事案件": "控方举证",
                "行政案件": "被告举证"
            }
        }
    
    def _generate_single(self, index: int, quality: str) -> Optional[Dict]:
        template_type = random.choice(list(self.templates.keys()))
        template = random.choice(self.templates[template_type])
        
        try:
            if template_type == "case_description":
                content = template.format(
                    plaintiff="原告",
                    defendant="被告",
                    case_type=random.choice(self.entities["case_types"]),
                    court=random.choice(self.entities["courts"]),
                    claim="请求判令被告承担相应责任",
                    fact="双方存在法律关系，被告存在违约行为"
                )
                return {
                    "id": index,
                    "domain": "法律",
                    "type": "案件描述",
                    "content": content
                }
            
            elif template_type == "legal_basis":
                content = template.format(
                    law_name=random.choice(self.entities["law_branches"]) + "典",
                    article=random.randint(1, 500),
                    legal_principle="当事人应当遵循诚实信用原则",
                    application="当事人的合法权益受法律保护",
                    reason="符合法律规定"
                )
                return {
                    "id": index,
                    "domain": "法律",
                    "type": "法律依据",
                    "content": content
                }
            
            elif template_type == "judgment_result":
                content = template.format(
                    judgment_content="被告于判决生效后十日内履行义务",
                    cost=random.randint(50, 5000),
                    bearer="被告",
                    reasoning="被告的行为构成违约，应承担相应责任",
                    legal_basis="相关法律规定",
                    judgment="支持原告的诉讼请求",
                    fact_finding="原告主张的事实成立"
                )
                return {
                    "id": index,
                    "domain": "法律",
                    "type": "判决结果",
                    "content": content
                }
            
            elif template_type == "evidence_analysis":
                content = template.format(
                    evidence=random.choice(self.entities["evidence_types"]),
                    analysis="内容真实、来源合法",
                    adoption="予以采信",
                    party=random.choice(self.entities["parties"]),
                    credibility="具有证明力",
                    fact="案件相关事实",
                    response="无异议"
                )
                return {
                    "id": index,
                    "domain": "法律",
                    "type": "证据分析",
                    "content": content
                }
            
            elif template_type == "legal_opinion":
                content = template.format(
                    opinion="当事人的主张有事实和法律依据",
                    legal_basis="相关法律规定",
                    content="根据案件事实和法律规定",
                    request="依法裁判",
                    advice="建议通过协商解决纠纷",
                    risk="诉讼存在不确定性"
                )
                return {
                    "id": index,
                    "domain": "法律",
                    "type": "法律意见",
                    "content": content
                }
            
            elif template_type == "contract_clause":
                content = template.format(
                    clause_num=random.randint(1, 30),
                    clause_content="双方权利义务的约定",
                    agreement="合同主要条款",
                    liability="违约方承担相应责任",
                    term="合同约定事项",
                    validity="合法有效"
                )
                return {
                    "id": index,
                    "domain": "法律",
                    "type": "合同条款",
                    "content": content
                }
            
            elif template_type == "procedure_notice":
                content = template.format(
                    date=f"2024年{random.randint(1,12)}月{random.randint(1,28)}日",
                    venue="本院第X审判庭",
                    parties_info="当事人应按时到庭",
                    days=random.choice([10, 15, 30]),
                    appeal_court="上级人民法院",
                    years=2
                )
                return {
                    "id": index,
                    "domain": "法律",
                    "type": "程序通知",
                    "content": content
                }
            
            elif template_type == "rights_protection":
                content = template.format(
                    party=random.choice(self.entities["parties"]),
                    right=random.choice(self.entities["legal_rights"]),
                    basis="法律明确规定",
                    remedy="依法维权",
                    limitation=random.choice([1, 2, 3]),
                    channel="诉讼、仲裁、调解",
                    materials="身份证明、证据材料"
                )
                return {
                    "id": index,
                    "domain": "法律",
                    "type": "权益保护",
                    "content": content
                }
            
        except Exception as e:
            return None
        
        return None
