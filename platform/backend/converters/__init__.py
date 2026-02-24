#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换层 - 懒加载入口
格式转换：AI训练格式、质量控制、模板填充等

使用方式：
    from converters import AIFormatConverter, QualityController
"""

__all__ = [
    'AIFormatConverter', 'AITrainingFormatConverter',
    'QualityController', 'TemplateFiller',
]

_lazy_modules = {
    'AIFormatConverter': ('.ai_format', 'AIFormatConverter'),
    'AITrainingFormatConverter': ('.ai_format', 'AITrainingFormatConverter'),
    'QualityController': ('.quality_controller', 'QualityController'),
    'TemplateFiller': ('.template_filler', 'TemplateFiller'),
}

def __getattr__(name):
    if name in _lazy_modules:
        module_path, class_name = _lazy_modules[name]
        import importlib
        module = importlib.import_module(module_path, package='converters')
        return getattr(module, class_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
