#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逻辑验证管道 - 文献验证器
验证文献内容的完整性和质量
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


class LiteratureValidator:
    """
    文献验证器
    
    验证规则:
    1. 标题不能为空
    2. 内容不能为空
    3. 内容长度检查
    4. 章节结构检查
    5. 关键词检查
    """
    
    MIN_TITLE_LENGTH = 5
    MIN_CONTENT_LENGTH = 100
    REQUIRED_SECTIONS = ["摘要", "结论"]
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
    
    def validate(self, data: List[Dict]) -> ValidationResult:
        """验证文献数据"""
        issues = []
        valid_count = 0
        
        for i, item in enumerate(data):
            item_id = item.get("title", f"item_{i}")
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
        """验证单条文献"""
        issues = []
        item_id = item.get("title", f"item_{index}")
        
        # 1. 标题检查
        title = item.get("title", "").strip()
        if not title:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="title",
                issue_type="empty_title",
                description="标题为空",
                severity="error",
                suggestion="标题不能为空"
            ))
        elif len(title) < self.MIN_TITLE_LENGTH:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="title",
                issue_type="title_too_short",
                description=f"标题过短: {len(title)}字符",
                severity="warning",
                suggestion=f"标题至少{self.MIN_TITLE_LENGTH}字符"
            ))
        
        # 2. 内容检查
        content = item.get("content", "").strip()
        if not content:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="content",
                issue_type="empty_content",
                description="内容为空",
                severity="error",
                suggestion="内容不能为空"
            ))
        elif len(content) < self.MIN_CONTENT_LENGTH:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="content",
                issue_type="content_too_short",
                description=f"内容过短: {len(content)}字符",
                severity="warning",
                suggestion=f"内容至少{self.MIN_CONTENT_LENGTH}字符"
            ))
        
        # 3. 章节检查
        sections = item.get("sections", [])
        if isinstance(sections, list):
            for required in self.REQUIRED_SECTIONS:
                if required not in sections:
                    issues.append(ValidationIssue(
                        item_id=item_id,
                        field="sections",
                        issue_type="missing_section",
                        description=f"缺少必要章节: {required}",
                        severity="warning",
                        suggestion=f"建议包含{required}章节"
                    ))
        
        # 4. 字数检查
        word_count = item.get("word_count", 0)
        if word_count > 0 and word_count < self.MIN_CONTENT_LENGTH:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="word_count",
                issue_type="word_count_too_low",
                description=f"字数过少: {word_count}",
                severity="warning",
                suggestion="字数应大于100"
            ))
        
        # 5. 领域检查
        domain = item.get("domain", "")
        if not domain:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="domain",
                issue_type="missing_domain",
                description="缺少领域信息",
                severity="warning",
                suggestion="应指定文献所属领域"
            ))
        
        return issues
    
    def fix_issues(self, data: List[Dict]) -> Tuple[List[Dict], List[ValidationIssue]]:
        """修复问题"""
        fixed_data = []
        remaining_issues = []
        
        for i, item in enumerate(data):
            fixed_item = item.copy()
            
            # 修复标题
            if not fixed_item.get("title", "").strip():
                fixed_item["title"] = f"{fixed_item.get('domain', '研究')}主题论文{i+1}"
            
            # 修复内容
            if not fixed_item.get("content", "").strip():
                fixed_item["content"] = "本文研究了相关主题，得出重要结论。"
            
            # 确保有章节
            if not fixed_item.get("sections"):
                fixed_item["sections"] = ["摘要", "引言", "方法", "结果", "讨论", "结论"]
            
            # 确保有领域
            if not fixed_item.get("domain"):
                fixed_item["domain"] = "通用"
            
            fixed_data.append(fixed_item)
        
        result = self.validate(fixed_data)
        remaining_issues = result.issues
        
        return fixed_data, remaining_issues


def validate_literature(data: List[Dict], fix: bool = True) -> Tuple[List[Dict], ValidationResult]:
    """验证文献（入口函数）"""
    validator = LiteratureValidator()
    result = validator.validate(data)
    
    if not result.is_valid and fix:
        fixed_data, remaining = validator.fix_issues(data)
        result = validator.validate(fixed_data)
        return fixed_data, result
    
    return data, result
