#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
垂直领域训练数据生成系统 v5.0
A块：输入层优化 | B块：模板层优化 | C块：输出层优化 | 毒性检测
"""

import json
import os
import sys
import sqlite3
import hashlib
import random
import urllib.request
import urllib.parse
import time
import re
from datetime import datetime, timedelta

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ============ A块：输入层优化 ============

INPUT_SOURCES = {
    "api": {
        "name": "API查询",
        "enabled": True,
        "priority": 1
    },
    "web_scraping": {
        "name": "网页爬取",
        "enabled": True,
        "priority": 2
    },
    "document": {
        "name": "文档上传",
        "enabled": False,
        "priority": 3
    }
}

def batch_query(subtypes, domain, source="api"):
    """
    批量查询多个子类型
    返回: {
        "domain": "领域名称",
        "subtypes": [
            {"name": "子类型1", "structure": {...}},
            {"name": "子类型2", "structure": {...}}
        ],
        "source": "API/爬虫/文档",
        "fetched_at": "时间戳"
    }
    """
    results = {
        "domain": domain,
        "subtypes": [],
        "source": source,
        "fetched_at": datetime.now().isoformat()
    }
    
    for subtype in subtypes:
        if source == "api":
            # 调用API查询
            structure = query_api_structure(subtype, domain)
        elif source == "web_scraping":
            # 网页爬取
            structure = scrape_web_structure(subtype, domain)
        else:
            # 文档上传（暂不实现）
            structure = {}
        
        results["subtypes"].append({
            "name": subtype,
            "structure": structure
        })
    
    return results

def query_api_structure(subtype, domain):
    """API查询结构"""
    return {
        "fields": ["field1", "field2", "field3"],
        "values": ["value1", "value2"],
        "metadata": {"source": "api"}
    }

def scrape_web_structure(subtype, domain):
    """网页爬取结构"""
    return {
        "fields": ["field1", "field2"],
        "values": ["value1"],
        "metadata": {"source": "web_scraping"}
    }

# ============ B块：模板层优化 ============

TEMPLATE_VERSIONS = []

def load_templates(template_file="templates.json"):
    """加载模板库"""
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": "1.0.0",
        "core": [],
        "extended": {},
        "custom": []
    }

def save_templates(templates, template_file="templates.json"):
    """保存模板库"""
    templates["last_modified"] = datetime.now().isoformat()
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)
    
    # 记录版本
    TEMPLATE_VERSIONS.append({
        "version": templates["version"],
        "reason": "自动保存",
        "timestamp": datetime.now().isoformat()
    })

def get_template(subtype, templates):
    """动态组装最匹配的模板"""
    # 优先使用扩展模板
    if subtype in templates.get("extended", {}):
        return templates["extended"][subtype]
    
    # 其次使用核心模板
    return templates["core"][0] if templates["core"] else {}

def generate_from_template(template, data):
    """根据模板和数据生成内容"""
    result = {}
    for field in template.get("fields", []):
        field_name = field["name"]
        field_type = field["type"]
        
        if field_type == "text":
            result[field_name] = data.get(field_name, "")
        elif field_type == "number":
            result[field_name] = data.get(field_name, 0)
        elif field_type == "date":
            result[field_name] = data.get(field_name, datetime.now().strftime("%Y-%m-%d"))
        elif field_type == "select":
            options = field.get("options", [])
            result[field_name] = data.get(field_name, options[0] if options else "")
    
    return result

# ============ C块：输出层优化 ============

OUTPUT_FORMATS = {
    "json": {"extension": ".json", "content_type": "application/json"},
    "csv": {"extension": ".csv", "content_type": "text/csv"},
    "xml": {"extension": ".xml", "content_type": "application/xml"},
    "txt": {"extension": ".txt", "content_type": "text/plain"}
}

def validate_output(data, format_type="json"):
    """输出前自动校验"""
    errors = []
    
    # 字段完整性检查
    required_fields = ["id", "text", "category", "source"]
    for item in data:
        for field in required_fields:
            if field not in item:
                errors.append(f"缺失字段: {field}")
    
    # 格式合规检查
    if format_type == "json":
        try:
            json.dumps(data)
        except:
            errors.append("JSON格式错误")
    
    # 明显错误检测
    for item in data:
        text = item.get("text", "")
        # 检测金额字段含字母
        if re.search(r'[a-zA-Z]', str(item.get("amount", ""))):
            errors.append(f"金额字段包含字母: {item.get('id')}")
    
    return errors

def format_output(data, format_type="json", metadata=None):
    """格式化输出"""
    # 校验
    errors = validate_output(data, format_type)
    if errors:
        return {"status": "error", "errors": errors, "data": None}
    
    # 添加元数据
    output = {
        "status": "success",
        "data": data,
        "metadata": metadata or {
            "generated_at": datetime.now().isoformat(),
            "format": format_type,
            "count": len(data)
        }
    }
    
    # 格式转换
    if format_type == "json":
        output["content"] = json.dumps(output, ensure_ascii=False, indent=2)
    elif format_type == "csv":
        output["content"] = convert_to_csv(data)
    elif format_type == "xml":
        output["content"] = convert_to_xml(output)
    elif format_type == "txt":
        output["content"] = convert_to_txt(data)
    
    return output

def convert_to_csv(data):
    """转换为CSV"""
    if not data:
        return ""
    headers = list(data[0].keys())
    lines = [",".join(headers)]
    for item in data:
        lines.append(",".join([str(item.get(h, "")) for h in headers]))
    return "\n".join(lines)

def convert_to_xml(data):
    """转换为XML"""
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<root>\n'
    for item in data:
        xml += '  <item>\n'
        for k, v in item.items():
            xml += f'    <{k}>{v}</{k}>\n'
        xml += '  </item>\n'
    xml += '</root>'
    return xml

def convert_to_txt(data):
    """转换为纯文本"""
    lines = []
    for item in data:
        lines.append(f"[{item.get('id')}] {item.get('text')}")
    return "\n".join(lines)

# ============ 毒性检测 ============

TOXICITY_CHECKLIST = {
    "discriminatory": [
        "只招男性", "只招女性", "不招外地人", "本地人优先",
        "限民族", "限户籍", "年龄歧视", "性别歧视"
    ],
    "illegal": [
        "试用期1年", "无薪试用", "不签合同", "违法条款",
        "强制加班", "无补偿加班", "不交社保"
    ],
    "extreme_bias": [
        "外地人不租", "本地人专享", "特定群体优惠",
        "歧视性条款", "不公平待遇"
    ]
}

def check_toxicity(text, checklist=TOXICITY_CHECKLIST):
    """检测文本毒性"""
    toxic_found = []
    
    for category, patterns in checklist.items():
        for pattern in patterns:
            if pattern in text:
                toxic_found.append({
                    "category": category,
                    "pattern": pattern,
                    "text": text
                })
    
    return toxic_found

def filter_toxic_data(data, checklist=TOXICITY_CHECKLIST):
    """过滤有毒数据"""
    clean_data = []
    toxic_count = 0
    
    for item in data:
        text = item.get("text", "")
        toxic_items = check_toxicity(text, checklist)
        
        if toxic_items:
            toxic_count += 1
            item["toxic"] = True
            item["toxic_details"] = toxic_items
        else:
            item["toxic"] = False
            clean_data.append(item)
    
    return clean_data, toxic_count

# ============ 主程序 ============

def main():
    print(f'\n{"="*60}')
    print(f'垂直领域训练数据生成系统 v5.0')
    print(f'A块：输入层 | B块：模板层 | C块：输出层 | 毒性检测')
    print(f'时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'{"="*60}\n')
    
    # 示例：批量查询
    print('[示例] A块：批量查询')
    subtypes = ["劳动合同", "租房合同", "合伙协议"]
    result = batch_query(subtypes, "法律")
    print(f'  查询结果: {len(result["subtypes"])} 个子类型\n')
    
    # 示例：模板加载
    print('[示例] B块：模板管理')
    templates = load_templates()
    print(f'  模板版本: {templates["version"]}')
    print(f'  核心模板: {len(templates.get("core", []))} 个')
    print(f'  扩展模板: {len(templates.get("extended", {}))} 个\n')
    
    # 示例：毒性检测
    print('[示例] 毒性检测')
    test_texts = [
        "只招男性，不招女性",
        "试用期1年，无薪试用",
        "公平招聘，不限性别"
    ]
    for text in test_texts:
        toxic = check_toxicity(text)
        status = "❌ 有毒" if toxic else "✅ 无毒"
        print(f'  "{text}" - {status}')
    
    print(f'\n{"="*60}')
    print(f'v5.0 功能模块已就绪')
    print(f'{"="*60}\n')

if __name__ == '__main__':
    main()