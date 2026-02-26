"""
统一价格配置 - 前后端共享
所有价格单位为"元"
"""

PRICING_PLANS = {
    "free": {
        "name": "体验版",
        "price": 0,
        "quota": 1000,
        "duration": None,
        "features": ["免费体验", "基础领域", "标准质量"],
        "quality_modes": ["free_trial"],
        "role": "free"
    },
    "starter_monthly": {
        "name": "入门版月付",
        "price": 2999,
        "quota": 10000,
        "duration": 30,
        "features": ["1万条/月", "全部垂直领域", "标准质量模式"],
        "quality_modes": ["standard"],
        "role": "standard"
    },
    "basic_monthly": {
        "name": "基础版月付",
        "price": 19999,
        "quota": 50000,
        "duration": 30,
        "features": ["5万条/月", "全部垂直领域", "标准质量模式"],
        "quality_modes": ["standard", "mixed"],
        "role": "standard"
    },
    "pro_monthly": {
        "name": "专业版月付",
        "price": 49999,
        "quota": 200000,
        "duration": 30,
        "features": ["20万条/月", "全部垂直领域", "标准+高质量模式", "优先生成队列"],
        "quality_modes": ["standard", "high", "mixed"],
        "role": "premium"
    },
    "pro_yearly": {
        "name": "专业版年付",
        "price": 499990,
        "quota": 2500000,
        "duration": 365,
        "features": ["250万条/年", "全部垂直领域", "标准+高质量模式", "优先生成队列"],
        "quality_modes": ["standard", "high", "mixed"],
        "role": "premium"
    },
    "enterprise_yearly": {
        "name": "企业版年付",
        "price": 799990,
        "quota": 1000000,
        "duration": 365,
        "features": ["100万条/年", "单一垂直领域定制", "高质量模式默认开启", "专属技术支持"],
        "quality_modes": ["high", "ultra"],
        "role": "admin"
    },
    "flagship_yearly": {
        "name": "旗舰版年付",
        "price": 1199990,
        "quota": 2000000,
        "duration": 365,
        "features": ["200万条/年", "多领域混合生成", "超高质量模式(90%+)", "专属客户经理"],
        "quality_modes": ["high", "ultra"],
        "role": "admin"
    }
}

PAYG_PACKAGES = {
    "10k": {"name": "1万条", "price": 3999, "quota": 10000, "unit_price": 0.40},
    "50k": {"name": "5万条", "price": 14999, "quota": 50000, "unit_price": 0.30},
    "200k": {"name": "20万条", "price": 49999, "quota": 200000, "unit_price": 0.25},
    "500k": {"name": "50万条", "price": 99999, "quota": 500000, "unit_price": 0.20},
    "800k": {"name": "80万条", "price": 159999, "quota": 800000, "unit_price": 0.20},
    "1m": {"name": "100万条", "price": 179999, "quota": 1000000, "unit_price": 0.18},
    "3m": {"name": "300万条", "price": 499999, "quota": 3000000, "unit_price": 0.17}
}

ROLE_QUOTA_LIMITS = {
    "free": {"daily": 100, "monthly": 1000},
    "standard": {"daily": 10000, "monthly": 100000},
    "premium": {"daily": 100000, "monthly": 1000000},
    "developer": {"daily": 1000000, "monthly": 10000000},
    "admin": {"daily": 1000000, "monthly": 10000000}
}

ROLE_OVERAGE_PRICES = {
    "free": 0,
    "standard": 0,
    "premium": 0,
    "developer": 0,
    "admin": 0
}

MARKET_PRICES = {
    "traditional_annotation": {"min": 0.5, "max": 2.0, "unit": "元/条"},
    "synthetic_data": {"min": 0.1, "max": 0.3, "unit": "元/条"}
}
