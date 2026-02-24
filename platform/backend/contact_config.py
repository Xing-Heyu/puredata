#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联系配置 - 客服电话、邮箱等
修改此文件来更新联系方式
"""

CONTACT_CONFIG = {
    "company_name": "PureData",
    "company_full_name": "PureData 数据科技",
    
    "phone": "400-XXX-XXXX",
    "phone_display": "400-XXX-XXXX（工作日 9:00-18:00）",
    
    "email": "support@puredata.ai",
    "sales_email": "sales@puredata.ai",
    
    "wechat": "PureData_AI",
    "wechat_qrcode": "",
    
    "address": "",
    
    "business_hours": "工作日 9:00-18:00",
    
    "social_links": {
        "website": "https://puredata.ai",
        "github": "",
        "weibo": ""
    }
}

def get_contact_info():
    return CONTACT_CONFIG.copy()

def get_phone():
    return CONTACT_CONFIG["phone"]

def get_email():
    return CONTACT_CONFIG["email"]

def get_sales_email():
    return CONTACT_CONFIG["sales_email"]
