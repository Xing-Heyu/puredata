#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支付配置 - 收款码、支付方式
修改此文件来更新支付信息
"""

PAYMENT_CONFIG = {
    "enabled": True,
    
    "wechat": {
        "enabled": True,
        "name": "微信支付",
        "qrcode_url": "/static/images/wechat_pay.png",
        "account": "",
        "note": "扫码付款后，订单将自动确认"
    },
    
    "alipay": {
        "enabled": True,
        "name": "支付宝",
        "qrcode_url": "/static/images/alipay.png",
        "account": "",
        "note": "扫码付款后，订单将自动确认"
    },
    
    "bank": {
        "enabled": False,
        "name": "银行转账",
        "bank_name": "",
        "account_name": "",
        "account_number": "",
        "note": "对公转账，需联系客服确认"
    },
    
    "auto_confirm": False,
    "confirm_note": "付款后请联系客服确认，客服电话：400-XXX-XXXX"
}

def get_payment_methods():
    methods = []
    for key in ["wechat", "alipay", "bank"]:
        if PAYMENT_CONFIG.get(key, {}).get("enabled", False):
            methods.append({
                "id": key,
                **PAYMENT_CONFIG[key]
            })
    return methods

def get_payment_config():
    return PAYMENT_CONFIG.copy()
