#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
劳动合同领域专精化模块
基于中国劳动法，专业术语、法律逻辑、实务场景
"""

from .base_specialist import DomainSpecialist
from typing import Dict, List, Any, Optional
import random

class LaborSpecialist(DomainSpecialist):
    """劳动合同领域专精生成器"""
    
    domain_name = "labor"
    domain_display_name = "劳动合同"
    
    def _load_entities(self) -> Dict[str, List[str]]:
        return {
            "contract_types": [
                "固定期限劳动合同", "无固定期限劳动合同", "以完成一定工作任务为期限的劳动合同",
                "全日制用工合同", "非全日制用工合同", "劳务派遣合同", "外包合同"
            ],
            "positions": [
                "软件工程师", "产品经理", "UI设计师", "测试工程师", "运维工程师",
                "销售代表", "市场专员", "人事专员", "财务会计", "行政助理",
                "项目经理", "技术总监", "运营经理", "客服专员", "数据分析师"
            ],
            "salary_components": [
                "基本工资", "岗位工资", "绩效工资", "加班工资", "奖金",
                "津贴补贴", "年终奖", "项目奖金", "销售提成", "股权激励"
            ],
            "working_hours": [
                "标准工时制", "综合计算工时制", "不定时工作制", "弹性工作制"
            ],
            "social_insurance": [
                "养老保险", "医疗保险", "失业保险", "工伤保险", "生育保险", "住房公积金"
            ],
            "leave_types": [
                "年休假", "病假", "事假", "婚假", "丧假", "产假", "陪产假",
                "工伤假", "法定节假日", "带薪年假", "调休"
            ],
            "termination_reasons": [
                "协商解除", "劳动者提前三十日书面通知", "用人单位过失性辞退",
                "用人单位非过失性辞退", "经济性裁员", "合同到期不续签",
                "劳动者单方解除", "用人单位违法解除", "退休", "死亡"
            ],
            "violations": [
                "未签订书面劳动合同", "未缴纳社会保险", "拖欠工资",
                "违法解除劳动合同", "未支付加班费", "超时加班",
                "未提供劳动保护", "强迫劳动", "歧视性条款"
            ],
            "compensations": [
                "经济补偿金", "赔偿金", "代通知金", "加班费补发",
                "未休年休假工资", "双倍工资差额", "工伤赔偿", "医疗期工资"
            ],
            "departments": [
                "技术研发部", "产品设计部", "市场营销部", "人力资源部",
                "财务部", "运营部", "客服部", "行政部", "法务部", "战略发展部"
            ],
            "probation_periods": [
                "一个月", "两个月", "三个月", "六个月"
            ],
            "contract_terms": [
                "工作内容", "工作地点", "工作时间", "休息休假", "劳动报酬",
                "社会保险", "劳动保护", "劳动条件", "职业危害防护", "合同期限"
            ]
        }
    
    def _load_relations(self) -> Dict[str, List[str]]:
        return {
            "employee_signs_contract": ["签订", "续签", "变更"],
            "employer_pays_salary": ["支付", "发放", "结算"],
            "violation_leads_to_compensation": ["导致", "引发", "产生"],
            "termination_requires_notice": ["需要", "应当", "必须"],
            "allowed": ["享有", "承担", "履行", "遵守", "约定"]
        }
    
    def _load_constraints(self) -> Dict[str, Any]:
        return {
            "probation_months": {"type": "range", "min": 1, "max": 6},
            "notice_days": {"type": "enum", "values": [3, 7, 15, 30]},
            "work_hours_per_day": {"type": "range", "min": 4, "max": 8},
            "annual_leave_days": {"type": "range", "min": 5, "max": 15},
            "overtime_rate": {"type": "enum", "values": [1.5, 2.0, 3.0]}
        }
    
    def _load_templates(self) -> Dict[str, List[str]]:
        return {
            "contract_signing": [
                "甲方{employer}与乙方{employee}于{date}签订{contract_type}，约定{position}岗位，合同期限{duration}年。",
                "{employee}入职{employer}担任{position}，双方签订{contract_type}，试用期{probation}。",
                "根据《劳动合同法》规定，{employer}应在用工之日起一个月内与{employee}签订书面劳动合同。"
            ],
            "salary_provision": [
                "劳动合同约定{employee}月工资为{salary}元，其中基本工资{base_salary}元，绩效工资{performance_salary}元。",
                "{employer}应于每月{pay_day}日支付{employee}上月工资，工资结构包括{salary_components}。",
                "根据劳动合同约定，{employee}享有年终奖，发放标准为{bonus_standard}。"
            ],
            "working_hours": [
                "{employee}实行{work_hour_system}，每日工作{hours}小时，每周工作{days}天。",
                "因生产经营需要，{employer}安排{employee}加班的，应支付加班工资，工作日加班按{rate}倍计算。",
                "{employee}享有带薪年休假{leave_days}天，应在不影响工作的情况下安排休年假。"
            ],
            "social_insurance": [
                "{employer}应依法为{employee}缴纳{insurances}，缴费基数按实际工资确定。",
                "根据《社会保险法》规定，用人单位应当自用工之日起三十日内为职工办理社会保险登记。",
                "{employee}的住房公积金缴存比例为{fund_rate}%，由用人单位和职工各承担一半。"
            ],
            "termination": [
                "因{reason}，{employer}与{employee}解除劳动合同，应支付经济补偿金{compensation}元。",
                "{employee}提前{notice_days}日书面通知{employer}解除劳动合同，符合法律规定。",
                "根据《劳动合同法》第{article}条规定，{employer}可以解除劳动合同的情形包括{situations}。"
            ],
            "violation_handling": [
                "{employer}存在{violation}行为，应向{employee}支付赔偿金{amount}元。",
                "因{employer}未依法为{employee}缴纳社会保险，{employee}可以解除劳动合同并要求经济补偿。",
                "根据《劳动合同法》第八十二条规定，用人单位自用工之日起超过一个月不满一年未与劳动者订立书面劳动合同的，应当向劳动者每月支付二倍的工资。"
            ],
            "rights_protection": [
                "{employee}因劳动争议向劳动仲裁委员会申请仲裁，要求{demands}。",
                "根据《劳动争议调解仲裁法》，劳动争议申请仲裁的时效期间为一年。",
                "{employee}对仲裁裁决不服的，可以自收到仲裁裁决书之日起十五日内向人民法院提起诉讼。"
            ],
            "contract_change": [
                "经双方协商一致，{employer}与{employee}变更劳动合同{change_content}，变更后的合同自{effective_date}起生效。",
                "{employee}因{reason}申请调岗至{new_position}，经{employer}同意后变更劳动合同。",
                "劳动合同变更应当采用书面形式，变更后的劳动合同文本由用人单位和劳动者各执一份。"
            ]
        }
    
    def _load_knowledge(self) -> Dict[str, Any]:
        return {
            "law_articles": {
                "第十条": "建立劳动关系，应当订立书面劳动合同",
                "第十九条": "劳动合同期限三个月以上不满一年的，试用期不得超过一个月",
                "第二十条": "劳动合同期限一年以上不满三年的，试用期不得超过二个月",
                "第三十七条": "劳动者提前三十日以书面形式通知用人单位，可以解除劳动合同",
                "第四十六条": "有下列情形之一的，用人单位应当向劳动者支付经济补偿",
                "第八十二条": "用人单位自用工之日起超过一个月不满一年未与劳动者订立书面劳动合同的，应当向劳动者每月支付二倍的工资"
            },
            "compensation_standards": {
                "经济补偿金": "按劳动者在本单位工作的年限，每满一年支付一个月工资",
                "双倍工资": "未签订书面劳动合同的，支付二倍工资",
                "加班工资": "工作日1.5倍，休息日2倍，法定节假日3倍"
            },
            "probation_rules": {
                "合同期限不满3个月": "不得约定试用期",
                "合同期限3个月至1年": "试用期不得超过1个月",
                "合同期限1年至3年": "试用期不得超过2个月",
                "合同期限3年以上或无固定期限": "试用期不得超过6个月"
            }
        }
    
    def _generate_single(self, index: int, quality: str) -> Optional[Dict]:
        template_type = random.choice(list(self.templates.keys()))
        template = random.choice(self.templates[template_type])
        
        try:
            if template_type == "contract_signing":
                content = template.format(
                    employer=random.choice(["公司", "用人单位", "甲方"]),
                    employee="劳动者",
                    date=f"2024年{random.randint(1,12)}月{random.randint(1,28)}日",
                    contract_type=random.choice(self.entities["contract_types"]),
                    position=random.choice(self.entities["positions"]),
                    duration=random.choice([1, 2, 3, 5]),
                    probation=random.choice(self.entities["probation_periods"])
                )
                return {
                    "id": index,
                    "domain": "劳动合同",
                    "type": "合同签订",
                    "content": content
                }
            
            elif template_type == "salary_provision":
                base = random.randint(5000, 20000)
                performance = random.randint(1000, 5000)
                total = base + performance
                content = template.format(
                    employee="劳动者",
                    employer="用人单位",
                    salary=total,
                    base_salary=base,
                    performance_salary=performance,
                    pay_day=random.choice([5, 10, 15, 20, 25]),
                    salary_components="、".join(random.sample(self.entities["salary_components"], 3)),
                    bonus_standard="当年绩效考核结果确定"
                )
                return {
                    "id": index,
                    "domain": "劳动合同",
                    "type": "薪资条款",
                    "content": content
                }
            
            elif template_type == "working_hours":
                content = template.format(
                    employee="劳动者",
                    employer="用人单位",
                    work_hour_system=random.choice(self.entities["working_hours"]),
                    hours=8,
                    days=5,
                    rate=random.choice([1.5, 2.0, 3.0]),
                    leave_days=random.randint(5, 15)
                )
                return {
                    "id": index,
                    "domain": "劳动合同",
                    "type": "工时休假",
                    "content": content
                }
            
            elif template_type == "social_insurance":
                content = template.format(
                    employer="用人单位",
                    employee="劳动者",
                    insurances="、".join(self.entities["social_insurance"][:5]),
                    fund_rate=random.choice([5, 8, 12])
                )
                return {
                    "id": index,
                    "domain": "劳动合同",
                    "type": "社会保险",
                    "content": content
                }
            
            elif template_type == "termination":
                reason = random.choice(self.entities["termination_reasons"])
                years = random.randint(1, 10)
                compensation = years * random.randint(8000, 15000)
                content = template.format(
                    reason=reason,
                    employer="用人单位",
                    employee="劳动者",
                    compensation=compensation,
                    notice_days=random.choice([3, 7, 15, 30]),
                    article=random.choice(["三十九条", "四十条", "四十一条", "四十六条"]),
                    situations="严重违反规章制度、不能胜任工作等"
                )
                return {
                    "id": index,
                    "domain": "劳动合同",
                    "type": "合同解除",
                    "content": content
                }
            
            elif template_type == "violation_handling":
                violation = random.choice(self.entities["violations"])
                content = template.format(
                    employer="用人单位",
                    employee="劳动者",
                    violation=violation,
                    amount=random.randint(10000, 100000),
                    demands="支付拖欠工资、经济补偿金"
                )
                return {
                    "id": index,
                    "domain": "劳动合同",
                    "type": "违法处理",
                    "content": content
                }
            
            elif template_type == "rights_protection":
                content = template.format(
                    employee="劳动者",
                    demands="支付经济补偿金、补缴社会保险"
                )
                return {
                    "id": index,
                    "domain": "劳动合同",
                    "type": "权益维护",
                    "content": content
                }
            
            elif template_type == "contract_change":
                content = template.format(
                    employer="用人单位",
                    employee="劳动者",
                    change_content="工作岗位",
                    effective_date=f"2024年{random.randint(1,12)}月{random.randint(1,28)}日",
                    reason="工作需要",
                    new_position=random.choice(self.entities["positions"])
                )
                return {
                    "id": index,
                    "domain": "劳动合同",
                    "type": "合同变更",
                    "content": content
                }
            
        except Exception as e:
            return None
        
        return None
