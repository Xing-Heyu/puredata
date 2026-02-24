#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI数据验证器
"""

class AIValidator:
    """AI数据验证器"""
    
    @staticmethod
    def validate_pretrain(data):
        """验证预训练格式"""
        errors = []
        for i, item in enumerate(data):
            if "text" not in item:
                errors.append(f"第{i+1}条缺少text字段")
            elif len(item["text"]) < 50:
                errors.append(f"第{i+1}条文本过短")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    @staticmethod
    def validate_instruction(data):
        """验证指令格式"""
        errors = []
        for i, item in enumerate(data):
            if "instruction" not in item:
                errors.append(f"第{i+1}条缺少instruction字段")
            if "output" not in item:
                errors.append(f"第{i+1}条缺少output字段")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    @staticmethod
    def validate_conversation(data):
        """验证对话格式"""
        errors = []
        for i, item in enumerate(data):
            if "conversations" not in item:
                errors.append(f"第{i+1}条缺少conversations字段")
            elif len(item["conversations"]) < 2:
                errors.append(f"第{i+1}条对话轮数过少")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    @staticmethod
    def check_ai_ready(data, format_type):
        """检查AI就绪状态"""
        validators = {
            "pretrain": AIValidator.validate_pretrain,
            "instruction": AIValidator.validate_instruction,
            "conversation": AIValidator.validate_conversation
        }
        
        validator = validators.get(format_type)
        if validator:
            result = validator(data)
            return result["valid"] and len(result.get("errors", [])) == 0
        
        return True
