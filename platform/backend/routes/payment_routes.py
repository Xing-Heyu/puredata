"""
支付相关路由处理
"""

def handle_payment_request(handler, path, method, body, context):
    """处理支付相关请求"""
    import json
    
    user_manager = context.get('user_manager')
    payment_manager = context.get('payment_manager')
    
    if path == '/api/payment/plans':
        plans = payment_manager.get_plans() if payment_manager else []
        handler._send_json(200, {"success": True, "plans": plans})
        return True
    
    elif path == '/api/payment/create':
        if method == 'POST':
            token = handler._get_token_from_request()
            user = user_manager.validate_token(token) if user_manager else None
            if not user:
                handler._send_json(401, {"success": False, "error": "请先登录"})
                return True
            
            plan_id = body.get('plan_id')
            result = payment_manager.create_order(user['username'], plan_id) if payment_manager else {"success": False, "error": "支付服务不可用"}
            handler._send_json(200, result)
            return True
    
    elif path == '/api/payment/status':
        order_id = body.get('order_id')
        status = payment_manager.get_order_status(order_id) if payment_manager else None
        handler._send_json(200, {"success": True, "status": status})
        return True
    
    elif path == '/api/payment_methods':
        payment_methods = [
            {"id": "wechat", "name": "微信支付", "icon": "wechat"},
            {"id": "alipay", "name": "支付宝", "icon": "alipay"},
            {"id": "bank", "name": "银行转账", "icon": "bank"}
        ]
        handler._send_json(200, {"success": True, "methods": payment_methods})
        return True
    
    return None
