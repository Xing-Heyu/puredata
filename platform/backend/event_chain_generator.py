#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用事件链数据生成器 - 支持多领域模板配置 (优化版)
生成"事件→影响→结果"完整因果链数据，支持置信度分级和可量化指标
"""

import os
import json
import re
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class ConfidenceLevel(Enum):
    """置信度分级"""
    COMMERCIAL = "commercial"      # 成熟商业化: 0.90-0.95
    PILOT = "pilot"                # 规模试点: 0.80-0.90
    EXPLORATORY = "exploratory"    # 前沿/探索: 0.70-0.80


@dataclass
class EventChain:
    """事件链数据结构 (优化版)"""
    chain_id: str
    domain: str
    source_event: str
    transmission_path: List[str]
    final_result: str
    confidence: float = 0.85
    confidence_level: str = "pilot"  # 新增: 置信度分级
    timestamp: str = ""
    metadata: Dict = field(default_factory=dict)
    quantifiable_metrics: Dict = field(default_factory=dict)  # 新增: 可量化指标
    extended_dimensions: Dict = field(default_factory=dict)   # 新增: 扩展维度
    
    def to_dict(self) -> Dict:
        result = {
            "chain_id": self.chain_id,
            "domain": self.domain,
            "source_event": self.source_event,
            "transmission_path": self.transmission_path,
            "final_result": self.final_result,
            "chain": f"{self.source_event} → {' → '.join(self.transmission_path)} → {self.final_result}",
            "confidence": self.confidence,
            "confidence_level": self.confidence_level,
            "timestamp": self.timestamp,
            **self.metadata
        }
        
        # 添加可量化指标
        if self.quantifiable_metrics:
            result["quantifiable_metrics"] = self.quantifiable_metrics
        
        # 添加扩展维度
        if self.extended_dimensions:
            result["extended_dimensions"] = self.extended_dimensions
        
        return result


class EventChainTemplates:
    """事件链模板配置 - 支持多领域 (优化版)"""
    
    # 评级顺序（从高到低）
    RATING_ORDER = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
    
    # 置信度分级配置
    CONFIDENCE_RANGES = {
        ConfidenceLevel.COMMERCIAL: (0.90, 0.95),
        ConfidenceLevel.PILOT: (0.80, 0.90),
        ConfidenceLevel.EXPLORATORY: (0.70, 0.80)
    }
    
    TEMPLATES = {
        "金融": {
            "chain_types": {
                "舆情→股价": {
                    "source_events": {
                        "negative": [
                            # 从"现象"改为"驱动"
                            "监管处罚力度加大驱动合规成本上升",
                            "业绩暴雷引发投资者信心危机",
                            "高管减持套现导致市场恐慌",
                            "财务造假曝光触发信任崩塌",
                            "行业监管趋严推动估值重构",
                            "国际局势紧张驱动避险情绪升温"
                        ],
                        "positive": [
                            "业绩预增超预期驱动估值修复",
                            "大额分红公告推动股东回报提升",
                            "核心技术突破驱动竞争力增强",
                            "政策利好释放推动行业景气度上升",
                            "重大订单落地驱动营收增长"
                        ]
                    },
                    "transmission_nodes": {
                        "negative": [
                            ["市场情绪转弱", "投资者信心下降", "风险偏好降低"],
                            ["机构主动减持", "北向资金流出", "主力资金撤离"],
                            ["散户跟风抛售", "融资盘平仓", "成交量异常放大"],
                            ["卖盘压力增加", "买盘承接不足", "流动性收紧"]
                        ],
                        "positive": [
                            ["市场情绪回暖", "投资者信心提振", "风险偏好回升"],
                            ["机构主动增持", "北向资金流入", "主力资金买入"],
                            ["散户跟风买入", "融资盘加仓", "成交量温和放大"],
                            ["买盘力量增强", "卖盘压力减轻", "流动性改善"]
                        ]
                    },
                    "results": {
                        "negative": [
                            "股价下跌{percent}%",
                            "市值蒸发{amount}亿",
                            "估值中枢下移{percent}%",
                            "机构持仓比例下降{percent}%"
                        ],
                        "positive": [
                            "股价上涨{percent}%",
                            "市值增长{amount}亿",
                            "估值中枢上移{percent}%",
                            "机构持仓比例提升{percent}%"
                        ]
                    },
                    # 可量化指标模板
                    "quantifiable_metrics": {
                        "price_change": "{change}%",
                        "market_value_change": "{value}亿元",
                        "turnover_rate": "{rate}%",
                        "institution_holding_change": "{change}%",
                        "pe_ratio_change": "{change}x"
                    },
                    # 扩展维度
                    "extended_dimensions": {
                        "affected_industry": ["科技", "消费", "金融", "医药", "新能源"],
                        "market_cap_segment": ["大盘股", "中盘股", "小盘股"],
                        "investor_structure": ["机构主导", "散户主导", "均衡结构"],
                        "policy_sensitivity": ["高敏感", "中敏感", "低敏感"]
                    },
                    "metadata_template": {
                        "event_type": "舆情事件",
                        "affected_stock": "{stock_name}",
                        "market_sentiment": "{sentiment}",
                        "liquidity_impact": "{impact}",
                        "confidence_source": "{source}"
                    }
                },
                "ESG→股价": {
                    "source_events": [
                        "碳排放超标驱动环保合规成本激增",
                        "劳动权益争议驱动人力成本上升",
                        "数据隐私泄露驱动合规风险暴露",
                        "商业道德问题驱动品牌价值受损",
                        "供应链ESG风险驱动运营中断",
                        "产品质量危机驱动消费者信任崩塌"
                    ],
                    "transmission_nodes": [
                        ["ESG评级下调", "ESG评分下降", "可持续性评级降低"],
                        ["ESG基金被动减持", "责任投资者撤资", "绿色资金流出"],
                        ["品牌形象受损", "消费者抵制", "市场份额下滑"],
                        ["营收增长放缓", "净利润率下降", "现金流承压"]
                    ],
                    "results": [
                        "股价长期承压下跌{percent}%",
                        "估值折价扩大{percent}%",
                        "机构持仓比例下降{percent}%",
                        "融资成本上升{bps}个基点"
                    ],
                    "quantifiable_metrics": {
                        "esg_score_change": "{change}分",
                        "carbon_cost_increase": "{amount}万元/年",
                        "brand_value_impact": "{amount}亿元",
                        "compliance_cost": "{amount}万元",
                        "market_share_change": "{change}%"
                    },
                    "extended_dimensions": {
                        "esg_dimension": ["环境E", "社会S", "治理G"],
                        "stakeholder_impact": ["投资者", "消费者", "员工", "供应商"],
                        "recovery_difficulty": ["容易", "中等", "困难"],
                        "regulatory_risk": ["高", "中", "低"]
                    },
                    "metadata_template": {
                        "event_type": "ESG事件",
                        "esg_dimension": "{dimension}",
                        "rating_before": "{rating_before}",
                        "rating_after": "{rating_after}",
                        "stakeholder_reaction": "{reaction}",
                        "confidence_source": "{source}"
                    }
                },
                "政策→板块": {
                    "source_events": [
                        "货币政策宽松驱动流动性改善",
                        "财政政策加码驱动基建投资升温",
                        "产业政策扶持驱动战略新兴行业崛起",
                        "监管政策收紧驱动行业格局重构",
                        "利率下调驱动融资成本下降",
                        "汇率波动驱动出口竞争力变化"
                    ],
                    "transmission_nodes": [
                        ["行业预期改变", "盈利预测调整", "估值逻辑重构"],
                        ["资金流向变化", "板块轮动加速", "主题投资升温"],
                        ["龙头股率先反应", "概念股跟涨", "产业链传导"]
                    ],
                    "results": [
                        "板块整体上涨{percent}%",
                        "板块内部分化加剧",
                        "龙头股市占率提升{percent}%",
                        "行业集中度CR5提升至{percent}%"
                    ],
                    "quantifiable_metrics": {
                        "sector_index_change": "{change}%",
                        "capital_inflow": "{amount}亿元",
                        "leading_stock_outperformance": "{change}%",
                        "market_concentration": "CR{cr}%",
                        "policy_beta": "{beta}"
                    },
                    "extended_dimensions": {
                        "policy_type": ["货币", "财政", "产业", "监管"],
                        "implementation_timeline": ["立即", "3个月内", "6个月内", "1年内"],
                        "beneficiary_scope": ["全行业", "细分龙头", "特定企业"],
                        "duration": ["短期", "中期", "长期"]
                    },
                    "metadata_template": {
                        "event_type": "政策事件",
                        "policy_type": "{policy}",
                        "affected_sector": "{sector}",
                        "policy_strength": "{strength}",
                        "confidence_source": "{source}"
                    }
                }
            },
            "variations": {
                "stock_name": ["某科技公司", "某上市公司", "龙头企业", "行业龙头", "中小盘股", "蓝筹股", "白马股"],
                "change_percent": ["3.5", "5.2", "8.7", "12.3", "15.6", "2.1", "5.8", "10.2"],
                "amount_billion": ["5", "10", "20", "50", "100", "200"],
                "turnover_rate": ["5", "10", "15", "20", "30"],
                "pe_ratio": ["15", "20", "25", "30", "35"],
                "sentiment": ["极度悲观", "悲观", "谨慎", "中性", "乐观", "积极"],
                "impact": ["流动性枯竭", "流动性收紧", "流动性中性", "流动性改善", "流动性充裕"],
                "dimension": ["环境E", "社会S", "治理G"],
                "rating_before": ["AAA", "AA", "A", "BBB"],
                "rating_after": ["AA", "A", "BBB", "BB", "B", "CCC"],
                "policy": ["货币政策", "财政政策", "产业政策", "监管政策"],
                "sector": ["科技板块", "消费板块", "金融板块", "医药板块", "新能源板块"],
                "strength": ["强力", "中等", "温和"],
                "source": ["历史数据回测", "专家共识", "模型预测", "情景分析"]
            }
        },
        "医疗": {
            "chain_types": {
                "技术→应用": {
                    "source_events": [
                        "AI影像筛查技术成熟驱动诊断效率提升",
                        "精准医疗突破驱动个性化治疗方案普及",
                        "远程医疗技术普及驱动医疗资源下沉",
                        "手术机器人应用驱动微创手术渗透率提升",
                        "基因编辑技术突破驱动罕见病治疗希望"
                    ],
                    "transmission_nodes": [
                        ["技术验证完成", "临床试点成功", "监管审批通过"],
                        ["医院采购增加", "医生培训普及", "患者接受度提升"],
                        ["诊疗流程优化", "医疗成本下降", "服务质量提升"]
                    ],
                    "results": [
                        "诊断准确率提升至{percent}%",
                        "诊疗时间缩短{percent}%",
                        "医疗成本降低{percent}%",
                        "患者满意度提升至{percent}%"
                    ],
                    "quantifiable_metrics": {
                        "diagnostic_accuracy": "{percent}%",
                        "time_reduction": "{percent}%",
                        "cost_reduction": "{percent}%",
                        "penetration_rate": "{percent}%",
                        "patient_satisfaction": "{score}分"
                    },
                    "extended_dimensions": {
                        "technology_type": ["AI诊断", "精准医疗", "远程医疗", "机器人手术"],
                        "application_scenario": ["三甲医院", "基层医疗", "专科医院", "体检中心"],
                        "disease_category": ["肿瘤", "心血管", "神经系统", "罕见病"],
                        "regulatory_status": ["已获批", "临床试验中", "研发阶段"]
                    },
                    "metadata_template": {
                        "event_type": "技术应用",
                        "technology": "{tech}",
                        "application": "{app}",
                        "clinical_evidence": "{evidence}",
                        "confidence_source": "{source}"
                    }
                },
                "需求→供给": {
                    "source_events": [
                        "人口老龄化加速驱动慢病管理需求激增",
                        "健康意识提升驱动预防性医疗需求增长",
                        "医保覆盖扩大驱动医疗服务可及性提升",
                        "疫情后健康管理意识驱动体检需求上升"
                    ],
                    "transmission_nodes": [
                        ["市场需求测算", "供给缺口分析", "投资机会识别"],
                        ["产能扩张计划", "人才引进策略", "设备采购增加"],
                        ["服务能力提升", "覆盖范围扩大", "运营效率优化"]
                    ],
                    "results": [
                        "市场渗透率提升至{percent}%",
                        "服务供给量增长{percent}%",
                        "人均医疗资源提升至{value}",
                        "行业集中度CR5提升至{percent}%"
                    ],
                    "quantifiable_metrics": {
                        "market_penetration": "{percent}%",
                        "supply_growth": "{percent}%",
                        "resource_per_capita": "{value}",
                        "market_concentration": "CR{cr}%",
                        "capacity_utilization": "{percent}%"
                    },
                    "extended_dimensions": {
                        "demand_type": ["刚性需求", "改善性需求", "预防性需求"],
                        "service_type": ["诊疗", "药品", "器械", "健康管理"],
                        "payment_method": ["医保", "商保", "自费"],
                        "geographic_coverage": ["一线城市", "二线城市", "三四线城市", "县域"]
                    },
                    "metadata_template": {
                        "event_type": "需求驱动",
                        "demand_driver": "{driver}",
                        "supply_response": "{response}",
                        "market_gap": "{gap}",
                        "confidence_source": "{source}"
                    }
                }
            },
            "variations": {
                "tech": ["深度学习", "计算机视觉", "自然语言处理", "知识图谱"],
                "app": ["影像诊断", "病理分析", "药物研发", "健康管理"],
                "evidence": ["多中心RCT", "真实世界研究", "回顾性分析", "专家共识"],
                "driver": ["人口结构", "疾病谱变化", "支付能力提升", "政策推动"],
                "response": ["快速扩张", "稳步增长", "结构优化", "模式创新"],
                "gap": ["显著缺口", "结构性缺口", "区域性缺口", "基本平衡"],
                "source": ["临床数据", "流行病学研究", "卫生统计", "专家调研"]
            }
        },
        "人工智能": {
            "chain_types": {
                "技术→应用": {
                    "source_events": [
                        "大模型技术突破驱动AIGC应用爆发",
                        "多模态融合技术成熟驱动交互体验升级",
                        "边缘AI芯片性能提升驱动端侧智能普及",
                        "联邦学习技术进步驱动隐私计算应用",
                        "AutoML技术成熟驱动AI开发门槛降低"
                    ],
                    "transmission_nodes": [
                        ["技术可行性验证", "场景适配优化", "工程化落地"],
                        ["产品化开发", "商业模式验证", "市场推广加速"],
                        ["用户规模增长", "数据飞轮效应", "模型持续优化"]
                    ],
                    "results": [
                        "应用渗透率提升至{percent}%",
                        "人机协作效率提升{percent}%",
                        "AI替代率提升至{percent}%",
                        "行业数字化程度提升至{percent}%"
                    ],
                    "quantifiable_metrics": {
                        "adoption_rate": "{percent}%",
                        "efficiency_gain": "{percent}%",
                        "automation_rate": "{percent}%",
                        "cost_reduction": "{percent}%",
                        "roi": "{ratio}x"
                    },
                    "extended_dimensions": {
                        "ai_capability": ["感知", "认知", "决策", "生成"],
                        "deployment_mode": ["云端", "边缘", "端侧", "混合"],
                        "business_model": ["SaaS", "PaaS", "解决方案", "API服务"],
                        "maturity_level": ["概念验证", "试点应用", "规模推广", "成熟应用"]
                    },
                    "metadata_template": {
                        "event_type": "技术落地",
                        "ai_technology": "{ai_tech}",
                        "application_domain": "{domain}",
                        "maturity": "{maturity}",
                        "confidence_source": "{source}"
                    }
                }
            },
            "variations": {
                "ai_tech": ["大语言模型", "计算机视觉", "语音合成", "推荐系统"],
                "domain": ["内容创作", "客户服务", "代码生成", "数据分析"],
                "maturity": ["早期探索", "快速增长", "成熟稳定", "衰退替代"],
                "source": ["技术论文", "产业报告", "企业案例", "用户调研"]
            }
        },
        "交通驾驶": {
            "chain_types": {
                "技术→安全": {
                    "source_events": [
                        "AEB自动紧急制动技术普及驱动主动安全提升",
                        "车道保持辅助系统成熟驱动偏离事故减少",
                        "盲区监测系统部署驱动变道安全性提升",
                        "驾驶员疲劳监测系统应用驱动疲劳驾驶事故下降"
                    ],
                    "transmission_nodes": [
                        ["传感器性能提升", "算法准确率优化", "系统集成完善"],
                        ["整车厂标配率提升", "消费者认知增强", "保险费率优惠"],
                        ["事故率下降", "伤亡率降低", "保险赔付减少"]
                    ],
                    "results": [
                        "主动安全系统装配率提升至{percent}%",
                        "相关类型事故率下降{percent}%",
                        "人员伤亡减少{percent}%",
                        "保险赔付成本降低{percent}%"
                    ],
                    "quantifiable_metrics": {
                        "adoption_rate": "{percent}%",
                        "accident_reduction": "{percent}%",
                        "casualty_reduction": "{percent}%",
                        "insurance_saving": "{amount}元/年",
                        "system_response_time": "{time}ms"
                    },
                    "extended_dimensions": {
                        "safety_system": ["AEB", "LKA", "BSD", "DMS"],
                        "vehicle_type": ["乘用车", "商用车", "新能源车", "传统燃油车"],
                        "road_condition": ["高速公路", "城市道路", "乡村道路"],
                        "weather_condition": ["晴天", "雨天", "雾天", "夜间"]
                    },
                    "metadata_template": {
                        "event_type": "安全提升",
                        "safety_tech": "{tech}",
                        "application_scenario": "{scenario}",
                        "effectiveness": "{effect}",
                        "confidence_source": "{source}"
                    }
                }
            },
            "variations": {
                "tech": ["自动刹车", "车道保持", "盲区监测", "疲劳监测"],
                "scenario": ["高速巡航", "城市拥堵", "泊车辅助", "紧急避让"],
                "effect": ["显著有效", "中等有效", "轻微有效", "待验证"],
                "source": ["NCAP测试", "保险公司数据", "交管部门统计", "车企报告"]
            }
        }
    }


class EventChainGenerator:
    """事件链数据生成器 (优化版)"""
    
    def __init__(self, api_key: str = None, default_confidence_level: ConfidenceLevel = ConfidenceLevel.PILOT):
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        self._qwen_api = None
        self.templates = EventChainTemplates.TEMPLATES
        self.default_confidence_level = default_confidence_level
    
    def _get_qwen_api(self):
        if self._qwen_api is None and self.api_key:
            try:
                from 千问API集成 import QwenAPI
                self._qwen_api = QwenAPI(self.api_key)
            except ImportError:
                pass
        return self._qwen_api
    
    def _generate_confidence(self, level: ConfidenceLevel = None) -> Tuple[float, str]:
        """生成置信度及分级"""
        if level is None:
            level = self.default_confidence_level
        
        min_val, max_val = EventChainTemplates.CONFIDENCE_RANGES[level]
        confidence = round(random.uniform(min_val, max_val), 2)
        return confidence, level.value
    
    def _generate_quantifiable_metrics(self, domain: str, chain_type: str, direction: str) -> Dict:
        """生成可量化指标"""
        metrics = {}
        
        if domain == "金融":
            if "股价" in chain_type or "ESG" in chain_type:
                metrics = {
                    "price_change": f"{random.choice(['-', '+'])}{random.choice(['3.5', '5.2', '8.7', '12.3', '15.6'])}%",
                    "market_value_change": f"{random.choice(['5', '10', '20', '50'])}亿元",
                    "turnover_rate": f"{random.choice(['5', '10', '15', '20', '30'])}%",
                    "institution_holding_change": f"{random.choice(['-5', '-3', '+2', '+5'])}%",
                    "pe_ratio_change": f"{random.choice(['-5', '-3', '+2', '+5'])}x"
                }
            elif "政策" in chain_type:
                metrics = {
                    "sector_index_change": f"{random.choice(['+', '-'])}{random.choice(['2.5', '5.0', '7.5', '10.0'])}%",
                    "capital_inflow": f"{random.choice(['5', '10', '20', '50'])}亿元",
                    "leading_stock_outperformance": f"{random.choice(['3', '5', '8', '12'])}%",
                    "market_concentration": f"CR{random.choice(['30', '40', '50', '60'])}%"
                }
        
        elif domain == "医疗":
            metrics = {
                "diagnostic_accuracy": f"{random.choice(['85', '90', '92', '95', '98'])}%",
                "time_reduction": f"{random.choice(['20', '30', '40', '50'])}%",
                "cost_reduction": f"{random.choice(['10', '15', '20', '25'])}%",
                "penetration_rate": f"{random.choice(['15', '25', '35', '50'])}%",
                "patient_satisfaction": f"{random.choice(['4.0', '4.2', '4.5', '4.8'])}分"
            }
        
        elif domain == "人工智能":
            metrics = {
                "adoption_rate": f"{random.choice(['20', '35', '50', '65'])}%",
                "efficiency_gain": f"{random.choice(['30', '50', '70', '100'])}%",
                "automation_rate": f"{random.choice(['15', '25', '40', '60'])}%",
                "cost_reduction": f"{random.choice(['20', '30', '40', '50'])}%",
                "roi": f"{random.choice(['2', '3', '5', '8'])}x"
            }
        
        elif domain == "交通驾驶":
            metrics = {
                "adoption_rate": f"{random.choice(['30', '50', '70', '85'])}%",
                "accident_reduction": f"{random.choice(['20', '35', '50', '65'])}%",
                "casualty_reduction": f"{random.choice(['25', '40', '55', '70'])}%",
                "system_response_time": f"{random.choice(['200', '300', '500', '800'])}ms"
            }
        
        return metrics
    
    def _generate_extended_dimensions(self, domain: str, chain_type: str) -> Dict:
        """生成扩展维度"""
        dimensions = {}
        
        domain_template = self.templates.get(domain, {})
        chain_config = domain_template.get("chain_types", {}).get(chain_type, {})
        extended_dims = chain_config.get("extended_dimensions", {})
        
        for dim_name, dim_values in extended_dims.items():
            if dim_values:
                dimensions[dim_name] = random.choice(dim_values)
        
        return dimensions
    
    def generate_chain(self, domain: str, chain_type: str = None, 
                      confidence_level: ConfidenceLevel = None) -> EventChain:
        """生成单条事件链 (优化版)"""
        domain_templates = self.templates.get(domain)
        if not domain_templates:
            return self._generate_generic_chain(domain)
        
        chain_types = domain_templates["chain_types"]
        if chain_type is None:
            chain_type = random.choice(list(chain_types.keys()))
        
        template = chain_types.get(chain_type)
        if not template:
            return self._generate_generic_chain(domain)
        
        # 判断事件方向
        source_events = template.get("source_events", {})
        if isinstance(source_events, dict):
            # 有正负区分
            event_direction = random.choice(["negative", "positive"])
            event_list = source_events.get(event_direction, [])
        else:
            event_list = source_events
            event_direction = "negative"
        
        source_event = random.choice(event_list) if event_list else f"{domain}相关事件"
        
        # 传导路径
        transmission_nodes = template.get("transmission_nodes", [])
        if isinstance(transmission_nodes, dict):
            nodes_list = transmission_nodes.get(event_direction, [])
        else:
            nodes_list = transmission_nodes
        
        transmission_path = [random.choice(node) for node in nodes_list] if nodes_list else ["影响扩大"]
        
        # 结果
        results = template.get("results", [])
        if isinstance(results, dict):
            results_list = results.get(event_direction, ["产生影响"])
        else:
            results_list = results
        
        final_result_template = random.choice(results_list) if results_list else "产生结果"
        
        # 填充结果模板中的变量
        final_result = final_result_template.format(
            percent=random.choice(["5", "10", "15", "20", "25", "30"]),
            amount=random.choice(["5", "10", "20", "50", "100"])
        )
        
        # 生成置信度
        confidence, conf_level = self._generate_confidence(confidence_level)
        
        # 生成元数据
        metadata = {}
        metadata_template = template.get("metadata_template", {})
        variations = domain_templates.get("variations", {})
        
        for key, value_template in metadata_template.items():
            value = value_template
            for var_key, var_values in variations.items():
                placeholder = "{" + var_key + "}"
                if placeholder in value and var_values:
                    value = value.replace(placeholder, random.choice(var_values))
            metadata[key] = value
        
        # 添加置信度来源
        metadata["confidence_source"] = random.choice([
            "历史数据回测验证",
            "专家共识评估",
            "统计模型预测",
            "多情景压力测试"
        ])
        
        # 生成可量化指标
        quantifiable_metrics = self._generate_quantifiable_metrics(domain, chain_type, event_direction)
        
        # 生成扩展维度
        extended_dimensions = self._generate_extended_dimensions(domain, chain_type)
        
        # 生成ID
        chain_id = f"{domain}_{chain_type.replace('→', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        return EventChain(
            chain_id=chain_id,
            domain=domain,
            source_event=source_event,
            transmission_path=transmission_path,
            final_result=final_result,
            confidence=confidence,
            confidence_level=conf_level,
            timestamp=datetime.now().isoformat(),
            metadata=metadata,
            quantifiable_metrics=quantifiable_metrics,
            extended_dimensions=extended_dimensions
        )
    
    def generate_chains_batch(self, domain: str, count: int, 
                             use_api: bool = True,
                             confidence_level: ConfidenceLevel = None) -> List[Dict]:
        """批量生成事件链 (优化版)"""
        chains = []
        
        if use_api:
            api_chains = self._generate_via_api(domain, count, confidence_level)
            if api_chains:
                chains.extend(api_chains)
        
        while len(chains) < count:
            chain = self.generate_chain(domain, confidence_level=confidence_level)
            chains.append(chain.to_dict())
        
        return chains[:count]
    
    def _generate_via_api(self, domain: str, count: int, 
                         confidence_level: ConfidenceLevel = None) -> List[Dict]:
        """通过API生成事件链 (优化版)"""
        qwen_api = self._get_qwen_api()
        if not qwen_api:
            return []
        
        domain_template = self.templates.get(domain, {})
        chain_types = list(domain_template.get("chain_types", {}).keys())
        chain_types_str = "、".join(chain_types) if chain_types else "通用事件链"
        
        # 获取置信度范围
        if confidence_level is None:
            confidence_level = self.default_confidence_level
        min_conf, max_conf = EventChainTemplates.CONFIDENCE_RANGES[confidence_level]
        
        prompt = f"""请生成{count}条关于"{domain}"领域的高质量事件链数据。

事件链格式：源头事件 → 传导路径 → 最终结果

支持的链类型：{chain_types_str}

要求：
1. 源头事件必须是"驱动型"描述（如"XX技术成熟驱动YY应用普及"）
2. 传导路径要有清晰的因果逻辑
3. 最终结果必须包含可量化指标（如"渗透率提升至XX%"）
4. 置信度必须在{min_conf}-{max_conf}之间
5. 按JSON数组格式输出

输出格式：
[
  {{
    "source_event": "驱动型源头事件",
    "transmission_path": ["传导节点1", "传导节点2"],
    "final_result": "可量化结果",
    "confidence": 0.85,
    "quantifiable_metrics": {{
      "metric1": "value1",
      "metric2": "value2"
    }},
    "extended_dimensions": {{
      "dimension1": "value1"
    }}
  }}
]

只输出JSON数组，不要其他内容。"""

        try:
            result = qwen_api.call(prompt, max_tokens=4000)
            if result and result.get("response"):
                response_text = result["response"]
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    chains = []
                    for i, item in enumerate(data[:count]):
                        chain_id = f"{domain}_api_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
                        
                        # 确保置信度在范围内
                        conf = item.get("confidence", 0.85)
                        conf = max(min_conf, min(max_conf, conf))
                        
                        chains.append({
                            "chain_id": chain_id,
                            "domain": domain,
                            "source_event": item.get("source_event", ""),
                            "transmission_path": item.get("transmission_path", []),
                            "final_result": item.get("final_result", ""),
                            "chain": f"{item.get('source_event', '')} → {' → '.join(item.get('transmission_path', []))} → {item.get('final_result', '')}",
                            "confidence": round(conf, 2),
                            "confidence_level": confidence_level.value if confidence_level else "pilot",
                            "timestamp": datetime.now().isoformat(),
                            "source": "api_generated",
                            "quantifiable_metrics": item.get("quantifiable_metrics", {}),
                            "extended_dimensions": item.get("extended_dimensions", {}),
                            **item
                        })
                    return chains
        except Exception as e:
            print(f"[事件链] API生成失败: {e}")
        
        return []
    
    def _generate_generic_chain(self, domain: str) -> EventChain:
        """生成通用事件链"""
        confidence, conf_level = self._generate_confidence()
        
        return EventChain(
            chain_id=f"{domain}_generic_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            domain=domain,
            source_event=f"{domain}领域关键驱动因素",
            transmission_path=["影响传导", "连锁反应"],
            final_result="产生可量化影响",
            confidence=confidence,
            confidence_level=conf_level,
            timestamp=datetime.now().isoformat(),
            quantifiable_metrics={"impact": "待量化"},
            extended_dimensions={"maturity": "探索阶段"}
        )


def generate_event_chains(domain: str, count: int, use_api: bool = True,
                         confidence_level: str = "pilot") -> List[Dict]:
    """生成事件链数据 - 入口函数 (优化版)"""
    # 转换置信度级别
    level_map = {
        "commercial": ConfidenceLevel.COMMERCIAL,
        "pilot": ConfidenceLevel.PILOT,
        "exploratory": ConfidenceLevel.EXPLORATORY
    }
    level = level_map.get(confidence_level, ConfidenceLevel.PILOT)
    
    generator = EventChainGenerator(default_confidence_level=level)
    return generator.generate_chains_batch(domain, count, use_api, level)


if __name__ == "__main__":
    # 测试不同置信度级别
    print("=== 测试商业化级别 (0.90-0.95) ===")
    chains = generate_event_chains("金融", 3, use_api=False, confidence_level="commercial")
    for chain in chains:
        print(f"置信度: {chain['confidence']} ({chain['confidence_level']})")
        print(f"可量化指标: {chain.get('quantifiable_metrics', {})}")
        print("-" * 50)
    
    print("\n=== 测试试点级别 (0.80-0.90) ===")
    chains = generate_event_chains("医疗", 3, use_api=False, confidence_level="pilot")
    for chain in chains:
        print(f"置信度: {chain['confidence']} ({chain['confidence_level']})")
        print(f"可量化指标: {chain.get('quantifiable_metrics', {})}")
        print("-" * 50)
