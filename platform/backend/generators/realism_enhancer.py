#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成器模块 - 真实感增强器
"""

import random
from datetime import datetime, timedelta


class RealismEnhancer:
    """真实感增强器 - 让数据更像真实用户生成"""
    
    TYPOS = {
        'a': ['s', 'q'],
        'e': ['r', 'w'],
        'i': ['o', 'u'],
        'o': ['i', 'p'],
        's': ['a', 'd'],
        'n': ['m', 'b'],
    }
    
    GRAMMAR_ERRORS = {
        "人工智能": [
            (" is ", " be "),
            (" are ", " is "),
            (" the ", " teh "),
            (" a ", " an "),
        ],
        "劳动合同": [
            ("的", "地"),
            ("了", "的"),
            ("在", "再"),
            ("和", "与"),
        ],
        "医疗": [
            (" the ", " teh "),
            (" patient ", " patience "),
        ],
        "金融": [
            (" the ", " teh "),
            (" investment ", " invesment "),
        ]
    }
    
    @staticmethod
    def add_typo(text, probability=0.1):
        if random.random() > probability:
            return text
        
        chars = list(text)
        for i in range(len(chars)):
            if chars[i].lower() in RealismEnhancer.TYPOS and random.random() < 0.05:
                wrong_char = random.choice(RealismEnhancer.TYPOS[chars[i].lower()])
                if chars[i].isupper():
                    wrong_char = wrong_char.upper()
                chars[i] = wrong_char
                break
        
        return ''.join(chars)
    
    @staticmethod
    def add_grammar_error(text, domain, probability=0.15):
        if random.random() > probability:
            return text
        
        errors = RealismEnhancer.GRAMMAR_ERRORS.get(domain, RealismEnhancer.GRAMMAR_ERRORS["人工智能"])
        if not errors:
            return text
        
        wrong_pair = random.choice(errors)
        if wrong_pair[0] in text:
            text = text.replace(wrong_pair[0], wrong_pair[1], 1)
        
        return text
    
    @staticmethod
    def add_timestamp_variation():
        """生成模拟时间戳"""
        base = datetime.now()
        offset = timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        return (base - offset).isoformat()
    
    @staticmethod
    def generate_user_id():
        """生成模拟用户ID"""
        prefixes = ["user", "admin", "expert", "guest", "bot", "ai"]
        return f"{random.choice(prefixes)}_{random.randint(1000, 9999)}"
    
    @staticmethod
    def add_realism(text, domain="人工智能", intensity="medium"):
        intensities = {
            "low": {"typo": 0.03, "grammar": 0.05},
            "medium": {"typo": 0.08, "grammar": 0.12},
            "high": {"typo": 0.15, "grammar": 0.2},
        }
        
        params = intensities.get(intensity, intensities["medium"])
        
        text = RealismEnhancer.add_typo(text, params["typo"])
        text = RealismEnhancer.add_grammar_error(text, domain, params["grammar"])
        
        return text
