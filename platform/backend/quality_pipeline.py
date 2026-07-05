#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一质量管道 - QualityPipeline
整合基本质量管道和逻辑验证管道
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class PipelineResult:
    """管道处理结果"""
    success: bool
    data: List[Dict]
    validation_results: Dict = field(default_factory=dict)
    quality_report: Dict = field(default_factory=dict)
    error: str = ""


class QualityPipeline:
    """
    统一质量管道
    
    工作流程:
    1. 基本质量验证 (格式、长度、空值)
    2. 逻辑验证 (根据output_type选择验证器)
    3. 自动修复 (如果开启)
    4. 返回结果
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self._init_validators()
    
    def _init_validators(self):
        """初始化验证器"""
        self.event_chain_validator = None
        self.knowledge_graph_validator = None
        self.literature_validator = None
        
        try:
            from validators.event_chain_validator import EventChainValidator
            self.event_chain_validator = EventChainValidator()
        except ImportError:
            print("[QualityPipeline] 事件链验证器加载失败")
        
        try:
            from validators.knowledge_graph_validator import KnowledgeGraphValidator
            self.knowledge_graph_validator = KnowledgeGraphValidator()
        except ImportError:
            print("[QualityPipeline] 知识图谱验证器加载失败")
        
        try:
            from validators.literature_validator import LiteratureValidator
            self.literature_validator = LiteratureValidator()
        except ImportError:
            print("[QualityPipeline] 文献验证器加载失败")
    
    def process(self, 
                data: List[Dict], 
                output_type: str,
                domain: str = "",
                auto_fix: bool = True) -> PipelineResult:
        """
        处理数据
        
        Args:
            data: 原始数据
            output_type: 输出类型
            domain: 领域
            auto_fix: 是否自动修复
        
        Returns:
            PipelineResult: 处理结果
        """
        if not data:
            return PipelineResult(
                success=False,
                data=[],
                error="数据为空"
            )
        
        print(f"[QualityPipeline] 开始处理: output_type={output_type}, count={len(data)}")
        
        validation_results = {}
        
        # 1. 基本质量验证
        basic_result = self._basic_validation(data)
        validation_results["basic"] = basic_result
        
        if not basic_result["is_valid"]:
            print(f"[QualityPipeline] 基本验证失败: {basic_result.get('error', '未知错误')}")
        
        # 2. 逻辑验证
        logic_result = self._logic_validation(data, output_type, auto_fix)
        validation_results["logic"] = logic_result
        
        # 3. 获取最终数据
        final_data = logic_result.get("data", data)
        
        # 4. 构建质量报告
        quality_report = self._build_quality_report(validation_results, output_type)
        
        print(f"[QualityPipeline] 处理完成: valid={logic_result.get('valid_count', 0)}/{len(final_data)}")
        
        return PipelineResult(
            success=len(final_data) > 0,
            data=final_data,
            validation_results=validation_results,
            quality_report=quality_report
        )
    
    def _basic_validation(self, data: List[Dict]) -> Dict:
        """基本质量验证"""
        valid_count = 0
        errors = []
        
        for i, item in enumerate(data):
            # 检查必填字段
            if not item:
                errors.append(f"第{i}条数据为空")
                continue
            
            # 检查必要字段
            has_content = False
            for field in ["text", "content", "chain", "head"]:
                if field in item and item[field]:
                    has_content = True
                    break
            
            if has_content:
                valid_count += 1
        
        return {
            "is_valid": valid_count == len(data),
            "total": len(data),
            "valid": valid_count,
            "error": "; ".join(errors[:5]) if errors else ""
        }
    
    def _logic_validation(self, data: List[Dict], output_type: str, auto_fix: bool) -> Dict:
        """逻辑验证"""
        result = {
            "is_valid": True,
            "valid_count": len(data),
            "data": data,
            "validator": output_type
        }
        
        if output_type == "event_chain" and self.event_chain_validator:
            print(f"[QualityPipeline] 使用事件链验证器...")
            validation_result = self.event_chain_validator.validate(data)
            
            if not validation_result.is_valid and auto_fix:
                print(f"[QualityPipeline] 自动修复事件链问题...")
                fixed_data, remaining = self.event_chain_validator.fix_issues(data)
                result["data"] = fixed_data
                result["valid_count"] = validation_result.valid_items
                result["remaining_issues"] = len(remaining)
            
            result["is_valid"] = validation_result.is_valid
            result["valid_count"] = validation_result.valid_items
            result["statistics"] = validation_result.statistics
            result["issues"] = [
                {"field": i.field, "issue": i.issue_type, "severity": i.severity}
                for i in validation_result.issues[:10]
            ]
        
        elif output_type == "knowledge_graph" and self.knowledge_graph_validator:
            print(f"[QualityPipeline] 使用知识图谱验证器...")
            validation_result = self.knowledge_graph_validator.validate(data)
            
            if not validation_result.is_valid and auto_fix:
                print(f"[QualityPipeline] 自动修复知识图谱问题...")
                fixed_data, remaining = self.knowledge_graph_validator.fix_issues(data)
                result["data"] = fixed_data
                result["valid_count"] = validation_result.valid_items
            
            result["is_valid"] = validation_result.is_valid
            result["valid_count"] = validation_result.valid_items
            result["statistics"] = validation_result.statistics
        
        elif output_type == "literature" and self.literature_validator:
            print(f"[QualityPipeline] 使用文献验证器...")
            validation_result = self.literature_validator.validate(data)
            
            if not validation_result.is_valid and auto_fix:
                print(f"[QualityPipeline] 自动修复文献问题...")
                fixed_data, remaining = self.literature_validator.fix_issues(data)
                result["data"] = fixed_data
                result["valid_count"] = validation_result.valid_items
            
            result["is_valid"] = validation_result.is_valid
            result["valid_count"] = validation_result.valid_items
            result["statistics"] = validation_result.statistics
        
        return result
    
    def _build_quality_report(self, validation_results: Dict, output_type: str) -> Dict:
        """构建质量报告"""
        basic = validation_results.get("basic", {})
        logic = validation_results.get("logic", {})
        
        # 计算综合评分
        basic_score = basic.get("valid", 0) / max(basic.get("total", 1), 1)
        logic_score = logic.get("valid_count", 0) / max(len(logic.get("data", [{}])), 1)
        
        overall_score = (basic_score * 0.3 + logic_score * 0.7)
        
        # 确定等级
        if overall_score >= 0.95:
            grade = "A+"
        elif overall_score >= 0.9:
            grade = "A"
        elif overall_score >= 0.8:
            grade = "B"
        elif overall_score >= 0.7:
            grade = "C"
        else:
            grade = "D"
        
        return {
            "overall_score": round(overall_score, 3),
            "grade": grade,
            "output_type": output_type,
            "basic_validation": {
                "passed": basic.get("is_valid", False),
                "valid_count": basic.get("valid", 0),
                "total": basic.get("total", 0)
            },
            "logic_validation": {
                "passed": logic.get("is_valid", True),
                "valid_count": logic.get("valid_count", 0),
                "issues_count": len(logic.get("issues", []))
            },
            "statistics": logic.get("statistics", {})
        }


# 全局实例
_quality_pipeline = None


def get_quality_pipeline(config: Dict = None) -> QualityPipeline:
    """获取质量管道实例"""
    global _quality_pipeline
    if _quality_pipeline is None:
        _quality_pipeline = QualityPipeline(config)
    return _quality_pipeline


def process_with_quality_pipeline(data: List[Dict], output_type: str, domain: str = "") -> PipelineResult:
    """统一入口函数"""
    pipeline = get_quality_pipeline()
    return pipeline.process(data, output_type, domain)
