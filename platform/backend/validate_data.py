#!/usr/bin/env python3
"""数据质量验证器 - 检查生成数据是否可用"""

import json
import os
from collections import Counter

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')

def validate_data_file(filepath):
    """验证单个数据文件"""
    print(f"\n{'='*60}")
    print(f"验证文件: {os.path.basename(filepath)}")
    print('='*60)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    issues = []
    warnings = []
    
    # 1. 检查数据量
    print(f"\n[1] 数据量检查")
    print(f"    总条数: {len(data)}")
    if len(data) == 0:
        issues.append("数据为空！")
    
    # 2. 检查字段完整性
    print(f"\n[2] 字段完整性检查")
    required_fields = ['id', 'word', 'text', 'category', 'source']
    optional_fields = ['confidence', 'timestamp', 'user_id', 'verified', 'quality_score']
    
    field_counts = Counter()
    for item in data:
        for field in item.keys():
            field_counts[field] += 1
    
    for field in required_fields:
        count = field_counts.get(field, 0)
        if count == len(data):
            print(f"    ✅ {field}: {count}/{len(data)} (完整)")
        else:
            issues.append(f"字段 {field} 缺失: {count}/{len(data)}")
            print(f"    ❌ {field}: {count}/{len(data)} (缺失)")
    
    for field in optional_fields:
        count = field_counts.get(field, 0)
        if count > 0:
            print(f"    📊 {field}: {count}/{len(data)} (可选)")
    
    # 3. 检查文本质量
    print(f"\n[3] 文本质量检查")
    text_lengths = [len(item.get('text', '')) for item in data]
    avg_len = sum(text_lengths) / len(text_lengths) if text_lengths else 0
    min_len = min(text_lengths) if text_lengths else 0
    max_len = max(text_lengths) if text_lengths else 0
    
    print(f"    平均长度: {avg_len:.1f} 字符")
    print(f"    最短: {min_len} 字符")
    print(f"    最长: {max_len} 字符")
    
    short_count = sum(1 for l in text_lengths if l < 10)
    if short_count > 0:
        warnings.append(f"有 {short_count} 条文本过短 (<10字符)")
    
    # 4. 检查重复
    print(f"\n[4] 重复检查")
    texts = [item.get('text', '') for item in data]
    unique_texts = set(texts)
    duplicates = len(texts) - len(unique_texts)
    print(f"    唯一文本: {len(unique_texts)}/{len(texts)}")
    print(f"    重复数量: {duplicates}")
    if duplicates > len(data) * 0.1:
        warnings.append(f"重复率过高: {duplicates/len(data)*100:.1f}%")
    
    # 5. 检查来源分布
    print(f"\n[5] 来源分布")
    sources = Counter(item.get('source', 'unknown') for item in data)
    for source, count in sources.most_common():
        pct = count / len(data) * 100
        print(f"    {source}: {count} ({pct:.1f}%)")
    
    # 6. 检查置信度分布
    if 'confidence' in field_counts:
        print(f"\n[6] 置信度分布")
        confidences = [item.get('confidence', 0) for item in data if 'confidence' in item]
        if confidences:
            avg_conf = sum(confidences) / len(confidences)
            high_conf = sum(1 for c in confidences if c >= 0.8)
            print(f"    平均置信度: {avg_conf:.2f}")
            print(f"    高置信度(≥0.8): {high_conf}/{len(confidences)}")
    
    # 7. 检查验证状态
    if 'verified' in field_counts:
        print(f"\n[7] 验证状态")
        verified = sum(1 for item in data if item.get('verified', False))
        print(f"    已验证: {verified}/{len(data)} ({verified/len(data)*100:.1f}%)")
    
    # 8. 样本展示
    print(f"\n[8] 数据样本")
    for i, item in enumerate(data[:3]):
        print(f"\n    样本 {i+1}:")
        print(f"    word: {item.get('word', 'N/A')}")
        print(f"    text: {item.get('text', 'N/A')[:60]}...")
        print(f"    source: {item.get('source', 'N/A')}")
        if 'confidence' in item:
            print(f"    confidence: {item.get('confidence')}")
    
    # 总结
    print(f"\n{'='*60}")
    print("验证结果:")
    print('='*60)
    
    if issues:
        print("❌ 问题:")
        for issue in issues:
            print(f"   - {issue}")
    
    if warnings:
        print("⚠️ 警告:")
        for warning in warnings:
            print(f"   - {warning}")
    
    if not issues and not warnings:
        print("✅ 数据质量良好，可用于训练！")
    elif not issues:
        print("✅ 数据可用，但建议关注警告项")
    else:
        print("❌ 数据存在严重问题，需要修复")
    
    return len(issues) == 0

def main():
    print("\n" + "="*60)
    print("DataGen Pro - 数据质量验证器")
    print("="*60)
    
    # 获取最新的几个文件
    files = sorted(
        [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')],
        key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)),
        reverse=True
    )[:3]
    
    if not files:
        print("没有找到数据文件！")
        return
    
    all_valid = True
    for f in files:
        filepath = os.path.join(OUTPUT_DIR, f)
        valid = validate_data_file(filepath)
        all_valid = all_valid and valid
    
    print("\n" + "="*60)
    if all_valid:
        print("🎉 所有数据文件验证通过！")
    else:
        print("⚠️ 部分数据文件存在问题")
    print("="*60)

if __name__ == '__main__':
    main()
