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
        "{word}服务覆盖大部分城镇人口。",
        "基于{word}的风控模型降低不良率。",
        "{word}产品创新提供融资选择。",
        "数字技术驱动{word}效率提升。",
        "{word}成为金融科技发展核心。",
        "监管机构规范{word}合规运营。",
        "{word}领域投资热度持续升温。",
        "多家银行将{word}作为转型重点。",
        "{word}服务下沉市场潜力巨大。",
        "区块链为{word}带来更高安全性。",
        "{word}服务已覆盖大部分人口。",
        "基于{word}的风控模型效果显著。",
        "监管机构发布新规规范{word}。",
        "{word}产品创新为融资提供选择。",
        "数字技术驱动{word}服务升级。",
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
