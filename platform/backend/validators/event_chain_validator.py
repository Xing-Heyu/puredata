#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逻辑验证管道 - 事件链验证器
验证事件链数据的逻辑一致性
"""

import json
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    """验证问题"""
    item_id: str
    field: str
    issue_type: str
    description: str
    severity: str  # error, warning, info
    suggestion: str = ""


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    total_items: int
    valid_items: int
    issues: List[ValidationIssue] = field(default_factory=list)
    statistics: Dict = field(default_factory=dict)


class EventChainValidator:
    """
    事件链逻辑验证器 (优化版)
    
    验证规则:
    1. 置信度分级一致性: confidence 必须在对应 level 的范围内
    2. 评级变化一致性: 评级必须下降
    3. 传导方向一致性: 负面事件→负面传导→负面结果
    4. 结果与影响匹配: 股价影响与结果方向一致
    5. 资金流向与涨跌匹配: 净流入→上涨，净流出→下跌
    6. 机构行为与情绪匹配: 情绪负面→机构减持
    7. 可量化指标完整性: 必须包含 quantifiable_metrics
    """
    
    # 评级顺序（从高到低）
    RATING_ORDER = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D"]
    
    # 置信度分级范围
    CONFIDENCE_RANGES = {
        "commercial": (0.90, 0.95),
        "pilot": (0.80, 0.90),
        "exploratory": (0.70, 0.80)
    }
    
    # 负面事件关键词（更新为驱动型描述）
    NEGATIVE_EVENTS = [
        "监管处罚", "业绩暴雷", "高管变动", "并购重组", "减持公告", "财务造假", 
        "股权质押", "行业风险", "国际局势", "环境污染", "碳排放", "劳动权益",
        "数据隐私", "商业道德", "供应链风险", "产品质量", "诉讼", "违约",
        "驱动合规成本", "引发投资者信心", "导致市场恐慌", "触发信任崩塌",
        "推动估值重构", "驱动避险情绪"
    ]
    
    # 正向事件关键词（更新为驱动型描述）
    POSITIVE_EVENTS = [
        "业绩预增", "分红公告", "中标项目", "技术突破", "政策利好", "订单大增",
        "业绩增长", "获得投资", "合作签约", "产品发布",
        "驱动估值修复", "推动股东回报", "驱动竞争力", "推动行业景气度",
        "驱动营收增长", "驱动应用普及", "驱动效率提升"
    ]
    
    # 负面结果关键词
    NEGATIVE_RESULTS = [
        "下跌", "暴跌", "走弱", "下调", "承压", "回调", "分化", "震荡", "蒸发"
    ]
    
    # 正向结果关键词
    POSITIVE_RESULTS = [
        "上涨", "涨停", "反弹", "企稳", "增长", "回升", "突破"
    ]
    
    # 负面机构行为
    NEGATIVE_ACTIONS = ["减持", "清仓", "撤资", "抛售", "换股"]
    
    # 正向机构行为
    POSITIVE_ACTIONS = ["增持", "加仓", "买入", "建仓"]
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.issues = []
    
    def validate(self, data: List[Dict]) -> ValidationResult:
        """
        验证事件链数据
        
        Args:
            data: 事件链数据列表
        
        Returns:
            ValidationResult: 验证结果
        """
        self.issues = []
        valid_count = 0
        
        for i, item in enumerate(data):
            item_id = item.get("chain_id", f"item_{i}")
            item_issues = self._validate_item(item, i)
            
            # 如果有严重问题，算作无效
            has_error = any(issue.severity == "error" for issue in item_issues)
            if not has_error:
                valid_count += 1
            
            self.issues.extend(item_issues)
        
        # 统计信息
        statistics = {
            "total": len(data),
            "valid": valid_count,
            "invalid": len(data) - valid_count,
            "error_count": sum(1 for i in self.issues if i.severity == "error"),
            "warning_count": sum(1 for i in self.issues if i.severity == "warning"),
        }
        
        return ValidationResult(
            is_valid=valid_count == len(data),
            total_items=len(data),
            valid_items=valid_count,
            issues=self.issues,
            statistics=statistics
        )
    
    def _validate_item(self, item: Dict, index: int) -> List[ValidationIssue]:
        """验证单条事件链 (优化版)"""
        issues = []
        item_id = item.get("chain_id", f"item_{index}")
        
        # 1. 验证置信度分级一致性
        issues.extend(self._validate_confidence_level(item, item_id))
        
        # 2. 验证可量化指标完整性
        issues.extend(self._validate_quantifiable_metrics(item, item_id))
        
        # 3. 根据链类型进行验证
        chain_type = item.get("chain_id", "").split("_")[1] if "_" in item.get("chain_id", "") else ""
        
        if "ESG" in chain_type:
            issues.extend(self._validate_esg_chain(item, item_id))
        elif "舆情" in chain_type or "舆情→股价" in item.get("chain_id", ""):
            issues.extend(self._validate_sentiment_chain(item, item_id))
        elif "政策" in chain_type:
            issues.extend(self._validate_policy_chain(item, item_id))
        
        return issues
    
    def _validate_confidence_level(self, item: Dict, item_id: str) -> List[ValidationIssue]:
        """验证置信度分级一致性"""
        issues = []
        
        confidence = item.get("confidence", 0.85)
        level = item.get("confidence_level", "pilot")
        
        # 检查置信度是否在对应范围内
        if level in self.CONFIDENCE_RANGES:
            min_val, max_val = self.CONFIDENCE_RANGES[level]
            if confidence < min_val or confidence > max_val:
                issues.append(ValidationIssue(
                    item_id=item_id,
                    field="confidence",
                    issue_type="confidence_level_mismatch",
                    description=f"置信度{confidence}不在{level}级别范围({min_val}-{max_val})",
                    severity="warning",
                    suggestion=f"调整置信度至{min_val}-{max_val}范围内"
                ))
        
        # 检查置信度是否合理
        if confidence < 0.5:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="confidence",
                issue_type="confidence_too_low",
                description=f"置信度过低: {confidence}",
                severity="error",
                suggestion="置信度应大于0.5"
            ))
        
        return issues
    
    def _validate_quantifiable_metrics(self, item: Dict, item_id: str) -> List[ValidationIssue]:
        """验证可量化指标完整性"""
        issues = []
        
        metrics = item.get("quantifiable_metrics", {})
        
        # 检查是否包含可量化指标
        if not metrics:
            issues.append(ValidationIssue(
                item_id=item_id,
                field="quantifiable_metrics",
                issue_type="missing_metrics",
                description="缺少可量化指标",
                severity="warning",
                suggestion="添加渗透率、效率提升、成本下降等量化指标"
            ))
        else:
            # 检查指标值是否包含数字
            for metric_name, metric_value in metrics.items():
                if not any(c.isdigit() for c in str(metric_value)):
                    issues.append(ValidationIssue(
                        item_id=item_id,
                        field=f"quantifiable_metrics.{metric_name}",
                        issue_type="non_quantitative_value",
                        description=f"指标{metric_name}值'{metric_value}'不包含数字",
                        severity="warning",
                        suggestion="指标值应包含具体数值，如'提升30%'"
                    ))
        
        return issues
    
    def _validate_esg_chain(self, item: Dict, item_id: str) -> List[ValidationIssue]:
        """验证ESG事件链"""
        issues = []
        
        # 1. 验证评级变化
        rating_before = item.get("rating_before", "")
        rating_after = item.get("rating_after", "")
        
        if rating_before and rating_after:
            before_idx = self._get_rating_index(rating_before)
            after_idx = self._get_rating_index(rating_after)
            
            if before_idx >= 0 and after_idx >= 0:
                # 评级应该下降（或保持不变，但不能上升）
                if after_idx > before_idx:
                    issues.append(ValidationIssue(
                        item_id=item_id,
                        field="rating_after",
                        issue_type="rating_increase",
                        description=f"ESG评级不应上升: {rating_before} → {rating_after}",
                        severity="error",
                        suggestion="ESG负面事件后，评级应该下调"
                    ))
        
        # 2. 验证机构行为与事件方向一致
        esg_fund_action = item.get("esg_fund_action", "")
        if esg_fund_action:
            action_is_positive = any(pos in esg_fund_action for pos in ["加仓", "增持", "买入"])
            # ESG负面事件应该导致减持
            issues.append(ValidationIssue(
                item_id=item_id,
                field="esg_fund_action",
                issue_type="action_inconsistent",
                description=f"ESG负面事件但机构{esg_fund_action}",
                severity="error",
                suggestion="ESG负面事件后，机构应该减持或撤资"
            ))
        
        # 3. 验证结果与影响一致
        final_result = item.get("final_result", "")
        price_impact = item.get("price_impact", "")
        
        if final_result and price_impact:
            result_is_negative = any(neg in final_result for neg in self.NEGATIVE_RESULTS)
            impact_is_positive = any(pos in price_impact for pos in ["反弹", "回升", "上涨"])
            
            if result_is_negative and impact_is_positive:
                issues.append(ValidationIssue(
                    item_id=item_id,
                    field="price_impact",
                    issue_type="result_inconsistent",
                    description=f"结果与影响矛盾: {final_result} vs {price_impact}",
                    severity="error",
                    suggestion="结果为下跌时，影响不应为反弹"
                ))
        
        return issues
    
    def _validate_sentiment_chain(self, item: Dict, item_id: str) -> List[ValidationIssue]:
        """验证舆情事件链"""
        issues = []
        
        source_event = item.get("source_event", "")
        
        # 1. 判断事件正负
        is_negative_event = any(neg in source_event for neg in self.NEGATIVE_EVENTS)
        is_positive_event = any(pos in source_event for pos in self.POSITIVE_EVENTS)
        
        # 2. 验证传导方向
        market_sentiment = item.get("market_sentiment", "")
        if is_negative_event:
            if "乐观" in market_sentiment or "积极" in market_sentiment:
                issues.append(ValidationIssue(
                    item_id=item_id,
                    field="market_sentiment",
                    issue_type="sentiment_inconsistent",
                    description=f"负面事件但情绪{market_sentiment}",
                    severity="error",
                    suggestion="负面事件应导致负面情绪"
                ))
        
        # 3. 验证机构行为与情绪一致
        institution_action = item.get("institution_action", "")
        if institution_action:
            action_is_positive = any(pos in institution_action for pos in self.POSITIVE_ACTIONS)
            sentiment_is_negative = "负面" in market_sentiment or "悲观" in market_sentiment or "谨慎" in market_sentiment
            
            if sentiment_is_negative and action_is_positive:
                issues.append(ValidationIssue(
                    item_id=item_id,
                    field="institution_action",
                    issue_type="action_inconsistent",
                    description=f"情绪{market_sentiment}但机构{institution_action}",
                    severity="error",
                    suggestion="负面情绪下机构应该减持"
                ))
        
        # 4. 验证股价变动与结果一致
        price_change = item.get("price_change", "")
        final_result = item.get("final_result", "")
        
        if price_change and final_result:
            try:
                price_val = float(price_change.replace("%", "").replace("+", ""))
                result_is_negative = any(neg in final_result for neg in self.NEGATIVE_RESULTS)
                result_is_positive = any(pos in final_result for pos in self.POSITIVE_RESULTS)
                
                if price_val < 0 and result_is_positive:
                    issues.append(ValidationIssue(
                        item_id=item_id,
                        field="final_result",
                        issue_type="result_inconsistent",
                        description=f"股价下跌{final_result}但结果为上涨",
                        severity="error",
                        suggestion="股价下跌时结果应为下跌"
                    ))
            except:
                pass
        
        return issues
    
    def _validate_policy_chain(self, item: Dict, item_id: str) -> List[ValidationIssue]:
        """验证政策事件链"""
        issues = []
        
        # 验证资金流向与板块涨跌一致
        capital_flow = item.get("capital_flow", "")
        final_result = item.get("final_result", "")
        
        if capital_flow and final_result:
            is_inflow = "净流入" in capital_flow
            is_outflow = "净流出" in capital_flow
            
            result_is_up = "上涨" in final_result
            result_is_down = "下跌" in final_result
            
            if is_inflow and result_is_down:
                issues.append(ValidationIssue(
                    item_id=item_id,
                    field="capital_flow",
                    issue_type="flow_inconsistent",
                    description=f"资金净流入但板块下跌",
                    severity="warning",
                    suggestion="资金净流入通常导致上涨"
                ))
            
            if is_outflow and result_is_up:
                issues.append(ValidationIssue(
                    item_id=item_id,
                    field="capital_flow",
                    issue_type="flow_inconsistent",
                    description=f"资金净流出但板块上涨",
                    severity="warning",
                    suggestion="资金净流出通常导致下跌"
                ))
        
        return issues
    
    def _get_rating_index(self, rating: str) -> int:
        """获取评级索引"""
        for i, r in enumerate(self.RATING_ORDER):
            if r in rating:
                return i
        return -1
    
    def fix_issues(self, data: List[Dict]) -> Tuple[List[Dict], List[ValidationIssue]]:
        """
        自动修复问题
        
        Args:
            data: 事件链数据
        
        Returns:
            修复后的数据和剩余问题
        """
        fixed_data = []
        remaining_issues = []
        
        for i, item in enumerate(data):
            item_id = item.get("chain_id", f"item_{i}")
            fixed_item = item.copy()
            
            # 修复评级问题
            if "rating_before" in item and "rating_after" in item:
                before_idx = self._get_rating_index(item["rating_before"])
                after_idx = self._get_rating_index(item["rating_after"])
                
                if before_idx >= 0 and after_idx >= 0 and after_idx > before_idx:
                    # 评级上升了，需要下调
                    new_rating = self.RATING_ORDER[min(before_idx + 1, len(self.RATING_ORDER) - 1)]
                    fixed_item["rating_after"] = new_rating
            
            # 修复机构行为问题
            if "esg_fund_action" in item and any(neg in item.get("source_event", "") for neg in self.NEGATIVE_EVENTS):
                action = item.get("esg_fund_action", "")
                if "加仓" in action or "增持" in action:
                    fixed_item["esg_fund_action"] = "减持5%"
            
            fixed_data.append(fixed_item)
        
        # 重新验证
        result = self.validate(fixed_data)
        remaining_issues = result.issues
        
        return fixed_data, remaining_issues


def validate_event_chains(data: List[Dict], fix: bool = True) -> Tuple[List[Dict], ValidationResult]:
    """
    验证事件链数据（入口函数）
    
    Args:
        data: 事件链数据
        fix: 是否自动修复
    
    Returns:
        (修复后的数据, 验证结果)
    """
    validator = EventChainValidator()
    result = validator.validate(data)
    
    if not result.is_valid and fix:
        fixed_data, remaining = validator.fix_issues(data)
        result = validator.validate(fixed_data)
        return fixed_data, result
    
    return data, result
