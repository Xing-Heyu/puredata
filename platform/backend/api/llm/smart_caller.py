#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API层 - 智能调用器
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from smart_api_caller import SmartAPICaller
    __all__ = ['SmartAPICaller']
except ImportError:
    class SmartAPICaller:
        """智能API调用器 - 占位实现"""
        def __init__(self):
            pass
        def call(self, prompt, **kwargs):
            return {"text": prompt, "status": "fallback"}
    
    __all__ = ['SmartAPICaller']
