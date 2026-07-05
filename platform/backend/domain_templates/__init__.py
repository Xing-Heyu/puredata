#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域模板系统 - Domain Template System
支持动态加载各领域的模板，方便扩展新领域

使用方法:
    from domain_templates import get_templates, get_variations, get_domain_config
    
    templates = get_templates("旅游")
    variations = get_variations("旅游")
    config = get_domain_config("旅游")
"""

import os
import json
from typing import Dict, List, Optional, Any

_DOMAIN_TEMPLATES_DIR = os.path.dirname(os.path.abspath(__file__))

_DOMAIN_CACHE = {}


class DomainConfig:
    """领域配置"""
    
    def __init__(self, domain: str, templates: List[str], variations: List[str],
                 knowledge: Dict[str, str] = None, keywords: List[str] = None,
                 structures: List[str] = None, noise_templates: List[str] = None):
        self.domain = domain
        self.templates = templates
        self.variations = variations
        self.knowledge = knowledge or {}
        self.keywords = keywords or []
        self.structures = structures or []
        self.noise_templates = noise_templates or []


def _load_domain_file(domain: str) -> Optional[Dict]:
    """加载领域配置文件"""
    if domain in _DOMAIN_CACHE:
        return _DOMAIN_CACHE[domain]
    
    filepath = os.path.join(_DOMAIN_TEMPLATES_DIR, f"{domain}.json")
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _DOMAIN_CACHE[domain] = data
                return data
        except Exception as e:
            print(f"[模板加载] 加载{domain}模板失败: {e}")
    
    return None


def get_templates(domain: str) -> List[str]:
    """获取领域模板"""
    data = _load_domain_file(domain)
    if data and "templates" in data:
        return data["templates"]
    
    return _get_default_templates(domain)


def get_variations(domain: str) -> List[str]:
    """获取领域变体"""
    data = _load_domain_file(domain)
    if data and "variations" in data:
        return data["variations"]
    
    return _get_default_variations(domain)


def get_domain_config(domain: str) -> DomainConfig:
    """获取完整领域配置"""
    data = _load_domain_file(domain)
    
    if data:
        return DomainConfig(
            domain=domain,
            templates=data.get("templates", _get_default_templates(domain)),
            variations=data.get("variations", _get_default_variations(domain)),
            knowledge=data.get("knowledge", {}),
            keywords=data.get("keywords", []),
            structures=data.get("structures", _get_default_structures(domain)),
            noise_templates=data.get("noise_templates", [])
        )
    
    return DomainConfig(
        domain=domain,
        templates=_get_default_templates(domain),
        variations=_get_default_variations(domain),
        structures=_get_default_structures(domain)
    )


def get_knowledge(domain: str) -> Dict[str, str]:
    """获取领域知识库"""
    data = _load_domain_file(domain)
    if data and "knowledge" in data:
        return data["knowledge"]
    return {}


def get_keywords(domain: str) -> List[str]:
    """获取领域关键词"""
    data = _load_domain_file(domain)
    if data and "keywords" in data:
        return data["keywords"]
    return []


def get_structures(domain: str) -> List[str]:
    """获取领域结构模板"""
    data = _load_domain_file(domain)
    if data and "structures" in data:
        return data["structures"]
    return _get_default_structures(domain)


def list_available_domains() -> List[str]:
    """列出所有可用领域（仅返回实际存在的JSON文件）"""
    domains = []
    
    if os.path.exists(_DOMAIN_TEMPLATES_DIR):
        for f in os.listdir(_DOMAIN_TEMPLATES_DIR):
            if f.endswith('.json') and f != '__init__.py':
                domains.append(f.replace('.json', ''))
    
    return domains


def _get_default_domains() -> List[str]:
    """获取默认领域列表（仅用于回退）"""
    return ["人工智能", "劳动合同", "医疗", "金融"]


def _get_default_templates(domain: str) -> List[str]:
    """获取默认模板（当文件不存在时使用）"""
    default_templates = {
        "人工智能": [
            "{word}是人工智能的核心技术，应用广泛。",
            "{word}技术发展迅速，应用场景不断扩展。",
            "基于{word}的创新解决方案正在重塑行业。",
            "{word}是机器学习的重要研究方向。",
            "在深度学习中，{word}扮演着关键角色。",
            "{word}技术已应用于图像和语音处理。",
            "专家预测{word}将成为未来的核心趋势。",
            "{word}是智能系统的基础技术。",
            "通过{word}，机器可以学习数据规律。",
            "{word}在自然语言处理中发挥重要作用。",
        ],
        "劳动合同": [
            "{word}是劳动关系的重要法律保障。",
            "根据规定，{word}条款需书面约定。",
            "处理{word}问题建议双方协商解决。",
            "{word}制度的完善有助于构建和谐劳动关系。",
            "劳动者在{word}方面的权利受到法律保护。",
            "用人单位应建立健全{word}管理制度。",
            "{word}纠纷中证据保存至关重要。",
            "{word}相关的合同条款应清晰明确。",
            "近年来{word}领域立法不断完善。",
            "妥善处理{word}问题能提升员工满意度。",
        ],
        "医疗": [
            "{word}技术在临床诊断中发挥着重要作用。",
            "基于{word}的医疗方案显著提升了治疗效率。",
            "{word}是现代医疗体系的重要组成部分。",
            "通过{word}技术，医生诊断更加准确。",
            "{word}技术已广泛应用于医疗影像分析。",
            "在疫情防控中，{word}功不可没。",
            "{word}设备提升了基层医疗服务能力。",
            "{word}对慢性病管理意义重大。",
            "多家医院已将{word}纳入标准诊疗流程。",
            "{word}技术有效缩短了患者康复周期。",
        ],
        "金融": [
            "【舆情事件】{word}事件引发市场关注，相关上市公司股价出现明显波动。",
            "【ESG影响】{word}问题暴露后，公司ESG评级下调，引发机构投资者减持。",
            "【股价联动】受{word}消息影响，板块整体走弱，龙头个股跌幅超过5%。",
            "【事件链条】{word}→市场情绪转弱→资金流出→股价下跌。",
            "【风险预警】{word}风险持续发酵，多家机构下调评级。",
            "【政策影响】{word}政策出台，利好相关板块，北向资金大幅流入。",
            "【机构动向】{word}引发机构关注，公募基金加仓，外资增持。",
            "【财务关联】{word}导致公司业绩下滑，净利润同比下降。",
            "【行业传导】{word}影响整个行业供应链，上下游企业股价联动下跌。",
            "【资金流向】{word}事件后，主力资金净流出超10亿，散户跟风抛售。",
        ],
        "交通驾驶": [
            "在{word}场景中，驾驶员需要保持高度警惕。",
            "{word}是智能驾驶系统的重要检测场景。",
            "遇到{word}情况，应立即采取避险措施。",
            "{word}场景对ADAS系统提出更高要求。",
            "研究表明{word}是交通事故的主要原因之一。",
            "在{word}情况下，反应时间至关重要。",
            "{word}场景需要多传感器融合感知。",
            "自动驾驶系统在{word}场景下的决策逻辑复杂。",
            "{word}是驾驶安全培训的重点内容。",
            "通过AI技术可以有效预警{word}风险。",
        ],
    }
    
    return default_templates.get(domain, default_templates["人工智能"])


def _get_default_variations(domain: str) -> List[str]:
    """获取默认变体"""
    return [
        "Note: {text}",
        "Ref: {text}",
        "【定义】{text}",
        "Step: {text}",
        "Key point: {text}",
        "→ {text}",
        "• {text}",
        "※ {text}",
        "★ {text}",
        "📌 {text}",
        "⚡ {text}",
        "💡 {text}",
        "📝 {text}",
        "👉 {text}",
        "✅ {text}",
        "[参考] {text}",
        "{text} [来源: 领域知识库]",
        "研究表明: {text}",
        "实践表明: {text}",
        "专家观点: {text}",
    ]


def _get_default_structures(domain: str) -> List[str]:
    """获取默认结构模板"""
    return [
        f"【定义】{{base}}",
        f"Q: 什么是{{keyword}}? A: {{base}}",
        f"参考: {{base}}",
        f"注: {{base}}",
        f"#{{index}} {{base}}",
        f"关于{{keyword}}: {{base}}",
        f"【{{keyword}}】{{base}}",
    ]


def create_domain_file(domain: str, templates: List[str] = None, 
                       variations: List[str] = None, knowledge: Dict = None,
                       keywords: List[str] = None, structures: List[str] = None):
    """创建新的领域模板文件"""
    data = {
        "domain": domain,
        "templates": templates or _get_default_templates(domain),
        "variations": variations or _get_default_variations(domain),
        "knowledge": knowledge or {},
        "keywords": keywords or [],
        "structures": structures or _get_default_structures(domain),
    }
    
    filepath = os.path.join(_DOMAIN_TEMPLATES_DIR, f"{domain}.json")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    _DOMAIN_CACHE[domain] = data
    
    print(f"[模板创建] 已创建{domain}领域模板文件: {filepath}")
    return filepath


if __name__ == "__main__":
    print("\n" + "="*60)
    print("领域模板系统测试")
    print("="*60)
    
    print("\n[1] 可用领域:")
    domains = list_available_domains()
    for d in domains:
        print(f"  - {d}")
    
    print("\n[2] 旅游领域模板:")
    templates = get_templates("旅游")
    for i, t in enumerate(templates[:5], 1):
        print(f"  {i}. {t}")
    
    print("\n[3] 旅游领域结构模板:")
    structures = get_structures("旅游")
    for s in structures:
        print(f"  - {s}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
