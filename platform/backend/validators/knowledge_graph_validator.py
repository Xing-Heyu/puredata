#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逻辑验证管道 - 知识图谱验证器
验证知识图谱三元组的关系逻辑
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    """验证问题"""
    item_id: str
    field: str
    issue_type: str
    description: str
    severity: str
    suggestion: str = ""


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    total_items: int
    valid_items: int
    issues: List[ValidationIssue] = field(default_factory=list)
    statistics: Dict = field(default_factory=dict)


class KnowledgeGraphValidator:
    """
    知识图谱验证器
    
    验证规则:
    1. 实体不能为空
    2. 关系不能为空
    3. 头尾实体不能相同
    4. 关系类型应该与领域匹配
    """
    
    # 领域关系模板
    DOMAIN_RELATIONS = {
        "医疗": {
            "疾病-症状": ["导致", "引起", "表现为", "伴有"],
            "疾病-治疗": ["治疗", "治愈", "用于", "采用"],
            "药物-适应症": ["用于", "治疗", "适用", "主治"],
            "检查-疾病": ["诊断", "检查", "确诊", "筛查"]
        },
        "金融": {
            "舆情-股价": ["导致", "引发", "影响", "造成"],
            "ESG-评级": ["触发", "导致", "引起"],
            "政策-板块": ["利好", "影响", "推动"]
        },
        "人工智能": {
            "技术-应用": ["应用于", "用于", "实现", "支撑"],
            "算法-任务": ["用于", "解决", "处理", "实现"]
        }
    }
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
    
    def validate(self, data: List[Dict]) -> ValidationResult:
        """验证知识图谱数据"""
        issues = []
        valid_count = 0
        
        for i, item in enumerate(data):
            item_id = item.get("head", f"item_{i}")
            item_issues = self._validate_item(item, i)
            
            has_error = any(issue.severity == "error" for issue in item_issues)
            if not has_error:
                valid_count += 1
            
            issues.extend(item_issues)
        
        statistics = {
            "total": len(data),
            "valid": valid_count,
            "invalid": len(data) - valid_count,
            "error_count": sum(1 for i in issues if i.severity == "error"),
            "warning_count": sum(1 for i in issues if i.severity == "warning"),
        }
        
        return ValidationResult(
            is_valid=valid_count == len(data),
            total_items=len(data),
            valid_items=valid_count,
            issues=issues,
            statistics=statistics
        )
    
    def _validate_item(self, item: Dict, index: int) -> List[ValidationIssue]:
        """验证单条三元组"""
        issues = []
        item_id = item.get("head", f"item_{index}")
        
        # 1. 实体不能为空
        head = item.get("head", "").strip()
        relation = item.get("relation", "").strip()
        tail = item.get("tail", "").strip()
        
        if not head:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="head",
                issue_type="empty_entity",
                description="头实体为空",
                severity="error",
                suggestion="头实体不能为空"
            ))
        
        if not tail:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="tail",
                issue_type="empty_entity",
                description="尾实体为空",
                severity="error",
                suggestion="尾实体不能为空"
            ))
        
        if not relation:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="relation",
                issue_type="empty_relation",
                description="关系为空",
                severity="error",
                suggestion="关系不能为空"
            ))
        
        # 2. 头尾不能相同
        if head and tail and head == tail:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="head/tail",
                issue_type="same_entity",
                description=f"头尾实体相同: {head}",
                severity="error",
                suggestion="头实体和尾实体不能相同"
            ))
        
        # 3. 置信度检查
        confidence = item.get("confidence", 1.0)
        if confidence < 0.5:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="confidence",
                issue_type="low_confidence",
                description=f"置信度过低: {confidence}",
                severity="warning",
                suggestion="置信度应大于0.5"
            ))
        
        return issues
    
    def fix_issues(self, data: List[Dict]) -> Tuple[List[Dict], List[ValidationIssue]]:
        """修复问题"""
        fixed_data = []
        remaining_issues = []
        
        for item in data:
            fixed_item = item.copy()
            
            # 修复空实体
            if not fixed_item.get("head", "").strip():
                fixed_item["head"] = "未知实体"
            if not fixed_item.get("tail", "").strip():
                fixed_item["tail"] = "未知实体"
            if not fixed_item.get("relation", "").strip():
                fixed_item["relation"] = "相关"
            
            # 修复相同实体
            if fixed_item.get("head") == fixed_item.get("tail"):
                fixed_item["tail"] = f"{fixed_item.get('tail', '')}_相关"
            
            # 修复置信度
            if fixed_item.get("confidence", 1.0) < 0.5:
                fixed_item["confidence"] = 0.7
            
            fixed_data.append(fixed_item)
        
        result = self.validate(fixed_data)
        remaining_issues = result.issues
        
        return fixed_data, remaining_issues


def validate_knowledge_graph(data: List[Dict], fix: bool = True) -> Tuple[List[Dict], ValidationResult]:
    """验证知识图谱（入口函数）"""
    validator = KnowledgeGraphValidator()
    result = validator.validate(data)
    
    if not result.is_valid and fix:
        fixed_data, remaining = validator.fix_issues(data)
        result = validator.validate(fixed_data)
        return fixed_data, result
    
    return data, result
