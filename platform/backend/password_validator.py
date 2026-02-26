#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码验证器 - 统一的密码验证逻辑
支持：密码强度验证、规则检查、错误提示
"""

import re
from typing import Tuple, Dict, List, Optional
from enum import Enum


class PasswordValidationError(Enum):
    """密码验证错误类型"""
    EMPTY = "empty"
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    MISSING_UPPERCASE = "missing_uppercase"
    MISSING_LOWERCASE = "missing_lowercase"
    MISSING_DIGIT = "missing_digit"


class PasswordStrength(Enum):
    """密码强度等级"""
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class PasswordValidator:
    """密码验证器 - 统一的密码验证逻辑"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    UPPERCASE_PATTERN = r'[A-Z]'
    LOWERCASE_PATTERN = r'[a-z]'
    DIGIT_PATTERN = r'\d'
    SPECIAL_CHAR_PATTERN = r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]'
    
    ERROR_MESSAGES = {
        PasswordValidationError.EMPTY: "密码不能为空",
        PasswordValidationError.TOO_SHORT: f"密码长度至少{MIN_LENGTH}位",
        PasswordValidationError.TOO_LONG: f"密码长度不能超过{MAX_LENGTH}位",
        PasswordValidationError.MISSING_UPPERCASE: "密码需包含大写字母",
        PasswordValidationError.MISSING_LOWERCASE: "密码需包含小写字母",
        PasswordValidationError.MISSING_DIGIT: "密码需包含数字"
    }
    
    @classmethod
    def validate(cls, password: Optional[str], check_complexity: bool = True) -> Tuple[bool, str]:
        """
        验证密码强度
        
        Args:
            password: 待验证的密码
            check_complexity: 是否检查复杂度（大小写、数字），默认True
            
        Returns:
            (是否有效, 错误消息)
        """
        if not password:
            return False, cls.ERROR_MESSAGES[PasswordValidationError.EMPTY]
        
        if len(password) < cls.MIN_LENGTH:
            return False, cls.ERROR_MESSAGES[PasswordValidationError.TOO_SHORT]
        
        if len(password) > cls.MAX_LENGTH:
            return False, cls.ERROR_MESSAGES[PasswordValidationError.TOO_LONG]
        
        if check_complexity:
            if not re.search(cls.UPPERCASE_PATTERN, password):
                return False, cls.ERROR_MESSAGES[PasswordValidationError.MISSING_UPPERCASE]
            
            if not re.search(cls.LOWERCASE_PATTERN, password):
                return False, cls.ERROR_MESSAGES[PasswordValidationError.MISSING_LOWERCASE]
            
            if not re.search(cls.DIGIT_PATTERN, password):
                return False, cls.ERROR_MESSAGES[PasswordValidationError.MISSING_DIGIT]
        
        return True, "密码强度合格"
    
    @classmethod
    def validate_dict(cls, password: Optional[str], check_complexity: bool = True) -> Dict:
        """
        验证密码强度，返回字典格式结果
        
        Args:
            password: 待验证的密码
            check_complexity: 是否检查复杂度
            
        Returns:
            {"valid": bool, "message": str}
        """
        valid, message = cls.validate(password, check_complexity)
        return {"valid": valid, "message": message}
    
    @classmethod
    def validate_success_dict(cls, password: Optional[str], check_complexity: bool = True) -> Dict:
        """
        验证密码强度，返回success格式的字典
        
        Args:
            password: 待验证的密码
            check_complexity: 是否检查复杂度
            
        Returns:
            {"success": bool, "error": str} 或 {"success": True, "message": str}
        """
        valid, message = cls.validate(password, check_complexity)
        if valid:
            return {"success": True, "message": message}
        else:
            return {"success": False, "error": message}
    
    @classmethod
    def validate_with_details(cls, password: Optional[str], check_complexity: bool = True) -> Dict:
        """
        验证密码强度，返回详细结果
        
        Args:
            password: 待验证的密码
            check_complexity: 是否检查复杂度
            
        Returns:
            {
                "valid": bool,
                "message": str,
                "errors": list,
                "strength": str
            }
        """
        errors: List[PasswordValidationError] = []
        
        if not password:
            errors.append(PasswordValidationError.EMPTY)
        else:
            if len(password) < cls.MIN_LENGTH:
                errors.append(PasswordValidationError.TOO_SHORT)
            
            if len(password) > cls.MAX_LENGTH:
                errors.append(PasswordValidationError.TOO_LONG)
            
            if check_complexity:
                if not re.search(cls.UPPERCASE_PATTERN, password):
                    errors.append(PasswordValidationError.MISSING_UPPERCASE)
                
                if not re.search(cls.LOWERCASE_PATTERN, password):
                    errors.append(PasswordValidationError.MISSING_LOWERCASE)
                
                if not re.search(cls.DIGIT_PATTERN, password):
                    errors.append(PasswordValidationError.MISSING_DIGIT)
        
        valid = len(errors) == 0
        message = cls.ERROR_MESSAGES[errors[0]] if errors else "密码强度合格"
        strength = cls._calculate_strength(password, errors) if password else PasswordStrength.WEAK.value
        
        return {
            "valid": valid,
            "message": message,
            "errors": [e.value for e in errors],
            "strength": strength
        }
    
    @classmethod
    def _calculate_strength(cls, password: str, errors: List[PasswordValidationError]) -> str:
        """计算密码强度"""
        if errors:
            return PasswordStrength.WEAK.value
        
        score = 0
        
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        
        if re.search(cls.SPECIAL_CHAR_PATTERN, password):
            score += 1
        
        if len(set(password)) >= len(password) * 0.7:
            score += 1
        
        if score >= 4:
            return PasswordStrength.VERY_STRONG.value
        elif score >= 3:
            return PasswordStrength.STRONG.value
        elif score >= 2:
            return PasswordStrength.MEDIUM.value
        else:
            return PasswordStrength.WEAK.value
    
    @classmethod
    def check_length_only(cls, password: Optional[str], min_length: int = None) -> Tuple[bool, str]:
        """
        仅检查密码长度（用于简单验证场景）
        
        Args:
            password: 待验证的密码
            min_length: 最小长度，默认使用类常量
            
        Returns:
            (是否有效, 错误消息)
        """
        if min_length is None:
            min_length = cls.MIN_LENGTH
            
        if not password:
            return False, "密码不能为空"
        
        if len(password) < min_length:
            return False, f"密码长度至少{min_length}位"
        
        if len(password) > cls.MAX_LENGTH:
            return False, f"密码长度不能超过{cls.MAX_LENGTH}位"
        
        return True, "密码长度合格"


password_validator = PasswordValidator()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("密码验证器测试")
    print("="*60)
    
    test_passwords = [
        ("", False),
        ("123", False),
        ("password", False),
        ("Password", False),
        ("Password1", True),
        ("VeryStrongPassword123!", True),
    ]
    
    print("\n[1] 基础验证测试...")
    for pwd, expected in test_passwords:
        valid, msg = PasswordValidator.validate(pwd)
        status = "✓" if valid == expected else "✗"
        print(f"  {status} '{pwd}': {msg}")
    
    print("\n[2] 详细验证测试...")
    result = PasswordValidator.validate_with_details("Test123!")
    print(f"  结果: {result}")
    
    print("\n[3] 仅长度验证测试...")
    valid, msg = PasswordValidator.check_length_only("123456", min_length=6)
    print(f"  6位密码(min_length=6): {msg}")
    
    print("\n" + "="*60)
    print("密码验证器测试完成")
    print("="*60)
