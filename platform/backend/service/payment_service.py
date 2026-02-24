#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务层 - 支付服务
整合自 payment_manager.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from payment_manager import PaymentManager, OrderStatus
    PaymentService = PaymentManager
    __all__ = ['PaymentService', 'PaymentManager', 'OrderStatus']
except ImportError:
    from typing import Dict, Optional
    from datetime import datetime
    from enum import Enum
    
    class OrderStatus(Enum):
        PENDING = "pending"
        PAID = "paid"
        CANCELLED = "cancelled"
        REFUNDED = "refunded"
    
    class PaymentService:
        """支付服务 - 占位实现"""
        
        def __init__(self):
            self.orders: Dict[str, Dict] = {}
        
        def create_order(self, user_id: str, amount: float, description: str = "") -> Dict:
            order_id = f"order_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.orders[order_id] = {
                "id": order_id,
                "user_id": user_id,
                "amount": amount,
                "description": description,
                "status": OrderStatus.PENDING.value,
                "created_at": datetime.now().isoformat()
            }
            return self.orders[order_id]
        
        def get_order(self, order_id: str) -> Optional[Dict]:
            return self.orders.get(order_id)
    
    PaymentManager = PaymentService
    __all__ = ['PaymentService', 'PaymentManager', 'OrderStatus']
