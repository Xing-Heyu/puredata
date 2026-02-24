#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PureData 免责声明和质量保障系统
"""

DISCLAIMER = {
    "version": "2.0",
    "effective_date": "2026-02-23",
    "language": "zh-CN",
    
    "core_disclaimer": {
        "title": "重要声明",
        "content": [
            "本平台生成的数据由人工智能（AI）自动生成，仅供参考。",
            "AI生成内容可能存在不准确、不完整或过时的信息。",
            "本平台不对数据的准确性、完整性和时效性作任何明示或暗示的保证。",
            "用户使用本平台生成的数据所产生的一切后果，由用户自行承担。"
        ]
    },
    
    "domain_specific": {
        "医疗": {
            "warning": "医疗领域数据仅供参考，不构成医疗建议",
            "details": [
                "生成的医疗内容不能替代专业医生的诊断和治疗建议",
                "医疗知识更新迅速，生成内容可能存在滞后",
                "药品信息、剂量、禁忌症等请以官方药品说明书为准",
                "疾病诊断请务必咨询专业医疗机构",
                "本平台不对因使用医疗数据导致的任何后果承担责任"
            ],
            "prohibited_uses": [
                "直接用于患者诊断",
                "替代专业医疗建议",
                "药品配方参考",
                "手术方案制定"
            ]
        },
        "金融": {
            "warning": "金融领域数据仅供参考，不构成投资建议",
            "details": [
                "生成的金融内容不能替代专业金融顾问的建议",
                "投资有风险，决策需谨慎",
                "市场信息变化迅速，生成内容可能已过时",
                "法律法规更新频繁，请以官方发布为准",
                "本平台不对因使用金融数据导致的投资损失承担责任"
            ],
            "prohibited_uses": [
                "直接用于投资决策",
                "替代专业金融咨询",
                "法律文件起草",
                "合同条款参考"
            ]
        },
        "劳动合同": {
            "warning": "劳动法领域数据仅供参考，不构成法律建议",
            "details": [
                "生成的法律内容不能替代专业律师的法律意见",
                "法律法规更新频繁，请以最新法律条文为准",
                "具体案件请咨询专业律师",
                "不同地区可能有不同的实施细则",
                "本平台不对因使用法律数据导致的法律后果承担责任"
            ],
            "prohibited_uses": [
                "直接用于法律诉讼",
                "替代专业法律咨询",
                "合同条款直接使用",
                "劳动仲裁证据"
            ]
        },
        "人工智能": {
            "warning": "AI领域数据仅供参考，技术发展迅速",
            "details": [
                "AI技术发展迅速，生成内容可能已过时",
                "具体技术实现请参考官方文档",
                "模型参数、API接口可能随时变化",
                "本平台不对因使用AI数据导致的技术问题承担责任"
            ],
            "prohibited_uses": [
                "直接用于生产环境",
                "替代官方技术文档",
                "安全关键系统"
            ]
        }
    },
    
    "quality_guarantee": {
        "title": "质量保障说明",
        "what_we_guarantee": [
            "✅ 数据格式规范：JSON格式，字段完整",
            "✅ 去重处理：通过MinHash LSH算法去重",
            "✅ 质量分级：四级质量分类（最高/高/中/低）",
            "✅ 血缘追溯：每条数据可追溯生成来源",
            "✅ 领域验证：基础领域术语检查",
            "✅ 长度过滤：过滤过短或过长内容"
        ],
        "what_we_cannot_guarantee": [
            "❌ 100%专业准确性：AI可能生成看似正确但实际错误的内容",
            "❌ 零幻觉：AI偶尔会编造不存在的信息",
            "❌ 时效性：知识可能有滞后，法规可能已更新",
            "❌ 适用性：数据可能不适合特定场景",
            "❌ 完整性：某些知识点可能未覆盖"
        ]
    },
    
    "usage_terms": {
        "allowed": [
            "AI模型训练",
            "模型微调",
            "学术研究",
            "数据分析",
            "算法测试",
            "教学演示"
        ],
        "forbidden": [
            "数据转售",
            "再分发原始数据",
            "直接用于医疗诊断",
            "直接用于投资决策",
            "直接用于法律诉讼",
            "任何非法用途"
        ]
    },
    
    "liability": {
        "platform_liability": [
            "保证平台服务稳定运行",
            "保证数据生成过程合规",
            "保证用户数据安全（符合数据安全法）",
            "提供数据质量报告"
        ],
        "user_responsibility": [
            "自行评估数据适用性",
            "自行验证关键信息",
            "遵守使用范围限制",
            "承担使用后果"
        ],
        "limitation": [
            "平台最大赔偿责任不超过用户支付的费用",
            "平台不对间接损失、附带损失承担责任",
            "因不可抗力导致的服务中断，平台不承担责任"
        ]
    },
    
    "compliance": {
        "laws": [
            "《中华人民共和国数据安全法》",
            "《中华人民共和国个人信息保护法》",
            "《中华人民共和国著作权法》",
            "《生成式人工智能服务管理暂行办法》",
            "《互联网信息服务管理办法》"
        ],
        "standards": [
            "数据脱敏处理",
            "无个人敏感信息",
            "无违法违规内容",
            "符合行业规范"
        ]
    }
}

def get_disclaimer(domain: str = None) -> dict:
    """获取免责声明"""
    result = {
        "core": DISCLAIMER["core_disclaimer"],
        "quality": DISCLAIMER["quality_guarantee"],
        "usage": DISCLAIMER["usage_terms"],
        "compliance": DISCLAIMER["compliance"]
    }
    
    if domain and domain in DISCLAIMER["domain_specific"]:
        result["domain_specific"] = DISCLAIMER["domain_specific"][domain]
    
    return result

def get_data_disclaimer_text(domain: str) -> str:
    """获取数据中嵌入的简短免责声明"""
    domain_info = DISCLAIMER["domain_specific"].get(domain, {})
    warning = domain_info.get("warning", "本数据仅供参考")
    
    return f"""
【免责声明】
{warning}
- 本数据由AI生成，可能存在不准确或过时的信息
- 请自行验证关键信息，不构成专业建议
- 使用本数据产生的一切后果由用户自行承担
- 详细免责声明请查看：https://puredata.ai/disclaimer
"""

def get_quality_badge(quality_score: float) -> dict:
    """获取质量徽章"""
    if quality_score >= 0.90:
        return {
            "level": "最高质量",
            "badge": "🏆",
            "color": "#10b981",
            "description": "通过多重验证，适合学术研究",
            "confidence": "高"
        }
    elif quality_score >= 0.80:
        return {
            "level": "高质量",
            "badge": "⭐",
            "color": "#3b82f6",
            "description": "专业级内容，适合模型训练",
            "confidence": "较高"
        }
    elif quality_score >= 0.65:
        return {
            "level": "中质量",
            "badge": "📊",
            "color": "#f59e0b",
            "description": "基础内容，适合数据增强",
            "confidence": "中等"
        }
    else:
        return {
            "level": "低质量",
            "badge": "📝",
            "color": "#ef4444",
            "description": "简单内容，适合压力测试",
            "confidence": "较低"
        }

def validate_for_critical_use(domain: str, quality_score: float) -> dict:
    """验证是否适合关键用途"""
    result = {
        "allowed": True,
        "warnings": [],
        "recommendations": []
    }
    
    domain_info = DISCLAIMER["domain_specific"].get(domain, {})
    
    if domain in ["医疗", "金融", "劳动合同"]:
        result["warnings"].append(f"⚠️ {domain}领域数据不应用于关键决策")
        result["recommendations"].append("建议人工审核后再使用")
        
        if quality_score < 0.85:
            result["warnings"].append("⚠️ 质量分数较低，不建议用于专业场景")
    
    if quality_score < 0.70:
        result["warnings"].append("⚠️ 质量分数低于70%，请谨慎使用")
    
    return result

if __name__ == "__main__":
    import json
    print("="*60)
    print("PureData 免责声明和质量保障系统")
    print("="*60)
    print(json.dumps(DISCLAIMER, ensure_ascii=False, indent=2))
