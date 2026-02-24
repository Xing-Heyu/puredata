#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI数据完整流程 - 从生成到可用
流程：生成 → 转换 → 验证 → 确认可用
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datagenpro.converters.ai_format_converter import AITrainingFormatConverter
from ai_data_validator import AIDataValidator, validate_and_report
from datagenpro.managers.fault_tolerance_manager import DataQuality, DataQualityController

class AIDataPipeline:
    """AI数据完整流程"""
    
    @staticmethod
    def process(raw_data, output_dir, quality=DataQuality.NORMAL):
        """
        完整处理流程
        1. 应用质量等级
        2. 转换为AI格式
        3. 验证数据
        4. 生成报告
        """
        os.makedirs(output_dir, exist_ok=True)
        
        report = {
            "input_count": len(raw_data),
            "quality": quality.value,
            "formats": {},
            "all_ready": True
        }
        
        print(f"\n{'='*60}")
        print("AI数据处理流程")
        print('='*60)
        print(f"输入数据: {len(raw_data)} 条")
        print(f"质量等级: {quality.value}")
        
        # 1. 应用质量等级
        print(f"\n[步骤1] 应用质量等级...")
        processed_data = DataQualityController.apply_quality(raw_data, quality)
        print(f"  处理后: {len(processed_data)} 条")
        
        # 2. 转换为各种AI格式
        print(f"\n[步骤2] 转换为AI格式...")
        
        # 预训练格式
        pretrain = AITrainingFormatConverter.to_pretrain_format(processed_data)
        report["formats"]["pretrain"] = {"count": len(pretrain)}
        print(f"  预训练格式: {len(pretrain)} 条")
        
        # 指令格式
        instruction = AITrainingFormatConverter.to_instruction_format(processed_data)
        report["formats"]["instruction"] = {"count": len(instruction)}
        print(f"  指令格式: {len(instruction)} 条")
        
        # 对话格式
        conversation = AITrainingFormatConverter.to_conversation_format(processed_data)
        report["formats"]["conversation"] = {"count": len(conversation)}
        print(f"  对话格式: {len(conversation)} 条")
        
        # ShareGPT格式
        sharegpt = AITrainingFormatConverter.to_sharegpt_format(processed_data)
        report["formats"]["sharegpt"] = {"count": len(sharegpt)}
        print(f"  ShareGPT格式: {len(sharegpt)} 条")
        
        # 3. 验证各格式
        print(f"\n[步骤3] 验证数据...")
        
        formats_data = {
            "pretrain": pretrain,
            "instruction": instruction,
            "conversation": conversation
        }
        
        for fmt, data in formats_data.items():
            result = AIDataValidator.check_ai_readiness(data, fmt)
            report["formats"][fmt]["ready"] = result["ready"]
            report["formats"][fmt]["stats"] = result.get("stats", {})
            
            status = "✅ 就绪" if result["ready"] else "❌ 未就绪"
            print(f"  {fmt}: {status}")
            
            if not result["ready"]:
                report["all_ready"] = False
        
        # 4. 保存文件
        print(f"\n[步骤4] 保存文件...")
        
        files = {
            "pretrain.jsonl": pretrain,
            "instruction.jsonl": instruction,
            "conversation.jsonl": conversation,
            "sharegpt.jsonl": sharegpt
        }
        
        for filename, data in files.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            print(f"  保存: {filename}")
        
        # 5. 生成报告
        report["output_dir"] = output_dir
        report["processed_at"] = str(os.path.getmtime(output_dir))
        
        report_path = os.path.join(output_dir, "report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"处理完成！")
        print(f"所有格式AI就绪: {'✅ 是' if report['all_ready'] else '❌ 否'}")
        print(f"输出目录: {output_dir}")
        print('='*60)
        
        return report
    
    @staticmethod
    def quick_generate_for_ai(domain, count, output_dir, quality=DataQuality.NORMAL):
        """快速生成AI可用数据"""
        import simple_main
        
        if not simple_main.TEMPLATES:
            simple_main.init_templates()
        
        if domain not in simple_main.DOMAINS:
            print(f"错误: 未知领域 {domain}")
            print(f"可用领域: {list(simple_main.DOMAINS.keys())}")
            return None
        
        keywords = simple_main.DOMAINS[domain]
        raw_data = []
        
        for i in range(count):
            keyword = keywords[i % len(keywords)]
            text, _ = simple_main.TopologyGenerator.generate_realistic_entry(
                keyword, domain, i, keywords, "medium"
            )
            
            raw_data.append({
                "id": i + 1,
                "word": keyword,
                "text": text,
                "category": domain,
                "source": "generated"
            })
        
        return AIDataPipeline.process(raw_data, output_dir, quality)


def demo():
    """演示完整流程"""
    print("\n" + "="*60)
    print("AI数据完整流程演示")
    print("="*60)
    
    # 示例原始数据
    raw_data = [
        {
            "id": 1,
            "word": "machine learning",
            "text": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
            "category": "人工智能",
            "source": "generated"
        },
        {
            "id": 2,
            "word": "deep learning",
            "text": "Deep learning is a subset of machine learning that uses neural networks with multiple layers to analyze various factors of data.",
            "category": "人工智能",
            "source": "generated"
        },
        {
            "id": 3,
            "word": "neural network",
            "text": "A neural network is a computing system inspired by biological neural networks that constitute animal brains.",
            "category": "人工智能",
            "source": "generated"
        }
    ]
    
    output_dir = os.path.join(os.path.dirname(__file__), "ai_output")
    
    # 执行完整流程
    report = AIDataPipeline.process(raw_data, output_dir, DataQuality.CLEAN)
    
    print("\n" + "="*60)
    print("生成的文件:")
    print("="*60)
    
    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        size = os.path.getsize(filepath)
        print(f"  {filename}: {size} bytes")
    
    print("\n" + "="*60)
    print("数据已准备好喂给AI！")
    print("="*60)


if __name__ == "__main__":
    demo()
