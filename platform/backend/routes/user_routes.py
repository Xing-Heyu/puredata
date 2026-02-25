"""
用户相关路由处理
完整版 - 包含所有用户相关的API处理逻辑
"""

import json
import re
from datetime import datetime

def handle_user_routes(handler, path, method, body, context):
    """
    处理用户相关请求
    
    context包含:
    - user_manager: 用户管理器
    - admin_auth: 管理员认证
    - client_ip: 客户端IP
    - ANTI_ABUSE_AVAILABLE: 反滥用是否可用
    - get_anti_abuse: 获取反滥用实例
    """
    
    user_manager = context.get('user_manager')
    admin_auth = context.get('admin_auth')
    client_ip = context.get('client_ip', '')
    ANTI_ABUSE_AVAILABLE = context.get('ANTI_ABUSE_AVAILABLE', False)
    get_anti_abuse = context.get('get_anti_abuse')
    
    if path == '/api/login':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        username = body.get('username', '')
        password = body.get('password', '')
        
        if not user_manager:
            handler._send_json(500, {"error": "用户系统不可用"})
            return True
        
        result = user_manager.login(username, password)
        if result.get("success"):
            handler._send_json(200, result)
        else:
            handler._send_json(401, result)
        return True
    
    elif path == '/api/register':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        if not user_manager:
            handler._send_json(500, {"error": "用户系统不可用"})
            return True
        
        try:
            username = body.get('username', '')
            password = body.get('password', '')
            account = body.get('account', body.get('email', ''))
            invite_code = body.get('invite_code')
            
            print(f"[DEBUG] 注册请求: username={username}, account={account}")
            
            is_phone = re.match(r'^1[3-9]\d{9}$', account)
            is_email = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', account)
            
            if not is_phone and not is_email:
                handler._send_json(400, {"success": False, "error": "请输入正确的手机号或邮箱"})
                return True
            
            email = account if is_email else ''
            phone = account if is_phone else ''
            
            print(f"[DEBUG] 调用 user_manager.register...")
            result = user_manager.register(username, password, email, phone=phone, invite_code=invite_code)
            print(f"[DEBUG] 注册结果: {result}")
            
            if result.get('success') and ANTI_ABUSE_AVAILABLE and get_anti_abuse:
                try:
                    anti_abuse_module = get_anti_abuse()
                    if anti_abuse_module and hasattr(anti_abuse_module, 'register_user'):
                        anti_abuse_module.register_user(email or phone, client_ip, username)
                except Exception as e:
                    print(f"[WARN] 反滥用记录失败: {e}")
            
            handler._send_json(200 if result.get('success') else 400, result)
        except Exception as e:
            import traceback
            print(f"[ERROR] 注册异常: {e}")
            print(f"[ERROR] 详细堆栈: {traceback.format_exc()}")
            handler._send_json(500, {"success": False, "error": "服务器内部错误，请稍后重试"})
        return True
    
    elif path == '/api/logout':
        token = handler._get_token_from_request()
        if user_manager:
            user_manager.logout(token)
        handler._send_json(200, {"success": True, "message": "已退出登录"})
        return True
    
    elif path == '/api/user/info':
        token = handler._get_token_from_request()
        if not user_manager:
            handler._send_json(500, {"error": "用户系统不可用"})
            return True
        
        user = user_manager.validate_token(token)
        if user:
            handler._send_json(200, {"success": True, "user": user})
        else:
            handler._send_json(401, {"error": "未登录"})
        return True
    
    elif path == '/api/user/quota':
        token = handler._get_token_from_request()
        if not user_manager:
            handler._send_json(500, {"error": "用户系统不可用"})
            return True
        
        user = user_manager.validate_token(token)
        if not user:
            handler._send_json(401, {"error": "未登录"})
            return True
        
        quota_info = user_manager.get_quota_status(user['username'])
        handler._send_json(200, {"success": True, "quota": quota_info})
        return True
    
    elif path == '/api/user/history':
        token = handler._get_token_from_request()
        if not user_manager:
            handler._send_json(500, {"error": "用户系统不可用"})
            return True
        
        user = user_manager.validate_token(token)
        if not user:
            handler._send_json(401, {"error": "未登录"})
            return True
        
        history = user.get('tasks_completed', [])
        handler._send_json(200, {"success": True, "history": history})
        return True
    
    elif path == '/api/password/reset/request':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        email = body.get('email', '')
        if not user_manager:
            handler._send_json(500, {"error": "用户系统不可用"})
            return True
        
        result = user_manager.request_password_reset(email)
        handler._send_json(200, result)
        return True
    
    elif path == '/api/password/reset':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        token = body.get('token', '')
        new_password = body.get('new_password', '')
        
        if not user_manager:
            handler._send_json(500, {"error": "用户系统不可用"})
            return True
        
        result = user_manager.reset_password(token, new_password)
        handler._send_json(200, result)
        return True
    
    elif path == '/api/send_verification':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        target = body.get('target', body.get('email', ''))
        otp_type_str = body.get('type', 'register')
        
        try:
            from otp_manager import otp_manager, OTPType
            otp_type = OTPType.REGISTER if otp_type_str == 'register' else OTPType.LOGIN
            result = otp_manager.send_code(target, otp_type)
        except Exception as e:
            result = {"success": True, "message": f"验证码已发送(演示模式)，验证码: 123456", "demo_code": "123456"}
        
        handler._send_json(200 if result.get('success') else 400, result)
        return True
    
    elif path == '/api/verify_code':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        target = body.get('target', '')
        code = body.get('code', '')
        otp_type_str = body.get('type', 'register')
        
        try:
            from otp_manager import otp_manager, OTPType
            otp_type = OTPType.REGISTER if otp_type_str == 'register' else OTPType.LOGIN
            result = otp_manager.verify_code(target, code, otp_type)
        except Exception as e:
            if code == '123456':
                result = {"success": True, "message": "验证成功"}
            else:
                result = {"success": False, "error": "验证码错误"}
        
        handler._send_json(200 if result.get('success') else 400, result)
        return True
    
    elif path == '/api/verify_email':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        email = body.get('email', '')
        code = body.get('code', '')
        
        if ANTI_ABUSE_AVAILABLE and get_anti_abuse:
            anti_abuse_module = get_anti_abuse()
            if anti_abuse_module:
                result = anti_abuse_module.anti_abuse.verify_email(email, code)
            else:
                result = {"success": True, "message": "验证成功(演示模式)"} if code == "123456" else {"success": False, "error": "验证码错误"}
        else:
            result = {"success": True, "message": "验证成功(演示模式)"} if code == "123456" else {"success": False, "error": "验证码错误"}
        
        handler._send_json(200 if result.get('success') else 400, result)
        return True
    
    elif path == '/api/password/check':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        password = body.get('password', '')
        
        if len(password) < 8:
            handler._send_json(200, {"valid": False, "message": "密码长度至少8位"})
        elif not re.search(r'[A-Z]', password):
            handler._send_json(200, {"valid": False, "message": "密码需包含大写字母"})
        elif not re.search(r'[a-z]', password):
            handler._send_json(200, {"valid": False, "message": "密码需包含小写字母"})
        elif not re.search(r'\d', password):
            handler._send_json(200, {"valid": False, "message": "密码需包含数字"})
        else:
            handler._send_json(200, {"valid": True, "message": "密码强度合格"})
        return True
    
    elif path == '/api/otp/send':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        target = body.get('target', '')
        otp_type = body.get('type', 'register')
        
        try:
            from otp_manager import otp_manager, OTPType
            otp_type_enum = OTPType.REGISTER if otp_type == 'register' else OTPType.LOGIN
            result = otp_manager.send_code(target, otp_type_enum)
        except Exception as e:
            result = {"success": True, "message": "验证码已发送(演示模式)", "demo_code": "123456"}
        
        handler._send_json(200, result)
        return True
    
    return None
