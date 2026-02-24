#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
防羊毛党系统
支持: 邮箱验证、IP监控、同IP多账号限制
"""

import json
import os
import re
import time
import secrets
import hashlib
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.request import urlopen
from urllib.error import URLError

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ANTI_ABUSE_FILE = os.path.join(BACKEND_DIR, 'anti_abuse.json')

EMAIL_VERIFICATION_FILE = os.path.join(BACKEND_DIR, 'email_verifications.json')

IP_TRACKING_FILE = os.path.join(BACKEND_DIR, 'ip_tracking.json')

MAX_ACCOUNTS_PER_IP = 3
MAX_REGISTRATIONS_PER_IP_PER_DAY = 5
MAX_VERIFICATION_ATTEMPTS = 3
VERIFICATION_CODE_EXPIRY = 600
SUSPICIOUS_IP_THRESHOLD = 10

class EmailVerifier:
    """邮箱验证器 - 基础层防羊毛"""
    
    def __init__(self):
        self.verifications = {}
        self.lock = threading.Lock()
        self._load()
    
    def _load(self):
        """加载邮箱验证数据 - 带异常处理"""
        if os.path.exists(EMAIL_VERIFICATION_FILE):
            try:
                with open(EMAIL_VERIFICATION_FILE, 'r', encoding='utf-8') as f:
                    self.verifications = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] 加载邮箱验证数据失败: {e}")
                self.verifications = {}
    
    def _save(self):
        """保存邮箱验证数据 - 带异常处理"""
        try:
            with open(EMAIL_VERIFICATION_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.verifications, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] 保存邮箱验证数据失败: {e}")
    
    def validate_email_format(self, email):
        if not email or '@' not in email:
            return False, "邮箱格式无效"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "邮箱格式无效"
        
        disposable_domains = [
            'tempmail.com', 'guerrillamail.com', '10minutemail.com',
            'mailinator.com', 'throwaway.email', 'fakeinbox.com',
            'temp-mail.org', 'dispostable.com', 'mailnesia.com',
            'tempail.com', 'mohmal.com', 'yopmail.com'
        ]
        
        domain = email.split('@')[1].lower()
        if domain in disposable_domains:
            return False, "不支持临时邮箱，请使用正规邮箱"
        
        return True, "邮箱格式有效"
    
    def generate_verification_code(self, email):
        with self.lock:
            valid, msg = self.validate_email_format(email)
            if not valid:
                return {"success": False, "error": msg}
            
            email_lower = email.lower()
            
            if email_lower in self.verifications:
                record = self.verifications[email_lower]
                if record.get('verified', False):
                    return {"success": False, "error": "该邮箱已验证"}
                
                attempts = record.get('attempts', 0)
                if attempts >= MAX_VERIFICATION_ATTEMPTS:
                    last_time = datetime.fromisoformat(record.get('last_attempt', datetime.now().isoformat()))
                    if datetime.now() - last_time < timedelta(hours=1):
                        return {"success": False, "error": "验证尝试次数过多，请1小时后再试"}
            
            code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            
            self.verifications[email_lower] = {
                "code": code,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(seconds=VERIFICATION_CODE_EXPIRY)).isoformat(),
                "verified": False,
                "attempts": self.verifications.get(email_lower, {}).get('attempts', 0)
            }
            
            self._save()
            
            print(f"\n[邮箱验证] 发送到 {email}")
            print(f"  验证码: {code}")
            print(f"  有效期: {VERIFICATION_CODE_EXPIRY}秒\n")
            
            return {
                "success": True,
                "message": f"验证码已发送到 {email}",
                "expires_in": VERIFICATION_CODE_EXPIRY,
                "demo_code": code
            }
    
    def verify_code(self, email, code):
        with self.lock:
            email_lower = email.lower()
            
            if email_lower not in self.verifications:
                return {"success": False, "error": "请先获取验证码"}
            
            record = self.verifications[email_lower]
            
            if record.get('verified', False):
                return {"success": True, "message": "邮箱已验证"}
            
            expires_at = datetime.fromisoformat(record['expires_at'])
            if datetime.now() > expires_at:
                return {"success": False, "error": "验证码已过期，请重新获取"}
            
            record['attempts'] = record.get('attempts', 0) + 1
            record['last_attempt'] = datetime.now().isoformat()
            
            if record['code'] != code:
                remaining = MAX_VERIFICATION_ATTEMPTS - record['attempts']
                self._save()
                return {
                    "success": False, 
                    "error": f"验证码错误，剩余{remaining}次尝试机会"
                }
            
            record['verified'] = True
            record['verified_at'] = datetime.now().isoformat()
            self._save()
            
            return {"success": True, "message": "邮箱验证成功"}
    
    def is_email_verified(self, email):
        email_lower = email.lower()
        if email_lower not in self.verifications:
            return False
        return self.verifications[email_lower].get('verified', False)
    
    def get_verification_status(self, email):
        email_lower = email.lower()
        if email_lower not in self.verifications:
            return {"verified": False, "status": "未验证"}
        
        record = self.verifications[email_lower]
        return {
            "verified": record.get('verified', False),
            "verified_at": record.get('verified_at'),
            "attempts": record.get('attempts', 0)
        }


class IPTracker:
    """IP追踪器 - 中级层防羊毛"""
    
    def __init__(self):
        self.ip_data = {}
        self.lock = threading.Lock()
        self._load()
    
    def _load(self):
        """加载IP追踪数据 - 带异常处理"""
        if os.path.exists(IP_TRACKING_FILE):
            try:
                with open(IP_TRACKING_FILE, 'r', encoding='utf-8') as f:
                    self.ip_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] 加载IP追踪数据失败: {e}")
                self.ip_data = {}
    
    def _save(self):
        """保存IP追踪数据 - 带异常处理"""
        try:
            with open(IP_TRACKING_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.ip_data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] 保存IP追踪数据失败: {e}")
    
    def _clean_old_records(self):
        now = datetime.now()
        for ip in list(self.ip_data.keys()):
            data = self.ip_data[ip]
            if 'first_seen' in data:
                first_seen = datetime.fromisoformat(data['first_seen'])
                if now - first_seen > timedelta(days=30):
                    del self.ip_data[ip]
    
    def record_registration(self, ip, username, email):
        with self.lock:
            self._clean_old_records()
            
            if ip not in self.ip_data:
                self.ip_data[ip] = {
                    "first_seen": datetime.now().isoformat(),
                    "registrations": [],
                    "login_attempts": [],
                    "suspicious_score": 0
                }
            
            self.ip_data[ip]["last_activity"] = datetime.now().isoformat()
            self.ip_data[ip]["registrations"].append({
                "username": username,
                "email": email,
                "timestamp": datetime.now().isoformat()
            })
            
            self._save()
    
    def record_login_attempt(self, ip, username, success):
        with self.lock:
            if ip not in self.ip_data:
                self.ip_data[ip] = {
                    "first_seen": datetime.now().isoformat(),
                    "registrations": [],
                    "login_attempts": [],
                    "suspicious_score": 0
                }
            
            self.ip_data[ip]["last_activity"] = datetime.now().isoformat()
            self.ip_data[ip]["login_attempts"].append({
                "username": username,
                "success": success,
                "timestamp": datetime.now().isoformat()
            })
            
            if not success:
                self.ip_data[ip]["suspicious_score"] = self.ip_data[ip].get("suspicious_score", 0) + 1
            
            self._save()
    
    def check_ip_restrictions(self, ip):
        with self.lock:
            if ip not in self.ip_data:
                return {"allowed": True, "reason": "新IP"}
            
            data = self.ip_data[ip]
            
            registrations = data.get('registrations', [])
            today = datetime.now().date()
            today_registrations = [
                r for r in registrations 
                if datetime.fromisoformat(r['timestamp']).date() == today
            ]
            
            if len(today_registrations) >= MAX_REGISTRATIONS_PER_IP_PER_DAY:
                return {
                    "allowed": False,
                    "reason": f"该IP今日注册次数已达上限({MAX_REGISTRATIONS_PER_IP_PER_DAY}次)"
                }
            
            if len(registrations) >= MAX_ACCOUNTS_PER_IP:
                return {
                    "allowed": False,
                    "reason": f"该IP关联账号已达上限({MAX_ACCOUNTS_PER_IP}个)，请联系客服"
                }
            
            suspicious_score = data.get('suspicious_score', 0)
            if suspicious_score >= SUSPICIOUS_IP_THRESHOLD:
                return {
                    "allowed": False,
                    "reason": "该IP存在异常行为，已被限制"
                }
            
            return {
                "allowed": True,
                "reason": "正常",
                "accounts_count": len(registrations),
                "today_registrations": len(today_registrations)
            }
    
    def get_accounts_by_ip(self, ip):
        with self.lock:
            if ip not in self.ip_data:
                return []
            
            return [
                {
                    "username": r['username'],
                    "email": r['email'],
                    "registered_at": r['timestamp']
                }
                for r in self.ip_data[ip].get('registrations', [])
            ]
    
    def get_ip_stats(self, ip):
        with self.lock:
            if ip not in self.ip_data:
                return {"exists": False}
            
            data = self.ip_data[ip]
            registrations = data.get('registrations', [])
            login_attempts = data.get('login_attempts', [])
            
            failed_logins = [a for a in login_attempts if not a.get('success', True)]
            
            return {
                "exists": True,
                "first_seen": data.get('first_seen'),
                "last_activity": data.get('last_activity'),
                "total_accounts": len(registrations),
                "total_login_attempts": len(login_attempts),
                "failed_login_attempts": len(failed_logins),
                "suspicious_score": data.get('suspicious_score', 0)
            }
    
    def mark_suspicious(self, ip, reason=""):
        with self.lock:
            if ip not in self.ip_data:
                self.ip_data[ip] = {
                    "first_seen": datetime.now().isoformat(),
                    "registrations": [],
                    "login_attempts": [],
                    "suspicious_score": 0
                }
            
            self.ip_data[ip]["suspicious_score"] = self.ip_data[ip].get("suspicious_score", 0) + 5
            self.ip_data[ip]["suspicious_reason"] = reason
            self.ip_data[ip]["marked_suspicious_at"] = datetime.now().isoformat()
            
            self._save()
    
    def whitelist_ip(self, ip):
        with self.lock:
            if ip in self.ip_data:
                self.ip_data[ip]["suspicious_score"] = 0
                self.ip_data[ip]["whitelisted"] = True
                self.ip_data[ip]["whitelisted_at"] = datetime.now().isoformat()
                self._save()
                return True
            return False


class AntiAbuseSystem:
    """防滥用系统 - 统一入口"""
    
    def __init__(self):
        self.email_verifier = EmailVerifier()
        self.ip_tracker = IPTracker()
        self.lock = threading.Lock()
    
    def check_registration(self, email, ip):
        results = {
            "allowed": True,
            "checks": {}
        }
        
        valid, msg = self.email_verifier.validate_email_format(email)
        results["checks"]["email_format"] = {"passed": valid, "message": msg}
        if not valid:
            results["allowed"] = False
            return results
        
        ip_check = self.ip_tracker.check_ip_restrictions(ip)
        results["checks"]["ip_restriction"] = ip_check
        if not ip_check["allowed"]:
            results["allowed"] = False
            return results
        
        return results
    
    def register_user(self, email, ip, username):
        self.ip_tracker.record_registration(ip, username, email)
    
    def send_verification(self, email):
        return self.email_verifier.generate_verification_code(email)
    
    def verify_email(self, email, code):
        return self.email_verifier.verify_code(email, code)
    
    def is_email_verified(self, email):
        return self.email_verifier.is_email_verified(email)
    
    def record_login(self, ip, username, success):
        self.ip_tracker.record_login_attempt(ip, username, success)
    
    def get_ip_info(self, ip):
        return self.ip_tracker.get_ip_stats(ip)
    
    def get_accounts_by_ip(self, ip):
        return self.ip_tracker.get_accounts_by_ip(ip)
    
    def mark_ip_suspicious(self, ip, reason=""):
        self.ip_tracker.mark_suspicious(ip, reason)
    
    def whitelist_ip(self, ip):
        return self.ip_tracker.whitelist_ip(ip)


anti_abuse = AntiAbuseSystem()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("防羊毛党系统测试")
    print("="*60)
    
    print("\n[1] 测试邮箱格式验证...")
    test_emails = [
        ("test@example.com", True),
        ("user.name+tag@gmail.com", True),
        ("test@tempmail.com", False),
        ("invalid-email", False),
    ]
    
    for email, expected in test_emails:
        valid, msg = anti_abuse.email_verifier.validate_email_format(email)
        status = "✓" if valid == expected else "✗"
        print(f"  {status} {email}: {msg}")
    
    print("\n[2] 测试IP限制...")
    test_ip = "192.168.1.100"
    
    for i in range(5):
        result = anti_abuse.ip_tracker.check_ip_restrictions(test_ip)
        if result["allowed"]:
            anti_abuse.ip_tracker.record_registration(test_ip, f"user{i}", f"user{i}@test.com")
            print(f"  注册 user{i}: 允许")
        else:
            print(f"  注册 user{i}: 拒绝 - {result['reason']}")
    
    print("\n[3] 测试邮箱验证...")
    email = "test@example.com"
    result = anti_abuse.send_verification(email)
    print(f"  发送验证码: {result}")
    
    if result["success"]:
        code = result.get("demo_code")
        verify_result = anti_abuse.verify_email(email, code)
        print(f"  验证结果: {verify_result}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
