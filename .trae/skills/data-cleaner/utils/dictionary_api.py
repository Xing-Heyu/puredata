#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字典API处理模块

本模块负责接入外部字典API，获取字典数据并进行缓存管理。
"""

import json
import os
import time
from datetime import datetime, timedelta

# 尝试导入requests库
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class DictionaryAPI:
    """字典API处理类"""
    
    def __init__(self, cache_dir='./cache', cache_expiry=24):
        """
        初始化字典API处理类
        
        Args:
            cache_dir: 缓存目录路径
            cache_expiry: 缓存过期时间（小时）
        """
        self.cache_dir = cache_dir
        self.cache_expiry = cache_expiry
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 内置字典API配置
        self.api_configs = {
            'example': {
                'name': '示例字典',
                'base_url': 'https://api.example.com/dictionary',
                'params': {},
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
        }
    
    def add_api_config(self, name, config):
        """
        添加字典API配置
        
        Args:
            name: API配置名称
            config: API配置字典，包含name、base_url、params、headers等字段
        """
        self.api_configs[name] = config
    
    def get_dictionary_data(self, api_name, endpoint, params=None, force_refresh=False):
        """
        获取字典数据
        
        Args:
            api_name: API配置名称
            endpoint: API端点
            params: 额外参数
            force_refresh: 是否强制刷新缓存
            
        Returns:
            字典数据
        """
        if api_name not in self.api_configs:
            raise ValueError(f"未知的API配置: {api_name}")
        
        # 构建缓存键
        cache_key = f"{api_name}_{endpoint}_{self._params_to_key(params)}"
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        # 检查缓存
        if not force_refresh and self._is_cache_valid(cache_file):
            return self._load_cache(cache_file)
        
        # 检查requests库是否可用
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests库不可用，无法调用外部API。请安装requests库或使用本地字典文件。")
        
        # 构建请求URL
        config = self.api_configs[api_name]
        url = f"{config['base_url']}/{endpoint}"
        
        # 合并参数
        request_params = config.get('params', {}).copy()
        if params:
            request_params.update(params)
        
        # 发送请求
        response = requests.get(
            url,
            params=request_params,
            headers=config.get('headers', {})
        )
        
        # 检查响应
        response.raise_for_status()
        
        # 解析响应数据
        data = response.json()
        
        # 保存缓存
        self._save_cache(cache_file, data)
        
        return data
    
    def get_multiple_sources(self, sources, endpoint, params=None):
        """
        从多个数据源获取字典数据
        
        Args:
            sources: 数据源名称列表
            endpoint: API端点
            params: 额外参数
            
        Returns:
            合并后的字典数据
        """
        all_data = {}
        
        for source in sources:
            try:
                data = self.get_dictionary_data(source, endpoint, params)
                all_data[source] = data
            except Exception as e:
                print(f"从{source}获取数据失败: {str(e)}")
        
        return all_data
    
    def _params_to_key(self, params):
        """
        将参数转换为缓存键
        
        Args:
            params: 参数字典
            
        Returns:
            缓存键字符串
        """
        if not params:
            return ""
        
        sorted_items = sorted(params.items())
        return "_".join([f"{k}={v}" for k, v in sorted_items])
    
    def _is_cache_valid(self, cache_file):
        """
        检查缓存是否有效
        
        Args:
            cache_file: 缓存文件路径
            
        Returns:
            缓存是否有效
        """
        if not os.path.exists(cache_file):
            return False
        
        # 检查文件修改时间
        mtime = os.path.getmtime(cache_file)
        expiry_time = time.time() - (self.cache_expiry * 3600)
        
        return mtime > expiry_time
    
    def _load_cache(self, cache_file):
        """
        加载缓存数据
        
        Args:
            cache_file: 缓存文件路径
            
        Returns:
            缓存数据
        """
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data['data']
    
    def _save_cache(self, cache_file, data):
        """
        保存缓存数据
        
        Args:
            cache_file: 缓存文件路径
            data: 要缓存的数据
        """
        cache_data = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(hours=self.cache_expiry)).isoformat()
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)


class LocalDictionary:
    """本地字典类"""
    
    def __init__(self, dict_dir='./dictionaries'):
        """
        初始化本地字典类
        
        Args:
            dict_dir: 字典文件目录
        """
        self.dict_dir = dict_dir
        os.makedirs(dict_dir, exist_ok=True)
    
    def load_dictionary(self, dict_name):
        """
        加载本地字典
        
        Args:
            dict_name: 字典名称
            
        Returns:
            字典数据
        """
        dict_file = os.path.join(self.dict_dir, f"{dict_name}.json")
        
        if not os.path.exists(dict_file):
            raise FileNotFoundError(f"本地字典不存在: {dict_name}")
        
        with open(dict_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_dictionary(self, dict_name, data):
        """
        保存本地字典
        
        Args:
            dict_name: 字典名称
            data: 字典数据
        """
        dict_file = os.path.join(self.dict_dir, f"{dict_name}.json")
        
        with open(dict_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)