#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题驱动数据生成模块

本模块支持通过指定主题，自动从字典API获取相关数据并生成训练数据。
核心功能：
1. 主题解析：理解用户输入的主题
2. 字典API调用：从外部字典获取相关数据
3. 数据生成：根据主题和字典数据生成训练数据
"""

import json
import os
from datetime import datetime

# 尝试导入requests库
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class TopicGenerator:
    """主题驱动数据生成器"""
    
    # 内置字典API配置
    DICTIONARY_APIS = {
        'free_dictionary': {
            'name': '免费字典API',
            'url': 'https://api.dictionaryapi.dev/api/v2/entries/en/{word}',
            'type': 'word_definition',
            'free': True
        },
        'baike': {
            'name': '百科API',
            'url': 'https://baike.baidu.com/api/openapi/BaikeLemmaCardApi',
            'type': 'encyclopedia',
            'free': True,
            'params': {
                'scope': '103',
                'format': 'json'
            }
        },
        'national_standard': {
            'name': '国家标准字典',
            'url': 'https://openstd.samr.gov.cn/bzgk/gb/std_list',
            'type': 'standard',
            'free': True
        }
    }
    
    # 内置主题关键词映射
    TOPIC_KEYWORDS = {
        '人工智能': ['AI', '机器学习', '深度学习', '神经网络', '自然语言处理', '计算机视觉'],
        '医疗': ['疾病', '症状', '治疗', '药物', '诊断', '手术', '医学'],
        '金融': ['股票', '债券', '基金', '投资', '理财', '银行', '金融'],
        '教育': ['课程', '学习', '考试', '教育', '培训', '学校'],
        '法律': ['法律', '法规', '合同', '诉讼', '律师', '法院'],
        '科技': ['人工智能', '机器学习', '大数据', '云计算', '区块链', '物联网'],
        '电商': ['商品', '订单', '支付', '物流', '库存', '促销'],
        '通用': ['基础', '常见', '通用', '标准']
    }
    
    def __init__(self, cache_dir=None):
        """
        初始化主题驱动数据生成器
        
        Args:
            cache_dir: 缓存目录
        """
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
        
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def generate_by_topic(self, topic, count=10, output_format='json', custom_keywords=None):
        """
        根据主题生成数据
        
        Args:
            topic: 主题名称
            count: 生成数量
            output_format: 输出格式
            custom_keywords: 自定义关键词列表
            
        Returns:
            生成的数据列表
        """
        # 获取主题相关关键词
        keywords = self._get_topic_keywords(topic, custom_keywords)
        
        # 从字典API获取数据
        dict_data = self._fetch_dictionary_data(topic, keywords)
        
        # 生成数据
        data = self._generate_data(topic, dict_data, keywords, count)
        
        return data
    
    def _get_topic_keywords(self, topic, custom_keywords=None):
        """
        获取主题关键词
        
        Args:
            topic: 主题名称
            custom_keywords: 自定义关键词
            
        Returns:
            关键词列表
        """
        if custom_keywords:
            return custom_keywords
        
        # 查找内置关键词
        for key, keywords in self.TOPIC_KEYWORDS.items():
            if key in topic or topic in key:
                return keywords
        
        # 如果没有找到，使用主题本身作为关键词
        return [topic]
    
    def _fetch_dictionary_data(self, topic, keywords):
        """
        从字典API获取数据
        
        Args:
            topic: 主题名称
            keywords: 关键词列表
            
        Returns:
            字典数据
        """
        dict_data = []
        
        if not REQUESTS_AVAILABLE:
            # 如果requests库不可用，使用内置示例数据
            return self._generate_sample_dict_data(topic, keywords)
        
        # 尝试从各个字典API获取数据
        for api_name, api_config in self.DICTIONARY_APIS.items():
            if not api_config.get('free', False):
                continue
            
            try:
                for keyword in keywords[:3]:  # 限制关键词数量
                    data = self._call_dictionary_api(api_config, keyword)
                    if data:
                        dict_data.extend(data)
            except Exception as e:
                print(f"从{api_name}获取数据失败: {str(e)}")
                continue
        
        # 如果没有获取到数据，使用示例数据
        if not dict_data:
            dict_data = self._generate_sample_dict_data(topic, keywords)
        
        return dict_data
    
    def _call_dictionary_api(self, api_config, keyword):
        """
        调用字典API
        
        Args:
            api_config: API配置
            keyword: 关键词
            
        Returns:
            API返回的数据
        """
        url = api_config['url']
        
        if '{word}' in url:
            url = url.replace('{word}', keyword)
        
        params = api_config.get('params', {})
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 解析不同API的返回格式
            if api_config['type'] == 'word_definition':
                return self._parse_word_definition(data, keyword)
            elif api_config['type'] == 'encyclopedia':
                return self._parse_encyclopedia(data, keyword)
            else:
                return [{'term': keyword, 'definition': str(data), 'category': 'API数据'}]
                
        except Exception as e:
            return None
    
    def _parse_word_definition(self, data, keyword):
        """解析单词定义API返回数据"""
        results = []
        
        if isinstance(data, list):
            for entry in data:
                if 'meanings' in entry:
                    for meaning in entry['meanings']:
                        for definition in meaning.get('definitions', []):
                            results.append({
                                'term': keyword,
                                'definition': definition.get('definition', ''),
                                'category': meaning.get('partOfSpeech', ''),
                                'source': 'dictionary_api'
                            })
        
        return results
    
    def _parse_encyclopedia(self, data, keyword):
        """解析百科API返回数据"""
        results = []
        
        if isinstance(data, dict):
            if 'abstract' in data:
                results.append({
                    'term': keyword,
                    'definition': data.get('abstract', ''),
                    'category': data.get('category', '百科'),
                    'source': 'baike_api'
                })
        
        return results
    
    def _generate_sample_dict_data(self, topic, keywords):
        """
        生成示例字典数据
        
        Args:
            topic: 主题名称
            keywords: 关键词列表
            
        Returns:
            示例字典数据
        """
        sample_data = []
        
        for keyword in keywords:
            sample_data.append({
                'term': keyword,
                'definition': f'{keyword}是{topic}领域的重要概念，具有广泛的应用价值。',
                'category': topic,
                'source': 'sample'
            })
        
        return sample_data
    
    def _generate_data(self, topic, dict_data, keywords, count):
        """
        生成最终数据
        
        Args:
            topic: 主题名称
            dict_data: 字典数据
            keywords: 关键词列表
            count: 生成数量
            
        Returns:
            生成的数据列表
        """
        data = []
        now = datetime.now().isoformat()
        
        for i in range(count):
            # 选择字典数据项
            item = dict_data[i % len(dict_data)] if dict_data else {}
            
            # 生成数据项
            data_item = {
                'id': str(i),
                'term': item.get('term', keywords[i % len(keywords)]),
                'definition': item.get('definition', f'{keywords[i % len(keywords)]}相关内容'),
                'category': item.get('category', topic),
                'domain': topic,
                'source': item.get('source', 'generated'),
                'generated_at': now
            }
            
            data.append(data_item)
        
        return data
    
    def list_available_apis(self):
        """
        列出可用的字典API
        
        Returns:
            可用API列表
        """
        apis = []
        for api_name, api_config in self.DICTIONARY_APIS.items():
            apis.append({
                'name': api_name,
                'description': api_config['name'],
                'type': api_config['type'],
                'free': api_config.get('free', False)
            })
        return apis
    
    def add_custom_api(self, name, url, api_type='general', params=None, free=True):
        """
        添加自定义字典API
        
        Args:
            name: API名称
            url: API URL
            api_type: API类型
            params: 额外参数
            free: 是否免费
        """
        self.DICTIONARY_APIS[name] = {
            'name': name,
            'url': url,
            'type': api_type,
            'params': params or {},
            'free': free
        }
    
    def add_topic_keywords(self, topic, keywords):
        """
        添加主题关键词映射
        
        Args:
            topic: 主题名称
            keywords: 关键词列表
        """
        self.TOPIC_KEYWORDS[topic] = keywords