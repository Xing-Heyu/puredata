#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据安全模块 - 敏感数据检测与脱敏
支持：敏感信息检测、不合规内容过滤、不良数据清洗
"""

import re
import hashlib
import json
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class SensitivityLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DataType(Enum):
    PHONE = "phone"
    EMAIL = "email"
    ID_CARD = "id_card"
    BANK_CARD = "bank_card"
    IP_ADDRESS = "ip_address"
    PASSWORD = "password"
    ADDRESS = "address"
    NAME = "name"
    URL = "url"
    PASSPORT = "passport"
    OFFICER_ID = "officer_id"
    HK_MACAU_PASS = "hk_macau_pass"
    TAIWAN_PASS = "taiwan_pass"
    SOCIAL_SECURITY = "social_security"
    DRIVER_LICENSE = "driver_license"
    CREDIT_CARD = "credit_card"
    CVV = "cvv"
    PLATE_NUMBER = "plate_number"
    WECHAT = "wechat"
    QQ = "qq"
    ALIPAY = "alipay"
    HEALTH_CODE = "health_code"
    MEDICAL_RECORD = "medical_record"
    MEDICAL_INSURANCE = "medical_insurance"
    SALARY = "salary"
    BIRTHDAY = "birthday"
    COMPANY = "company"
    POSITION = "position"
    EDUCATION = "education"
    SCHOOL = "school"
    UNIFIED_SOCIAL_CREDIT = "unified_social_credit"
    ORG_CODE = "org_code"
    TAX_ID = "tax_id"
    STOCK_CODE = "stock_code"
    FUND_ACCOUNT = "fund_account"
    INSURANCE_POLICY = "insurance_policy"
    CONTRACT_NUMBER = "contract_number"
    INVOICE_NUMBER = "invoice_number"
    ORDER_NUMBER = "order_number"
    TRACKING_NUMBER = "tracking_number"
    MAC_ADDRESS = "mac_address"
    IMEI = "imei"
    DEVICE_ID = "device_id"
    GPS_LOCATION = "gps_location"
    FACE_ID = "face_id"
    FINGERPRINT = "fingerprint"
    VOICE_PRINT = "voice_print"
    RETINA = "retina"
    DNA = "dna"
    BLOOD_TYPE = "blood_type"
    MEDICAL_HISTORY = "medical_history"
    DISABILITY = "disability"
    RELIGION = "religion"
    ETHNICITY = "ethnicity"
    POLITICAL_STATUS = "political_status"
    MARITAL_STATUS = "marital_status"
    SEXUAL_ORIENTATION = "sexual_orientation"
    CRIMINAL_RECORD = "criminal_record"
    BANKRUPTCY = "bankruptcy"
    CREDIT_SCORE = "credit_score"
    DEBT = "debt"
    ASSET = "asset"

@dataclass
class SensitiveMatch:
    data_type: DataType
    value: str
    position: Tuple[int, int]
    level: SensitivityLevel
    suggestion: str

@dataclass
class DataCheckResult:
    is_safe: bool
    sensitivity_level: SensitivityLevel
    matches: List[SensitiveMatch]
    cleaned_text: str
    warnings: List[str]
    stats: Dict[str, int] = field(default_factory=dict)

@dataclass
class SanitizationReport:
    total_items: int
    safe_items: int
    sanitized_items: int
    blocked_items: int
    warning_items: int
    sensitive_types_found: Dict[str, int]
    prohibited_words_found: List[str]
    processing_time_ms: float
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "total_items": self.total_items,
            "safe_items": self.safe_items,
            "sanitized_items": self.sanitized_items,
            "blocked_items": self.blocked_items,
            "warning_items": self.warning_items,
            "sensitive_types_found": self.sensitive_types_found,
            "prohibited_words_found": self.prohibited_words_found,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "timestamp": self.timestamp
        }

SENSITIVE_PATTERNS = {
    DataType.PHONE: {
        "patterns": [
            r'1[3-9]\d{9}',
            r'\d{3,4}[-\s]?\d{7,8}',
            r'\(\d{3,4}\)\s*\d{7,8}',
            r'0086[-\s]?\d{11}',
            r'\+86[-\s]?\d{11}',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "手机号已脱敏"
    },
    DataType.EMAIL: {
        "patterns": [
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "邮箱已脱敏"
    },
    DataType.ID_CARD: {
        "patterns": [
            r'\d{17}[\dXx]',
            r'\d{15}',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "身份证号已脱敏"
    },
    DataType.PASSPORT: {
        "patterns": [
            r'[EeGg]\d{8}',
            r'[Pp]\d{7}',
            r'[Dd]\d{7,9}',
            r'[Aa]\d{8}',
            r'[Ss]\d{7,8}',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "护照号已脱敏"
    },
    DataType.OFFICER_ID: {
        "patterns": [
            r'[军]\d{7}',
            r'[文]\d{7}',
            r'[A-Z]\d{6,8}[A-Z]?',
            r'军字第\d{6,8}号',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "军官证已脱敏"
    },
    DataType.HK_MACAU_PASS: {
        "patterns": [
            r'[Cc]\d{8}',
            r'[Hh]\d{8}',
            r'[Mm]\d{8}',
            r'[Ww]\d{8}',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "港澳通行证已脱敏"
    },
    DataType.TAIWAN_PASS: {
        "patterns": [
            r'[Tt]\d{8}',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "台湾通行证已脱敏"
    },
    DataType.SOCIAL_SECURITY: {
        "patterns": [
            r'社保[号：:]\s*\d{18}',
            r'社会保障[号：:]\s*\d{18}',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "社保号已脱敏"
    },
    DataType.DRIVER_LICENSE: {
        "patterns": [
            r'驾驶证[号：:]\s*\d{12}',
            r'驾照[号：:]\s*\d{12}',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "驾驶证号已脱敏"
    },
    DataType.BANK_CARD: {
        "patterns": [
            r'\d{16,19}',
            r'银行卡[号：:]\s*\d{16,19}',
            r'卡号[：:]\s*\d{16,19}',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "银行卡号已脱敏"
    },
    DataType.CREDIT_CARD: {
        "patterns": [
            r'(?:4\d{12}|5[1-5]\d{11}|6\d{15}|3[47]\d{13})',
            r'信用卡[号：:]\s*\d{15,16}',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "信用卡号已脱敏"
    },
    DataType.CVV: {
        "patterns": [
            r'cvv[：:]\s*\d{3,4}',
            r'安全码[：:]\s*\d{3,4}',
            r'cvv2[：:]\s*\d{3,4}',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "CVV已移除"
    },
    DataType.IP_ADDRESS: {
        "patterns": [
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "IP地址已脱敏"
    },
    DataType.PASSWORD: {
        "patterns": [
            r'password\s*[=:：]\s*\S+',
            r'pwd\s*[=:：]\s*\S+',
            r'密码\s*[=:：]\s*\S+',
            r'passwd\s*[=:：]\s*\S+',
            r'口令\s*[=:：]\s*\S+',
            r'登录密码\s*[=:：]\s*\S+',
            r'支付密码\s*[=:：]\s*\S+',
            r'交易密码\s*[=:：]\s*\S+',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "密码信息已移除"
    },
    DataType.PLATE_NUMBER: {
        "patterns": [
            r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼][A-Z][A-HJ-NP-Z0-9]{5,6}',
            r'车牌[号：:]\s*[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼][A-Z][A-HJ-NP-Z0-9]{5,6}',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "车牌号已脱敏"
    },
    DataType.WECHAT: {
        "patterns": [
            r'微信[号：:]\s*[a-zA-Z0-9_-]{6,20}',
            r'微信号[：:]\s*[a-zA-Z0-9_-]{6,20}',
            r'wx[id]_[a-zA-Z0-9]{8,}',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "微信号已脱敏"
    },
    DataType.QQ: {
        "patterns": [
            r'QQ[号：:]\s*\d{5,11}',
            r'qq[号：:]\s*\d{5,11}',
            r'Q[号：:]\s*\d{5,11}',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "QQ号已脱敏"
    },
    DataType.ALIPAY: {
        "patterns": [
            r'支付宝[账号：:]\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'支付宝[账号：:]\s*1[3-9]\d{9}',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "支付宝账号已脱敏"
    },
    DataType.HEALTH_CODE: {
        "patterns": [
            r'健康码[号：:]\s*\S+',
            r'核酸[结果报告：:]\s*[阴阳]性',
            r'核酸检测[结果：:]\s*[阴阳]性',
            r'行程码[：:]\s*\S+',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "健康信息已脱敏"
    },
    DataType.MEDICAL_RECORD: {
        "patterns": [
            r'病历[号：:]\s*\d+',
            r'门诊号[：:]\s*\d+',
            r'住院号[：:]\s*\d+',
            r'就诊号[：:]\s*\d+',
            r'挂号[号：:]\s*\d+',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "病历号已脱敏"
    },
    DataType.MEDICAL_INSURANCE: {
        "patterns": [
            r'医保卡[号：:]\s*\d+',
            r'医保[号：:]\s*\d+',
            r'医疗保险[号：:]\s*\d+',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "医保卡号已脱敏"
    },
    DataType.SALARY: {
        "patterns": [
            r'工资[：:]\s*[\d,]+元?',
            r'月薪[：:]\s*[\d,]+元?',
            r'年薪[：:]\s*[\d,]+元?',
            r'收入[：:]\s*[\d,]+元?',
            r'薪资[：:]\s*[\d,]+元?',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "薪资信息已脱敏"
    },
    DataType.BIRTHDAY: {
        "patterns": [
            r'出生日期[：:]\s*\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?',
            r'生日[：:]\s*\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?',
            r'出生[年月日：:]+\d{4}[-年]\d{1,2}[-月]\d{1,2}',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "出生日期已脱敏"
    },
    DataType.UNIFIED_SOCIAL_CREDIT: {
        "patterns": [
            r'[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}',
            r'统一社会信用代码[：:]\s*[0-9A-HJ-NPQRTUWXY]{18}',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "统一社会信用代码已脱敏"
    },
    DataType.ORG_CODE: {
        "patterns": [
            r'组织机构代码[：:]\s*[0-9A-Z]{8}-?[0-9X]',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "组织机构代码已脱敏"
    },
    DataType.TAX_ID: {
        "patterns": [
            r'纳税人识别号[：:]\s*[0-9A-Z]{15,20}',
            r'税号[：:]\s*[0-9A-Z]{15,20}',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "纳税人识别号已脱敏"
    },
    DataType.MAC_ADDRESS: {
        "patterns": [
            r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})',
            r'MAC[地址：:]\s*([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "MAC地址已脱敏"
    },
    DataType.IMEI: {
        "patterns": [
            r'IMEI[：:]\s*\d{15}',
            r'设备号[：:]\s*\d{15}',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "IMEI已脱敏"
    },
    DataType.GPS_LOCATION: {
        "patterns": [
            r'GPS[：:]\s*\d{1,3}\.\d+[,，]\s*\d{1,3}\.\d+',
            r'经纬度[：:]\s*\d{1,3}\.\d+[,，]\s*\d{1,3}\.\d+',
            r'位置[：:]\s*\d{1,3}\.\d+[,，]\s*\d{1,3}\.\d+',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "GPS位置已脱敏"
    },
    DataType.FACE_ID: {
        "patterns": [
            r'人脸[识别数据：:]\s*\S+',
            r'FaceID[：:]\s*\S+',
            r'面部识别[数据：:]\s*\S+',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "人脸数据已移除"
    },
    DataType.FINGERPRINT: {
        "patterns": [
            r'指纹[数据：:]\s*\S+',
            r'fingerprint[：:]\s*\S+',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "指纹数据已移除"
    },
    DataType.DNA: {
        "patterns": [
            r'DNA[数据序列：:]\s*\S+',
            r'基因[检测数据：:]\s*\S+',
        ],
        "level": SensitivityLevel.CRITICAL,
        "suggestion": "DNA数据已移除"
    },
    DataType.BLOOD_TYPE: {
        "patterns": [
            r'血型[：:]\s*[ABO][AB]?[型]?',
            r'血液型[：:]\s*[ABO][AB]?',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "血型已脱敏"
    },
    DataType.MEDICAL_HISTORY: {
        "patterns": [
            r'病史[：:]\s*\S+',
            r'既往病史[：:]\s*\S+',
            r'家族病史[：:]\s*\S+',
            r'过敏史[：:]\s*\S+',
            r'手术史[：:]\s*\S+',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "病史信息已脱敏"
    },
    DataType.DISABILITY: {
        "patterns": [
            r'残疾证[号：:]\s*\S+',
            r'残疾[等级：:]\s*\S+',
            r'残疾状况[：:]\s*\S+',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "残疾信息已脱敏"
    },
    DataType.RELIGION: {
        "patterns": [
            r'宗教[信仰：:]\s*\S+',
            r'信仰[：:]\s*\S+',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "宗教信仰已脱敏"
    },
    DataType.ETHNICITY: {
        "patterns": [
            r'民族[：:]\s*(汉|蒙古|回|藏|维吾尔|苗|彝|壮|布依|朝鲜|满|侗|瑶|白|土家|哈尼|哈萨克|傣|黎|傈僳|佤|畲|高山|拉祜|水|东乡|纳西|景颇|柯尔克孜|土|达斡尔|仫佬|羌|布朗|撒拉|毛南|仡佬|锡伯|阿昌|普米|塔吉克|怒|乌孜别克|俄罗斯|鄂温克|德昂|保安|裕固|京|塔塔尔|独龙|鄂伦春|赫哲|门巴|珞巴|基诺)',
        ],
        "level": SensitivityLevel.LOW,
        "suggestion": "民族信息已脱敏"
    },
    DataType.POLITICAL_STATUS: {
        "patterns": [
            r'政治面貌[：:]\s*(党员|团员|群众|民主党派)',
            r'党派[：:]\s*\S+',
        ],
        "level": SensitivityLevel.MEDIUM,
        "suggestion": "政治面貌已脱敏"
    },
    DataType.MARITAL_STATUS: {
        "patterns": [
            r'婚姻状况[：:]\s*(已婚|未婚|离异|丧偶)',
            r'婚史[：:]\s*\S+',
        ],
        "level": SensitivityLevel.LOW,
        "suggestion": "婚姻状况已脱敏"
    },
    DataType.CREDIT_SCORE: {
        "patterns": [
            r'征信[分数：:]\s*\d+',
            r'信用分[数：:]\s*\d+',
            r'芝麻信用[分：:]\s*\d+',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "信用分数已脱敏"
    },
    DataType.DEBT: {
        "patterns": [
            r'负债[：:]\s*[\d,]+元?',
            r'欠款[：:]\s*[\d,]+元?',
            r'贷款余额[：:]\s*[\d,]+元?',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "负债信息已脱敏"
    },
    DataType.ASSET: {
        "patterns": [
            r'资产[：:]\s*[\d,]+元?',
            r'存款[：:]\s*[\d,]+元?',
            r'房产[价值：:]\s*[\d,]+元?',
        ],
        "level": SensitivityLevel.HIGH,
        "suggestion": "资产信息已脱敏"
    },
}

PROHIBITED_WORDS = [
    "赌博", "博彩", "六合彩", "时时彩", "私彩", "澳门赌场", "威尼斯人", "金沙", "永利", "美高梅", "新葡京", "葡京",
    "百家乐", "二十一点", "老虎机", "轮盘", "押注", "下注", "庄家", "闲家", "龙虎斗", "牛牛", "炸金花",
    "代开发票", "买卖发票", "虚开发票", "开票", "发票代办", "增值税发票", "专用发票", "普通发票",
    "套现", "洗钱", "非法集资", "传销", "庞氏骗局", "资金盘", "拆分盘", "返利盘",
    "枪支", "弹药", "爆炸物", "管制刀具", "迷药", "听话水", "催情药", "春药", "迷魂药",
    "毒品", "贩毒", "吸毒", "冰毒", "海洛因", "大麻", "K粉", "摇头丸", "可卡因", "吗啡", "鸦片",
    "邪教", "法轮功", "全能神", "呼喊派", "门徒会", "统一教", "科学教",
    "诈骗", "骗贷", "信用卡套现", "网贷", "高利贷", "套路贷", "校园贷", "裸贷", "714高炮",
    "代孕", "买卖器官", "卵子交易", "代孕妈妈", "试管代孕",
    "假币", "伪造证件", "办证刻章", "假证", "假文凭", "假学历",
    "黑客", "木马", "病毒", "钓鱼网站", "盗号", "撞库", "拖库", "洗库",
    "水军", "刷单", "刷评", "刷量", "买粉", "买赞", "买流量", "买评论",
    "代考", "代写论文", "论文代发", "论文买卖", "学术不端",
    "私服", "外挂", "游戏币交易", "游戏代练", "游戏账号买卖",
    "色情", "裸聊", "约炮", "一夜情", "招嫖", "卖淫", "嫖娼", "红灯区",
    "偷拍", "针孔摄像头", "偷窥", "窃听", "窃照",
    "暴力", "恐怖", "爆炸", "杀人", "绑架", "勒索", "劫持",
    "种族歧视", "地域歧视", "性别歧视", "仇恨言论",
    "反华", "分裂", "台独", "藏独", "疆独", "港独",
    "法轮", "明慧网", "九评", "退党", "退团", "退队",
    "六四", "天安门", "学运", "民运",
    "活摘", "集中营", "迫害",
    "翻墙", "VPN", "代理", "GFW", "防火墙",
    "比特币洗钱", "虚拟货币洗钱", "数字货币交易",
    "内幕交易", "操纵股价", "老鼠仓",
    "偷税漏税", "逃税", "避税天堂",
    "非法移民", "偷渡", "蛇头",
    "人体实验", "生化武器", "细菌战",
    "儿童色情", "未成年人保护", "虐童",
    "动物虐待", "虐杀动物",
    "自杀", "自残", "厌世",
    "造谣", "传谣", "虚假信息", "假新闻",
    "网络暴力", "人肉搜索", "网络欺凌",
    "侵犯隐私", "泄露隐私", "隐私买卖",
    "数据泄露", "数据买卖", "信息贩卖",
    "网络攻击", "DDoS", "CC攻击", "SQL注入",
    "零日漏洞", "漏洞利用", "渗透测试",
    "社工库", "开盒", "人肉",
    "薅羊毛", "漏洞刷单", "优惠券套现",
    "恶意退款", "职业差评", "恶意投诉",
    "仿冒品牌", "假冒伪劣", "山寨",
    "走私", "逃汇", "套汇",
    "洗稿", "抄袭", "侵权",
    "非法行医", "假药", "保健品诈骗",
    "非法集资", "非法吸收存款", "集资诈骗",
]

INAPPROPRIATE_PATTERNS = [
    r'[色情].{0,10}[视频|图片|网站|直播|小说]',
    r'[赌博|博彩].{0,10}[网站|平台|APP|app|软件]',
    r'[代开|买卖].{0,5}发票',
    r'刷.{0,5}单',
    r'兼职.{0,10}日结',
    r'日赚.{0,5}[百千万]',
    r'月入.{0,5}[百千万]',
    r'躺赚|躺赢|睡后收入',
    r'免费领取.{0,10}红包',
    r'点击.{0,5}领取',
    r'加微信.{0,10}领',
    r'扫码.{0,5}领',
    r'限时.{0,5}免费',
    r'仅限今天',
    r'最后.{0,5}名额',
    r'错过.{0,5}后悔',
    r'机会.{0,5}难得',
    r'内部.{0,5}渠道',
    r'特殊.{0,5}关系',
    r'代.{0,5}办.{0,5}证',
    r'包.{0,5}过',
    r'包.{0,5}中',
    r'稳.{0,5}赚',
    r'必.{0,5}赚',
    r'100%.{0,5}通过',
    r'无.{0,5}门槛',
    r'零.{0,5}风险',
    r'保.{0,5}收益',
    r'高.{0,5}回报',
    r'投.{0,5}资.{0,5}返.{0,5}利',
    r'充.{0,5}值.{0,5}返.{0,5}现',
    r'推.{0,5}荐.{0,5}返.{0,5}佣',
    r'拉.{0,5}人.{0,5}头',
    r'发.{0,5}展.{0,5}下.{0,5}线',
    r'团.{0,5}队.{0,5}奖.{0,5}金',
    r'动.{0,5}态.{0,5}奖.{0,5}金',
    r'静.{0,5}态.{0,5}收.{0,5}益',
    r'复.{0,5}投',
    r'倍.{0,5}增',
    r'裂.{0,5}变',
    r'私.{0,5}募',
    r'内.{0,5}幕',
    r'消.{0,5}息',
    r'渠.{0,5}道',
]

class DataSanitizer:
    """数据安全处理器"""
    
    def __init__(self, strict_mode: bool = True, custom_rules: Optional[Dict] = None):
        self.strict_mode = strict_mode
        self.custom_rules = custom_rules or {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        self.compiled_patterns = {}
        for data_type, config in SENSITIVE_PATTERNS.items():
            self.compiled_patterns[data_type] = [
                (re.compile(p, re.IGNORECASE), config["level"], config["suggestion"])
                for p in config["patterns"]
            ]
        
        self.compiled_prohibited = [
            re.compile(re.escape(word), re.IGNORECASE) for word in PROHIBITED_WORDS
        ]
        
        self.compiled_inappropriate = [
            re.compile(p, re.IGNORECASE) for p in INAPPROPRIATE_PATTERNS
        ]
        
        if self.custom_rules:
            for rule_name, rule_config in self.custom_rules.items():
                patterns = rule_config.get("patterns", [])
                level = SensitivityLevel(rule_config.get("level", "medium"))
                suggestion = rule_config.get("suggestion", "已脱敏")
                self.compiled_patterns[rule_name] = [
                    (re.compile(p, re.IGNORECASE), level, suggestion)
                    for p in patterns
                ]
    
    def add_custom_rule(self, name: str, patterns: List[str], level: str = "medium", suggestion: str = "已脱敏"):
        """添加自定义脱敏规则"""
        self.custom_rules[name] = {
            "patterns": patterns,
            "level": level,
            "suggestion": suggestion
        }
        self.compiled_patterns[name] = [
            (re.compile(p, re.IGNORECASE), SensitivityLevel(level), suggestion)
            for p in patterns
        ]
    
    def check_sensitive(self, text: str) -> List[SensitiveMatch]:
        matches = []
        
        for data_type, patterns in self.compiled_patterns.items():
            for pattern, level, suggestion in patterns:
                for match in pattern.finditer(text):
                    matches.append(SensitiveMatch(
                        data_type=data_type if isinstance(data_type, DataType) else DataType.PHONE,
                        value=match.group(),
                        position=(match.start(), match.end()),
                        level=level,
                        suggestion=suggestion
                    ))
        
        return matches
    
    def check_prohibited(self, text: str) -> List[str]:
        found = []
        for pattern in self.compiled_prohibited:
            match = pattern.search(text)
            if match:
                found.append(match.group())
        return found
    
    def check_inappropriate(self, text: str) -> List[str]:
        found = []
        for pattern in self.compiled_inappropriate:
            match = pattern.search(text)
            if match:
                found.append(match.group())
        return found
    
    def mask_phone(self, phone: str) -> str:
        if len(phone) >= 11:
            return phone[:3] + "****" + phone[-4:]
        return phone[:2] + "***" + phone[-2:] if len(phone) >= 4 else "***"
    
    def mask_email(self, email: str) -> str:
        if "@" in email:
            parts = email.split("@")
            if len(parts[0]) > 2:
                return parts[0][:2] + "***@" + parts[1]
            return "***@" + parts[1]
        return "***"
    
    def mask_id_card(self, id_card: str) -> str:
        if len(id_card) >= 15:
            return id_card[:6] + "********" + id_card[-4:]
        return "****"
    
    def mask_passport(self, passport: str) -> str:
        if len(passport) >= 8:
            return passport[:2] + "****" + passport[-2:]
        return "****"
    
    def mask_bank_card(self, card: str) -> str:
        if len(card) >= 8:
            return card[:4] + "****" + card[-4:]
        return "****"
    
    def mask_ip(self, ip: str) -> str:
        parts = ip.split(".")
        if len(parts) == 4:
            return parts[0] + "." + parts[1] + ".*.*"
        return "***"
    
    def mask_plate(self, plate: str) -> str:
        if len(plate) >= 7:
            return plate[:2] + "***" + plate[-2:]
        return "****"
    
    def mask_qq(self, qq: str) -> str:
        if len(qq) >= 5:
            return qq[:2] + "***" + qq[-2:]
        return "***"
    
    def mask_wechat(self, wechat: str) -> str:
        if len(wechat) >= 6:
            return wechat[:2] + "***" + wechat[-2:]
        return "***"
    
    def mask_generic(self, value: str) -> str:
        if len(value) >= 8:
            return value[:2] + "****" + value[-2:]
        return "****"
    
    def sanitize_text(self, text: str) -> Tuple[str, List[SensitiveMatch]]:
        matches = self.check_sensitive(text)
        sanitized = text
        
        mask_functions = {
            DataType.PHONE: self.mask_phone,
            DataType.EMAIL: self.mask_email,
            DataType.ID_CARD: self.mask_id_card,
            DataType.BANK_CARD: self.mask_bank_card,
            DataType.IP_ADDRESS: self.mask_ip,
            DataType.PASSWORD: lambda x: "[已移除]",
            DataType.PASSPORT: self.mask_passport,
            DataType.OFFICER_ID: self.mask_passport,
            DataType.HK_MACAU_PASS: self.mask_passport,
            DataType.TAIWAN_PASS: self.mask_passport,
            DataType.SOCIAL_SECURITY: self.mask_id_card,
            DataType.DRIVER_LICENSE: self.mask_id_card,
            DataType.CREDIT_CARD: self.mask_bank_card,
            DataType.CVV: lambda x: "[已移除]",
            DataType.PLATE_NUMBER: self.mask_plate,
            DataType.WECHAT: self.mask_wechat,
            DataType.QQ: self.mask_qq,
            DataType.ALIPAY: self.mask_generic,
            DataType.HEALTH_CODE: lambda x: "[已脱敏]",
            DataType.MEDICAL_RECORD: self.mask_generic,
            DataType.MEDICAL_INSURANCE: self.mask_generic,
            DataType.SALARY: lambda x: "[已脱敏]",
            DataType.BIRTHDAY: lambda x: "[已脱敏]",
            DataType.UNIFIED_SOCIAL_CREDIT: self.mask_generic,
            DataType.ORG_CODE: self.mask_generic,
            DataType.TAX_ID: self.mask_generic,
            DataType.MAC_ADDRESS: self.mask_generic,
            DataType.IMEI: self.mask_generic,
            DataType.GPS_LOCATION: lambda x: "[已脱敏]",
            DataType.FACE_ID: lambda x: "[已移除]",
            DataType.FINGERPRINT: lambda x: "[已移除]",
            DataType.DNA: lambda x: "[已移除]",
            DataType.BLOOD_TYPE: lambda x: "[已脱敏]",
            DataType.MEDICAL_HISTORY: lambda x: "[已脱敏]",
            DataType.DISABILITY: lambda x: "[已脱敏]",
            DataType.RELIGION: lambda x: "[已脱敏]",
            DataType.ETHNICITY: lambda x: "[已脱敏]",
            DataType.POLITICAL_STATUS: lambda x: "[已脱敏]",
            DataType.MARITAL_STATUS: lambda x: "[已脱敏]",
            DataType.CREDIT_SCORE: lambda x: "[已脱敏]",
            DataType.DEBT: lambda x: "[已脱敏]",
            DataType.ASSET: lambda x: "[已脱敏]",
        }
        
        sorted_matches = sorted(matches, key=lambda m: m.position[0], reverse=True)
        
        for match in sorted_matches:
            if match.data_type in mask_functions:
                masked = mask_functions[match.data_type](match.value)
                sanitized = sanitized[:match.position[0]] + masked + sanitized[match.position[1]:]
        
        return sanitized, matches
    
    def check_data(self, text: str) -> DataCheckResult:
        sanitized, sensitive_matches = self.sanitize_text(text)
        prohibited = self.check_prohibited(text)
        inappropriate = self.check_inappropriate(text)
        
        warnings = []
        stats = {
            "sensitive_count": len(sensitive_matches),
            "prohibited_count": len(prohibited),
            "inappropriate_count": len(inappropriate)
        }
        
        if prohibited:
            warnings.append(f"发现违禁词: {', '.join(prohibited[:3])}")
        
        if inappropriate:
            warnings.append(f"发现不当内容: {', '.join(inappropriate[:3])}")
        
        max_level = SensitivityLevel.SAFE
        for match in sensitive_matches:
            if match.level.value > max_level.value:
                max_level = match.level
        
        is_safe = len(prohibited) == 0 and len(inappropriate) == 0
        
        if self.strict_mode and prohibited:
            is_safe = False
        
        return DataCheckResult(
            is_safe=is_safe,
            sensitivity_level=max_level,
            matches=sensitive_matches,
            cleaned_text=sanitized,
            warnings=warnings,
            stats=stats
        )
    
    def process_batch(self, items: List[Dict], text_field: str = "text") -> Tuple[List[Dict], Dict]:
        processed = []
        stats = {
            "total": len(items),
            "safe": 0,
            "warning": 0,
            "blocked": 0,
            "sanitized": 0
        }
        
        for item in items:
            if text_field not in item:
                processed.append(item)
                stats["safe"] += 1
                continue
            
            result = self.check_data(item[text_field])
            
            if not result.is_safe:
                stats["blocked"] += 1
                if self.strict_mode:
                    continue
            
            if result.matches:
                stats["sanitized"] += 1
                item[text_field] = result.cleaned_text
            
            if result.warnings:
                stats["warning"] += 1
                item["_warnings"] = result.warnings
            
            item["_sensitivity_level"] = result.sensitivity_level.value
            
            processed.append(item)
        
        return processed, stats
    
    def generate_report(self, items: List[Dict], text_field: str = "text") -> SanitizationReport:
        """生成脱敏报告"""
        start_time = datetime.now()
        
        processed, stats = self.process_batch(items, text_field)
        
        sensitive_types = {}
        prohibited_found = []
        
        for item in items:
            if text_field in item:
                result = self.check_data(item[text_field])
                for match in result.matches:
                    type_name = match.data_type.value
                    sensitive_types[type_name] = sensitive_types.get(type_name, 0) + 1
                prohibited = self.check_prohibited(item[text_field])
                prohibited_found.extend(prohibited)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return SanitizationReport(
            total_items=stats["total"],
            safe_items=stats["safe"],
            sanitized_items=stats["sanitized"],
            blocked_items=stats["blocked"],
            warning_items=stats["warning"],
            sensitive_types_found=sensitive_types,
            prohibited_words_found=list(set(prohibited_found)),
            processing_time_ms=processing_time,
            timestamp=datetime.now().isoformat()
        )

sanitizer = DataSanitizer()

def sanitize_data(data: List[Dict], text_field: str = "text") -> Tuple[List[Dict], Dict]:
    return sanitizer.process_batch(data, text_field)

def check_text(text: str) -> DataCheckResult:
    return sanitizer.check_data(text)

def generate_sanitization_report(data: List[Dict], text_field: str = "text") -> SanitizationReport:
    return sanitizer.generate_report(data, text_field)

def add_custom_sanitization_rule(name: str, patterns: List[str], level: str = "medium", suggestion: str = "已脱敏"):
    sanitizer.add_custom_rule(name, patterns, level, suggestion)

if __name__ == "__main__":
    test_cases = [
        "我的手机号是13812345678，邮箱是test@example.com",
        "身份证号：110101199001011234",
        "银行卡：6222021234567890123",
        "护照号：E12345678",
        "港澳通行证：C12345678",
        "车牌号：京A12345",
        "微信号：wx123456",
        "QQ号：12345678",
        "这是一条正常的数据",
        "赌博网站推荐，点击进入",
        "信用卡：4111111111111111，CVV：123",
        "工资：15000元，年薪：20万",
        "出生日期：1990年01月01日",
        "医保卡号：1234567890",
        "病历号：2023010001",
        "核酸检测结果：阴性",
        "GPS位置：116.404,39.915",
        "人脸识别数据：xxxxx",
        "征信分数：750",
        "民族：汉族，政治面貌：党员",
    ]
    
    print("="*60)
    print("数据安全检测测试")
    print("="*60)
    
    for text in test_cases:
        result = check_text(text)
        print(f"\n原文: {text}")
        print(f"安全: {result.is_safe}")
        print(f"敏感级别: {result.sensitivity_level.value}")
        print(f"脱敏后: {result.cleaned_text}")
        if result.warnings:
            print(f"警告: {result.warnings}")
        if result.stats:
            print(f"统计: {result.stats}")
