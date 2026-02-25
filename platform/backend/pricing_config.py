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
        "overage_price": 0.08,
        "features": ["免费体验", "20%高+40%中+40%低质量", "基础领域"],
        "quality_modes": ["free_trial"],
        "role": "free"
    },
    "starter_monthly": {
        "name": "入门版月付",
        "price": 1199,
        "quota": 10000,
        "duration": 30,
        "overage_price": 0.12,
        "features": ["1万条/月", "标准质量模式", "基础领域"],
        "quality_modes": ["standard"],
        "role": "standard"
    },
    "basic_monthly": {
        "name": "基础版月付",
        "price": 11999,
        "quota": 50000,
        "duration": 30,
        "overage_price": 0.24,
        "features": ["5万条/月", "标准质量模式", "全部垂直领域"],
        "quality_modes": ["standard", "mixed"],
        "role": "standard"
    },
    "basic_yearly": {
        "name": "基础版年付",
        "price": 119990,
        "quota": 600000,
        "duration": 365,
        "overage_price": 0.20,
        "features": ["5万条/月", "标准质量模式", "全部垂直领域", "年付省¥23,998"],
        "quality_modes": ["standard", "mixed"],
        "role": "standard"
    },
    "pro_monthly": {
        "name": "专业版月付",
        "price": 29999,
        "quota": 200000,
        "duration": 30,
        "overage_price": 0.15,
        "features": ["20万条/月", "标准+高质量模式", "全部垂直领域", "优先支持"],
        "quality_modes": ["standard", "high", "mixed"],
        "role": "premium"
    },
    "pro_yearly": {
        "name": "专业版年付",
        "price": 299990,
        "quota": 2400000,
        "duration": 365,
        "overage_price": 0.12,
        "features": ["20万条/月", "标准+高质量模式", "全部垂直领域", "年付省¥59,998"],
        "quality_modes": ["standard", "high", "mixed"],
        "role": "premium"
    },
    "pro_high_monthly": {
        "name": "专业版+高质量月付",
        "price": 49999,
        "quota": 200000,
        "duration": 30,
        "overage_price": 0.15,
        "features": ["20万条/月", "80%高质量数据", "全部垂直领域", "专属客服"],
        "quality_modes": ["high", "ultra"],
        "role": "premium"
    },
    "enterprise_yearly": {
        "name": "企业版年付",
        "price": 699990,
        "quota": 9600000,
        "duration": 365,
        "overage_price": 0.10,
        "features": ["80万条/月", "全部质量模式", "全部垂直领域", "专属客服", "API接入"],
        "quality_modes": ["standard", "high", "ultra"],
        "role": "admin"
    },
    "enterprise_high_yearly": {
        "name": "企业版+高质量年付",
        "price": 999990,
        "quota": 9600000,
        "duration": 365,
        "overage_price": 0.10,
        "features": ["80万条/月", "80%高质量数据", "全部垂直领域", "专属客服", "API接入"],
        "quality_modes": ["high", "ultra"],
        "role": "admin"
    },
    "flagship_yearly": {
        "name": "旗舰版年付",
        "price": 1999990,
        "quota": 36000000,
        "duration": 365,
        "overage_price": 0.08,
        "features": ["300万条/月", "全部质量模式", "全部垂直领域", "专属团队", "定制开发"],
        "quality_modes": ["standard", "high", "ultra"],
        "role": "admin"
    }
}

PAYG_PACKAGES = {
    "10k": {"name": "1万条", "price": 2999, "quota": 10000, "unit_price": 0.30},
    "50k": {"name": "5万条", "price": 9999, "quota": 50000, "unit_price": 0.20},
    "200k": {"name": "20万条", "price": 29999, "quota": 200000, "unit_price": 0.15},
    "800k": {"name": "80万条", "price": 79999, "quota": 800000, "unit_price": 0.10},
    "3m": {"name": "300万条", "price": 199999, "quota": 3000000, "unit_price": 0.067}
}

ROLE_QUOTA_LIMITS = {
    "free": {"daily": 100, "monthly": 1000},
    "standard": {"daily": 10000, "monthly": 100000},
    "premium": {"daily": 100000, "monthly": 1000000},
    "admin": {"daily": 1000000, "monthly": 10000000}
}

ROLE_OVERAGE_PRICES = {
    "free": 0.08,
    "standard": 0.24,
    "premium": 0.15,
    "admin": 0.08
}

MARKET_PRICES = {
    "traditional_annotation": {"min": 0.5, "max": 2.0, "unit": "元/条"},
    "synthetic_data": {"min": 0.1, "max": 0.3, "unit": "元/条"}
}
