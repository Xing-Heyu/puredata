#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
领域专精化模块
每个垂直领域的专业数据生成器
支持领域：人工智能、医疗、金融、劳动合同、交通驾驶
"""

from .base_specialist import DomainSpecialist
from .ai_specialist import AISpecialist
from .labor_specialist import LaborSpecialist
from .medical_specialist import MedicalSpecialist
from .finance_specialist import FinanceSpecialist
from .traffic_driving_specialist import TrafficDrivingSpecialist
from .ecommerce_specialist import EcommerceSpecialist
from .education_specialist import EducationSpecialist
from .legal_specialist import LegalSpecialist
from .tech_specialist import TechSpecialist

SPECIALISTS = {
    "人工智能": AISpecialist,
    "ai": AISpecialist,
    "医疗": MedicalSpecialist,
    "medical": MedicalSpecialist,
    "金融": FinanceSpecialist,
    "finance": FinanceSpecialist,
    "劳动合同": LaborSpecialist,
    "labor": LaborSpecialist,
    "交通驾驶": TrafficDrivingSpecialist,
    "traffic": TrafficDrivingSpecialist,
    "driving": TrafficDrivingSpecialist,
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
    return ["人工智能", "医疗", "金融", "劳动合同", "交通驾驶"]

__all__ = [
    "DomainSpecialist",
    "AISpecialist",
    "LaborSpecialist",
    "MedicalSpecialist",
    "FinanceSpecialist",
    "TrafficDrivingSpecialist",
    "get_specialist",
    "get_all_specialists",
    "list_domains",
    "SPECIALISTS"
]
