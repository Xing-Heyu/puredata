#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融领域专精化模块
金融术语、市场逻辑、投资分析
"""

from .base_specialist import DomainSpecialist
from typing import Dict, List, Any, Optional
import random

class FinanceSpecialist(DomainSpecialist):
    """金融领域专精生成器"""
    
    domain_name = "finance"
    domain_display_name = "金融"
    
    def _load_entities(self) -> Dict[str, List[str]]:
        return {
            "markets": [
                "股票市场", "债券市场", "外汇市场", "期货市场", "期权市场",
                "货币市场", "资本市场", "衍生品市场", "黄金市场", "大宗商品市场"
            ],
            "instruments": [
                "股票", "债券", "基金", "期货", "期权", "ETF", "REITs",
                "国债", "企业债", "可转债", "权证", "掉期"
            ],
            "indicators": [
                "市盈率", "市净率", "净资产收益率", "资产负债率", "流动比率",
                "速动比率", "毛利率", "净利率", "股息率", "换手率",
                "成交量", "成交额", "涨跌幅", "振幅", "市销率"
            ],
            "risks": [
                "市场风险", "信用风险", "流动性风险", "操作风险", "法律风险",
                "政策风险", "汇率风险", "利率风险", "通胀风险", "系统性风险"
            ],
            "strategies": [
                "价值投资", "成长投资", "指数投资", "量化投资", "对冲策略",
                "套利策略", "资产配置", "定投策略", "波段操作", "趋势跟踪"
            ],
            "institutions": [
                "商业银行", "投资银行", "证券公司", "基金公司", "保险公司",
                "信托公司", "期货公司", "资产管理公司", "私募基金", "央行"
            ],
            "currencies": [
                "人民币", "美元", "欧元", "日元", "英镑", "港币", "韩元"
            ],
            "sectors": [
                "银行", "证券", "保险", "房地产", "科技", "医药", "消费",
                "能源", "材料", "工业", "公用事业", "电信", "互联网"
            ],
            "actions": [
                "买入", "卖出", "持有", "增持", "减持", "清仓", "建仓", "调仓"
            ],
            "analysis_methods": [
                "基本面分析", "技术分析", "量化分析", "宏观经济分析",
                "行业分析", "财务分析", "估值分析", "风险分析"
            ]
        }
    
    def _load_relations(self) -> Dict[str, List[str]]:
        return {
            "indicator_reflects_performance": ["反映", "体现", "显示"],
            "risk_affects_return": ["影响", "导致", "决定"],
            "strategy_guides_investment": ["指导", "用于", "应用于"],
            "institution_provides_service": ["提供", "发行", "管理"],
            "allowed": ["投资于", "配置于", "持有", "交易"]
        }
    
    def _load_constraints(self) -> Dict[str, Any]:
        return {
            "pe_ratio": {"type": "range", "min": 0, "max": 500},
            "pb_ratio": {"type": "range", "min": 0, "max": 50},
            "roe": {"type": "range", "min": -50, "max": 100},
            "debt_ratio": {"type": "range", "min": 0, "max": 100},
            "dividend_yield": {"type": "range", "min": 0, "max": 20},
            "change_percent": {"type": "range", "min": -20, "max": 20}
        }
    
    def _load_templates(self) -> Dict[str, List[str]]:
        return {
            "market_analysis": [
                "{market}今日{trend}，成交额达{volume}亿元，{reason}。",
                "受{factor}影响，{market}{trend}，{sector}板块{sector_trend}。",
                "{market}收盘报{index}点，{change}%，市场情绪{sentiment}。"
            ],
            "stock_analysis": [
                "{stock}当前市盈率{pe}倍，市净率{pb}倍，{valuation}。",
                "{stock}发布财报，净利润同比增长{profit_growth}%，{comment}。",
                "{stock}股价{change}%，成交额{volume}万元，{reason}。"
            ],
            "financial_indicator": [
                "{company}{indicator}为{value}，{comparison}行业平均水平。",
                "根据财务数据，{company}{indicator}{trend}，{analysis}。",
                "{indicator}是衡量{aspect}的重要指标，{company}该指标为{value}。"
            ],
            "investment_strategy": [
                "采用{strategy}策略，建议{action}{instrument}，{reason}。",
                "{strategy}适合{investor_type}投资者，{advantage}。",
                "基于{analysis_method}，推荐关注{sector}板块，{reason}。"
            ],
            "risk_warning": [
                "{instrument}存在{risk}风险，投资者需{precaution}。",
                "市场波动加剧，{risk}上升，建议{action}。",
                "投资{instrument}前，应充分了解{risk}，做好{preparation}。"
            ],
            "economic_data": [
                "{country}{data_type}为{value}，{comparison}预期，{impact}。",
                "央行{action}，{instrument}利率调整为{rate}%，{reason}。",
                "{data_type}数据公布，{value}，市场反应{reaction}。"
            ],
            "fund_performance": [
                "{fund_name}近一年收益率{return_rate}%，{ranking}。",
                "{fund_type}基金平均收益率{return_rate}%，{analysis}。",
                "{fund_name}规模{scale}亿元，主要持仓{holdings}。"
            ],
            "bond_info": [
                "{bond_name}票面利率{coupon_rate}%，期限{term}年，评级{rating}。",
                "国债收益率曲线{trend}，{maturity}年期收益率为{yield_rate}%。",
                "{bond_type}发行规模{amount}亿元，认购倍数{subscription_ratio}倍。"
            ]
        }
    
    def _load_knowledge(self) -> Dict[str, Any]:
        return {
            "valuation_levels": {
                "低估": {"pe_max": 15, "pb_max": 1.5},
                "合理": {"pe_max": 25, "pb_max": 3},
                "高估": {"pe_min": 25, "pb_min": 3}
            },
            "risk_levels": {
                "低风险": ["国债", "货币基金", "银行存款"],
                "中风险": ["债券基金", "混合基金", "蓝筹股"],
                "高风险": ["股票基金", "期货", "期权"]
            },
            "market_sentiments": ["乐观", "谨慎", "悲观", "中性", "观望"],
            "investor_types": ["保守型", "稳健型", "激进型", "平衡型"]
        }
    
    def _generate_single(self, index: int, quality: str) -> Optional[Dict]:
        template_type = random.choice(list(self.templates.keys()))
        template = random.choice(self.templates[template_type])
        
        try:
            if template_type == "market_analysis":
                content = template.format(
                    market=random.choice(self.entities["markets"]),
                    trend=random.choice(["上涨", "下跌", "震荡", "持平"]),
                    volume=round(random.uniform(500, 10000), 1),
                    reason=random.choice(["受政策利好刺激", "受外部因素影响", "市场情绪回暖"]),
                    factor=random.choice(["宏观经济数据", "政策变化", "国际形势"]),
                    sector=random.choice(self.entities["sectors"]),
                    sector_trend=random.choice(["领涨", "领跌", "活跃"]),
                    index=round(random.uniform(2500, 4000), 2),
                    change=round(random.uniform(-3, 3), 2),
                    sentiment=random.choice(self.knowledge["market_sentiments"])
                )
                return {
                    "id": index,
                    "domain": "金融",
                    "type": "市场分析",
                    "content": content
                }
            
            elif template_type == "stock_analysis":
                pe = round(random.uniform(5, 50), 1)
                pb = round(random.uniform(0.5, 5), 1)
                valuation = "估值偏低" if pe < 15 else "估值合理" if pe < 25 else "估值偏高"
                content = template.format(
                    stock=f"{random.choice(self.entities['sectors'])}龙头股",
                    pe=pe,
                    pb=pb,
                    valuation=valuation,
                    profit_growth=round(random.uniform(-20, 50), 1),
                    comment="业绩表现亮眼" if random.random() > 0.5 else "业绩承压",
                    change=round(random.uniform(-10, 10), 2),
                    volume=round(random.uniform(1000, 50000), 0),
                    reason=random.choice(["受行业景气度提升", "受市场情绪影响", "资金持续流入"])
                )
                return {
                    "id": index,
                    "domain": "金融",
                    "type": "个股分析",
                    "content": content
                }
            
            elif template_type == "financial_indicator":
                indicator = random.choice(self.entities["indicators"])
                content = template.format(
                    company=f"{random.choice(self.entities['sectors'])}企业",
                    indicator=indicator,
                    value=round(random.uniform(0.1, 100), 2),
                    comparison="高于" if random.random() > 0.5 else "低于",
                    trend=random.choice(["上升", "下降", "持平"]),
                    aspect=random.choice(["盈利能力", "偿债能力", "运营效率", "成长能力"]),
                    analysis="财务状况良好" if random.random() > 0.5 else "需关注财务风险"
                )
                return {
                    "id": index,
                    "domain": "金融",
                    "type": "财务指标",
                    "indicator": indicator,
                    "content": content
                }
            
            elif template_type == "investment_strategy":
                strategy = random.choice(self.entities["strategies"])
                content = template.format(
                    strategy=strategy,
                    action=random.choice(self.entities["actions"]),
                    instrument=random.choice(self.entities["instruments"]),
                    reason="符合当前市场环境",
                    investor_type=random.choice(self.knowledge["investor_types"]),
                    advantage="风险收益比较优",
                    analysis_method=random.choice(self.entities["analysis_methods"]),
                    sector=random.choice(self.entities["sectors"])
                )
                return {
                    "id": index,
                    "domain": "金融",
                    "type": "投资策略",
                    "strategy": strategy,
                    "content": content
                }
            
            elif template_type == "risk_warning":
                content = template.format(
                    instrument=random.choice(self.entities["instruments"]),
                    risk=random.choice(self.entities["risks"]),
                    precaution="合理控制仓位",
                    action="降低杠杆、分散投资",
                    preparation="风险评估和资金规划"
                )
                return {
                    "id": index,
                    "domain": "金融",
                    "type": "风险提示",
                    "content": content
                }
            
            elif template_type == "economic_data":
                content = template.format(
                    country=random.choice(["中国", "美国", "欧元区", "日本"]),
                    data_type=random.choice(["GDP增速", "CPI", "PMI", "失业率"]),
                    value=round(random.uniform(-2, 10), 1),
                    comparison="高于" if random.random() > 0.5 else "低于",
                    impact="利好市场" if random.random() > 0.5 else "市场承压",
                    action=random.choice(["降息", "加息", "降准", "维持利率不变"]),
                    rate=round(random.uniform(0.25, 5), 2),
                    reaction="积极" if random.random() > 0.5 else "谨慎"
                )
                return {
                    "id": index,
                    "domain": "金融",
                    "type": "经济数据",
                    "content": content
                }
            
            elif template_type == "fund_performance":
                content = template.format(
                    fund_name=f"{random.choice(['沪深300', '中证500', '创业板'])}指数基金",
                    return_rate=round(random.uniform(-20, 50), 1),
                    ranking="排名前10%" if random.random() > 0.5 else "排名中等",
                    fund_type=random.choice(["股票型", "债券型", "混合型", "货币型"]),
                    scale=round(random.uniform(1, 500), 1),
                    holdings=f"{random.choice(self.entities['sectors'])}板块"
                )
                return {
                    "id": index,
                    "domain": "金融",
                    "type": "基金表现",
                    "content": content
                }
            
            elif template_type == "bond_info":
                content = template.format(
                    bond_name=f"{random.randint(2024, 2030)}年国债",
                    coupon_rate=round(random.uniform(1, 5), 2),
                    term=random.choice([1, 3, 5, 10, 30]),
                    rating=random.choice(["AAA", "AA+", "AA"]),
                    trend=random.choice(["上行", "下行", "平坦化"]),
                    maturity=random.choice([1, 3, 5, 10]),
                    yield_rate=round(random.uniform(1, 5), 2),
                    bond_type=random.choice(["国债", "企业债", "地方债"]),
                    amount=round(random.uniform(10, 500), 1),
                    subscription_ratio=round(random.uniform(1, 5), 1)
                )
                return {
                    "id": index,
                    "domain": "金融",
                    "type": "债券信息",
                    "content": content
                }
            
        except Exception as e:
            return None
        
        return None
