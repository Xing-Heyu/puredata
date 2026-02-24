#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务层 - 租户服务
整合自 tenant_manager.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tenant_manager import TenantManager, TenantPlan
    TenantService = TenantManager
    __all__ = ['TenantService', 'TenantManager', 'TenantPlan']
except ImportError:
    from typing import Dict, Optional
    from datetime import datetime
    from enum import Enum
    
    class TenantPlan(Enum):
        FREE = "free"
        BASIC = "basic"
        PRO = "pro"
        ENTERPRISE = "enterprise"
    
    class TenantService:
        """租户服务 - 占位实现"""
        
        def __init__(self):
            self.tenants: Dict[str, Dict] = {}
        
        def create_tenant(self, name: str, plan: TenantPlan = TenantPlan.FREE) -> Dict:
            tenant_id = f"tenant_{len(self.tenants) + 1}"
            self.tenants[tenant_id] = {
                "id": tenant_id,
                "name": name,
                "plan": plan.value,
                "created_at": datetime.now().isoformat()
            }
            return self.tenants[tenant_id]
        
        def get_tenant(self, tenant_id: str) -> Optional[Dict]:
            return self.tenants.get(tenant_id)
    
    TenantManager = TenantService
    __all__ = ['TenantService', 'TenantManager', 'TenantPlan']
