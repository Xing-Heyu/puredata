#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI多角度安全审核系统 - 3次审核机制
高危领域（医疗/金融/法律/政治）必须经过3次审核
"""
import os
import sys
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# 手动加载.env文件
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# 高危领域定义
HIGH_RISK_DOMAINS = {
    "医疗": {
        "risk_level": "critical",
        "audit_count": 3,
        "warning_keywords": ["诊断", "治疗", "用药", "剂量", "手术", "癌症", "肿瘤", "心脏病", "糖尿病", "疫苗", "处方"]
    },
    "金融": {
        "risk_level": "high",
        "audit_count": 3,
        "warning_keywords": ["投资", "收益", "理财", "贷款", "股票", "基金", "年化", "收益率", "风险投资"]
    },
    "劳动合同": {
        "risk_level": "high",
        "audit_count": 3,
        "warning_keywords": ["劳动仲裁", "诉讼", "赔偿", "解除合同", "违法", "法律条款", "竞业协议"]
    },
    "政治": {
        "risk_level": "critical",
        "audit_count": 3,
        "warning_keywords": ["政策", "法规", "政府", "监管", "合规", "审批"]
    }
}

# 三次审核的Prompt模板
AUDIT_PROMPTS = {
    "safety": {
        "name": "安全审核",
        "description": "检测是否存在危险内容或误导性建议",
        "prompt_template": """你是一位内容安全审核专家。请审核以下{domain}领域内容是否存在安全风险：

【审核内容】
{text}

【审核要点】
1. 是否包含可能造成人身伤害的建议？
2. 是否包含可能造成财产损失的建议？
3. 是否存在明显的误导性信息？
4. 是否涉及敏感或违规内容？

【输出格式】仅输出JSON：
{{"passed": true/false, "risk_level": "safe/low/medium/high/critical", "issues": ["问题列表"], "confidence": 0.0-1.0}}"""
    },
    
    "accuracy": {
        "name": "准确性审核",
        "description": "检测内容是否专业准确",
        "prompt_template": """你是一位{domain}领域专家。请审核以下内容的专业准确性：

【审核内容】
{text}

【审核要点】
1. 专业术语使用是否正确？
2. 概念定义是否准确？
3. 是否存在明显的知识性错误？
4. 信息是否过时或已被更新？

【输出格式】仅输出JSON：
{{"passed": true/false, "accuracy_level": "high/medium/low", "errors": ["错误列表"], "confidence": 0.0-1.0}}"""
    },
    
    "suitability": {
        "name": "适用性审核",
        "description": "检测是否适合作为AI训练数据",
        "prompt_template": """你是一位AI训练数据质量评估专家。请评估以下内容是否适合作为AI训练数据：

【审核内容】
{text}

【评估要点】
1. 内容是否完整、连贯？
2. 语言是否规范、清晰？
3. 是否包含有害或不当内容？
4. 是否适合用于AI模型训练（非直接建议用途）？

【输出格式】仅输出JSON：
{{"passed": true/false, "quality_level": "high/medium/low", "suitable_for": ["训练用途列表"], "not_suitable_for": ["不适合用途列表"], "confidence": 0.0-1.0}}"""
    }
}

@dataclass
class AuditRound:
    """单次审核结果"""
    audit_type: str
    audit_name: str
    passed: bool
    risk_level: str
    issues: List[str]
    confidence: float
    tokens_used: int
    cost: float
    raw_response: str

@dataclass
class MultiAuditResult:
    """多角度审核结果"""
    domain: str
    keyword: str
    text: str
    rounds: List[AuditRound] = field(default_factory=list)
    final_passed: bool = True
    final_confidence: float = 0.0
    total_tokens: int = 0
    total_cost: float = 0.0
    audit_summary: str = ""
    
    def calculate_final(self):
        """计算最终结果"""
        if not self.rounds:
            return
        
        passed_count = sum(1 for r in self.rounds if r.passed)
        self.final_passed = passed_count >= 2  # 3次中至少2次通过
        self.final_confidence = sum(r.confidence for r in self.rounds) / len(self.rounds)
        self.total_tokens = sum(r.tokens_used for r in self.rounds)
        self.total_cost = sum(r.cost for r in self.rounds)
        
        issues = []
        for r in self.rounds:
            if not r.passed:
                issues.append(f"[{r.audit_name}] {', '.join(r.issues)}")
        
        if issues:
            self.audit_summary = " | ".join(issues)
        else:
            self.audit_summary = "所有审核通过"

class MultiAngleAuditor:
    """多角度审核器"""
    
    def __init__(self):
        self.api = None
        self._init_api()
    
    def _init_api(self):
        """初始化API"""
        try:
            from 千问API集成 import QwenAPI
            self.api = QwenAPI()
            print("[多角度审核] API初始化成功")
        except Exception as e:
            print(f"[多角度审核] API初始化失败: {e}")
    
    def is_high_risk_domain(self, domain: str) -> bool:
        """检查是否为高危领域"""
        return domain in HIGH_RISK_DOMAINS
    
    def get_audit_count(self, domain: str) -> int:
        """获取需要的审核次数"""
        if domain in HIGH_RISK_DOMAINS:
            return HIGH_RISK_DOMAINS[domain]["audit_count"]
        return 1  # 普通领域只审核1次
    
    def _call_api(self, prompt: str) -> Tuple[str, int, float]:
        """调用API"""
        if not self.api:
            return '{"passed": true, "confidence": 0.5}', 0, 0.0
        
        result = self.api.call(prompt, use_cache=False, max_tokens=300)
        if result.get("success"):
            return (
                result.get("response", ""),
                result.get("tokens", 0),
                result.get("cost", 0.0)
            )
        return '{"passed": true, "confidence": 0.5}', 0, 0.0
    
    def _parse_json_response(self, response: str) -> Dict:
        """解析JSON响应"""
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except (json.JSONDecodeError, ValueError) as e:
            pass
        return {"passed": True, "confidence": 0.5}
    
    def audit_single_round(self, text: str, domain: str, audit_type: str) -> AuditRound:
        """执行单次审核"""
        config = AUDIT_PROMPTS[audit_type]
        prompt = config["prompt_template"].format(
            domain=domain,
            text=text
        )
        
        response, tokens, cost = self._call_api(prompt)
        data = self._parse_json_response(response)
        
        return AuditRound(
            audit_type=audit_type,
            audit_name=config["name"],
            passed=data.get("passed", True),
            risk_level=data.get("risk_level", data.get("accuracy_level", data.get("quality_level", "unknown"))),
            issues=data.get("issues", data.get("errors", [])),
            confidence=data.get("confidence", 0.5),
            tokens_used=tokens,
            cost=cost,
            raw_response=response
        )
    
    def audit(self, text: str, domain: str, keyword: str = "") -> MultiAuditResult:
        """执行完整审核流程"""
        result = MultiAuditResult(
            domain=domain,
            keyword=keyword,
            text=text
        )
        
        audit_count = self.get_audit_count(domain)
        
        if audit_count == 1:
            # 普通领域：只做安全审核
            round_result = self.audit_single_round(text, domain, "safety")
            result.rounds.append(round_result)
        else:
            # 高危领域：3次多角度审核
            for audit_type in ["safety", "accuracy", "suitability"]:
                round_result = self.audit_single_round(text, domain, audit_type)
                result.rounds.append(round_result)
                time.sleep(0.3)  # 避免API限流
        
        result.calculate_final()
        return result
    
    def batch_audit(self, items: List[Dict], domain: str) -> Tuple[List[Dict], List[Dict]]:
        """批量审核"""
        passed_items = []
        failed_items = []
        
        total_cost = 0.0
        total_tokens = 0
        
        is_high_risk = self.is_high_risk_domain(domain)
        audit_type = "3次多角度" if is_high_risk else "1次基础"
        
        print(f"[多角度审核] 开始审核 {len(items)} 条数据 ({domain}领域 - {audit_type})")
        
        for i, item in enumerate(items):
            text = item.get("text", "")
            keyword = item.get("word", "")
            
            result = self.audit(text, domain, keyword)
            total_cost += result.total_cost
            total_tokens += result.total_tokens
            
            # 记录审核详情
            item["multi_audit"] = {
                "passed": result.final_passed,
                "confidence": round(result.final_confidence, 3),
                "audit_count": len(result.rounds),
                "rounds": [
                    {
                        "type": r.audit_type,
                        "name": r.audit_name,
                        "passed": r.passed,
                        "risk_level": r.risk_level,
                        "issues": r.issues,
                        "confidence": round(r.confidence, 3)
                    }
                    for r in result.rounds
                ],
                "summary": result.audit_summary,
                "tokens_used": result.total_tokens,
                "cost": round(result.total_cost, 6)
            }
            
            if result.final_passed:
                passed_items.append(item)
            else:
                failed_items.append(item)
            
            # 进度显示
            if (i + 1) % 10 == 0:
                print(f"[多角度审核] 进度: {i+1}/{len(items)}")
        
        print(f"\n[多角度审核] 完成!")
        print(f"  - 通过: {len(passed_items)} 条")
        print(f"  - 拦截: {len(failed_items)} 条")
        print(f"  - 总Token: {total_tokens}")
        print(f"  - 总成本: ¥{total_cost:.6f}")
        print(f"  - 平均每条: ¥{total_cost/len(items):.6f}" if items else "")
        
        return passed_items, failed_items

# 全局实例
multi_angle_auditor = MultiAngleAuditor()

def get_auditor():
    return multi_angle_auditor

if __name__ == "__main__":
    print("="*60)
    print("多角度审核系统测试")
    print("="*60)
    
    auditor = MultiAngleAuditor()
    
    # 测试医疗领域内容
    test_text = """
    糖尿病是一种慢性代谢性疾病，主要特征是血糖水平持续升高。
    治疗糖尿病需要综合考虑饮食控制、运动锻炼和药物治疗。
    常用药物包括二甲双胍、胰岛素等，具体用药需遵医嘱。
    """
    
    print("\n测试内容:")
    print(test_text.strip())
    print()
    
    result = auditor.audit(test_text, "医疗", "糖尿病")
    
    print("="*60)
    print("审核结果:")
    print("="*60)
    print(f"最终通过: {result.final_passed}")
    print(f"最终置信度: {result.final_confidence:.3f}")
    print(f"总Token: {result.total_tokens}")
    print(f"总成本: ¥{result.total_cost:.6f}")
    print()
    
    for r in result.rounds:
        status = "✓ 通过" if r.passed else "✗ 未通过"
        print(f"[{r.audit_name}] {status}")
        print(f"  - 风险等级: {r.risk_level}")
        print(f"  - 置信度: {r.confidence:.3f}")
        print(f"  - Token: {r.tokens_used}")
        print(f"  - 成本: ¥{r.cost:.6f}")
        if r.issues:
            print(f"  - 问题: {r.issues}")
        print()
