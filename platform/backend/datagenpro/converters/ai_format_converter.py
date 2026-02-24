#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI格式转换器
支持：预训练、指令微调、对话、ShareGPT格式、行为序列格式

合并自：
- ai_format_converter.py（根目录完整版）
- datagenpro/converters/ai_format_converter.py（基础版）
"""

import json
import os
import random
from datetime import datetime


class AIFormatConverter:
    """AI格式转换器 - 基础版接口"""
    
    @staticmethod
    def to_pretrain(data):
        """转换为预训练格式"""
        return AITrainingFormatConverter.to_pretrain_format(data)
    
    @staticmethod
    def to_instruction(data):
        """转换为指令微调格式"""
        return AITrainingFormatConverter.to_instruction_format(data)
    
    @staticmethod
    def to_conversation(data):
        """转换为对话格式"""
        return AITrainingFormatConverter.to_conversation_format(data)
    
    @staticmethod
    def to_sharegpt(data):
        """转换为ShareGPT格式"""
        return AITrainingFormatConverter.to_sharegpt_format(data)


class AITrainingFormatConverter:
    """AI训练数据格式转换器 - 完整版"""
    
    @staticmethod
    def to_pretrain_format(data, min_length=100):
        """
        转换为预训练格式
        适用于：GPT、LLaMA等基座模型预训练
        """
        results = []
        
        for item in data:
            text = item.get("text", "")
            word = item.get("word", "")
            category = item.get("category", "")
            
            extended_text = f"""
{category}领域知识：

{word}的定义：
{text}

相关概念：
在{category}领域中，{word}是一个重要的概念。理解{word}对于掌握{category}的核心知识至关重要。

应用场景：
{word}在实际应用中有着广泛的用途，包括但不限于：
1. 学术研究
2. 工业应用
3. 技术开发

总结：
{word}是{category}领域的基础知识，需要深入理解和掌握。
"""
            
            if len(extended_text) >= min_length:
                results.append({
                    "text": extended_text.strip(),
                    "meta": {
                        "source": item.get("source", "unknown"),
                        "category": category,
                        "word": word,
                        "length": len(extended_text)
                    }
                })
        
        return results
    
    @staticmethod
    def to_instruction_format(data):
        """
        转换为指令微调格式
        适用于：Alpaca、ChatML等指令微调
        """
        results = []
        
        instruction_templates = [
            {
                "instruction": "请解释以下概念：{word}",
                "input": "",
                "output": "{text}"
            },
            {
                "instruction": "什么是{word}？请详细说明。",
                "input": "",
                "output": "{text}\n\n{word}是{category}领域的重要概念。"
            },
            {
                "instruction": "在{category}领域中，{word}是什么意思？",
                "input": "",
                "output": "{text}"
            },
            {
                "instruction": "请用简单的话解释{word}",
                "input": "",
                "output": "简单来说，{text}"
            },
            {
                "instruction": "请举例说明{word}的应用",
                "input": "{word}是{category}领域的概念",
                "output": "{text}\n\n例如：在实际项目中，{word}被广泛应用于解决复杂问题，提高系统效率和准确性。"
            }
        ]
        
        for item in data:
            template = random.choice(instruction_templates)
            
            instruction = template["instruction"].format(
                word=item.get("word", ""),
                category=item.get("category", "")
            )
            
            output = template["output"].format(
                word=item.get("word", ""),
                text=item.get("text", ""),
                category=item.get("category", "")
            )
            
            results.append({
                "instruction": instruction,
                "input": template["input"].format(
                    word=item.get("word", ""),
                    category=item.get("category", "")
                ),
                "output": output,
                "system": f"你是一个{item.get('category', '通用')}领域的专业助手。"
            })
        
        return results
    
    @staticmethod
    def to_conversation_format(data):
        """
        转换为对话格式
        适用于：ChatGPT、Claude等对话模型
        """
        results = []
        
        for item in data:
            word = item.get("word", "")
            text = item.get("text", "")
            category = item.get("category", "")
            
            conversations = [
                {
                    "role": "system",
                    "content": f"你是一个{category}领域的专业助手，请用专业但易懂的方式回答问题。"
                },
                {
                    "role": "user",
                    "content": f"你好，我想了解{word}是什么？"
                },
                {
                    "role": "assistant",
                    "content": f"你好！很高兴为你解释{word}。\n\n{text}"
                },
                {
                    "role": "user",
                    "content": f"能再详细说说{word}的应用吗？"
                },
                {
                    "role": "assistant",
                    "content": f"当然！{word}在{category}领域有很多重要应用：\n\n1. **学术研究**：{word}是基础研究方向之一\n2. **工业应用**：许多企业使用{word}解决实际问题\n3. **技术开发**：{word}是核心技术栈的重要组成部分\n\n你想了解哪个方面的更多细节？"
                }
            ]
            
            results.append({
                "conversations": conversations,
                "meta": {
                    "word": word,
                    "category": category,
                    "turns": len(conversations) // 2
                }
            })
        
        return results
    
    @staticmethod
    def to_sharegpt_format(data):
        """
        转换为ShareGPT格式
        适用于：ShareGPT数据集格式
        """
        results = []
        
        for item in data:
            word = item.get("word", "")
            text = item.get("text", "")
            category = item.get("category", "")
            
            results.append({
                "conversations": [
                    {
                        "from": "human",
                        "value": f"请解释一下{category}领域中的{word}概念"
                    },
                    {
                        "from": "gpt",
                        "value": f"好的，我来为你详细解释{word}：\n\n{text}\n\n希望这个解释对你有帮助！如果还有疑问，请随时提问。"
                    }
                ]
            })
        
        return results
    
    @staticmethod
    def behavior_sequence_to_training_format(sequences):
        """
        将行为序列转换为训练格式
        适用于：用户行为预测、推荐系统训练
        """
        results = []
        
        user_sequences = {}
        for item in sequences:
            user_id = item.get("user_id")
            if user_id not in user_sequences:
                user_sequences[user_id] = []
            user_sequences[user_id].append(item)
        
        for user_id, seq in user_sequences.items():
            if len(seq) < 3:
                continue
            
            for i in range(len(seq) - 2):
                history = [s["behavior"] for s in seq[:i+1]]
                next_behavior = seq[i+1]["behavior"]
                
                results.append({
                    "instruction": "根据用户历史行为，预测下一个行为",
                    "input": f"用户历史行为序列：{' -> '.join(history)}",
                    "output": f"预测下一个行为：{next_behavior}",
                    "meta": {
                        "user_id": user_id,
                        "sequence_length": len(seq),
                        "position": i + 1
                    }
                })
        
        return results
    
    @staticmethod
    def convert_all(data, output_dir):
        """转换所有格式并保存"""
        os.makedirs(output_dir, exist_ok=True)
        
        pretrain = AITrainingFormatConverter.to_pretrain_format(data)
        with open(os.path.join(output_dir, "pretrain.jsonl"), "w", encoding="utf-8") as f:
            for item in pretrain:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        instruction = AITrainingFormatConverter.to_instruction_format(data)
        with open(os.path.join(output_dir, "instruction.jsonl"), "w", encoding="utf-8") as f:
            for item in instruction:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        conversation = AITrainingFormatConverter.to_conversation_format(data)
        with open(os.path.join(output_dir, "conversation.jsonl"), "w", encoding="utf-8") as f:
            for item in conversation:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        sharegpt = AITrainingFormatConverter.to_sharegpt_format(data)
        with open(os.path.join(output_dir, "sharegpt.jsonl"), "w", encoding="utf-8") as f:
            for item in sharegpt:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        return {
            "pretrain": len(pretrain),
            "instruction": len(instruction),
            "conversation": len(conversation),
            "sharegpt": len(sharegpt)
        }
    
    @staticmethod
    def to_xml_format(data, root_name="dataset", item_name="item"):
        """
        转换为XML格式
        适用于：传统NLP工具、XML数据处理系统
        """
        xml_lines = [f'<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append(f'<{root_name}>')
        
        for i, item in enumerate(data, 1):
            xml_lines.append(f'  <{item_name} id="{i}">')
            
            # 递归处理字典
            def dict_to_xml(d, indent=4):
                lines = []
                for key, value in d.items():
                    tag = str(key).replace(' ', '_').replace('-', '_')
                    if isinstance(value, dict):
                        lines.append(' ' * indent + f'<{tag}>')
                        lines.extend(dict_to_xml(value, indent + 2))
                        lines.append(' ' * indent + f'</{tag}>')
                    elif isinstance(value, list):
                        lines.append(' ' * indent + f'<{tag}>')
                        for v in value:
                            if isinstance(v, dict):
                                lines.extend(dict_to_xml(v, indent + 2))
                            else:
                                lines.append(' ' * (indent + 2) + f'<item>{escape_xml(str(v))}</item>')
                        lines.append(' ' * indent + f'</{tag}>')
                    else:
                        lines.append(' ' * indent + f'<{tag}>{escape_xml(str(value))}</{tag}>')
                return lines
            
            xml_lines.extend(dict_to_xml(item))
            xml_lines.append(f'  </{item_name}>')
        
        xml_lines.append(f'</{root_name}>')
        return '\n'.join(xml_lines)
    
    @staticmethod
    def to_yaml_format(data):
        """
        转换为YAML格式
        适用于：配置文件、人类可读的数据交换
        """
        yaml_lines = []
        
        for i, item in enumerate(data, 1):
            yaml_lines.append(f'- item_{i}:')
            
            def dict_to_yaml(d, indent=2):
                lines = []
                for key, value in d.items():
                    if isinstance(value, dict):
                        lines.append(' ' * indent + f'{key}:')
                        lines.extend(dict_to_yaml(value, indent + 2))
                    elif isinstance(value, list):
                        lines.append(' ' * indent + f'{key}:')
                        for v in value:
                            if isinstance(v, dict):
                                lines.append(' ' * (indent + 2) + '-')
                                lines.extend(dict_to_yaml(v, indent + 4))
                            else:
                                lines.append(' ' * (indent + 2) + f'- {escape_yaml(str(v))}')
                    else:
                        lines.append(' ' * indent + f'{key}: {escape_yaml(str(value))}')
                return lines
            
            yaml_lines.extend(dict_to_yaml(item))
            yaml_lines.append('')  # 空行分隔
        
        return '\n'.join(yaml_lines)
    
    @staticmethod
    def to_csv_format(data, delimiter=',', include_header=True):
        """
        转换为CSV格式
        适用于：表格处理、Excel导入、数据分析
        """
        if not data:
            return ''
        
        import csv
        import io
        
        # 获取所有可能的字段
        all_fields = set()
        for item in data:
            all_fields.update(item.keys())
        all_fields = sorted(all_fields)
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=all_fields, delimiter=delimiter, 
                                extrasaction='ignore', quoting=csv.QUOTE_MINIMAL)
        
        if include_header:
            writer.writeheader()
        
        for item in data:
            # 处理嵌套字典，将其转换为JSON字符串
            flat_item = {}
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    flat_item[key] = json.dumps(value, ensure_ascii=False)
                else:
                    flat_item[key] = value
            writer.writerow(flat_item)
        
        return output.getvalue()
    
    @staticmethod
    def to_parquet_format(data, output_path):
        """
        转换为Parquet格式
        适用于：大数据处理、Pandas分析、列式存储
        注意：需要安装 pandas 和 pyarrow
        """
        try:
            import pandas as pd
            
            # 将数据转换为DataFrame
            df = pd.json_normalize(data, sep='_')
            
            # 保存为Parquet
            df.to_parquet(output_path, index=False, compression='snappy')
            
            return {"success": True, "path": output_path, "rows": len(df), "columns": len(df.columns)}
        except ImportError:
            return {"success": False, "error": "缺少依赖：请安装 pandas 和 pyarrow (pip install pandas pyarrow)"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def to_excel_format(data, output_path, sheet_name='Data'):
        """
        转换为Excel格式
        适用于：商务报表、人工审核、Excel分析
        注意：需要安装 openpyxl
        """
        try:
            import pandas as pd
            
            # 将数据转换为DataFrame
            df = pd.json_normalize(data, sep='_')
            
            # 保存为Excel
            df.to_excel(output_path, sheet_name=sheet_name, index=False, engine='openpyxl')
            
            return {"success": True, "path": output_path, "rows": len(df), "columns": len(df.columns)}
        except ImportError:
            return {"success": False, "error": "缺少依赖：请安装 pandas 和 openpyxl (pip install pandas openpyxl)"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def convert_to_format(data, format_type, output_path=None, **kwargs):
        """
        统一格式转换接口
        
        Args:
            data: 原始数据列表
            format_type: 目标格式 (json, jsonl, xml, yaml, csv, parquet, excel, pretrain, instruction, conversation, sharegpt)
            output_path: 输出文件路径（对于parquet和excel需要）
            **kwargs: 其他参数
        
        Returns:
            转换后的数据或保存结果
        """
        format_type = format_type.lower()
        
        if format_type == 'json':
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        elif format_type == 'jsonl':
            lines = [json.dumps(item, ensure_ascii=False) for item in data]
            return '\n'.join(lines)
        
        elif format_type == 'xml':
            root_name = kwargs.get('root_name', 'dataset')
            item_name = kwargs.get('item_name', 'item')
            return AITrainingFormatConverter.to_xml_format(data, root_name, item_name)
        
        elif format_type == 'yaml':
            return AITrainingFormatConverter.to_yaml_format(data)
        
        elif format_type == 'csv':
            delimiter = kwargs.get('delimiter', ',')
            include_header = kwargs.get('include_header', True)
            return AITrainingFormatConverter.to_csv_format(data, delimiter, include_header)
        
        elif format_type == 'tsv':
            return AITrainingFormatConverter.to_csv_format(data, delimiter='\t', include_header=True)
        
        elif format_type == 'parquet':
            if not output_path:
                return {"success": False, "error": "parquet格式需要提供output_path参数"}
            return AITrainingFormatConverter.to_parquet_format(data, output_path)
        
        elif format_type == 'excel' or format_type == 'xlsx':
            if not output_path:
                return {"success": False, "error": "excel格式需要提供output_path参数"}
            sheet_name = kwargs.get('sheet_name', 'Data')
            return AITrainingFormatConverter.to_excel_format(data, output_path, sheet_name)
        
        elif format_type == 'pretrain':
            return AITrainingFormatConverter.to_pretrain_format(data)
        
        elif format_type == 'instruction':
            return AITrainingFormatConverter.to_instruction_format(data)
        
        elif format_type == 'conversation':
            return AITrainingFormatConverter.to_conversation_format(data)
        
        elif format_type == 'sharegpt':
            return AITrainingFormatConverter.to_sharegpt_format(data)
        
        else:
            return {"success": False, "error": f"不支持的格式: {format_type}"}


def escape_xml(text):
    """XML特殊字符转义"""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))


def escape_yaml(text):
    """YAML特殊字符转义"""
    # 如果包含特殊字符，用引号包裹
    if any(c in text for c in [':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'"]):
        # 处理双引号
        text = text.replace('"', '\\"')
        return f'"{text}"'
    return text


ai_format_converter = AIFormatConverter()
