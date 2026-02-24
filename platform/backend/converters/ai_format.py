#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换层 - AI格式转换器
整合自 datagenpro/converters/ai_format_converter.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from datagenpro.converters.ai_format_converter import AIFormatConverter, AITrainingFormatConverter
    __all__ = ['AIFormatConverter', 'AITrainingFormatConverter']
except ImportError:
    import json
    from typing import Dict, List, Any
    
    class AIFormatConverter:
        """AI格式转换器 - 占位实现"""
        
        @staticmethod
        def to_pretrain_format(data: List[Dict]) -> List[Dict]:
            """转换为预训练格式"""
            return [{"text": item.get("text", "")} for item in data]
        
        @staticmethod
        def to_instruction_format(data: List[Dict]) -> List[Dict]:
            """转换为指令格式"""
            return [
                {
                    "instruction": f"请解释{item.get('word', '')}的概念",
                    "input": "",
                    "output": item.get("text", "")
                }
                for item in data
            ]
        
        @staticmethod
        def to_conversation_format(data: List[Dict]) -> List[Dict]:
            """转换为对话格式"""
            return [
                {
                    "conversations": [
                        {"role": "user", "content": f"请解释{item.get('word', '')}"},
                        {"role": "assistant", "content": item.get("text", "")}
                    ]
                }
                for item in data
            ]
    
    AITrainingFormatConverter = AIFormatConverter
    __all__ = ['AIFormatConverter', 'AITrainingFormatConverter']
