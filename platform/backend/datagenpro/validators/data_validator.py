#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证器
"""

class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate(data):
        """验证数据"""
        errors = []
        warnings = []
        
        if not data:
            errors.append("数据为空")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        for i, item in enumerate(data):
            if "text" not in item:
                errors.append(f"第{i+1}条缺少text字段")
            
            if "text" in item and len(item["text"]) < 10:
                warnings.append(f"第{i+1}条文本过短")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "count": len(data)
        }
