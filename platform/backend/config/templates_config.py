#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块 - 模板配置
支持领域：人工智能、劳动合同、医疗、金融
"""

TEMPLATES = {
    "人工智能": [
        "{word}是AI核心技术，应用于智能系统。",
        "{word}技术发展迅速，应用场景扩展。",
        "基于{word}的方案改变传统行业。",
        "{word}是机器学习重要研究方向。",
        "在深度学习中，{word}扮演关键角色。",
        "{word}技术应用于图像语音处理。",
        "专家预测{word}将成为核心趋势。",
        "{word}是智能系统的基础技术。",
        "通过{word}，机器学习数据规律。",
        "{word}在NLP中发挥重要作用。",
        "{word}是人工智能的核心技术之一，应用广泛。",
        "基于{word}的创新解决方案正在重塑行业。",
        "专家预测，{word}将成为未来核心趋势。",
        "在{word}领域，国内企业已实现突破。",
        "{word}技术的商业化落地正在加速。",
    ],
    "劳动合同": [
        "{word}是劳动关系重要法律保障。",
        "根据规定，{word}条款需书面约定。",
        "处理{word}问题建议双方协商。",
        "{word}制度完善有助于和谐关系。",
        "劳动者在{word}方面权利受保护。",
        "用人单位应建立{word}管理制度。",
        "{word}纠纷中证据保存至关重要。",
        "{word}相关合同条款应清晰明确。",
        "近年来{word}领域立法不断完善。",
        "妥善处理{word}问题提升满意度。",
        "{word}是劳动法中的重要概念。",
        "在劳动合同中，{word}具有重要意义。",
        "{word}是保障劳动者权益的重要内容。",
        "根据最新规定，{word}需书面约定。",
        "{word}制度的完善对劳动关系重要。",
    ],
    "医疗": [
        "{word}技术在临床诊断中作用重要。",
        "基于{word}的医疗方案提升效率。",
        "{word}是现代医疗的重要组成部分。",
        "通过{word}，医生诊断更准确。",
        "{word}技术应用于医疗影像分析。",
        "在疫情防控中，{word}功不可没。",
        "{word}设备提升基层医疗能力。",
        "{word}对慢性病管理意义重大。",
        "多家医院将{word}纳入标准流程。",
        "{word}技术缩短患者康复周期。",
        "{word}技术在临床应用中疗效显著。",
        "通过{word}技术，医生诊断更精准。",
        "最新研究表明，{word}对治疗重要。",
        "{word}设备的普及提升了医疗能力。",
        "在疫情防控中，{word}发挥重要作用。",
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
        "【评级调整】{word}发生后，券商研报密集发布，多家机构调整目标价。",
        "【治理风险】{word}暴露公司治理缺陷，ESG投资者撤资。",
        "【环境风险】{word}引发环保关注，公司面临处罚风险。",
        "【社会责任】{word}事件影响公司社会形象，品牌价值受损。",
        "【投资机会】{word}带来行业洗牌机会，优质企业市场份额提升。",
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
        "{word}场景的模拟数据对训练很重要。",
        "在{word}情况下，人机协同尤为关键。",
        "{word}是智能汽车安全测试的必测项目。",
        "针对{word}场景的算法优化持续进行。",
        "{word}风险预警系统正在普及应用。",
    ],
}

_DEFAULT_VARIATION_TEMPLATES = [
    "【定义】{text}",
    "参考：{text}",
    "注：{text}",
    "说明：{text}",
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

VARIATIONS = {
    "人工智能": ["🤖 {text}", "🧠 {text}", "💻 {text}", "【AI知识】{text}", "技术要点: {text}"] + _DEFAULT_VARIATION_TEMPLATES,
    "劳动合同": ["【劳动法】{text}", "⚖️ {text}", "【权益保障】{text}"] + _DEFAULT_VARIATION_TEMPLATES,
    "医疗": ["🏥 {text}", "💊 {text}", "【医疗知识】{text}", "临床要点: {text}"] + _DEFAULT_VARIATION_TEMPLATES,
    "金融": ["💰 {text}", "📈 {text}", "【金融知识】{text}", "投资要点: {text}"] + _DEFAULT_VARIATION_TEMPLATES,
    "交通驾驶": ["🚗 {text}", "🚦 {text}", "【驾驶场景】{text}", "安全要点: {text}", "⚠️ {text}"] + _DEFAULT_VARIATION_TEMPLATES,
}

_DEFAULT_STRUCTURE_TEMPLATES = [
    "【定义】{base}",
    "Q: 什么是{keyword}? A: {base}",
    "参考: {base}",
    "注: {base}",
    "#{index} {base}",
    "关于{keyword}: {base}",
    "【{keyword}】{base}",
]

STRUCTURES = {
    "人工智能": ["【AI知识】{base}", "技术参考: {base}", "AI笔记: {base}"] + _DEFAULT_STRUCTURE_TEMPLATES,
    "劳动合同": ["【劳动法】{base}", "权益参考: {base}", "法条解读: {base}"] + _DEFAULT_STRUCTURE_TEMPLATES,
    "医疗": ["【医疗知识】{base}", "临床参考: {base}", "健康提示: {base}"] + _DEFAULT_STRUCTURE_TEMPLATES,
    "金融": ["【金融知识】{base}", "投资参考: {base}", "理财提示: {base}"] + _DEFAULT_STRUCTURE_TEMPLATES,
    "交通驾驶": ["【驾驶场景】{base}", "安全参考: {base}", "行车提示: {base}", "场景描述: {base}"] + _DEFAULT_STRUCTURE_TEMPLATES,
}

QUALITY_MODES = {
    "high_quality": {
        "high_ratio": 0.80,
        "medium_ratio": 0.15,
        "low_ratio": 0.05,
        "description": "高质量模式 - 适合模型训练、知识库构建"
    },
    "standard": {
        "high_ratio": 0.50,
        "medium_ratio": 0.30,
        "low_ratio": 0.20,
        "description": "标准质量模式 - 适合数据增强、一般训练"
    },
    "mixed": {
        "high_ratio": 0.25,
        "medium_ratio": 0.50,
        "low_ratio": 0.25,
        "description": "混合质量模式 - 适合鲁棒性测试、压力测试"
    }
}
