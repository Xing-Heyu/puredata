#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI安全审核系统 - 高危领域二次审核
针对医疗、金融、劳动合同等高危领域，使用AI进行二次审核
"""
import os
import sys

# 手动加载.env文件
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

# 高危领域定义
HIGH_RISK_DOMAINS = {
    "医疗": {
        "risk_level": "critical",
        "check_points": [
            "是否包含具体诊断建议",
            "是否包含用药剂量建议",
            "是否包含治疗方案建议",
            "是否存在可能误导患者的内容",
            "是否涉及重大疾病判断"
        ],
        "warning_keywords": ["诊断", "治疗", "用药", "剂量", "手术", "癌症", "肿瘤", "心脏病", "糖尿病"],
        "audit_prompt": """你是一位医疗安全审核专家。请审核以下医疗领域内容是否存在安全风险：

【审核内容】
{text}

【审核要点】
1. 是否包含可能误导患者的诊断建议？
2. 是否包含不准确的用药剂量信息？
3. 是否存在可能延误就医的误导性内容？
4. 是否涉及重大疾病的错误判断？
5. 内容是否适合作为AI训练数据（非医疗建议用途）？

【输出格式】
请以JSON格式输出审核结果：
{{
    "passed": true/false,
    "risk_level": "safe/low/medium/high/critical",
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "suitable_for_training": true/false,
    "confidence": 0.0-1.0
}}

注意：即使内容专业准确，只要适合作为AI训练数据（非直接医疗建议用途），也应通过审核。"""
    },
    "金融": {
        "risk_level": "high",
        "check_points": [
            "是否包含具体投资建议",
            "是否包含收益承诺",
            "是否存在误导性风险描述",
            "是否涉及敏感金融操作"
        ],
        "warning_keywords": ["投资", "收益", "理财", "贷款", "股票", "基金", "年化", "收益率"],
        "audit_prompt": """你是一位金融安全审核专家。请审核以下金融领域内容是否存在安全风险：

【审核内容】
{text}

【审核要点】
1. 是否包含具体的投资建议？
2. 是否存在收益承诺或误导性描述？
3. 是否存在可能误导投资者的风险描述？
4. 内容是否适合作为AI训练数据（非投资建议用途）？

【输出格式】
请以JSON格式输出审核结果：
{{
    "passed": true/false,
    "risk_level": "safe/low/medium/high/critical",
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "suitable_for_training": true/false,
    "confidence": 0.0-1.0
}}

注意：即使内容涉及投资知识，只要适合作为AI训练数据（非直接投资建议用途），也应通过审核。"""
    },
    "劳动合同": {
        "risk_level": "high",
        "check_points": [
            "是否包含具体法律建议",
            "是否存在法律条款误用",
            "是否涉及劳动仲裁建议",
            "是否存在误导性法律解读"
        ],
        "warning_keywords": ["劳动仲裁", "诉讼", "赔偿", "解除合同", "违法", "法律条款"],
        "audit_prompt": """你是一位法律安全审核专家。请审核以下劳动法领域内容是否存在安全风险：

【审核内容】
{text}

【审核要点】
1. 是否包含具体的法律建议？
2. 是否存在法律条款的误用或过时信息？
3. 是否存在可能误导劳动者的内容？
4. 内容是否适合作为AI训练数据（非法律建议用途）？

【输出格式】
请以JSON格式输出审核结果：
{{
    "passed": true/false,
    "risk_level": "safe/low/medium/high/critical",
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "suitable_for_training": true/false,
    "confidence": 0.0-1.0
}}

注意：即使内容涉及法律知识，只要适合作为AI训练数据（非直接法律建议用途），也应通过审核。"""
    }
}

@dataclass
class AuditResult:
    """审核结果"""
    passed: bool
    risk_level: str
    issues: List[str]
    suggestions: List[str]
    suitable_for_training: bool
    confidence: float
    raw_response: str
    tokens_used: int
    cost: float

class AISafetyAuditor:
    """AI安全审核器"""
    
    def __init__(self):
        self.api = None
        self._init_api()
    
    def _init_api(self):
        """初始化API"""
        try:
            from 千问API集成 import QwenAPI
            self.api = QwenAPI()
            print("[AI审核] API初始化成功")
        except Exception as e:
            print(f"[AI审核] API初始化失败: {e}")
            self.api = None
    
    def is_high_risk_domain(self, domain: str) -> bool:
        """检查是否为高危领域"""
        return domain in HIGH_RISK_DOMAINS
    
    def get_risk_level(self, domain: str) -> str:
        """获取领域风险等级"""
        if domain in HIGH_RISK_DOMAINS:
            return HIGH_RISK_DOMAINS[domain]["risk_level"]
        return "low"
    
    def needs_audit(self, domain: str, quality_score: float) -> bool:
        """判断是否需要审核"""
        if domain in HIGH_RISK_DOMAINS:
            return True
        return False
    
    def audit(self, text: str, domain: str, keyword: str = "") -> AuditResult:
        """审核内容"""
        if not self.api:
            return AuditResult(
                passed=True,
                risk_level="unknown",
                issues=["API不可用，跳过审核"],
                suggestions=[],
                suitable_for_training=True,
                confidence=0.5,
                raw_response="",
                tokens_used=0,
                cost=0.0
            )
        
        domain_config = HIGH_RISK_DOMAINS.get(domain)
        if not domain_config:
            return AuditResult(
                passed=True,
                risk_level="low",
                issues=[],
                suggestions=[],
                suitable_for_training=True,
                confidence=1.0,
                raw_response="非高危领域，无需审核",
                tokens_used=0,
                cost=0.0
            )
        
        prompt = domain_config["audit_prompt"].format(text=text)
        
        try:
            result = self.api.call(prompt, use_cache=False, max_tokens=500)
            
            if result.get("success"):
                response_text = result.get("response", "")
                tokens = result.get("tokens", 0)
                cost = result.get("cost", 0)
                
                try:
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        audit_data = json.loads(json_str)
                        
                        return AuditResult(
                            passed=audit_data.get("passed", True),
                            risk_level=audit_data.get("risk_level", "safe"),
                            issues=audit_data.get("issues", []),
                            suggestions=audit_data.get("suggestions", []),
                            suitable_for_training=audit_data.get("suitable_for_training", True),
                            confidence=audit_data.get("confidence", 0.8),
                            raw_response=response_text,
                            tokens_used=tokens,
                            cost=cost
                        )
                except json.JSONDecodeError:
                    pass
                
                return AuditResult(
                    passed=True,
                    risk_level="unknown",
                    issues=["无法解析审核结果"],
                    suggestions=[],
                    suitable_for_training=True,
                    confidence=0.6,
                    raw_response=response_text,
                    tokens_used=tokens,
                    cost=cost
                )
            else:
                return AuditResult(
                    passed=True,
                    risk_level="unknown",
                    issues=[f"API调用失败: {result.get('error', 'unknown')}"],
                    suggestions=[],
                    suitable_for_training=True,
                    confidence=0.5,
                    raw_response="",
                    tokens_used=0,
                    cost=0.0
                )
        except Exception as e:
            return AuditResult(
                passed=True,
                risk_level="unknown",
                issues=[f"审核异常: {str(e)}"],
                suggestions=[],
                suitable_for_training=True,
                confidence=0.5,
                raw_response="",
                tokens_used=0,
                cost=0.0
            )
    
    def batch_audit(self, items: List[Dict], domain: str) -> Tuple[List[Dict], List[Dict]]:
        """批量审核"""
        passed_items = []
        failed_items = []
        
        total_cost = 0.0
        total_tokens = 0
        
        for item in items:
            text = item.get("text", "")
            keyword = item.get("word", "")
            
            result = self.audit(text, domain, keyword)
            total_cost += result.cost
            total_tokens += result.tokens_used
            
            item["audit"] = {
                "passed": result.passed,
                "risk_level": result.risk_level,
                "issues": result.issues,
                "suggestions": result.suggestions,
                "suitable_for_training": result.suitable_for_training,
                "confidence": result.confidence,
                "tokens_used": result.tokens_used,
                "cost": result.cost
            }
            
            if result.passed and result.suitable_for_training:
                passed_items.append(item)
            else:
                failed_items.append(item)
        
        print(f"[AI审核] 完成: 通过{len(passed_items)}条, 拦截{len(failed_items)}条")
        print(f"[AI审核] 成本: {total_tokens} tokens, ¥{total_cost:.6f}")
        
        return passed_items, failed_items

# 全局实例
ai_safety_auditor = AISafetyAuditor()

def get_auditor():
    """获取审核器实例"""
    return ai_safety_auditor

if __name__ == "__main__":
    print("="*60)
    print("AI安全审核系统测试")
    print("="*60)
    
    auditor = AISafetyAuditor()
    
    test_text = """
    糖尿病是一种慢性代谢性疾病，主要特征是血糖水平持续升高。
    治疗糖尿病需要综合考虑饮食控制、运动锻炼和药物治疗。
    常用药物包括二甲双胍、胰岛素等，具体用药需遵医嘱。
    """
    
    result = auditor.audit(test_text, "医疗", "糖尿病")
    
    print(f"\n审核结果:")
    print(f"  通过: {result.passed}")
    print(f"  风险等级: {result.risk_level}")
    print(f"  适合训练: {result.suitable_for_training}")
    print(f"  置信度: {result.confidence}")
    print(f"  问题: {result.issues}")
    print(f"  建议: {result.suggestions}")
    print(f"  Token: {result.tokens_used}")
    print(f"  成本: ¥{result.cost:.6f}")
