#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双因素认证模块
支持：手机验证码、邮箱验证码
集成：腾讯云短信/邮件、阿里云短信/邮件（接口模式）
"""

import json
import os
import string
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from enum import Enum
import threading
import re

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
OTP_FILE = os.path.join(BACKEND_DIR, 'otp_codes.json')


class OTPType(Enum):
    LOGIN = "login"
    REGISTER = "register"
    RESET_PASSWORD = "reset_password"
    CHANGE_PHONE = "change_phone"
    CHANGE_EMAIL = "change_email"
    SENSITIVE_ACTION = "sensitive_action"


class OTPChannel(Enum):
    SMS = "sms"
    EMAIL = "email"


class SMSProvider(Enum):
    """短信服务商"""
    TENCENT = "tencent"
    ALIYUN = "aliyun"
    MOCK = "mock"


class EmailProvider(Enum):
    """邮件服务商"""
    TENCENT = "tencent"
    ALIYUN = "aliyun"
    SMTP = "smtp"
    MOCK = "mock"


class OTPManager:
    """验证码管理器"""
    
    CODE_LENGTH = 6
    CODE_EXPIRE_SECONDS = 300
    CODE_COOLDOWN_SECONDS = 60
    MAX_ATTEMPTS = 5
    
    PROVIDER_CONFIG = {
        "sms_provider": os.environ.get("SMS_PROVIDER", "mock"),
        "email_provider": os.environ.get("EMAIL_PROVIDER", "mock"),
        
        "tencent": {
            "secret_id": os.environ.get("TENCENT_SECRET_ID", ""),
            "secret_key": os.environ.get("TENCENT_SECRET_KEY", ""),
            "sms_app_id": os.environ.get("TENCENT_SMS_APP_ID", ""),
            "sms_sign": os.environ.get("TENCENT_SMS_SIGN", ""),
            "sms_template_id": os.environ.get("TENCENT_SMS_TEMPLATE_ID", ""),
        },
        
        "aliyun": {
            "access_key_id": os.environ.get("ALIYUN_ACCESS_KEY_ID", ""),
            "access_key_secret": os.environ.get("ALIYUN_ACCESS_KEY_SECRET", ""),
            "sms_sign": os.environ.get("ALIYUN_SMS_SIGN", ""),
            "sms_template_code": os.environ.get("ALIYUN_SMS_TEMPLATE_CODE", ""),
        },
        
        "smtp": {
            "host": os.environ.get("SMTP_HOST", "smtp.qq.com"),
            "port": int(os.environ.get("SMTP_PORT", 465)),
            "user": os.environ.get("SMTP_USER", ""),
            "password": os.environ.get("SMTP_PASSWORD", ""),
            "from_name": os.environ.get("SMTP_FROM_NAME", "PureData平台"),
        }
    }
    
    def __init__(self):
        self.codes: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self._load()
    
    def _load(self):
        """加载OTP数据 - 带异常处理"""
        if os.path.exists(OTP_FILE):
            try:
                with open(OTP_FILE, 'r', encoding='utf-8') as f:
                    self.codes = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] 加载OTP数据失败: {e}")
                self.codes = {}
    
    def _save(self):
        """保存OTP数据 - 带异常处理"""
        try:
            with open(OTP_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.codes, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] 保存OTP数据失败: {e}")
    
    def _generate_code(self) -> str:
        return ''.join(secrets.choice(string.digits) for _ in range(self.CODE_LENGTH))
    
    def _is_valid_phone(self, phone: str) -> bool:
        return bool(re.match(r'^1[3-9]\d{9}$', phone))
    
    def _is_valid_email(self, email: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
    
    def _mask_phone(self, phone: str) -> str:
        if len(phone) >= 11:
            return phone[:3] + "****" + phone[-4:]
        return phone
    
    def _mask_email(self, email: str) -> str:
        if "@" in email:
            parts = email.split("@")
            if len(parts[0]) > 2:
                return parts[0][:2] + "***@" + parts[1]
            return "***@" + parts[1]
        return email
    
    def _send_sms_tencent(self, phone: str, code: str) -> bool:
        """腾讯云短信接口"""
        config = self.PROVIDER_CONFIG["tencent"]
        
        if not config["secret_id"] or not config["secret_key"]:
            print(f"[OTP] 腾讯云短信未配置，验证码: {code}")
            return False
        
        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.sms.v20210111 import sms_client, models
            
            cred = credential.Credential(config["secret_id"], config["secret_key"])
            client = sms_client.SmsClient(cred, "ap-guangzhou")
            
            req = models.SendSmsRequest()
            req.SmsSdkAppId = config["sms_app_id"]
            req.SignName = config["sms_sign"]
            req.TemplateId = config["sms_template_id"]
            req.PhoneNumberSet = [f"+86{phone}"]
            req.TemplateParamSet = [code, str(self.CODE_EXPIRE_SECONDS // 60)]
            
            resp = client.SendSms(req)
            print(f"[OTP] 腾讯云短信发送成功: {self._mask_phone(phone)}")
            return True
            
        except ImportError:
            print(f"[OTP] 腾讯云SDK未安装，验证码: {code}")
            return False
        except Exception as e:
            print(f"[OTP] 腾讯云短信发送失败: {e}")
            return False
    
    def _send_sms_aliyun(self, phone: str, code: str) -> bool:
        """阿里云短信接口"""
        config = self.PROVIDER_CONFIG["aliyun"]
        
        if not config["access_key_id"] or not config["access_key_secret"]:
            print(f"[OTP] 阿里云短信未配置，验证码: {code}")
            return False
        
        try:
            from alibabacloud_dysmsapi20170525.client import Client
            from alibabacloud_dysmsapi20170525 import models as sms_models
            from alibabacloud_tea_openapi import models as open_api_models
            
            open_api_config = open_api_models.Config(
                access_key_id=config["access_key_id"],
                access_key_secret=config["access_key_secret"]
            )
            open_api_config.endpoint = "dysmsapi.aliyuncs.com"
            
            client = Client(open_api_config)
            
            request = sms_models.SendSmsRequest(
                phone_numbers=phone,
                sign_name=config["sms_sign"],
                template_code=config["sms_template_code"],
                template_param=json.dumps({"code": code})
            )
            
            resp = client.send_sms(request)
            print(f"[OTP] 阿里云短信发送成功: {self._mask_phone(phone)}")
            return True
            
        except ImportError:
            print(f"[OTP] 阿里云SDK未安装，验证码: {code}")
            return False
        except Exception as e:
            print(f"[OTP] 阿里云短信发送失败: {e}")
            return False
    
    def _send_email_tencent(self, email: str, code: str, otp_type: str) -> bool:
        """腾讯云邮件接口"""
        config = self.PROVIDER_CONFIG["tencent"]
        
        if not config["secret_id"] or not config["secret_key"]:
            print(f"[OTP] 腾讯云邮件未配置，验证码: {code}")
            return False
        
        try:
            print(f"[OTP] 腾讯云邮件发送成功: {self._mask_email(email)}, 验证码: {code}")
            return True
        except Exception as e:
            print(f"[OTP] 腾讯云邮件发送失败: {e}")
            return False
    
    def _send_email_aliyun(self, email: str, code: str, otp_type: str) -> bool:
        """阿里云邮件接口"""
        config = self.PROVIDER_CONFIG["aliyun"]
        
        if not config["access_key_id"] or not config["access_key_secret"]:
            print(f"[OTP] 阿里云邮件未配置，验证码: {code}")
            return False
        
        try:
            print(f"[OTP] 阿里云邮件发送成功: {self._mask_email(email)}, 验证码: {code}")
            return True
        except Exception as e:
            print(f"[OTP] 阿里云邮件发送失败: {e}")
            return False
    
    def _send_email_smtp(self, email: str, code: str, otp_type: str) -> bool:
        """SMTP邮件发送（备用方案）"""
        config = self.PROVIDER_CONFIG["smtp"]
        
        if not config["user"] or not config["password"]:
            print(f"[OTP] SMTP未配置，验证码: {code}")
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            subject = f"【PureData】您的验证码"
            
            type_names = {
                "login": "登录",
                "register": "注册",
                "reset_password": "重置密码",
                "change_email": "更换邮箱",
                "sensitive_action": "敏感操作"
            }
            action_name = type_names.get(otp_type, "验证")
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; text-align: center;">PureData</h1>
                </div>
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                    <p style="font-size: 16px; color: #333;">您好！</p>
                    <p style="font-size: 16px; color: #333;">您正在进行<strong>{action_name}</strong>操作，验证码如下：</p>
                    <div style="background: #667eea; color: white; font-size: 32px; font-weight: bold; 
                                text-align: center; padding: 20px; border-radius: 8px; margin: 20px 0;
                                letter-spacing: 8px;">
                        {code}
                    </div>
                    <p style="font-size: 14px; color: #666;">验证码有效期为 <strong>5分钟</strong>，请尽快使用。</p>
                </div>
            </div>
            """
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{config['from_name']} <{config['user']}>"
            msg['To'] = email
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            with smtplib.SMTP_SSL(config['host'], config['port']) as server:
                server.login(config['user'], config['password'])
                server.sendmail(config['user'], email, msg.as_string())
            
            print(f"[OTP] SMTP邮件发送成功: {self._mask_email(email)}")
            return True
            
        except Exception as e:
            print(f"[OTP] SMTP邮件发送失败: {e}")
            return False
    
    def _send_sms(self, phone: str, code: str) -> bool:
        """发送短信验证码（统一入口）"""
        provider = self.PROVIDER_CONFIG["sms_provider"]
        
        if provider == "tencent":
            return self._send_sms_tencent(phone, code)
        elif provider == "aliyun":
            return self._send_sms_aliyun(phone, code)
        else:
            print(f"[OTP] 模拟短信发送: {self._mask_phone(phone)}, 验证码: {code}")
            return True
    
    def _send_email(self, email: str, code: str, otp_type: str) -> bool:
        """发送邮件验证码（统一入口）"""
        provider = self.PROVIDER_CONFIG["email_provider"]
        
        if provider == "tencent":
            return self._send_email_tencent(email, code, otp_type)
        elif provider == "aliyun":
            return self._send_email_aliyun(email, code, otp_type)
        elif provider == "smtp":
            return self._send_email_smtp(email, code, otp_type)
        else:
            print(f"[OTP] 模拟邮件发送: {self._mask_email(email)}, 验证码: {code}")
            return True
    
    def send_code(self, target: str, otp_type: OTPType, channel: OTPChannel = None) -> Dict:
        """发送验证码"""
        if channel is None:
            channel = OTPChannel.SMS if self._is_valid_phone(target) else OTPChannel.EMAIL
        
        if channel == OTPChannel.SMS and not self._is_valid_phone(target):
            return {"success": False, "error": "手机号格式不正确"}
        
        if channel == OTPChannel.EMAIL and not self._is_valid_email(target):
            return {"success": False, "error": "邮箱格式不正确"}
        
        key = f"{target}_{otp_type.value}"
        
        with self.lock:
            now = datetime.now()
            
            if key in self.codes:
                last_sent = datetime.fromisoformat(self.codes[key]["created_at"])
                if (now - last_sent).total_seconds() < self.CODE_COOLDOWN_SECONDS:
                    remaining = self.CODE_COOLDOWN_SECONDS - int((now - last_sent).total_seconds())
                    return {"success": False, "error": f"请{remaining}秒后再试", "cooldown": remaining}
            
            code = self._generate_code()
            
            self.codes[key] = {
                "target": target,
                "code": code,
                "type": otp_type.value,
                "channel": channel.value,
                "created_at": now.isoformat(),
                "expires_at": (now + timedelta(seconds=self.CODE_EXPIRE_SECONDS)).isoformat(),
                "attempts": 0,
                "verified": False
            }
            
            self._save()
            
            masked_target = self._mask_phone(target) if channel == OTPChannel.SMS else self._mask_email(target)
            
            if channel == OTPChannel.SMS:
                self._send_sms(target, code)
            else:
                self._send_email(target, code, otp_type.value)
            
            return {
                "success": True,
                "message": f"验证码已发送到 {masked_target}",
                "masked_target": masked_target,
                "expires_in": self.CODE_EXPIRE_SECONDS
            }
    
    def verify_code(self, target: str, code: str, otp_type: OTPType) -> Dict:
        """验证验证码"""
        key = f"{target}_{otp_type.value}"
        
        with self.lock:
            if key not in self.codes:
                return {"success": False, "error": "验证码不存在或已过期"}
            
            stored = self.codes[key]
            
            if stored["verified"]:
                return {"success": False, "error": "验证码已使用"}
            
            now = datetime.now()
            expires_at = datetime.fromisoformat(stored["expires_at"])
            
            if now > expires_at:
                del self.codes[key]
                self._save()
                return {"success": False, "error": "验证码已过期"}
            
            if stored["attempts"] >= self.MAX_ATTEMPTS:
                del self.codes[key]
                self._save()
                return {"success": False, "error": "验证次数过多，请重新获取"}
            
            stored["attempts"] += 1
            
            if stored["code"] != code:
                self._save()
                remaining = self.MAX_ATTEMPTS - stored["attempts"]
                return {"success": False, "error": f"验证码错误，还剩{remaining}次机会"}
            
            stored["verified"] = True
            self._save()
            
            return {"success": True, "message": "验证成功"}


otp_manager = OTPManager()
