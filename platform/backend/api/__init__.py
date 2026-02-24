#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API层入口
"""

__all__ = ['llm']

def __getattr__(name):
    if name == 'llm':
        from . import llm as llm_module
        return llm_module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
