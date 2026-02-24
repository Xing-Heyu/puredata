#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
噪音生成器 - 多样化噪音类型
支持: OCR错误、ASR错误、拼写错误、格式混乱、口语化插入
包含: 噪音分类标签、强度梯度控制、场景特定噪音
"""

import random
import re
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

class NoiseType(Enum):
    OCR_ERROR = "ocr_error"
    ASR_ERROR = "asr_error"
    SPELLING_ERROR = "spelling_error"
    FORMAT_CHAOS = "format_chaos"
    COLLOQUIAL_INSERT = "colloquial_insert"
    PREFIX_MARKER = "prefix_marker"
    EMOJI = "emoji"
    CAPITALIZATION_ERROR = "capitalization_error"
    PUNCTUATION_ERROR = "punctuation_error"
    WHITESPACE_ERROR = "whitespace_error"
    MIXED_LANGUAGE = "mixed_language"
    ABBREVIATION = "abbreviation"
    HANDWRITING_SIM = "handwriting_sim"
    ENVIRONMENT_NOISE = "environment_noise"

class NoiseLevel(Enum):
    CLEAN = 0
    LIGHT = 1
    MEDIUM = 2
    HEAVY = 3
    EXTREME = 4

@dataclass
class NoiseResult:
    text_clean: str
    text_noisy: str
    noise_types: List[str] = field(default_factory=list)
    noise_level: int = 0
    noise_details: Dict[str, Any] = field(default_factory=dict)

class OCRNoiseGenerator:
    """OCR错误生成器 - 模拟扫描文档识别错误"""
    
    OCR_ERROR_MAP = {
        'a': ['@', '4', 'o', 'q'],
        'e': ['3', 'c'],
        'i': ['1', 'l', '|', '!', 'j'],
        'o': ['0', 'O', 'Q', 'a'],
        's': ['5', '$', 'z'],
        't': ['7', '+', 'f'],
        'l': ['1', 'i', '|', 'I'],
        'b': ['6', '8', 'h'],
        'g': ['9', 'q', 'p'],
        'd': ['cl', 'ol'],
        'm': ['rn', 'nn'],
        'rn': ['m'],
        'vv': ['w'],
        'w': ['vv'],
        'ck': ['k', 'c'],
        'ph': ['f'],
        'tion': ['tian', 'tian'],
    }
    
    MEDICAL_OCR_ERRORS = {
        'patient': ['patlent', 'patlent', 'patient'],
        'medicine': ['medlcine', 'medicme'],
        'treatment': ['treatment', 'treatrnent'],
        'diagnosis': ['diagnosls', 'diagnosl5'],
        'symptom': ['symptorn', 'syniptom'],
        'clinical': ['cllnical', 'clinica1'],
        'hospital': ['hospita1', 'hospitaI'],
        'doctor': ['doctar', 'doct0r'],
        'disease': ['diseasc', 'disea5e'],
    }
    
    FINANCIAL_OCR_ERRORS = {
        'investment': ['investrnent', 'lnvestment'],
        'portfolio': ['portfollo', 'portfo1io'],
        'transaction': ['transactian', 'transactlon'],
        'securities': ['securitles', 'securitles'],
        'dividend': ['dlvidend', 'divldend'],
    }
    
    def add_ocr_noise(self, text: str, domain: str = "人工智能", intensity: float = 0.1) -> Tuple[str, List[str]]:
        result = text
        applied_noises = []
        
        domain_errors = {}
        if domain == "医疗":
            domain_errors = self.MEDICAL_OCR_ERRORS
        elif domain == "金融":
            domain_errors = self.FINANCIAL_OCR_ERRORS
        
        for correct, errors in domain_errors.items():
            if correct in result.lower() and random.random() < intensity:
                error = random.choice(errors)
                result = re.sub(correct, error, result, count=1, flags=re.IGNORECASE)
                applied_noises.append(NoiseType.OCR_ERROR.value)
        
        chars = list(result)
        for i, char in enumerate(chars):
            if char.lower() in self.OCR_ERROR_MAP and random.random() < intensity * 0.3:
                error_char = random.choice(self.OCR_ERROR_MAP[char.lower()])
                if char.isupper():
                    error_char = error_char.upper()
                chars[i] = error_char
                if NoiseType.OCR_ERROR.value not in applied_noises:
                    applied_noises.append(NoiseType.OCR_ERROR.value)
        
        return ''.join(chars), applied_noises

class ASRNoiseGenerator:
    """ASR错误生成器 - 模拟语音识别错误"""
    
    ASR_ERROR_MAP = {
        'patient': ['pay-shunt', 'pay-shent', 'pei-shent'],
        'treatment': ['tree-t-ment', 'treet-ment'],
        'medicine': ['med-i-sin', 'med-uh-sin'],
        'diagnosis': ['di-ag-no-sis', 'diag-nosis'],
        'symptom': ['simp-tum', 'sim-tom'],
        'doctor': ['doc-tor', 'dock-ter'],
        'hospital': ['hos-pi-tal', 'hos-pit-al'],
        'clinical': ['clin-i-cal', 'klin-i-cal'],
        'disease': ['dis-ease', 'diz-ease'],
        'treatment': ['treet-ment', 'treat-ment'],
        'analysis': ['a-nal-y-sis', 'anal-i-sis'],
        'research': ['re-search', 'ree-search'],
        'development': ['de-vel-op-ment', 'dev-el-op-ment'],
        'management': ['man-age-ment', 'man-aj-ment'],
        'investment': ['in-vest-ment', 'in-ves-ment'],
    }
    
    PHONETIC_ERRORS = {
        'th': ['t', 'd', 'f'],
        'ph': ['f'],
        'tion': ['shun', 'sion'],
        'ough': ['ow', 'off', 'uff'],
        'ight': ['ite', 'ite'],
    }
    
    def add_asr_noise(self, text: str, intensity: float = 0.1) -> Tuple[str, List[str]]:
        result = text
        applied_noises = []
        
        for correct, errors in self.ASR_ERROR_MAP.items():
            if correct in result.lower() and random.random() < intensity:
                error = random.choice(errors)
                result = re.sub(correct, error, result, count=1, flags=re.IGNORECASE)
                if NoiseType.ASR_ERROR.value not in applied_noises:
                    applied_noises.append(NoiseType.ASR_ERROR.value)
        
        for correct, errors in self.PHONETIC_ERRORS.items():
            if correct in result.lower() and random.random() < intensity * 0.5:
                error = random.choice(errors)
                result = re.sub(correct, error, result, count=1, flags=re.IGNORECASE)
                if NoiseType.ASR_ERROR.value not in applied_noises:
                    applied_noises.append(NoiseType.ASR_ERROR.value)
        
        return result, applied_noises

class SpellingNoiseGenerator:
    """拼写错误生成器 - 模拟人工输入错误"""
    
    COMMON_TYPOS = {
        'the': ['teh', 'hte', 'th'],
        'and': ['adn', 'nad', 'an'],
        'that': ['taht', 'thta', 'htat'],
        'with': ['wiht', 'wtih', 'wthi'],
        'this': ['tihs', 'htis', 'thsi'],
        'from': ['form', 'frmo', 'fomr'],
        'have': ['ahve', 'haev', 'hvae'],
        'are': ['aer', 'rae', 'rea'],
        'been': ['ebne', 'bene', 'been'],
        'their': ['thier', 'tehir', 'their'],
        'would': ['woudl', 'wolud', 'wulod'],
        'could': ['coudl', 'cluod', 'culod'],
        'should': ['shoudl', 'shuold', 'sholud'],
        'about': ['abuot', 'baout', 'abotu'],
        'which': ['whcih', 'wich', 'whihc'],
        'other': ['otehr', 'otehr', 'othre'],
        'people': ['peolpe', 'pepole', 'poeple'],
        'because': ['becuase', 'beacuse', 'becasue'],
        'important': ['importnat', 'improtant', 'imporatnt'],
        'information': ['inforamtion', 'infomration', 'informatoin'],
    }
    
    DOMAIN_TYPOS = {
        "医疗": {
            'patient': ['patent', 'patint', 'pateint'],
            'treatment': ['treatement', 'tretment', 'treatmnt'],
            'medicine': ['medcine', 'medicne', 'medicin'],
            'diagnosis': ['diagnosos', 'diagnosiss', 'diagnsis'],
            'hospital': ['hospitol', 'hospitel', 'hospial'],
        },
        "金融": {
            'investment': ['investmant', 'invetment', 'investmnt'],
            'portfolio': ['portfolo', 'portfollio', 'portfolo'],
            'transaction': ['transacton', 'transactin', 'transactoin'],
            'dividend': ['divident', 'devidend', 'dividand'],
        },
        "劳动合同": {
            'contract': ['contarct', 'contrat', 'contact'],
            'employee': ['emplyee', 'employe', 'empolyee'],
            'employer': ['emplyer', 'employr', 'emplyoer'],
            'salary': ['salery', 'sallary', 'salry'],
        },
    }
    
    KEYBOARD_ADJACENT = {
        'a': ['q', 's', 'z'],
        'b': ['v', 'g', 'h', 'n'],
        'c': ['x', 'd', 'f', 'v'],
        'd': ['s', 'e', 'r', 'f', 'c', 'x'],
        'e': ['w', 'r', 'd', 's'],
        'f': ['d', 'r', 't', 'g', 'v', 'c'],
        'g': ['f', 't', 'y', 'h', 'b', 'v'],
        'h': ['g', 'y', 'u', 'j', 'n', 'b'],
        'i': ['u', 'o', 'k', 'j'],
        'j': ['h', 'u', 'i', 'k', 'm', 'n'],
        'k': ['j', 'i', 'l', 'm'],
        'l': ['k', 'o', 'p'],
        'm': ['n', 'j', 'k'],
        'n': ['b', 'h', 'j', 'm'],
        'o': ['i', 'p', 'l', 'k'],
        'p': ['o', 'l'],
        'q': ['w', 'a', 's'],
        'r': ['e', 't', 'f', 'd'],
        's': ['a', 'w', 'd', 'x', 'z'],
        't': ['r', 'y', 'g', 'f'],
        'u': ['y', 'i', 'j', 'h'],
        'v': ['c', 'f', 'g', 'b'],
        'w': ['q', 'e', 's', 'a'],
        'x': ['z', 's', 'd', 'c'],
        'y': ['t', 'u', 'h', 'g'],
        'z': ['a', 's', 'x'],
    }
    
    def add_spelling_noise(self, text: str, domain: str = "人工智能", intensity: float = 0.1) -> Tuple[str, List[str]]:
        result = text
        applied_noises = []
        
        all_typos = {**self.COMMON_TYPOS}
        if domain in self.DOMAIN_TYPOS:
            all_typos.update(self.DOMAIN_TYPOS[domain])
        
        for correct, errors in all_typos.items():
            if correct in result.lower() and random.random() < intensity:
                error = random.choice(errors)
                result = re.sub(r'\b' + correct + r'\b', error, result, count=1, flags=re.IGNORECASE)
                if NoiseType.SPELLING_ERROR.value not in applied_noises:
                    applied_noises.append(NoiseType.SPELLING_ERROR.value)
        
        words = result.split()
        for i, word in enumerate(words):
            if len(word) > 2 and random.random() < intensity * 0.2:
                chars = list(word)
                pos = random.randint(1, len(chars) - 2)
                char = chars[pos].lower()
                if char in self.KEYBOARD_ADJACENT:
                    chars[pos] = random.choice(self.KEYBOARD_ADJACENT[char])
                    words[i] = ''.join(chars)
                    if NoiseType.SPELLING_ERROR.value not in applied_noises:
                        applied_noises.append(NoiseType.SPELLING_ERROR.value)
        
        return ' '.join(words), applied_noises

class FormatNoiseGenerator:
    """格式混乱生成器 - 模拟网页爬取数据"""
    
    PREFIX_MARKERS = [
        "注：", "注意：", "Note:", "Note: ", "# ", "## ", "※ ", "★ ", "☆ ",
        "📌 ", "⚡ ", "💡 ", "⚠️ ", "📝 ", "👉 ", "【", "〔", "［",
        "Ref[", "参考[", "来源:", "Source:", "Step ", "步骤",
    ]
    
    SUFFIX_MARKERS = [
        " 等", "等等", "……", "...", "（续）", "(cont.)",
        " [补充说明]", " [参考]", " (continued)", "（未完）",
    ]
    
    EMOJIS = ["📌", "⚡", "💡", "⚠️", "📝", "👉", "✅", "❌", "🔥", "💪", "👍", "🎯"]
    
    def add_format_noise(self, text: str, intensity: float = 0.1) -> Tuple[str, List[str]]:
        result = text
        applied_noises = []
        
        if random.random() < intensity:
            prefix = random.choice(self.PREFIX_MARKERS)
            result = prefix + result
            applied_noises.append(NoiseType.PREFIX_MARKER.value)
        
        if random.random() < intensity * 0.5:
            emoji = random.choice(self.EMOJIS)
            if random.random() < 0.5:
                result = emoji + " " + result
            else:
                result = result + " " + emoji
            applied_noises.append(NoiseType.EMOJI.value)
        
        if random.random() < intensity * 0.3:
            suffix = random.choice(self.SUFFIX_MARKERS)
            result = result + suffix
            if NoiseType.FORMAT_CHAOS.value not in applied_noises:
                applied_noises.append(NoiseType.FORMAT_CHAOS.value)
        
        if random.random() < intensity * 0.2:
            words = result.split()
            if len(words) > 3:
                insert_pos = random.randint(1, len(words) - 1)
                words.insert(insert_pos, "\n")
                result = ' '.join(words).replace(" \n ", "\n")
                if NoiseType.WHITESPACE_ERROR.value not in applied_noises:
                    applied_noises.append(NoiseType.WHITESPACE_ERROR.value)
        
        return result, applied_noises

class ColloquialNoiseGenerator:
    """口语化插入生成器 - 模拟真实对话"""
    
    COLLOQUIAL_INSERTIONS = {
        "人工智能": [
            "呃...这个...", "嗯...", "怎么说呢...", "其实吧...",
            "你懂的...", "简单来说...", "就是...", "那个...",
        ],
        "医疗": [
            "呃...病人...", "嗯...这个症状...", "怎么说呢...",
            "临床上...", "一般来讲...", "通俗点说...",
        ],
        "金融": [
            "呃...投资...", "嗯...市场...", "怎么说呢...",
            "简单说...", "实际上...", "通俗点讲...",
        ],
        "劳动合同": [
            "呃...合同...", "嗯...条款...", "怎么说呢...",
            "法律上...", "简单说...", "一般情况...",
        ],
    }
    
    HESITATIONS = [
        "呃...", "嗯...", "啊...", "这个...", "那个...",
        "怎么说呢...", "让我想想...", "等一下...",
    ]
    
    def add_colloquial_noise(self, text: str, domain: str = "人工智能", intensity: float = 0.1) -> Tuple[str, List[str]]:
        result = text
        applied_noises = []
        
        insertions = self.COLLOQUIAL_INSERTIONS.get(domain, self.COLLOQUIAL_INSERTIONS["人工智能"])
        
        if random.random() < intensity:
            insertion = random.choice(insertions)
            if random.random() < 0.5:
                result = insertion + result
            else:
                words = result.split()
                if len(words) > 2:
                    insert_pos = random.randint(1, len(words) - 1)
                    words.insert(insert_pos, insertion)
                    result = ' '.join(words)
            applied_noises.append(NoiseType.COLLOQUIAL_INSERT.value)
        
        if random.random() < intensity * 0.5:
            hesitation = random.choice(self.HESITATIONS)
            if "。" in result:
                parts = result.split("。", 1)
                result = parts[0] + "。" + hesitation + parts[1]
            if NoiseType.COLLOQUIAL_INSERT.value not in applied_noises:
                applied_noises.append(NoiseType.COLLOQUIAL_INSERT.value)
        
        return result, applied_noises

class CapitalizationNoiseGenerator:
    """大小写错误生成器"""
    
    def add_capitalization_noise(self, text: str, intensity: float = 0.1) -> Tuple[str, List[str]]:
        result = text
        applied_noises = []
        
        if random.random() < intensity:
            words = result.split()
            for i, word in enumerate(words):
                if len(word) > 2 and word.isalpha() and random.random() < 0.3:
                    if word[0].isupper() and word[1:].islower():
                        words[i] = word.lower()
                    elif word.islower():
                        words[i] = word.capitalize()
                    elif random.random() < 0.5:
                        words[i] = word.upper()
                    else:
                        words[i] = word.lower()
                    if NoiseType.CAPITALIZATION_ERROR.value not in applied_noises:
                        applied_noises.append(NoiseType.CAPITALIZATION_ERROR.value)
            result = ' '.join(words)
        
        if random.random() < intensity * 0.3:
            chars = list(result)
            for i, char in enumerate(chars):
                if char.isalpha() and random.random() < 0.1:
                    chars[i] = char.swapcase()
            result = ''.join(chars)
            if NoiseType.CAPITALIZATION_ERROR.value not in applied_noises:
                applied_noises.append(NoiseType.CAPITALIZATION_ERROR.value)
        
        return result, applied_noises

class PunctuationNoiseGenerator:
    """标点符号错误生成器"""
    
    def add_punctuation_noise(self, text: str, intensity: float = 0.1) -> Tuple[str, List[str]]:
        result = text
        applied_noises = []
        
        if random.random() < intensity:
            result = result.replace('。', '.').replace('，', ',').replace('：', ':')
            applied_noises.append(NoiseType.PUNCTUATION_ERROR.value)
        
        if random.random() < intensity * 0.5:
            result = result.replace('.', '。').replace(',', '，').replace(':', '：')
            if NoiseType.PUNCTUATION_ERROR.value not in applied_noises:
                applied_noises.append(NoiseType.PUNCTUATION_ERROR.value)
        
        if random.random() < intensity * 0.3:
            result = result.replace('.', '!').replace('。', '！')
            if NoiseType.PUNCTUATION_ERROR.value not in applied_noises:
                applied_noises.append(NoiseType.PUNCTUATION_ERROR.value)
        
        if random.random() < intensity * 0.2:
            result = result.replace(' ', '  ').replace('  ', '   ')
            if NoiseType.WHITESPACE_ERROR.value not in applied_noises:
                applied_noises.append(NoiseType.WHITESPACE_ERROR.value)
        
        return result, applied_noises

class NoiseGenerator:
    """噪音生成器 - 统一入口"""
    
    def __init__(self):
        self.ocr = OCRNoiseGenerator()
        self.asr = ASRNoiseGenerator()
        self.spelling = SpellingNoiseGenerator()
        self.format = FormatNoiseGenerator()
        self.colloquial = ColloquialNoiseGenerator()
        self.capitalization = CapitalizationNoiseGenerator()
        self.punctuation = PunctuationNoiseGenerator()
    
    def generate_noisy_text(self, text_clean: str, domain: str = "人工智能",
                           noise_level: int = 2) -> NoiseResult:
        result = text_clean
        all_noises = []
        
        level_intensities = {
            0: 0.0,
            1: 0.05,
            2: 0.15,
            3: 0.30,
            4: 0.50,
        }
        
        intensity = level_intensities.get(noise_level, 0.15)
        
        if intensity == 0:
            return NoiseResult(
                text_clean=text_clean,
                text_noisy=text_clean,
                noise_types=[],
                noise_level=0
            )
        
        noise_functions = [
            (self.ocr.add_ocr_noise, {"domain": domain}),
            (self.asr.add_asr_noise, {}),
            (self.spelling.add_spelling_noise, {"domain": domain}),
            (self.format.add_format_noise, {}),
            (self.colloquial.add_colloquial_noise, {"domain": domain}),
            (self.capitalization.add_capitalization_noise, {}),
            (self.punctuation.add_punctuation_noise, {}),
        ]
        
        random.shuffle(noise_functions)
        
        for func, kwargs in noise_functions:
            if random.random() < intensity:
                result, noises = func(result, intensity=intensity, **kwargs)
                all_noises.extend(noises)
        
        all_noises = list(set(all_noises))
        
        return NoiseResult(
            text_clean=text_clean,
            text_noisy=result,
            noise_types=all_noises,
            noise_level=noise_level,
            noise_details={
                "intensity": intensity,
                "noise_count": len(all_noises)
            }
        )
    
    def generate_with_labels(self, text_clean: str, domain: str = "人工智能",
                            noise_level: int = 2) -> Dict:
        result = self.generate_noisy_text(text_clean, domain, noise_level)
        
        return {
            "text_clean": result.text_clean,
            "text_noisy": result.text_noisy,
            "noise_types": result.noise_types,
            "noise_level": result.noise_level,
            "noise_details": result.noise_details
        }


noise_generator = NoiseGenerator()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("噪音生成器测试")
    print("="*70)
    
    test_texts = [
        "The patient requires immediate treatment for their symptoms.",
        "Investment portfolio management is crucial for financial success.",
        "劳动合同的签订需要双方协商一致。",
    ]
    
    domains = ["医疗", "金融", "劳动合同"]
    
    print("\n[1] 噪音级别梯度测试")
    print("-"*70)
    
    for level in range(5):
        result = noise_generator.generate_noisy_text(test_texts[0], "医疗", level)
        print(f"\nLevel {level}:")
        print(f"  原文: {result.text_clean[:50]}...")
        print(f"  噪音: {result.text_noisy[:50]}...")
        print(f"  类型: {result.noise_types}")
    
    print("\n\n[2] 噪音类型展示")
    print("-"*70)
    
    for i, (text, domain) in enumerate(zip(test_texts, domains)):
        result = noise_generator.generate_with_labels(text, domain, 3)
        print(f"\n[{domain}]")
        print(f"  text_clean: {result['text_clean'][:40]}...")
        print(f"  text_noisy:  {result['text_noisy'][:40]}...")
        print(f"  noise_types: {result['noise_types']}")
        print(f"  noise_level: {result['noise_level']}")
    
    print("\n\n[3] 批量噪音分布测试")
    print("-"*70)
    
    noise_type_counts = {}
    for _ in range(100):
        result = noise_generator.generate_noisy_text(test_texts[0], "医疗", 2)
        for nt in result.noise_types:
            noise_type_counts[nt] = noise_type_counts.get(nt, 0) + 1
    
    print(f"  生成100条噪音数据，噪音类型分布:")
    for nt, count in sorted(noise_type_counts.items(), key=lambda x: -x[1]):
        print(f"    {nt}: {count}次 ({count}%)")
    
    print("\n" + "="*70)
    print("测试完成")
    print("="*70)
