#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入处理模块

本模块负责读取不同格式的输入文件并转换为字典/字典列表。
"""

import json
import csv
import os


class InputHandler:
    """输入处理器"""
    
    def read_file(self, file_path, format):
        """
        读取文件并转换为字典/字典列表
        
        Args:
            file_path: 文件路径
            format: 文件格式 ('json', 'csv', 'txt')
            
        Returns:
            转换后的数据
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if format == 'json':
            return self._read_json(file_path)
        elif format == 'csv':
            return self._read_csv(file_path)
        elif format == 'txt':
            return self._read_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {format}")
    
    def _read_json(self, file_path):
        """
        读取JSON文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            JSON数据（字典或字典列表）
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _read_csv(self, file_path):
        """
        读取CSV文件并转换为字典列表
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            字典列表
        """
        data = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        
        return data
    
    def _read_txt(self, file_path):
        """
        读取文本文件并转换为字典列表
        
        文本文件格式要求：
        - 每行一条记录
        - 记录格式：key1=value1,key2=value2
        
        Args:
            file_path: 文本文件路径
            
        Returns:
            字典列表
        """
        data = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 解析行数据
                record = {}
                items = line.split(',')
                
                for item in items:
                    if '=' in item:
                        key, value = item.split('=', 1)
                        record[key.strip()] = value.strip()
                
                if record:
                    data.append(record)
        
        return data