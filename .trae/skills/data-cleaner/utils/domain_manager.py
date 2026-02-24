#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
垂直领域管理模块

本模块负责管理垂直领域配置，支持多种数据格式的输出。
"""

import json
import os


class DomainManager:
    """垂直领域管理类"""
    
    def __init__(self, domains_dir=None):
        """
        初始化垂直领域管理类
        
        Args:
            domains_dir: 领域配置文件目录
        """
        if domains_dir is None:
            domains_dir = os.path.join(os.path.dirname(__file__), '..', 'domains')
        
        self.domains_dir = domains_dir
        os.makedirs(domains_dir, exist_ok=True)
        
        # 内置领域配置
        self.domain_configs = {
            'medical': {
                'name': '医疗',
                'description': '医疗健康领域数据',
                'keywords': ['疾病', '症状', '治疗', '药物', '诊断', '手术'],
                'output_format': 'json',
                'template': {
                    'id': '{{id}}',
                    'term': '{{term}}',
                    'definition': '{{definition}}',
                    'category': '{{category}}',
                    'domain': '医疗'
                }
            },
            'finance': {
                'name': '金融',
                'description': '金融投资领域数据',
                'keywords': ['股票', '债券', '基金', '投资', '理财', '银行'],
                'output_format': 'json',
                'template': {
                    'id': '{{id}}',
                    'term': '{{term}}',
                    'definition': '{{definition}}',
                    'category': '{{category}}',
                    'domain': '金融'
                }
            },
            'education': {
                'name': '教育',
                'description': '教育培训领域数据',
                'keywords': ['课程', '学习', '考试', '教育', '培训', '学校'],
                'output_format': 'json',
                'template': {
                    'id': '{{id}}',
                    'term': '{{term}}',
                    'definition': '{{definition}}',
                    'category': '{{category}}',
                    'domain': '教育'
                }
            },
            'legal': {
                'name': '法律',
                'description': '法律法务领域数据',
                'keywords': ['法律', '法规', '合同', '诉讼', '律师', '法院'],
                'output_format': 'json',
                'template': {
                    'id': '{{id}}',
                    'term': '{{term}}',
                    'definition': '{{definition}}',
                    'category': '{{category}}',
                    'domain': '法律'
                }
            },
            'tech': {
                'name': '科技',
                'description': '科技互联网领域数据',
                'keywords': ['人工智能', '机器学习', '大数据', '云计算', '区块链', '物联网'],
                'output_format': 'json',
                'template': {
                    'id': '{{id}}',
                    'term': '{{term}}',
                    'definition': '{{definition}}',
                    'category': '{{category}}',
                    'domain': '科技'
                }
            }
        }
        
        # 加载用户自定义领域配置
        self._load_custom_domains()
    
    def _load_custom_domains(self):
        """加载用户自定义领域配置"""
        if not os.path.exists(self.domains_dir):
            return
        
        for file in os.listdir(self.domains_dir):
            if file.endswith('.json'):
                domain_name = file.replace('.json', '')
                config_file = os.path.join(self.domains_dir, file)
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    self.domain_configs[domain_name] = config
                except Exception as e:
                    print(f"加载领域配置失败 {file}: {str(e)}")
    
    def get_domain(self, domain_name):
        """
        获取领域配置
        
        Args:
            domain_name: 领域名称
            
        Returns:
            领域配置字典
        """
        if domain_name not in self.domain_configs:
            raise ValueError(f"未知领域: {domain_name}")
        return self.domain_configs[domain_name]
    
    def add_domain(self, domain_name, config):
        """
        添加自定义领域配置
        
        Args:
            domain_name: 领域名称
            config: 领域配置字典
        """
        self.domain_configs[domain_name] = config
        
        # 保存到文件
        config_file = os.path.join(self.domains_dir, f"{domain_name}.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def list_domains(self):
        """
        列出所有可用领域
        
        Returns:
            领域名称列表
        """
        return list(self.domain_configs.keys())
    
    def get_domain_info(self, domain_name):
        """
        获取领域详细信息
        
        Args:
            domain_name: 领域名称
            
        Returns:
            领域信息字典
        """
        config = self.get_domain(domain_name)
        return {
            'name': config.get('name', domain_name),
            'description': config.get('description', ''),
            'keywords': config.get('keywords', []),
            'output_format': config.get('output_format', 'json')
        }
    
    def create_custom_domain(self, name, description, keywords, template=None):
        """
        创建自定义领域
        
        Args:
            name: 领域名称
            description: 领域描述
            keywords: 关键词列表
            template: 输出模板
            
        Returns:
            领域配置
        """
        domain_name = name.lower().replace(' ', '_')
        
        config = {
            'name': name,
            'description': description,
            'keywords': keywords,
            'output_format': 'json',
            'template': template or {
                'id': '{{id}}',
                'term': '{{term}}',
                'definition': '{{definition}}',
                'category': '{{category}}',
                'domain': name
            }
        }
        
        self.add_domain(domain_name, config)
        return config