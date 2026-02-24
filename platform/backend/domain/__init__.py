#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域层 - 懒加载入口
垂直领域专精：人工智能、医疗、金融、劳动合同

使用方式：
    from domain import MedicalSpecialist, FinanceSpecialist
    from domain import get_specialist
"""

__all__ = [
    'DomainSpecialist',
    'AISpecialist', 'MedicalSpecialist', 'FinanceSpecialist', 'LaborSpecialist',
    'get_specialist', 'list_domains',
]

_lazy_modules = {
    'DomainSpecialist': ('.base', 'DomainSpecialist'),
    'AISpecialist': ('.ai', 'AISpecialist'),
    'MedicalSpecialist': ('.medical', 'MedicalSpecialist'),
    'FinanceSpecialist': ('.finance', 'FinanceSpecialist'),
    'LaborSpecialist': ('.labor', 'LaborSpecialist'),
}

def __getattr__(name):
    """懒加载领域模块"""
    if name in _lazy_modules:
        module_path, class_name = _lazy_modules[name]
        import importlib
        module = importlib.import_module(module_path, package='domain')
        return getattr(module, class_name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def get_specialist(domain: str):
    """获取领域专精器"""
    specialists = {
        "人工智能": ".ai",
        "医疗": ".medical",
        "金融": ".finance",
        "劳动合同": ".labor",
    }
    
    if domain in specialists:
        import importlib
        module = importlib.import_module(specialists[domain], package='domain')
        specialist_class = {
            "人工智能": "AISpecialist",
            "医疗": "MedicalSpecialist",
            "金融": "FinanceSpecialist",
            "劳动合同": "LaborSpecialist",
        }
        return getattr(module, specialist_class[domain])()
    
    return None

def list_domains():
    """列出所有支持的领域"""
    return ["人工智能", "医疗", "金融", "劳动合同"]
