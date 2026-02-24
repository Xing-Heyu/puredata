#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'simple_main.py')

try:
    with open(file_path, encoding='utf-8') as f:
        ast.parse(f.read())
    print('Syntax OK')
except FileNotFoundError:
    print(f'文件不存在: {file_path}')
except SyntaxError as e:
    print(f'语法错误: {e}')
