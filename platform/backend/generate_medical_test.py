#!/usr/bin/env python3
"""
直接调用后端生成医疗类数据 - 最高质量
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("生成医疗类数据 - 最高质量")
print("="*70)

# 导入必要的模块
from simple_main import (
    generate_data_clean, 
    get_variation_engine,
    get_data_sanitizer,
    DOMAINS,
    TEMPLATES
)

print("\n【配置信息】")
print(f"领域: 医疗")
print(f"数量: 20条")
print(f"质量: 最高质量 (high)")
print(f"模式: clean")

# 生成数据
print("\n【开始生成】...")
try:
    data = generate_data_clean(
        domain="医疗",
        count=20,
        task_id="medical_test_001",
        quality_mode="high"
    )
    
    print(f"✅ 生成完成！共 {len(data)} 条数据\n")
    
    # 显示前10条
    print("="*70)
    print("数据样例（前10条）：")
    print("="*70)
    
    for i, item in enumerate(data[:10], 1):
        text = item.get('text', '')
        # 截断显示，保持可读性
        display_text = text[:200] + "..." if len(text) > 200 else text
        print(f"\n[{i}] {display_text}")
    
    # 统计信息
    print("\n" + "="*70)
    print("统计信息：")
    print("="*70)
    
    total_chars = sum(len(item.get('text', '')) for item in data)
    avg_chars = total_chars / len(data) if data else 0
    
    print(f"总条数: {len(data)}")
    print(f"总字符数: {total_chars}")
    print(f"平均长度: {avg_chars:.1f} 字符")
    print(f"质量等级: 最高质量 (≥0.85)")
    
    # 保存到文件
    import json
    output_file = "medical_high_quality_20.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存到: {output_file}")
    
except Exception as e:
    print(f"❌ 生成失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("生成完成！")
print("="*70)
