#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据生成模块

本模块负责根据领域配置生成垂直领域数据，支持多种输出格式：
- JSON: 标准JSON格式，适合API传输和存储
- JSONL: JSON Lines格式，适合流式处理和大数据场景
- CSV: 表格格式，适合Excel和数据分析工具
- TXT: 文本格式，适合自然语言处理
- DICT: Python字典格式，适合程序内部使用
"""

import json
import os
from datetime import datetime
import hashlib


class DataGenerator:
    """数据生成器"""
    
    SUPPORTED_FORMATS = ['json', 'jsonl', 'csv', 'txt', 'dict']
    
    def __init__(self):
        """初始化数据生成器"""
        pass
    
    def generate(self, domain_config, count=10, source_data=None):
        """
        生成垂直领域数据
        
        Args:
            domain_config: 领域配置
            count: 生成数量
            source_data: 源数据（可选）
            
        Returns:
            生成的数据列表
        """
        template = domain_config.get('template', self._get_default_template())
        domain_name = domain_config.get('name', 'unknown')
        keywords = domain_config.get('keywords', [])
        
        generated_data = []
        
        # 如果有源数据，使用源数据
        if source_data:
            items = self._extract_items(source_data)
        else:
            # 否则根据关键词生成示例数据
            items = self._generate_sample_items(keywords, domain_name)
        
        # 生成数据
        for i in range(count):
            item = items[i % len(items)] if items else {}
            data_item = self._apply_template(item, template, i, domain_name)
            generated_data.append(data_item)
        
        return generated_data
    
    def _get_default_template(self):
        """获取默认模板"""
        return {
            'id': '{{id}}',
            'term': '{{term}}',
            'definition': '{{definition}}',
            'category': '{{category}}',
            'domain': '{{domain}}',
            'generated_at': '{{generated_at}}'
        }
    
    def _generate_sample_items(self, keywords, domain_name):
        """
        根据关键词生成示例数据项
        
        Args:
            keywords: 关键词列表
            domain_name: 领域名称
            
        Returns:
            示例数据项列表
        """
        items = []
        
        if not keywords:
            keywords = ['示例']
        
        for i, keyword in enumerate(keywords):
            items.append({
                'term': keyword,
                'definition': f'{keyword}是{domain_name}领域的重要概念，指代相关的内容和应用。',
                'category': domain_name
            })
        
        # 如果关键词数量少于5个，扩展示例数据
        while len(items) < 5:
            idx = len(items)
            keyword = keywords[idx % len(keywords)]
            items.append({
                'term': f'{keyword}相关概念{idx}',
                'definition': f'与{keyword}相关的概念和应用，在{domain_name}领域具有重要意义。',
                'category': domain_name
            })
        
        return items
    
    def _extract_items(self, source_data):
        """
        从源数据中提取数据项
        
        Args:
            source_data: 源数据
            
        Returns:
            数据项列表
        """
        items = []
        
        if isinstance(source_data, list):
            items.extend([item for item in source_data if isinstance(item, dict)])
        elif isinstance(source_data, dict):
            # 处理嵌套字典
            for key, value in source_data.items():
                if isinstance(value, list):
                    items.extend([item for item in value if isinstance(item, dict)])
                elif isinstance(value, dict):
                    items.append(value)
        
        return items if items else [{}]
    
    def _apply_template(self, item, template, index, domain_name):
        """
        应用模板生成单个数据项
        
        Args:
            item: 源数据项
            template: 模板
            index: 索引
            domain_name: 领域名称
            
        Returns:
            生成的数据项
        """
        generated_item = {}
        now = datetime.now().isoformat()
        
        for key, value_template in template.items():
            value = value_template
            
            # 替换内置变量
            value = value.replace('{{id}}', str(index))
            value = value.replace('{{domain}}', domain_name)
            value = value.replace('{{generated_at}}', now)
            
            # 替换源数据项中的值
            for item_key, item_value in item.items():
                placeholder = f'{{{{{item_key}}}}}'
                if placeholder in value:
                    value = value.replace(placeholder, str(item_value))
            
            generated_item[key] = value
        
        return generated_item
    
    def format_output(self, data, output_format='json'):
        """
        格式化输出数据
        
        Args:
            data: 数据列表
            output_format: 输出格式 (json, jsonl, csv, txt, dict)
            
        Returns:
            格式化后的数据
        """
        if output_format == 'json':
            return self._format_json(data)
        elif output_format == 'jsonl':
            return self._format_jsonl(data)
        elif output_format == 'csv':
            return self._format_csv(data)
        elif output_format == 'txt':
            return self._format_txt(data)
        elif output_format == 'dict':
            return data
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
    
    def _format_json(self, data):
        """格式化为JSON"""
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _format_jsonl(self, data):
        """格式化为JSONL"""
        lines = [json.dumps(item, ensure_ascii=False) for item in data]
        return '\n'.join(lines)
    
    def _format_csv(self, data):
        """格式化为CSV"""
        if not data:
            return ''
        
        # 获取所有字段
        fields = set()
        for item in data:
            fields.update(item.keys())
        fields = sorted(fields)
        
        # 构建CSV内容
        lines = [','.join(fields)]
        for item in data:
            values = [str(item.get(field, '')).replace(',', '，') for field in fields]
            lines.append(','.join(values))
        
        return '\n'.join(lines)
    
    def _format_txt(self, data):
        """格式化为文本"""
        lines = []
        for item in data:
            parts = [f'{key}={value}' for key, value in item.items()]
            lines.append(','.join(parts))
        return '\n'.join(lines)
    
    def save_to_file(self, data, file_path, output_format='json'):
        """
        保存数据到文件
        
        Args:
            data: 数据列表
            file_path: 文件路径
            output_format: 输出格式
        """
        # 确保目录存在
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 格式化数据
        formatted_data = self.format_output(data, output_format)
        
        # 写入文件
        mode = 'w' if output_format in ['json', 'jsonl', 'csv', 'txt'] else 'wb'
        with open(file_path, mode, encoding='utf-8') as f:
            if output_format == 'dict':
                import pickle
                pickle.dump(formatted_data, f)
            else:
                f.write(formatted_data)
    
    def get_format_description(self):
        """
        获取支持的格式描述
        
        Returns:
            格式描述字典
        """
        return {
            'json': {
                'name': 'JSON',
                'description': '标准JSON格式，适合API传输和存储',
                'extension': '.json',
                'use_case': 'Web应用、API接口、数据存储'
            },
            'jsonl': {
                'name': 'JSON Lines',
                'description': 'JSON Lines格式，每行一个JSON对象',
                'extension': '.jsonl',
                'use_case': '大数据处理、流式处理、日志分析'
            },
            'csv': {
                'name': 'CSV',
                'description': '逗号分隔值格式，适合表格数据',
                'extension': '.csv',
                'use_case': 'Excel导入、数据分析、数据库导入'
            },
            'txt': {
                'name': '文本',
                'description': '纯文本格式，每行一条记录',
                'extension': '.txt',
                'use_case': '自然语言处理、简单数据交换'
            },
            'dict': {
                'name': 'Python字典',
                'description': 'Python字典对象，适合程序内部使用',
                'extension': '.pkl',
                'use_case': 'Python程序、机器学习训练'
            }
        }