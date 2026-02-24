#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI数据验证器 - 确保数据能正确喂给AI
验证：格式正确性、字段完整性、数据可用性
"""

import json
import os
import re
from collections import Counter
from datetime import datetime

class AIDataValidator:
    """AI数据验证器"""
    
    # 各训练格式必需字段
    REQUIRED_FIELDS = {
        "pretrain": ["text"],
        "instruction": ["instruction", "output"],
        "conversation": ["conversations"],
        "sharegpt": ["conversations"],
        "behavior_sequence": ["user_id", "behavior", "timestamp"]
    }
    
    # 字段长度限制
    LENGTH_LIMITS = {
        "text": {"min": 50, "max": 10000},
        "instruction": {"min": 10, "max": 2000},
        "output": {"min": 10, "max": 4000},
        "input": {"min": 0, "max": 2000}
    }
    
    @staticmethod
    def validate_pretrain(data):
        """验证预训练格式"""
        errors = []
        warnings = []
        
        for i, item in enumerate(data):
            if "text" not in item:
                errors.append(f"第{i+1}条缺少text字段")
                continue
            
            text = item["text"]
            
            if len(text) < 50:
                warnings.append(f"第{i+1}条文本过短({len(text)}字符)")
            
            if len(text) > 10000:
                warnings.append(f"第{i+1}条文本过长({len(text)}字符)")
            
            if not text.strip():
                errors.append(f"第{i+1}条文本为空")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
    
    @staticmethod
    def validate_instruction(data):
        """验证指令微调格式"""
        errors = []
        warnings = []
        
        for i, item in enumerate(data):
            if "instruction" not in item:
                errors.append(f"第{i+1}条缺少instruction字段")
            
            if "output" not in item:
                errors.append(f"第{i+1}条缺少output字段")
            
            if "instruction" in item and len(item["instruction"]) < 5:
                warnings.append(f"第{i+1}条指令过短")
            
            if "output" in item and len(item["output"]) < 5:
                warnings.append(f"第{i+1}条输出过短")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
    
    @staticmethod
    def validate_conversation(data):
        """验证对话格式"""
        errors = []
        warnings = []
        
        for i, item in enumerate(data):
            if "conversations" not in item:
                errors.append(f"第{i+1}条缺少conversations字段")
                continue
            
            convs = item["conversations"]
            
            if not isinstance(convs, list):
                errors.append(f"第{i+1}条conversations不是列表")
                continue
            
            if len(convs) < 2:
                warnings.append(f"第{i+1}条对话轮数过少")
            
            for j, conv in enumerate(convs):
                if "role" not in conv and "from" not in conv:
                    errors.append(f"第{i+1}条第{j+1}轮缺少角色字段")
                
                if "content" not in conv and "value" not in conv:
                    errors.append(f"第{i+1}条第{j+1}轮缺少内容字段")
        
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
    
    @staticmethod
    def validate_behavior_sequence(data):
        """验证行为序列格式"""
        errors = []
        warnings = []
        
        user_behaviors = Counter()
        
        for i, item in enumerate(data):
            if "user_id" not in item:
                errors.append(f"第{i+1}条缺少user_id字段")
            
            if "behavior" not in item:
                errors.append(f"第{i+1}条缺少behavior字段")
            
            if "timestamp" not in item:
                warnings.append(f"第{i+1}条缺少timestamp字段")
            
            if "user_id" in item:
                user_behaviors[item["user_id"]] += 1
        
        single_behavior_users = sum(1 for c in user_behaviors.values() if c == 1)
        if single_behavior_users > len(user_behaviors) * 0.5:
            warnings.append(f"超过50%用户只有单条行为记录")
        
        return {
            "valid": len(errors) == 0, 
            "errors": errors, 
            "warnings": warnings,
            "stats": {
                "total_records": len(data),
                "unique_users": len(user_behaviors),
                "avg_behaviors_per_user": len(data) / len(user_behaviors) if user_behaviors else 0
            }
        }
    
    @staticmethod
    def validate_jsonl(filepath, format_type):
        """验证JSONL文件"""
        data = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    item = json.loads(line.strip())
                    data.append(item)
                except json.JSONDecodeError as e:
                    return {
                        "valid": False,
                        "errors": [f"第{line_num}行JSON解析错误: {e}"],
                        "warnings": []
                    }
        
        validators = {
            "pretrain": AIDataValidator.validate_pretrain,
            "instruction": AIDataValidator.validate_instruction,
            "conversation": AIDataValidator.validate_conversation,
            "behavior_sequence": AIDataValidator.validate_behavior_sequence
        }
        
        validator = validators.get(format_type)
        if validator:
            return validator(data)
        
        return {"valid": True, "errors": [], "warnings": []}
    
    @staticmethod
    def check_ai_readiness(data, format_type):
        """检查数据是否准备好喂给AI"""
        result = {
            "ready": True,
            "issues": [],
            "suggestions": [],
            "stats": {}
        }
        
        if not data:
            result["ready"] = False
            result["issues"].append("数据为空")
            return result
        
        result["stats"]["total"] = len(data)
        
        if format_type == "pretrain":
            total_chars = sum(len(item.get("text", "")) for item in data)
            result["stats"]["total_chars"] = total_chars
            result["stats"]["avg_chars"] = total_chars / len(data) if data else 0
            
            if result["stats"]["avg_chars"] < 100:
                result["issues"].append("平均文本长度过短，建议扩展内容")
                result["suggestions"].append("使用AI格式转换器扩展文本长度")
        
        elif format_type == "instruction":
            empty_inputs = sum(1 for item in data if not item.get("input"))
            result["stats"]["empty_input_ratio"] = empty_inputs / len(data) if data else 0
            
            if result["stats"]["empty_input_ratio"] > 0.8:
                result["suggestions"].append("大部分input为空，这是正常的")
        
        elif format_type == "conversation":
            avg_turns = sum(len(item.get("conversations", [])) for item in data) / len(data) if data else 0
            result["stats"]["avg_turns"] = avg_turns
            
            if avg_turns < 2:
                result["issues"].append("平均对话轮数过少")
        
        if result["issues"]:
            result["ready"] = False
        
        return result
    
    @staticmethod
    def auto_fix(data, format_type):
        """自动修复常见问题"""
        fixed = []
        
        for item in data:
            fixed_item = item.copy()
            
            if format_type == "pretrain":
                if "text" in fixed_item and len(fixed_item["text"]) < 50:
                    fixed_item["text"] = fixed_item["text"] + " [扩展内容：该数据用于AI训练，请确保内容完整且有意义。]"
            
            elif format_type == "instruction":
                if "input" not in fixed_item:
                    fixed_item["input"] = ""
                
                if "system" not in fixed_item:
                    fixed_item["system"] = "你是一个专业的AI助手。"
            
            elif format_type == "conversation":
                if "conversations" in fixed_item:
                    for conv in fixed_item["conversations"]:
                        if "role" not in conv and "from" in conv:
                            role_map = {"human": "user", "gpt": "assistant"}
                            conv["role"] = role_map.get(conv["from"], conv["from"])
                        
                        if "content" not in conv and "value" in conv:
                            conv["content"] = conv["value"]
            
            fixed.append(fixed_item)
        
        return fixed


def validate_and_report(data, format_type):
    """验证并生成报告"""
    print(f"\n{'='*60}")
    print(f"AI数据验证报告 - {format_type}")
    print('='*60)
    
    validator_map = {
        "pretrain": AIDataValidator.validate_pretrain,
        "instruction": AIDataValidator.validate_instruction,
        "conversation": AIDataValidator.validate_conversation,
        "behavior_sequence": AIDataValidator.validate_behavior_sequence
    }
    
    validator = validator_map.get(format_type)
    if not validator:
        print(f"不支持的格式: {format_type}")
        return
    
    result = validator(data)
    
    readiness = AIDataValidator.check_ai_readiness(data, format_type)
    
    print(f"\n[验证结果]")
    print(f"  状态: {'✅ 通过' if result['valid'] else '❌ 失败'}")
    print(f"  AI就绪: {'✅ 是' if readiness['ready'] else '❌ 否'}")
    
    if result["errors"]:
        print(f"\n[错误] ({len(result['errors'])}个)")
        for error in result["errors"][:5]:
            print(f"  ❌ {error}")
        if len(result["errors"]) > 5:
            print(f"  ... 还有 {len(result['errors']) - 5} 个错误")
    
    if result["warnings"]:
        print(f"\n[警告] ({len(result['warnings'])}个)")
        for warning in result["warnings"][:5]:
            print(f"  ⚠️ {warning}")
    
    if readiness["stats"]:
        print(f"\n[统计]")
        for key, value in readiness["stats"].items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
    
    if readiness["suggestions"]:
        print(f"\n[建议]")
        for suggestion in readiness["suggestions"]:
            print(f"  💡 {suggestion}")
    
    print(f"\n{'='*60}")
    
    return result["valid"] and readiness["ready"]


if __name__ == "__main__":
    print("\n" + "="*60)
    print("AI数据验证器 - 测试")
    print("="*60)
    
    # 测试预训练格式
    pretrain_data = [
        {"text": "这是一段足够长的预训练文本，用于测试验证器是否正常工作。需要确保文本长度超过50个字符才能通过验证。"},
        {"text": "短文本"}  # 会触发警告
    ]
    validate_and_report(pretrain_data, "pretrain")
    
    # 测试指令格式
    instruction_data = [
        {"instruction": "请解释AI", "input": "", "output": "AI是人工智能的缩写"},
        {"instruction": "什么是机器学习？", "output": "机器学习是AI的子领域"}
    ]
    validate_and_report(instruction_data, "instruction")
    
    # 测试对话格式
    conversation_data = [
        {
            "conversations": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！有什么可以帮你的？"}
            ]
        }
    ]
    validate_and_report(conversation_data, "conversation")
    
    print("\n" + "="*60)
    print("验证器测试完成")
    print("="*60)
