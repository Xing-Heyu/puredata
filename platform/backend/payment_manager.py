#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支付系统模块
支持：订单管理、支付状态、发票申请
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import threading

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BACKEND_DIR, 'orders.json')
INVOICES_FILE = os.path.join(BACKEND_DIR, 'invoices.json')

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class InvoiceStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ISSUED = "issued"

from pricing_config import PRICING_PLANS, PAYG_PACKAGES

PLANS = {plan_id: {
    "name": plan["name"],
    "price": plan["price"],
    "quota": plan["quota"],
    "duration": plan["duration"] or 36500
} for plan_id, plan in PRICING_PLANS.items() if plan["price"] > 0}

PAYG = PAYG_PACKAGES

class PaymentManager:
    """支付管理器"""
    
    def __init__(self):
        self.orders: Dict[str, Dict] = {}
        self.invoices: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self._load()
    
    def _load(self):
        """加载订单和发票数据 - 带异常处理"""
        if os.path.exists(ORDERS_FILE):
            try:
                with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                    self.orders = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] 加载订单数据失败: {e}")
                self.orders = {}
        if os.path.exists(INVOICES_FILE):
            try:
                with open(INVOICES_FILE, 'r', encoding='utf-8') as f:
                    self.invoices = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] 加载发票数据失败: {e}")
                self.invoices = {}
    
    def _save(self):
        """保存订单和发票数据 - 带异常处理"""
        try:
            with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.orders, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] 保存订单数据失败: {e}")
        try:
            with open(INVOICES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.invoices, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] 保存发票数据失败: {e}")
    
    def create_order(self, user_id: str, plan_id: str, payment_method: str = "wechat") -> Dict:
        if plan_id not in PLANS:
            return {"success": False, "error": "无效的套餐"}
        
        plan = PLANS[plan_id]
        order_id = f"ORD{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        
        with self.lock:
            order = {
                "order_id": order_id,
                "user_id": user_id,
                "plan_id": plan_id,
                "plan_name": plan["name"],
                "amount": plan["price"],
                "quota": plan["quota"],
                "duration": plan["duration"],
                "status": OrderStatus.PENDING.value,
                "payment_method": payment_method,
                "created_at": datetime.now().isoformat(),
                "paid_at": None,
                "expire_at": None
            }
            
            self.orders[order_id] = order
            self._save()
            
            return {
                "success": True,
                "order_id": order_id,
                "amount": plan["price"],
                "plan_name": plan["name"],
                "payment_url": f"/pay/{order_id}",
                "message": "订单创建成功，请完成支付"
            }
    
    def confirm_payment(self, order_id: str, transaction_id: str = None, user_manager=None) -> Dict:
        # 阶段1: 获取订单信息并更新订单状态（需要锁）
        with self.lock:
            if order_id not in self.orders:
                return {"success": False, "error": "订单不存在"}
            
            order = self.orders[order_id]
            if order["status"] != OrderStatus.PENDING.value:
                return {"success": False, "error": "订单状态异常"}
            
            order["status"] = OrderStatus.PAID.value
            order["paid_at"] = datetime.now().isoformat()
            order["transaction_id"] = transaction_id or f"TXN{uuid.uuid4().hex[:16].upper()}"
            order["expire_at"] = (datetime.now() + timedelta(days=order["duration"])).isoformat()
            
            # 保存需要外部调用的信息
            user_id = order["user_id"]
            quota = order["quota"]
            
            self._save()
        
        # 阶段2: 调用外部 user_manager（锁外执行，避免死锁）
        quota_added = False
        if user_manager:
            try:
                user_manager.add_paid_quota(user_id, quota)
                quota_added = True
            except Exception as e:
                print(f"[WARN] 添加配额失败: {e}")
                quota_added = False
            
            # 更新订单的配额添加状态（需要锁）
            with self.lock:
                if order_id in self.orders:
                    self.orders[order_id]["quota_added"] = quota_added
                    self._save()
        
        # 阶段3: 返回结果（无需锁）
        return {
            "success": True,
            "order_id": order_id,
            "message": "支付成功",
            "quota": quota,
            "expire_at": order["expire_at"],
            "quota_added": quota_added
        }
    
    def cancel_order(self, order_id: str, user_id: str = None) -> Dict:
        with self.lock:
            if order_id not in self.orders:
                return {"success": False, "error": "订单不存在"}
            
            order = self.orders[order_id]
            if user_id and order["user_id"] != user_id:
                return {"success": False, "error": "无权操作此订单"}
            
            if order["status"] != OrderStatus.PENDING.value:
                return {"success": False, "error": "只能取消待支付订单"}
            
            order["status"] = OrderStatus.CANCELLED.value
            self._save()
            
            return {"success": True, "message": "订单已取消"}
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        return self.orders.get(order_id)
    
    def get_user_orders(self, user_id: str) -> List[Dict]:
        return [order for order in self.orders.values() if order["user_id"] == user_id]
    
    def get_plans(self) -> List[Dict]:
        plans = []
        for plan_id, plan_info in PLANS.items():
            plans.append({
                "plan_id": plan_id,
                "name": plan_info["name"],
                "price": plan_info["price"],
                "quota": plan_info["quota"],
                "duration": plan_info["duration"]
            })
        return plans
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        order = self.orders.get(order_id)
        if not order:
            return None
        
        return {
            "order_id": order["order_id"],
            "status": order["status"],
            "plan_name": order["plan_name"],
            "amount": order["amount"],
            "created_at": order["created_at"],
            "paid_at": order.get("paid_at"),
            "expire_at": order.get("expire_at")
        }
    
    def apply_invoice(self, order_id: str, user_id: str, invoice_info: Dict) -> Dict:
        with self.lock:
            if order_id not in self.orders:
                return {"success": False, "error": "订单不存在"}
            
            order = self.orders[order_id]
            if order["user_id"] != user_id:
                return {"success": False, "error": "无权操作此订单"}
            
            if order["status"] != OrderStatus.PAID.value:
                return {"success": False, "error": "只能对已支付订单申请发票"}
            
            invoice_id = f"INV{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
            
            invoice = {
                "invoice_id": invoice_id,
                "order_id": order_id,
                "user_id": user_id,
                "amount": order["amount"],
                "title": invoice_info.get("title", ""),
                "tax_id": invoice_info.get("tax_id", ""),
                "address": invoice_info.get("address", ""),
                "phone": invoice_info.get("phone", ""),
                "bank": invoice_info.get("bank", ""),
                "bank_account": invoice_info.get("bank_account", ""),
                "email": invoice_info.get("email", ""),
                "status": InvoiceStatus.PENDING.value,
                "created_at": datetime.now().isoformat(),
                "approved_at": None,
                "issued_at": None,
                "reject_reason": None
            }
            
            self.invoices[invoice_id] = invoice
            self._save()
            
            return {
                "success": True,
                "invoice_id": invoice_id,
                "message": "发票申请已提交，请等待审核"
            }
    
    def approve_invoice(self, invoice_id: str, admin_id: str) -> Dict:
        with self.lock:
            if invoice_id not in self.invoices:
                return {"success": False, "error": "发票申请不存在"}
            
            invoice = self.invoices[invoice_id]
            if invoice["status"] != InvoiceStatus.PENDING.value:
                return {"success": False, "error": "发票状态异常"}
            
            invoice["status"] = InvoiceStatus.APPROVED.value
            invoice["approved_at"] = datetime.now().isoformat()
            invoice["approved_by"] = admin_id
            self._save()
            
            return {"success": True, "message": "发票已审核通过"}
    
    def reject_invoice(self, invoice_id: str, admin_id: str, reason: str) -> Dict:
        with self.lock:
            if invoice_id not in self.invoices:
                return {"success": False, "error": "发票申请不存在"}
            
            invoice = self.invoices[invoice_id]
            invoice["status"] = InvoiceStatus.REJECTED.value
            invoice["reject_reason"] = reason
            invoice["rejected_at"] = datetime.now().isoformat()
            invoice["rejected_by"] = admin_id
            self._save()
            
            return {"success": True, "message": "发票已驳回"}
    
    def issue_invoice(self, invoice_id: str, invoice_number: str) -> Dict:
        with self.lock:
            if invoice_id not in self.invoices:
                return {"success": False, "error": "发票申请不存在"}
            
            invoice = self.invoices[invoice_id]
            if invoice["status"] != InvoiceStatus.APPROVED.value:
                return {"success": False, "error": "发票未审核"}
            
            invoice["status"] = InvoiceStatus.ISSUED.value
            invoice["invoice_number"] = invoice_number
            invoice["issued_at"] = datetime.now().isoformat()
            self._save()
            
            return {"success": True, "message": "发票已开具"}
    
    def get_user_invoices(self, user_id: str) -> List[Dict]:
        return [inv for inv in self.invoices.values() if inv["user_id"] == user_id]
    
    def get_pending_invoices(self) -> List[Dict]:
        return [inv for inv in self.invoices.values() if inv["status"] == InvoiceStatus.PENDING.value]
    
    def check_subscription_expiry(self, days: int = 7) -> List[Dict]:
        cutoff = (datetime.now() + timedelta(days=days)).isoformat()
        expiring = []
        
        for order in self.orders.values():
            if order["status"] == OrderStatus.PAID.value:
                if order.get("expire_at") and order["expire_at"] <= cutoff:
                    expiring.append(order)
        
        return expiring
    
    def refund_order(self, order_id: str, reason: str = "", admin_id: str = None) -> Dict:
        """
        订单退款 - 合成数据服务特殊退款规则
        
        合成数据服务特点：
        - 数据一旦生成下载即视为交付
        - 数据可无限复制，无法真正"退货"
        
        退款规则：
        - 未使用配额：可全额退款
        - 已使用部分：按比例退款
        - 已全部使用：不支持退款，提供技术支持
        """
        with self.lock:
            if order_id not in self.orders:
                return {"success": False, "error": "订单不存在"}
            
            order = self.orders[order_id]
            
            if order["status"] not in [OrderStatus.PAID.value]:
                return {"success": False, "error": "只能退款已支付的订单"}
            
            paid_at = order.get("paid_at")
            days_since_payment = 0  # 防御性初始化，避免变量未定义
            
            if paid_at:
                try:
                    paid_time = datetime.fromisoformat(paid_at)
                    days_since_payment = (datetime.now() - paid_time).days
                except (ValueError, TypeError):
                    # 如果日期解析失败，默认允许退款（保守策略）
                    days_since_payment = 0
                
                if days_since_payment > 7:
                    return {
                        "success": False, 
                        "error": "支付已超过7天，不支持自助退款。如有问题请联系客服处理。"
                    }
            
            quota_total = order.get("quota", 0)
            quota_used = order.get("quota_used", 0)
            usage_ratio = quota_used / quota_total if quota_total > 0 else 0
            
            if usage_ratio >= 1.0:
                return {
                    "success": False,
                    "error": "配额已全部使用，不支持退款。如有数据质量问题，请联系客服申请技术支持或补偿。",
                    "suggestion": "技术支持"
                }
            
            if usage_ratio > 0.5:
                return {
                    "success": False,
                    "error": f"已使用{int(usage_ratio*100)}%配额，超过50%不支持自助退款。请联系客服处理。",
                    "usage_ratio": usage_ratio,
                    "suggestion": "联系客服"
                }
            
            refund_ratio = 1.0 - usage_ratio
            refund_amount = int(order["amount"] * refund_ratio)
            
            order["status"] = OrderStatus.REFUNDED.value
            order["refunded_at"] = datetime.now().isoformat()
            order["refund_reason"] = reason
            order["refunded_by"] = admin_id or order["user_id"]
            order["refund_amount"] = refund_amount
            order["refund_ratio"] = refund_ratio
            
            self._save()
            
            return {
                "success": True,
                "order_id": order_id,
                "refund_amount": refund_amount,
                "refund_ratio": refund_ratio,
                "message": f"退款申请已提交，退还{int(refund_ratio*100)}%金额（{refund_amount/100:.2f}元），预计1-3个工作日内原路退回"
            }
    
    def request_refund(self, order_id: str, user_id: str, reason: str) -> Dict:
        """
        用户申请退款 - 合成数据服务
        """
        with self.lock:
            if order_id not in self.orders:
                return {"success": False, "error": "订单不存在"}
            
            order = self.orders[order_id]
            
            if order["user_id"] != user_id:
                return {"success": False, "error": "无权操作此订单"}
            
            if order["status"] != OrderStatus.PAID.value:
                return {"success": False, "error": "只能退款已支付的订单"}
            
            paid_at = order.get("paid_at")
            if paid_at:
                paid_time = datetime.fromisoformat(paid_at)
                days_since_payment = (datetime.now() - paid_time).days
                
                if days_since_payment > 7:
                    return {
                        "success": False, 
                        "error": "支付已超过7天，不支持自助退款。如有问题请联系客服处理。"
                    }
            
            quota_total = order.get("quota", 0)
            quota_used = order.get("quota_used", 0)
            usage_ratio = quota_used / quota_total if quota_total > 0 else 0
            
            if usage_ratio >= 1.0:
                return {
                    "success": False,
                    "error": "配额已全部使用，不支持退款。如有数据质量问题，请提交工单申请技术支持。",
                    "quota_used": quota_used,
                    "quota_total": quota_total
                }
            
            order["refund_requested"] = True
            order["refund_request_time"] = datetime.now().isoformat()
            order["refund_reason"] = reason
            order["status"] = "refund_pending"
            order["usage_ratio_at_refund"] = usage_ratio
            
            self._save()
            
            if usage_ratio == 0:
                return {
                    "success": True,
                    "order_id": order_id,
                    "message": "退款申请已提交（未使用配额，可全额退款），请等待审核"
                }
            else:
                return {
                    "success": True,
                    "order_id": order_id,
                    "message": f"退款申请已提交（已使用{int(usage_ratio*100)}%配额），请等待审核"
                }
    
    def get_refundable_orders(self, user_id: str) -> List[Dict]:
        """
        获取用户可退款的订单列表
        """
        refundable = []
        
        for order in self.orders.values():
            if order["user_id"] != user_id:
                continue
            
            if order["status"] != OrderStatus.PAID.value:
                continue
            
            paid_at = order.get("paid_at")
            if paid_at:
                paid_time = datetime.fromisoformat(paid_at)
                days_since_payment = (datetime.now() - paid_time).days
                
                if days_since_payment > 7:
                    continue
            
            quota_total = order.get("quota", 0)
            quota_used = order.get("quota_used", 0)
            usage_ratio = quota_used / quota_total if quota_total > 0 else 0
            
            if usage_ratio < 0.5:
                order_copy = order.copy()
                order_copy["refundable"] = True
                order_copy["days_remaining"] = 7 - days_since_payment
                order_copy["usage_ratio"] = usage_ratio
                order_copy["estimated_refund_ratio"] = 1.0 - usage_ratio
                refundable.append(order_copy)
        
        return refundable
    
    def get_pending_refunds(self) -> List[Dict]:
        """
        获取待审核的退款申请列表（管理员用）
        """
        pending = []
        
        for order in self.orders.values():
            if order.get("refund_requested") and order["status"] == "refund_pending":
                pending.append(order)
        
        return pending
    
    def approve_refund(self, order_id: str, admin_id: str) -> Dict:
        """
        管理员批准退款
        """
        with self.lock:
            if order_id not in self.orders:
                return {"success": False, "error": "订单不存在"}
            
            order = self.orders[order_id]
            
            if order["status"] != "refund_pending":
                return {"success": False, "error": "订单状态异常"}
            
            order["status"] = OrderStatus.REFUNDED.value
            order["refunded_at"] = datetime.now().isoformat()
            order["refund_approved_by"] = admin_id
            
            self._save()
            
            return {
                "success": True,
                "order_id": order_id,
                "refund_amount": order["amount"],
                "message": "退款已批准"
            }
    
    def reject_refund(self, order_id: str, admin_id: str, reason: str) -> Dict:
        """
        管理员拒绝退款
        """
        with self.lock:
            if order_id not in self.orders:
                return {"success": False, "error": "订单不存在"}
            
            order = self.orders[order_id]
            
            if order["status"] != "refund_pending":
                return {"success": False, "error": "订单状态异常"}
            
            order["status"] = OrderStatus.PAID.value
            order["refund_rejected"] = True
            order["refund_reject_reason"] = reason
            order["refund_rejected_by"] = admin_id
            order["refund_rejected_at"] = datetime.now().isoformat()
            
            self._save()
            
            return {
                "success": True,
                "message": "退款申请已拒绝"
            }

payment_manager = PaymentManager()

if __name__ == "__main__":
    print("="*60)
    print("支付系统测试")
    print("="*60)
    
    result = payment_manager.create_order("test_user", "pro_monthly")
    print(f"\n创建订单: {result}")
    
    if result["success"]:
        order_id = result["order_id"]
        confirm = payment_manager.confirm_payment(order_id)
        print(f"确认支付: {confirm}")
        
        invoice = payment_manager.apply_invoice(order_id, "test_user", {
            "title": "测试公司",
            "tax_id": "1234567890123456"
        })
        print(f"申请发票: {invoice}")
