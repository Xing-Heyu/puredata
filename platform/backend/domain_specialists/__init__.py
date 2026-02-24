#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域专精化模块
每个垂直领域的专业数据生成器
只保留核心领域：人工智能、医疗、金融、劳动合同
"""

from .base_specialist import DomainSpecialist
from .ai_specialist import AISpecialist
from .labor_specialist import LaborSpecialist
from .medical_specialist import MedicalSpecialist
from .finance_specialist import FinanceSpecialist

SPECIALISTS = {
    "人工智能": AISpecialist,
    "ai": AISpecialist,
    "劳动合同": LaborSpecialist,
    "labor": LaborSpecialist,
    "医疗": MedicalSpecialist,
    "medical": MedicalSpecialist,
    "金融": FinanceSpecialist,
    "finance": FinanceSpecialist,
}

def get_specialist(domain: str) -> DomainSpecialist:
    """获取领域专精生成器"""
    specialist_class = SPECIALISTS.get(domain)
    if specialist_class:
        return specialist_class()
    return None

def get_all_specialists() -> dict:
    """获取所有领域专精生成器"""
    return {name: cls() for name, cls in SPECIALISTS.items()}

def list_domains() -> list:
    """列出所有支持的领域"""
    return ["人工智能", "医疗", "金融", "劳动合同"]

__all__ = [
    "DomainSpecialist",
    "AISpecialist",
    "LaborSpecialist",
    "MedicalSpecialist",
    "FinanceSpecialist",
    "get_specialist",
    "get_all_specialists",
    "list_domains",
    "SPECIALISTS"
]
