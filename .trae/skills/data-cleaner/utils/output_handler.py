#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出处理模块

本模块负责将清洗后的数据写入到不同格式的文件中。
"""

import json
import csv
import os


class OutputHandler:
    """输出处理器"""
    
    def write_file(self, data, file_path, format):
        """
        将数据写入文件
        
        Args:
            data: 要写入的数据（字典或字典列表）
            file_path: 文件路径
            format: 文件格式 ('json', 'csv', 'txt')
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if format == 'json':
            self._write_json(data, file_path)
        elif format == 'csv':
            self._write_csv(data, file_path)
        elif format == 'txt':
            self._write_txt(data, file_path)
        else:
            raise ValueError(f"不支持的文件格式: {format}")
    
    def _write_json(self, data, file_path):
        """
        将数据写入JSON文件
        
        Args:
            data: 要写入的数据
            file_path: JSON文件路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _write_csv(self, data, file_path):
        """
        将数据写入CSV文件
        
        Args:
            data: 要写入的数据（字典列表）
            file_path: CSV文件路径
        """
        if not isinstance(data, list):
            data = [data] if isinstance(data, dict) else []
        
        if not data:
            return
        
        # 获取所有字段名
        fieldnames = set()
        for item in data:
            if isinstance(item, dict):
                fieldnames.update(item.keys())
        fieldnames = sorted(fieldnames)
        
        # 写入CSV文件
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                if isinstance(item, dict):
                    writer.writerow(item)
    
    def _write_txt(self, data, file_path):
        """
        将数据写入文本文件
        
        Args:
            data: 要写入的数据（字典列表）
            file_path: 文本文件路径
        """
        if not isinstance(data, list):
            data = [data] if isinstance(data, dict) else []
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                if isinstance(item, dict):
                    items = []
                    for key, value in item.items():
                        items.append(f"{key}={value}")
                    line = ','.join(items)
                    f.write(line + '\n')