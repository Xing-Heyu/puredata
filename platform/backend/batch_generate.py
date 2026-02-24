#!/usr/bin/env python3
"""批量生成高质量数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import time
from datetime import datetime
import uuid

print("="*60)
print("批量生成高质量数据")
print("="*60)

from high_quality_generator import HighQualityGenerator, KnowledgeBase

gen = HighQualityGenerator()
KNOWLEDGE = KnowledgeBase.KNOWLEDGE

# 生成配置
domains = ["劳动合同", "人工智能", "医疗", "金融"]
counts = {
    "劳动合同": 500,
    "人工智能": 500,
    "医疗": 500,
    "金融": 500
}

total_generated = 0
all_data = []

for domain in domains:
    count = counts[domain]
    print(f"\n[{domain}] 生成 {count} 条数据...")
    
    try:
        # 获取关键词列表
        keywords = list(KNOWLEDGE.get(domain, {}).keys())
        if len(keywords) < count:
            # 扩展关键词
            keywords = keywords * (count // len(keywords) + 1)
        keywords = keywords[:count]
        
        data = gen.generate_batch(keywords, domain)
        
        for item in data:
            if item.quality_score >= 0.85:
                quality_tier = "high"
            elif item.quality_score >= 0.75:
                quality_tier = "medium"
            else:
                quality_tier = "low"
            
            item_dict = {
                "id": item.id,
                "word": item.word,
                "text": item.text,
                "category": item.category,
                "source": item.source,
                "quality_score": item.quality_score,
                "quality_tier": quality_tier,
                "timestamp": datetime.now().isoformat(),
                "verified": item.quality_score >= 0.80,
                "provenance": {
                    "platform": "PureData",
                    "version": "2.0.0",
                    "generated_at": datetime.now().isoformat(),
                    "license": "PureData-Commercial-1.0",
                    "license_url": "https://puredata.ai/license/commercial",
                    "compliance": ["数据安全法", "个人信息保护法", "著作权法"]
                }
            }
            all_data.append(item_dict)
        
        total_generated += len(data)
        print(f"  完成: {len(data)} 条")
        
    except Exception as e:
        import traceback
        print(f"  错误: {e}")
        traceback.print_exc()

# 保存到文件
output_file = f"outputs/batch_{total_generated}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
os.makedirs("outputs", exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"总计生成: {total_generated} 条")
print(f"保存到: {output_file}")
print(f"{'='*60}")
