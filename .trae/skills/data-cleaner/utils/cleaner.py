#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗核心模块

本模块实现了以字典/字典列表为载体的数据清洗功能，包括去重、去空格、空值处理、日期标准化等。
"""

from datetime import datetime
import hashlib


class DataCleaner:
    """数据清洗器"""
    
    def __init__(self, remove_duplicates=False, trim_spaces=False, 
                 handle_null=False, normalize_dates=False, fields=None):
        """
        初始化数据清洗器
        
        Args:
            remove_duplicates: 是否移除重复项
            trim_spaces: 是否去除空格
            handle_null: 是否处理空值
            normalize_dates: 是否标准化日期格式
            fields: 需要保留的字段列表
        """
        self.remove_duplicates = remove_duplicates
        self.trim_spaces = trim_spaces
        self.handle_null = handle_null
        self.normalize_dates = normalize_dates
        self.fields = fields
    
    def clean(self, data):
        """
        执行数据清洗
        
        Args:
            data: 输入数据，字典或字典列表
            
        Returns:
            清洗后的数据
        """
        if isinstance(data, list):
            # 处理字典列表
            cleaned_items = []
            seen_hashes = set()
            
            for item in data:
                if isinstance(item, dict):
                    # 清洗单个字典
                    cleaned_item = self._clean_dict(item)
                    
                    # 处理去重
                    if self.remove_duplicates:
                        item_hash = self._get_dict_hash(cleaned_item)
                        if item_hash not in seen_hashes:
                            seen_hashes.add(item_hash)
                            cleaned_items.append(cleaned_item)
                    else:
                        cleaned_items.append(cleaned_item)
            
            return cleaned_items
        elif isinstance(data, dict):
            # 处理单个字典
            return self._clean_dict(data)
        else:
            # 不支持的数据类型
            raise ValueError(f"不支持的数据类型: {type(data).__name__}")
    
    def _clean_dict(self, item):
        """
        清洗单个字典
        
        Args:
            item: 输入字典
            
        Returns:
            清洗后的字典
        """
        cleaned_item = {}
        
        # 遍历字典键值对
        for key, value in item.items():
            # 检查是否需要保留该字段
            if self.fields and key not in self.fields:
                continue
            
            # 处理值
            cleaned_value = value
            
            # 去除空格
            if self.trim_spaces and isinstance(value, str):
                cleaned_value = value.strip()
            
            # 处理空值
            if self.handle_null:
                if cleaned_value is None or (isinstance(cleaned_value, str) and cleaned_value == ''):
                    cleaned_value = ''
            
            # 标准化日期
            if self.normalize_dates and isinstance(cleaned_value, str):
                cleaned_value = self._normalize_date(cleaned_value)
            
            # 添加到结果字典
            cleaned_item[key] = cleaned_value
        
        # 添加处理时间
        cleaned_item['processed_at'] = datetime.now().isoformat()
        
        return cleaned_item
    
    def _normalize_date(self, date_str):
        """
        标准化日期格式
        
        Args:
            date_str: 日期字符串
            
        Returns:
            标准化后的日期字符串 (ISO 8601格式)
        """
        # 常见日期格式列表
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y年%m月%d日',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%d-%m-%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.isoformat()
            except ValueError:
                continue
        
        # 如果无法解析，返回原始字符串
        return date_str
    
    def _get_dict_hash(self, item):
        """
        获取字典的哈希值，用于去重
        
        Args:
            item: 字典
            
        Returns:
            字典的哈希值
        """
        # 排除processed_at字段，因为它每次都会变化
        filtered_item = {k: v for k, v in item.items() if k != 'processed_at'}
        # 将字典转换为有序元组
        sorted_items = tuple(sorted(filtered_item.items()))
        # 计算哈希值
        return hashlib.md5(str(sorted_items).encode('utf-8')).hexdigest()